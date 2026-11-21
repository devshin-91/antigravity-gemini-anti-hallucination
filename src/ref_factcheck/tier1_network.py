"""Tier 1: Zero-LLM-token network bibliometric verification with persistent SQLite cache."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import closing
import json
import os
from pathlib import Path
import re
import sqlite3
import ssl
import time
from typing import Any
import urllib.error
import urllib.parse
import urllib.request

from .models import FileCheckSummary, Issue, ReferenceEntry
from .tier0_local import strip_accents

DEFAULT_CACHE_PATH = Path.home() / ".cache" / "agy-ref-factcheck" / "cache.db"
DOI_CACHE_TTL_SEC = 30 * 24 * 3600
URL_CACHE_TTL_SEC = 7 * 24 * 3600
USER_AGENT = "AGYRefFactChecker/2.0 (mailto:research-audit@example.org)"
SSL_CTX = ssl.create_default_context()


class CacheDB:
    """Thread/process-safe SQLite WAL cache for DOI, PubMed, and URL lookups."""

    def __init__(self, db_path: Path | None = None) -> None:
        env_override = os.environ.get("AGY_FACTCHECK_CACHE_DB")
        self.db_path = db_path or (Path(env_override) if env_override else DEFAULT_CACHE_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_db(self) -> None:
        with closing(self._connect()) as conn:
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS verification_cache (
                        cache_key TEXT PRIMARY KEY,
                        provider TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        fetched_at REAL NOT NULL
                    )
                    """
                )

    def get(self, cache_key: str, ttl_sec: int) -> dict[str, Any] | None:
        now = time.time()
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT payload_json, fetched_at FROM verification_cache WHERE cache_key = ?",
                (cache_key,),
            ).fetchone()
        if not row:
            return None
        payload_json, fetched_at = row
        if (now - float(fetched_at)) > ttl_sec:
            return None
        try:
            return json.loads(payload_json)
        except json.JSONDecodeError:
            return None

    def set(self, cache_key: str, provider: str, payload: dict[str, Any]) -> None:
        with closing(self._connect()) as conn:
            with conn:
                conn.execute(
                    """
                    INSERT INTO verification_cache(cache_key, provider, payload_json, fetched_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(cache_key) DO UPDATE SET
                        provider=excluded.provider,
                        payload_json=excluded.payload_json,
                        fetched_at=excluded.fetched_at
                    """,
                    (cache_key, provider, json.dumps(payload, ensure_ascii=False), time.time()),
                )


def _http_get_json(
    url: str,
    timeout: int = 12,
    accept: str = "application/json",
    retries: int = 2,
) -> tuple[int | str, dict[str, Any] | None]:
    for attempt in range(retries + 1):
        req = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": accept},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                return resp.status, json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < retries:
                time.sleep(0.35 * (2**attempt))
                continue
            return e.code, None
        except Exception as e:
            if attempt < retries:
                time.sleep(0.25 * (2**attempt))
                continue
            return f"ERR:{e}", None
    return "ERR:exhausted", None


def _http_head_or_get(url: str, timeout: int = 10) -> tuple[int | str, str]:
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
                return resp.status, resp.geturl()
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue
            return e.code, e.geturl() if hasattr(e, "geturl") else url
        except Exception as e:
            if method == "HEAD":
                continue
            return f"ERR:{e}", url
    return "ERR:unknown", url


def _parse_csl_meta(csl: dict[str, Any]) -> dict[str, Any]:
    """Normalize CSL-JSON metadata (from doi.org content negotiation) into common schema."""
    years: set[int] = set()
    for field in ("issued", "published-print", "published-online", "created"):
        parts = csl.get(field, {}).get("date-parts", [])
        if parts and parts[0] and isinstance(parts[0][0], int):
            years.add(parts[0][0])
    authors = [
        {"family": a.get("family", ""), "given": a.get("given", "")}
        for a in csl.get("author", [])
        if a.get("family") or a.get("given")
    ]
    return {
        "title": csl.get("title", ""),
        "subtitle": csl.get("subtitle", "") if isinstance(csl.get("subtitle"), str) else "",
        "original_title": "",
        "authors": authors,
        "container": csl.get("container-title", ""),
        "volume": str(csl.get("volume", "")),
        "issue": str(csl.get("issue", "")),
        "page": str(csl.get("page", "")),
        "article_number": str(csl.get("article-number", "")),
        "years": sorted(years),
    }


