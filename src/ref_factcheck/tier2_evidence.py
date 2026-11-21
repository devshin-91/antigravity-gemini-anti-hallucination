"""Tier 2: Minimal-snippet PDF evidence slicer and lightweight-model semantic verifier."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any

from .dirty_state import compute_sha256
from .models import ReferenceEntry
from .tier0_local import parse_academic_document, strip_accents

POPPLER_FALLBACK = Path(r"C:\Users\ckstn\.agents\poppler\Library\bin\pdftotext.exe")

KOREAN_SURNAME_ROMANIZATION: dict[str, list[str]] = {
    "안": ["ahn", "an"],
    "노": ["noh", "roh"],
    "최": ["choi", "choe"],
    "이": ["lee", "yi", "rhee"],
    "김": ["kim"],
    "정": ["jung", "jeong", "chung"],
    "박": ["park", "pak"],
    "강": ["kang"],
    "조": ["cho", "jo"],
    "윤": ["yoon", "yun"],
    "장": ["jang", "chang"],
    "임": ["lim", "im"],
    "한": ["han"],
    "오": ["oh"],
    "서": ["seo", "suh"],
    "신": ["shin", "sin"],
    "권": ["kwon"],
    "황": ["hwang"],
    "송": ["song"],
    "유": ["yoo", "yu"],
}


def find_pdftotext() -> str | None:
    exe = shutil.which("pdftotext")
    if exe:
        return exe
    if POPPLER_FALLBACK.exists():
        return str(POPPLER_FALLBACK)
    return None


def extract_pdf_pages(pdf_path: Path, cache_dir: Path | None = None) -> list[str]:
    """Extract per-page text via Poppler pdftotext, cached by PDF SHA-256."""
    sha = compute_sha256(pdf_path)[:16]
    cdir = cache_dir or (Path.home() / ".cache" / "agy-ref-factcheck" / "pdf_pages")
    cdir.mkdir(parents=True, exist_ok=True)
    cache_file = cdir / f"{sha}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    exe = find_pdftotext()
    if not exe:
        raise RuntimeError("pdftotext executable not found on PATH or poppler fallback.")

    proc = subprocess.run(
        [exe, "-enc", "UTF-8", str(pdf_path), "-"],
        capture_output=True,
        check=True,
    )
    raw_text = proc.stdout.decode("utf-8", errors="replace")
    pages = [p.strip() for p in raw_text.split("\x0c")]
    while pages and not pages[-1]:
        pages.pop()
    cache_file.write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")
    return pages


def match_local_pdf(ref: ReferenceEntry, references_dir: Path) -> Path | None:
    """Match a ReferenceEntry to a PDF file inside references_dir by year + surname/romanization."""
    if not references_dir.exists():
        return None
    pdfs = sorted(references_dir.glob("*.pdf"))
    yr_m = re.match(r"(\d{4})", ref.year)
    yr = yr_m.group(1) if yr_m else ""

    candidates: list[str] = []
    if ref.is_korean and ref.first_author_key:
        surname_char = ref.first_author_key[0]
        candidates.extend(KOREAN_SURNAME_ROMANIZATION.get(surname_char, []))
        candidates.append(ref.first_author_key)
    else:
        candidates.append(ref.first_author_key.split("-")[0])

    best: tuple[int, Path] | None = None
    for pdf in pdfs:
        stem_low = strip_accents(pdf.stem)
        score = 0
        if yr and yr in stem_low:
            score += 2
        for c in candidates:
            if c and c in stem_low:
                score += 3
                break
        if score >= 5 and (best is None or score > best[0]):
            best = (score, pdf)
    return best[1] if best else None


def _extract_claim_numbers(sentence: str) -> list[str]:
    """Extract signed numeric/statistical anchors (preserving minus signs, skipping years/ordinals)."""
    cleaned = re.sub(r"\((?:19|20)\d{2}[a-z]?\)", " ", sentence)
    anchors: list[str] = []
    for m in re.finditer(r"([-−]?\s*\d+(?:[.,]\d+)?|[-−]?\s*\.\d+)", cleaned):
        raw = m.group(1).replace("−", "-").replace(" ", "")
        unsigned = raw.lstrip("-")
        if re.fullmatch(r"(?:19|20)\d{2}", unsigned):
            continue
        # Only preserve leading '-' when paired with '=' or directly attached to decimal/number (avoid range "15-30")
        before = cleaned[max(0, m.start() - 4) : m.start()]
        is_range_hyphen = raw.startswith("-") and bool(re.search(r"\d\s*$", before))
        if is_range_hyphen:
            raw = unsigned
        norm = ("-" + "0" + raw[1:]) if raw.startswith("-.") else (("0" + raw) if raw.startswith(".") else raw)
        norm = norm.replace(",", "")
        after = cleaned[m.end() : m.end() + 6]
        has_unit_or_stat = bool(
            re.match(r"^\s*(?:%|분|시간|명|편|세|dB|lux|ppm|°C|배)", after, re.I)
            or re.search(r"[=<>±~]\s*$", before)
        )
        if "." not in norm and len(norm.lstrip("-")) == 1 and not has_unit_or_stat:
            continue
        if norm not in anchors:
            anchors.append(norm)
    return anchors


_ONES = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def _english_number_word_pattern(n_str: str) -> str | None:
    """Return regex pattern for 2-digit integer written in English words (e.g., 43 -> forty[- ]?three)."""
    if not n_str.isdigit():
        return None
    val = int(n_str)
    if 21 <= val <= 99 and val % 10 != 0:
        return rf"{_TENS[val // 10]}[- ]?{_ONES[val % 10]}"
    if 20 <= val <= 90 and val % 10 == 0:
        return _TENS[val // 10]
    return None


def _is_bibliography_header(page_text: str) -> bool:
    """Detect the start of the References/Bibliography section (excluding data tables)."""
    if re.search(r"(?m)^\s*(?:references|bibliography|참고\s*문헌)\s*$", page_text.lower()):
        return True
    doi_hits = len(re.findall(r"doi:\s*10\.|https?://(?:dx\.)?doi\.org/", page_text, re.I))
    return doi_hits >= 4


def slice_relevant_snippets(
    pages: list[str],
    claim_sentence: str,
    window_chars: int = 550,
    max_windows: int = 4,
    max_per_page: int = 1,
) -> list[dict[str, Any]]:
    """Slice minimal +-3 sentence / window_chars excerpts via signed-anchor greedy set-cover across body pages."""
    anchors = _extract_claim_numbers(claim_sentence)
    ascii_terms = [
        t.lower()
        for t in re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", claim_sentence)
        if t.lower() not in {"that", "with", "from", "this", "have", "were", "sleep", "al"}
    ]

    bib_start_page: int | None = None
    for page_idx, page_text in enumerate(pages, 1):
        if page_idx >= max(2, len(pages) // 2) and _is_bibliography_header(page_text):
            bib_start_page = page_idx
            break

    body_page_count = (bib_start_page - 1) if bib_start_page else len(pages)
    # Each candidate: (score, page_idx, offset, snippet, matched_anchors_set)
    candidates: list[tuple[float, int, int, str, set[str]]] = []
    for page_idx, page_text in enumerate(pages, 1):
        if bib_start_page and page_idx >= bib_start_page:
            continue
        norm_page = page_text.replace(",", "").replace("−", "-").replace("–", "-")
        low_page = norm_page.lower()
        hit_positions: list[tuple[int, float, str | None]] = []

        for anc in anchors:
            if anc.startswith("-"):
                pat = rf"(?:-\s*{re.escape(anc[1:])})(?!\d)"
            else:
                pat = rf"(?<![\d\.\-]){re.escape(anc)}(?!\d)"
                en_word = _english_number_word_pattern(anc)
                if en_word:
                    pat = rf"(?:{pat}|\b{en_word}\b)"
            w = 6.0 if "." in anc or len(anc.lstrip("-")) >= 3 else 3.0
            for m in re.finditer(pat, norm_page, re.I):
                ctx_before = norm_page[max(0, m.start() - 6) : m.start()]
                stat_boost = 3.0 if re.search(r"[=<>±]\s*$", ctx_before) else 0.0
                hit_positions.append((m.start(), w + stat_boost, anc))

        for term in dict.fromkeys(ascii_terms):
            w = 4.0 if len(term) >= 4 else 2.5
            for m in re.finditer(rf"(?<![a-z]){re.escape(term)}(?![a-z])", low_page):
                hit_positions.append((m.start(), w, None))

        if not hit_positions:
            continue

        # Reward prose results/statistical reporting over dense raw-table cells
        prose_bonus = 4.0 if re.search(r"\b(?:results|meta-analysis|summary|abstract|conclusion|discussion)\b", low_page) else 0.0
        if re.search(r"\b(?:z|r|d|b|f|t|α|β)\s*=\s*[-−]?\d", low_page) and re.search(r"95%\s*ci|p\s*[<=]|fig\.", low_page):
            prose_bonus += 6.0
        non_empty_lines = [ln.strip() for ln in page_text.splitlines() if ln.strip()]
        avg_line_len = sum(len(ln) for ln in non_empty_lines) / max(len(non_empty_lines), 1)
        if avg_line_len >= 45:
            prose_bonus += 4.0

        hit_positions.sort(key=lambda x: x[0])
        clusters: list[tuple[float, int, set[str]]] = []
        cur_start, cur_score, first_anc = hit_positions[0]
        cur_end = cur_start
        cur_ancs: set[str] = {first_anc} if first_anc else set()
        for pos, w, anc in hit_positions[1:]:
            if pos - cur_end <= window_chars:
                cur_end = pos
                cur_score += w
                if anc:
                    cur_ancs.add(anc)
            else:
                clusters.append((cur_score, (cur_start + cur_end) // 2, cur_ancs))
                cur_start, cur_end, cur_score = pos, pos, w
                cur_ancs = {anc} if anc else set()
        clusters.append((cur_score, (cur_start + cur_end) // 2, cur_ancs))

        for sc, center, anc_set in clusters:
            lo = max(0, center - window_chars // 2)
            hi = min(len(page_text), center + window_chars // 2)
            # Snap to whitespace boundaries so words/numbers are never sliced mid-token
            while lo > 0 and not page_text[lo - 1].isspace():
                lo -= 1
            while hi < len(page_text) and not page_text[hi].isspace():
                hi += 1
            snippet = " ".join(page_text[lo:hi].split())
            final_sc = round(sc + len(anc_set) * 2.0 + prose_bonus, 2)
            candidates.append((final_sc, page_idx, lo, snippet, anc_set))

    # Greedy set-cover selection: reward covering uncovered anchors & distinct body zones
    chosen: list[dict[str, Any]] = []
    covered_ancs: set[str] = set()
    seen_snippets: set[str] = set()
    page_counts: dict[int, int] = {}
    num_body = max(body_page_count, 1)
    covered_zones: set[int] = set()

    remaining = list(candidates)
    while remaining and len(chosen) < max_windows:
        best_idx = -1
        best_gain = -1.0
        for idx, (sc, page_no, _, snip, anc_set) in enumerate(remaining):
            if page_counts.get(page_no, 0) >= max_per_page:
                continue
            if snip[:80] in seen_snippets:
                continue
            uncovered = len(anc_set - covered_ancs)
            zone = min(2, (page_no - 1) * 3 // num_body)
            zone_bonus = 8.0 if zone not in covered_zones else 0.0
            gain = sc + uncovered * 12.0 + zone_bonus
            if gain > best_gain:
                best_gain = gain
                best_idx = idx
        if best_idx < 0:
            break
        sc, page_no, _, snip, anc_set = remaining.pop(best_idx)
        seen_snippets.add(snip[:80])
        page_counts[page_no] = page_counts.get(page_no, 0) + 1
        covered_ancs.update(anc_set)
        covered_zones.add(min(2, (page_no - 1) * 3 // num_body))
        chosen.append({"page": page_no, "score": sc, "snippet": snip})
    return chosen


def build_claim_evidence_bundles(
    draft_path: Path,
    references_dir: Path,
    max_claims: int = 8,
) -> list[dict[str, Any]]:
    """Build compact claim -> local PDF snippet bundles from a markdown draft."""
    lines = draft_path.read_text(encoding="utf-8", errors="replace").splitlines()
    body_lines, refs = parse_academic_document(lines)
    bundles: list[dict[str, Any]] = []
    pdf_cache: dict[Path, list[str]] = {}

    for line_no, line in body_lines:
        if line.lstrip().startswith(("#", "|", ">", "---")) or not line.strip():
            continue
        # Split Korean/English sentences heuristically
        sentences = re.split(r"(?<=[.!?다])\s+", line.strip())
        for sent in sentences:
            anchors = _extract_claim_numbers(sent)
            if not anchors:
                continue
            for ref in refs:
                yr_m = re.match(r"(\d{4})", ref.year)
                yr = yr_m.group(1) if yr_m else ""
                if not yr or yr not in sent:
                    continue
                if ref.first_author_key not in strip_accents(sent) and ref.first_author_key not in sent:
                    continue
                pdf_path = match_local_pdf(ref, references_dir)
                if not pdf_path:
                    continue
                if pdf_path not in pdf_cache:
                    pdf_cache[pdf_path] = extract_pdf_pages(pdf_path)
                pages = pdf_cache[pdf_path]
                snippets = slice_relevant_snippets(pages, sent)
                if not snippets:
                    continue
                full_chars = sum(len(p) for p in pages)
                snip_chars = sum(len(s["snippet"]) for s in snippets)
                bundles.append(
                    {
                        "line": line_no,
                        "ref_index": ref.index,
                        "author": ref.first_author_key,
                        "year": yr,
                        "pdf_file": pdf_path.name,
                        "claim": sent,
                        "anchors": anchors,
                        "full_pdf_chars": full_chars,
                        "snippet_chars": snip_chars,
                        "reduction_pct": round((1 - snip_chars / max(full_chars, 1)) * 100, 1),
                        "snippets": snippets,
                        "full_text": "\n\n".join(
                            f"[p.{i}] {p}" for i, p in enumerate(pages, 1)
                        ),
                    }
                )
                if len(bundles) >= max_claims:
                    return bundles
    return bundles


def verify_bundle_with_genai(
    bundle: dict[str, Any],
    model: str = "gemini-3.8-flash",
    mode: str = "snippet",
    thinking_level: str = "low",
) -> dict[str, Any]:
    """Evaluate claim vs PDF evidence using google-genai Interactions API (current SDK)."""
    from google import genai  # type: ignore

    evidence_text = (
        "\n".join(f"[p.{s['page']}] {s['snippet']}" for s in bundle["snippets"])
        if mode == "snippet"
        else bundle["full_text"]
    )
    prompt = (
        "You are a strict academic numerical fact-checker. Compare the DRAFT CLAIM against the SOURCE EXCERPT.\n"
        "Respond strictly in JSON with keys: verdict ('MATCH' or 'MISMATCH' or 'INSUFFICIENT'), "
        "reason (1 concise sentence).\n\n"
        f"DRAFT CLAIM: {bundle['claim']}\n\n"
        f"SOURCE ({bundle['pdf_file']}):\n{evidence_text}"
    )

    client = genai.Client()
    t0 = time.perf_counter()
    interaction = client.interactions.create(
        model=model,
        input=prompt,
        store=False,
        generation_config={
            "thinking_level": thinking_level,
            "max_output_tokens": 2048,
        },
    )
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

    output_text = getattr(interaction, "output_text", "") or ""
    if not output_text and getattr(interaction, "steps", None):
        parts = []
        for st in interaction.steps:
            if getattr(st, "type", "") == "model_output":
                for c in getattr(st, "content", []) or []:
                    if getattr(c, "type", "") == "text":
                        parts.append(getattr(c, "text", ""))
        output_text = "".join(parts)

    usage = getattr(interaction, "usage", None)
    usage_dict = {
        "input_tokens": getattr(usage, "total_input_tokens", None) or getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "total_output_tokens", None) or getattr(usage, "output_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }

    parsed_verdict = "UNKNOWN"
    m = re.search(r"\{.*\}", output_text, re.S)
    parsed_reason = output_text.strip()
    if m:
        try:
            obj = json.loads(m.group(0))
            parsed_verdict = str(obj.get("verdict", "UNKNOWN")).upper()
            parsed_reason = str(obj.get("reason", ""))
        except Exception:
            pass

    return {
        "model": model,
        "mode": mode,
        "verdict": parsed_verdict,
        "reason": parsed_reason,
        "elapsed_ms": elapsed_ms,
        "usage": usage_dict,
        "prompt_chars": len(prompt),
    }