def fetch_doi_metadata(
    doi: str,
    cache: CacheDB,
    use_cache: bool = True,
) -> tuple[dict[str, Any], bool]:
    """Fetch DOI metadata from Crossref (+ CSL-JSON & Handle fallback) using SQLite cache."""
    norm_doi = doi.strip().lower()
    cache_key = f"doi:{norm_doi}"
    if use_cache:
        cached = cache.get(cache_key, DOI_CACHE_TTL_SEC)
        if cached is not None:
            return cached, True

    quoted = urllib.parse.quote(doi.strip(), safe="/")
    cr_status, cr_data = _http_get_json(f"https://api.crossref.org/works/{quoted}")
    result: dict[str, Any] = {
        "doi": doi.strip(),
        "crossref_status": cr_status,
        "provider": "crossref",
        "handle_status": None,
        "handle_response_code": None,
        "handle_url": None,
        "meta": None,
    }

    if cr_status == 200 and cr_data and "message" in cr_data:
        msg = cr_data["message"]
        years: set[int] = set()
        for field in ("published-print", "published-online", "issued", "created"):
            parts = msg.get(field, {}).get("date-parts", [])
            if parts and parts[0] and isinstance(parts[0][0], int):
                years.add(parts[0][0])

        authors = []
        for a in msg.get("author", []):
            fam = a.get("family", "")
            giv = a.get("given", "")
            if fam or giv:
                authors.append({"family": fam, "given": giv})

        result["meta"] = {
            "title": (msg.get("title") or [""])[0],
            "subtitle": (msg.get("subtitle") or [""])[0] if msg.get("subtitle") else "",
            "original_title": (msg.get("original-title") or [""])[0] if msg.get("original-title") else "",
            "authors": authors,
            "container": (msg.get("container-title") or [""])[0],
            "volume": str(msg.get("volume", "")),
            "issue": str(msg.get("issue", "")),
            "page": str(msg.get("page", "")),
            "article_number": str(msg.get("article-number", "")),
            "years": sorted(years),
        }
    else:
        # Fallback 1: doi.org CSL-JSON Content Negotiation (also covers DataCite/KCI when Crossref throttles)
        csl_status, csl_data = _http_get_json(
            f"https://doi.org/{quoted}",
            accept="application/vnd.citationstyles.csl+json",
            retries=1,
        )
        if csl_status == 200 and isinstance(csl_data, dict) and csl_data.get("title"):
            result["crossref_status"] = 200
            result["provider"] = "doi_csl_fallback"
            result["meta"] = _parse_csl_meta(csl_data)
        else:
            # Fallback 2: DOI Handle API existence check
            h_status, h_data = _http_get_json(f"https://doi.org/api/handles/{quoted}", retries=1)
            result["handle_status"] = h_status
            if h_status == 200 and h_data:
                result["handle_response_code"] = h_data.get("responseCode")
                for v in h_data.get("values", []):
                    if v.get("type") == "URL":
                        result["handle_url"] = v.get("data", {}).get("value")

    # Only cache complete metadata hits (avoid pinning transient 429 partial records into long-TTL cache)
    if use_cache and result.get("meta") is not None:
        cache.set(cache_key, result["provider"], result)
    return result, False


def _extract_title_words(text: str) -> set[str]:
    clean = strip_accents(re.sub(r"<[^>]+>", " ", text))
    words = set(re.findall(r"[a-z0-9]{3,}|[가-힣]{2,}", clean))
    stop = {"the", "and", "for", "with", "from", "that", "this", "are", "into", "study", "analysis"}
    return words - stop


def _compare_doi_metadata(
    file_path: Path,
    ref: ReferenceEntry,
    record: dict[str, Any],
    summary: FileCheckSummary,
) -> None:
    """Compare ReferenceEntry fields against Crossref/Handle metadata with zero LLM tokens."""
    cr_status = record.get("crossref_status")
    meta = record.get("meta")
    if cr_status != 200 or not meta:
        if record.get("handle_response_code") == 1:
            summary.issues.append(
                Issue(
                    code="DOI_NO_CROSSREF_META",
                    severity="WARN",
                    track="academic_ref",
                    file=str(file_path),
                    line=ref.line,
                    target=f"doi:{ref.doi}",
                    message=f"DOI resolves via Handle API ({record.get('handle_url')}) but lacks Crossref metadata (status={cr_status}).",
                )
            )
            return
        summary.issues.append(
            Issue(
                code="INVALID_OR_DEAD_DOI",
                severity="FAIL",
                track="academic_ref",
                file=str(file_path),
                line=ref.line,
                target=f"doi:{ref.doi}",
                message=f"DOI does not resolve in Crossref (HTTP {cr_status}) or DOI Handle API (code={record.get('handle_response_code')}).",
                expected="HTTP 200 in Crossref or Handle responseCode=1",
                actual=f"crossref={cr_status}, handle={record.get('handle_status')}",
                fix_hint="Verify the exact DOI string against publisher page or remove fabricated DOI.",
            )
        )
        return

    # 1. Year check
    ref_yr_m = re.match(r"(\d{4})", ref.year)
    if ref_yr_m and meta.get("years"):
        ref_yr = int(ref_yr_m.group(1))
        if ref_yr not in meta["years"]:
            summary.issues.append(
                Issue(
                    code="DOI_YEAR_MISMATCH",
                    severity="FAIL",
                    track="academic_ref",
                    file=str(file_path),
                    line=ref.line,
                    target=f"doi:{ref.doi}",
                    message=f"Cited year ({ref_yr}) does not match Crossref publication years {meta['years']}.",
                    expected=str(meta["years"]),
                    actual=str(ref_yr),
                    fix_hint=f"Update publication year to {meta['years'][0]} or verify DOI.",
                )
            )

    # 2. First author surname check (English entries; Korean authors may be romanized in Crossref)
    cr_authors = meta.get("authors") or []
    if cr_authors and not ref.is_korean:
        cr_first_fam = strip_accents(cr_authors[0].get("family", ""))
        # Handle multi-part or hyphenated names ("de Ridder" vs "Kroese")
        if cr_first_fam and ref.first_author_key not in cr_first_fam and cr_first_fam not in ref.first_author_key:
            summary.issues.append(
                Issue(
                    code="DOI_AUTHOR_MISMATCH",
                    severity="FAIL",
                    track="academic_ref",
                    file=str(file_path),
                    line=ref.line,
                    target=f"doi:{ref.doi}",
                    message=f"First author {ref.first_author_key!r} mismatches Crossref author {cr_authors[0].get('family')!r}.",
                    expected=cr_authors[0].get("family", ""),
                    actual=ref.first_author_key,
                    fix_hint="Correct the author list or replace mismatched DOI.",
                )
            )

    # 3. Title overlap check (only when both draft title and Crossref title share script)
    draft_title = ref.title_hint
    cr_title_full = f"{meta.get('title', '')} {meta.get('subtitle', '')} {meta.get('original_title', '')}".strip()
    draft_has_latin = bool(re.search(r"[A-Za-z]{4,}", draft_title))
    cr_has_latin = bool(re.search(r"[A-Za-z]{4,}", cr_title_full))
    if draft_has_latin and cr_has_latin and not ref.is_korean:
        dw = _extract_title_words(draft_title)
        cw = _extract_title_words(cr_title_full)
        if dw and cw:
            jaccard_like = len(dw & cw) / min(len(dw), len(cw))
            if jaccard_like < 0.35:
                summary.issues.append(
                    Issue(
                        code="DOI_TITLE_MISMATCH",
                        severity="FAIL",
                        track="academic_ref",
                        file=str(file_path),
                        line=ref.line,
                        target=f"doi:{ref.doi}",
                        message="Draft paper title has low token overlap with Crossref title for this DOI.",
                        expected=meta.get("title", ""),
                        actual=draft_title[:120],
                        fix_hint="Verify that the DOI corresponds to the cited article.",
                    )
                )

    # 4. Volume mismatch check (normalize prefixes like "Volume 11" or "Vol. 11")
    cr_vol_raw = meta.get("volume", "").strip()
    cr_vol = re.sub(r"^(?:vol(?:ume)?\.?\s*)", "", cr_vol_raw, flags=re.I).strip()
    if ref.volume_hint and cr_vol and ref.volume_hint != cr_vol:
        summary.issues.append(
            Issue(
                code="DOI_VOLUME_MISMATCH",
                severity="FAIL",
                track="academic_ref",
                file=str(file_path),
                line=ref.line,
                target=f"doi:{ref.doi}",
                message=f"Cited volume {ref.volume_hint!r} disagrees with Crossref volume {cr_vol_raw!r}.",
                expected=cr_vol,
                actual=ref.volume_hint,
                fix_hint=f"Update volume number to {cr_vol}.",
            )
        )


def run_tier1_network_check(
    file_path: Path,
    refs: list[ReferenceEntry],
    summary: FileCheckSummary,
    cache: CacheDB | None = None,
    use_cache: bool = True,
    max_workers: int = 3,
) -> None:
    """Verify all DOI references in parallel against Crossref/Handle + SQLite cache."""
    doi_refs = [r for r in refs if r.doi]
    if not doi_refs:
        return

    db = cache or CacheDB()
    results: dict[int, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        fut_map = {
            pool.submit(fetch_doi_metadata, r.doi or "", db, use_cache): r
            for r in doi_refs
        }
        for fut in as_completed(fut_map):
            ref = fut_map[fut]
            try:
                rec, from_cache = fut.result()
                results[ref.index] = rec
                if from_cache:
                    summary.network_cache_hits += 1
                else:
                    summary.network_live_calls += 1
            except Exception as exc:
                summary.network_live_calls += 1
                summary.issues.append(
                    Issue(
                        code="DOI_LOOKUP_ERROR",
                        severity="WARN",
                        track="academic_ref",
                        file=str(file_path),
                        line=ref.line,
                        target=f"doi:{ref.doi}",
                        message=f"DOI lookup raised exception: {exc}",
                    )
                )

    for ref in doi_refs:
        if ref.index in results:
            _compare_doi_metadata(file_path, ref, results[ref.index], summary)
