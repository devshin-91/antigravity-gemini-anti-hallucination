"""Tier 0: Zero-token, offline deterministic reference and citation checker."""

from __future__ import annotations

import re
import time
import unicodedata
from pathlib import Path
from urllib.parse import unquote

from .dirty_state import compute_sha256
from .models import CitationMention, FileCheckSummary, Issue, ReferenceEntry

FILE_LINK_RE = re.compile(r"\[([^\]]+)\]\(file:///([^#)]+)(?:#L(\d+)(?:-L(\d+))?)?\)")
DOI_RE = re.compile(r"https?://(?:dx\.)?doi\.org/(\S+)")
URL_RE = re.compile(r"https?://[^\s)>\]\"']+")
YEAR_PAREN_RE = re.compile(r"\(((?:19|20)\d{2}[a-z]?)(?:\.\s*\d{1,2}\.\s*\d{1,2}\.?)?\)")
BACKTICK_RE = re.compile(r"`([^`\n]{3,80})`")
REF_HEADING_RE = re.compile(r"^\s{0,3}#{1,4}\s*(?:참고\s*문헌|참고문헌|References|Bibliography)\s*$", re.I)

RULE_BUDGET_FILENAMES = {"GEMINI.md", "GEMINI.ko.md", "GEMINI.en.md", "AGENTS.md"}
AGY_RULE_MAX_BYTES = 24_000

STOP_TOKENS = {
    "file", "line", "lines", "docs", "skill", "skills", "guide", "readme", "code",
    "check", "pass", "fail", "note", "http", "https", "true", "false", "none", "null",
    "json", "yaml", "python", "markdown", "section", "table", "figure",
}

NON_AUTHOR_PREFIXES = {
    "그림", "표", "예", "예컨대", "참고", "단", "주", "약", "총", "평균", "각", "즉",
    "fig", "figure", "table", "step", "phase", "draft", "version", "see", "e.g", "i.e",
    "ci", "sd", "se", "or", "and", "vs", "n", "p", "r", "f", "t", "b", "z",
}


def strip_accents(text: str) -> str:
    """Normalize accented Latin characters (e.g., Borbély -> borbely) for matching."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch)).lower().strip()


def _extract_semantic_tokens(text: str) -> set[str]:
    tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_.\-]{2,}|[가-힣]{2,}|\d+\.\d+", text))
    cleaned: set[str] = set()
    for tok in tokens:
        low = tok.lower().strip(".,:;()[]{}")
        if len(low) >= 3 and low not in STOP_TOKENS:
            cleaned.add(low)
    return cleaned


def check_local_file_references(
    path: Path,
    lines: list[str],
    summary: FileCheckSummary,
    check_rule_budget: bool | None = None,
) -> None:
    """Verify file:/// references, line ranges, context quote alignment, and AGY 24KB budget."""
    raw_bytes = path.read_bytes()
    should_check_budget = (
        check_rule_budget if check_rule_budget is not None else path.name in RULE_BUDGET_FILENAMES
    )
    if should_check_budget and len(raw_bytes) > AGY_RULE_MAX_BYTES:
        summary.issues.append(
            Issue(
                code="RULE_BUDGET_EXCEEDED",
                severity="FAIL",
                track="rule_budget",
                file=str(path),
                line=1,
                target=path.name,
                message=f"Rule file size {len(raw_bytes)} bytes exceeds AGY {AGY_RULE_MAX_BYTES}-byte limit.",
                expected=f"<= {AGY_RULE_MAX_BYTES} bytes",
                actual=f"{len(raw_bytes)} bytes",
                fix_hint="Trim or move bulky reference details into Progressive Disclosure skill references/.",
            )
        )

    line_cache: dict[Path, list[str]] = {}
    for line_no, line in enumerate(lines, 1):
        for m in FILE_LINK_RE.finditer(line):
            summary.local_refs_checked += 1
            label, raw_target, l_start_s, l_end_s = m.groups()
            target_path = Path(unquote(raw_target))
            if not target_path.exists():
                summary.issues.append(
                    Issue(
                        code="MISSING_LOCAL_FILE",
                        severity="FAIL",
                        track="local_ref",
                        file=str(path),
                        line=line_no,
                        target=m.group(0),
                        message=f"Referenced local file does not exist: {target_path}",
                        expected="existing file path",
                        actual=str(target_path),
                        fix_hint="Verify the exact file path using find/ls/read_file before citing.",
                    )
                )
                continue

            if not l_start_s:
                continue

            if target_path not in line_cache:
                try:
                    line_cache[target_path] = target_path.read_text(
                        encoding="utf-8", errors="replace"
                    ).splitlines()
                except OSError as exc:
                    summary.issues.append(
                        Issue(
                            code="UNREADABLE_LOCAL_FILE",
                            severity="FAIL",
                            track="local_ref",
                            file=str(path),
                            line=line_no,
                            target=str(target_path),
                            message=f"Failed to read referenced file: {exc}",
                        )
                    )
                    continue

            target_lines = line_cache[target_path]
            total = len(target_lines)
            s = int(l_start_s)
            e = int(l_end_s) if l_end_s else s
            if not (1 <= s <= e <= total):
                summary.issues.append(
                    Issue(
                        code="LINE_RANGE_OUT_OF_BOUNDS",
                        severity="FAIL",
                        track="local_ref",
                        file=str(path),
                        line=line_no,
                        target=f"{target_path.name}#L{s}-L{e}",
                        message=f"Cited range L{s}-L{e} out of bounds for {target_path.name} ({total} lines).",
                        expected=f"1 <= start <= end <= {total}",
                        actual=f"L{s}-L{e}",
                        fix_hint=f"Read {target_path.name} and update the line range within 1..{total}.",
                    )
                )
                continue

            cited_block = "\n".join(target_lines[s - 1 : e]).lower()
            # Collect verbatim/code evidence tokens from:
            # (a) ASCII identifiers inside label parenthetical hints,
            # (b) inline backticks on same line,
            # (c) adjacent quote block lines starting with '>'.
            # Korean summary translations inside link labels are excluded to avoid cross-lingual false positives.
            context_pieces: list[str] = []
            paren_in_label = re.findall(r"\(([^)]+)\)", label)
            for p in paren_in_label:
                ascii_ids = re.findall(r"[A-Za-z_][A-Za-z0-9_.\-]{2,}", p)
                context_pieces.extend(ascii_ids)
            for bt in BACKTICK_RE.findall(line):
                if bt not in m.group(0):
                    context_pieces.append(bt)
            for offset in (-2, -1, 1, 2):
                idx = line_no - 1 + offset
                if 0 <= idx < len(lines):
                    adj = lines[idx].strip()
                    if adj.startswith(">"):
                        context_pieces.append(adj.lstrip("> "))

            if context_pieces:
                expected_tokens = _extract_semantic_tokens(" ".join(context_pieces))
                stem_low = target_path.stem.lower()
                expected_tokens.discard(stem_low)
                if len(expected_tokens) >= 2:
                    matched = [t for t in expected_tokens if t in cited_block]
                    overlap = len(matched) / len(expected_tokens)
                    if overlap == 0.0:
                        summary.issues.append(
                            Issue(
                                code="LINE_SEMANTIC_MISMATCH",
                                severity="FAIL",
                                track="local_ref",
                                file=str(path),
                                line=line_no,
                                target=f"{target_path.name}#L{s}-L{e}",
                                message=(
                                    "None of the adjacent quote/backtick/identifier tokens appear in "
                                    f"{target_path.name}#L{s}-L{e} (likely shifted line numbers)."
                                ),
                                expected=f"tokens like {sorted(expected_tokens)[:5]}",
                                actual=f"lines {s}-{e} lack all expected tokens",
                                fix_hint=f"Re-read {target_path.name} around L{s}-L{e} and fix line numbers.",
                            )
                        )


def _normalize_author_key(raw_lead: str) -> tuple[str, bool, bool]:
    """Return (normalized_first_author_key, is_korean, is_solo)."""
    s = raw_lead.strip()
    is_korean = bool(re.match(r"^[가-힣]", s))
    if is_korean:
        # Multi-author Korean: "김선희" vs "노해림, 권오진, 심은정" vs "통계청"
        parts = [p.strip() for p in re.split(r"[,·&]", s) if p.strip()]
        is_solo = len(parts) <= 1 and " 등" not in s and "외" not in s
        first = parts[0] if parts else s
        return first, True, is_solo

    # English APA: "Borbély, A. A., Daan, S., & Deboer, T." or "Hilditch, C. J., & McHill, A. W."
    # Institutional English: "World Health Organization" (no comma)
    is_solo = "&" not in s and len(re.findall(r",\s*[A-Z]\.", s)) <= 1
    if "," in s:
        first_surname = s.split(",", 1)[0].strip()
    else:
        first_surname = s.strip()
    return strip_accents(first_surname), False, is_solo


def _apa_sort_key(ref: ReferenceEntry) -> tuple[int, str, str, int, str]:
    """Compute APA 7th comparison key (Korean first, then English alphabetical)."""
    lang_group = 0 if ref.is_korean else 1
    solo_rank = 0 if ref.is_solo else 1
    if ref.is_korean:
        return (lang_group, ref.first_author_key, ref.authors_raw, solo_rank, ref.year)

    # Extract first author's given initials after first comma: "Borbély, A. A." -> "a a"
    first_part = ref.authors_raw.split("&")[0]
    pieces = [p.strip() for p in first_part.split(",")]
    initials = strip_accents(pieces[1]) if len(pieces) > 1 else ""
    # Strip extra authors from initials if single-author detection missed
    initials = re.sub(r"[^a-z\s]", "", initials).strip()
    return (lang_group, ref.first_author_key, initials, solo_rank, ref.year)


def parse_academic_document(lines: list[str]) -> tuple[list[tuple[int, str]], list[ReferenceEntry]]:
    """Split markdown into body lines (excluding references/appendices) and ReferenceEntry list."""
    ref_heading_idx: int | None = None
    for idx, line in enumerate(lines):
        if REF_HEADING_RE.match(line):
            ref_heading_idx = idx
            break

    if ref_heading_idx is None:
        return list(enumerate(lines, 1)), []

    body_lines = [(idx + 1, line) for idx, line in enumerate(lines[:ref_heading_idx])]
    refs: list[ReferenceEntry] = []

    for idx in range(ref_heading_idx + 1, len(lines)):
        line_no = idx + 1
        s = lines[idx].strip()
        if not s:
            continue
        if s == "---" or re.match(r"^#{1,4}\s+", s):
            break
        entry_m = re.match(r"^(?:[\*\-]|\d+\.)\s+(.*)$", s)
        if not entry_m:
            continue
        entry = entry_m.group(1).strip()
        yr_m = YEAR_PAREN_RE.search(entry)
        if not yr_m:
            continue
        year = yr_m.group(1)
        authors_raw = entry[: yr_m.start()].strip().rstrip(".")
        rest = entry[yr_m.end() :].strip().lstrip(". ")

        doi_m = DOI_RE.search(entry)
        doi = doi_m.group(1).rstrip(".,)") if doi_m else None
        url_m = URL_RE.search(entry)
        url = url_m.group(0).rstrip(".,)") if url_m else None

        # Extract title / journal hints split around first italicized segment *Journal*
        title_hint = rest
        journal_hint = ""
        vol_hint = ""
        pages_hint = ""
        ital_m = re.search(r"\*([^*]+)\*(?:,\s*\*([^*]+)\*(?:\(([^)]+)\))?(?:,\s*([^.\n]+))?)?", rest)
        if ital_m:
            title_hint = rest[: ital_m.start()].strip().rstrip(". ")
            journal_hint = ital_m.group(1).strip()
            vol_hint = (ital_m.group(2) or "").strip()
            pages_hint = (ital_m.group(4) or "").strip()

        first_key, is_korean, is_solo = _normalize_author_key(authors_raw)
        refs.append(
            ReferenceEntry(
                index=len(refs) + 1,
                line=line_no,
                raw=entry,
                authors_raw=authors_raw,
                first_author_key=first_key,
                is_korean=is_korean,
                is_solo=is_solo,
                year=year,
                doi=doi,
                url=url,
                title_hint=title_hint,
                journal_hint=journal_hint,
                volume_hint=vol_hint,
                pages_or_article_hint=pages_hint,
            )
        )
    return body_lines, refs


def _clean_citation_author(raw_author: str) -> tuple[str, bool]:
    """Normalize an in-text citation author token into (author_key, is_et_al)."""
    s = raw_author.strip()
    is_et_al = False
    if re.search(r"(?:\s+et\s+al\.?|\s*등)$", s, re.I):
        is_et_al = True
        s = re.sub(r"(?:\s+et\s+al\.?|\s*등)$", "", s, flags=re.I).strip()

    # Korean multi-author: "이정희와 정혜선" or "이정희, 정혜선" -> "이정희"
    if re.match(r"^[가-힣]", s):
        s = re.split(r"(?:\s*[·,&]\s*|와\s+|과\s+)", s)[0].strip()
        # Trim dangling Korean particles if attached to non-entity
        return s, is_et_al

    # English + Korean connector: "Okamoto-Mizuno와 Mizuno" or "Hilditch & McHill"
    s = re.split(r"(?:\s+&\s+|\s+and\s+|와\s+|과\s+)", s)[0].strip()
    # If comma exists in "Surname, F.", take Surname
    if "," in s:
        s = s.split(",", 1)[0].strip()
    return strip_accents(s), is_et_al


def extract_intext_citations(body_lines: list[tuple[int, str]]) -> tuple[list[CitationMention], list[tuple[int, str, list[str]]]]:
    """Extract parenthetical, narrative, and table citations plus multi-citation blocks for sort checking."""
    mentions: list[CitationMention] = []
    paren_blocks: list[tuple[int, str, list[str]]] = []

    narrative_re = re.compile(
        r"(?<![A-Za-z0-9_])("
        r"(?:[가-힣]{2,4}[·,]\s*[가-힣]{2,4}(?:\s*등)?)"
        r"|(?:[가-힣]{2,15}(?:(?:와|과)\s+[가-힣]{2,10}|\s*등)?)"
        r"|(?:[A-Z][A-Za-zÀ-ÖØ-öø-ÿ'\-]+(?:\s+et\s+al\.|\s*(?:&|and|와|과)\s*[A-Z][A-Za-zÀ-ÖØ-öø-ÿ'\-]+)?(?:\s*등)?)"
        r")\s*\(((?:19|20)\d{2}[a-z]?)\)"
    )

    korean_clause_lead_re = re.compile(
        r"^(?:첫째|둘째|셋째|넷째|끝으로|또한|반면|그러나|따라서|즉|한편|.*(?:으나|지만|으며|면서|는데|하고|되어|이고)),\s*(.+)$"
    )

    for line_no, raw_line in body_lines:
        is_table = raw_line.lstrip().startswith("|")
        # Strip inline LaTeX math and markdown links before citation matching
        line = re.sub(r"\$[^$]+\$", " ", raw_line)
        line = re.sub(r"\[[^\]]+\]\([^)]+\)", " ", line)

        # 1. Parenthetical citations: (... , 2020; ... , 2021)
        for pm in re.finditer(r"\(([^()]{4,180})\)", line):
            inside = pm.group(1).strip()
            # Must contain ", <4-digit year>" to qualify as APA parenthetical citation
            if not re.search(r",\s*(?:19|20)\d{2}[a-z]?\b", inside):
                continue
            units = [u.strip() for u in inside.split(";") if u.strip()]
            parsed_units_for_order: list[str] = []
            valid_block = True
            for u in units:
                um = re.match(r"^(.+?),\s*((?:19|20)\d{2}[a-z]?)$", u)
                if not um:
                    valid_block = False
                    continue
                author_part, yr = um.group(1).strip(), um.group(2)
                # Guard against false matches like "8시간 12분 대비 -8분, 1999년..."
                if re.search(r"\d", author_part):
                    valid_block = False
                    continue
                key, is_et_al = _clean_citation_author(author_part)
                if not key or key.lower() in NON_AUTHOR_PREFIXES:
                    valid_block = False
                    continue
                mentions.append(
                    CitationMention(
                        line=line_no,
                        raw=u,
                        author_key=key,
                        year=yr,
                        is_et_al=is_et_al,
                        style="table" if is_table else "parenthetical",
                    )
                )
                parsed_units_for_order.append(author_part)
            if valid_block and len(parsed_units_for_order) >= 2:
                paren_blocks.append((line_no, pm.group(0), parsed_units_for_order))

        # 2. Narrative citations: Name(2020), Name 등(2021), Name et al.(2016)
        for nm in narrative_re.finditer(line):
            author_part, yr = nm.group(1).strip(), nm.group(2)
            clause_m = korean_clause_lead_re.match(author_part)
            if clause_m:
                author_part = clause_m.group(1).strip()
            # Exclude Korean temporal/numeric nouns like "2019년" or "제3차"
            if author_part.endswith(("년", "월", "일", "차", "쪽", "장", "편", "회", "단계")):
                continue
            key, is_et_al = _clean_citation_author(author_part)
            if not key or key.lower() in NON_AUTHOR_PREFIXES:
                continue
            mentions.append(
                CitationMention(
                    line=line_no,
                    raw=nm.group(0),
                    author_key=key,
                    year=yr,
                    is_et_al=is_et_al,
                    style="table" if is_table else "narrative",
                )
            )

    return mentions, paren_blocks


def _citation_sort_key(author_part: str) -> tuple[int, str]:
    key, _ = _clean_citation_author(author_part)
    is_kor = bool(re.match(r"^[가-힣]", key))
    return (0 if is_kor else 1, key)


def check_academic_citations_and_apa(
    path: Path,
    lines: list[str],
    summary: FileCheckSummary,
) -> list[ReferenceEntry]:
    """Run Tier 0 academic checks: 1:1 in-text mapping, APA 7th bibliography order, multi-citation order."""
    body_lines, refs = parse_academic_document(lines)
    if not refs:
        return []

    summary.academic_refs_checked = len(refs)

    # 1. Check bibliography APA 7th ordering
    expected_sorted = sorted(refs, key=_apa_sort_key)
    if [r.index for r in refs] != [r.index for r in expected_sorted]:
        # Pinpoint first out-of-order entry
        for pos, (actual_r, exp_r) in enumerate(zip(refs, expected_sorted), 1):
            if actual_r.index != exp_r.index:
                summary.issues.append(
                    Issue(
                        code="APA_REFERENCE_ORDER",
                        severity="FAIL",
                        track="academic_ref",
                        file=str(path),
                        line=actual_r.line,
                        target=f"{actual_r.first_author_key} ({actual_r.year})",
                        message=(
                            f"Bibliography entry #{actual_r.index} is out of APA 7th order at position {pos}."
                        ),
                        expected=f"{exp_r.authors_raw} ({exp_r.year}) before {actual_r.authors_raw} ({actual_r.year})",
                        actual=f"#{actual_r.index}: {actual_r.authors_raw} ({actual_r.year})",
                        fix_hint="Sort Korean entries (가나다) then English entries (A-Z); solo works precede multi-author works.",
                    )
                )
                break

    # 2. Extract and match in-text citations 1:1
    mentions, paren_blocks = extract_intext_citations(body_lines)
    summary.intext_citations_checked = len(mentions)

    ref_lookup: dict[tuple[str, str], list[ReferenceEntry]] = {}
    for r in refs:
        ref_lookup.setdefault((r.first_author_key, r.year), []).append(r)

    matched_ref_indices: set[int] = set()
    for m in mentions:
        hits = ref_lookup.get((m.author_key, m.year))
        if not hits:
            # Also try exact prefix match for multi-word Korean/English institutional keys
            fuzzy_hits = [
                r
                for r in refs
                if r.year == m.year
                and (r.first_author_key == m.author_key or strip_accents(r.authors_raw).startswith(m.author_key))
            ]
            hits = fuzzy_hits
        if not hits:
            summary.issues.append(
                Issue(
                    code="ORPHAN_INTEXT_CITATION",
                    severity="FAIL",
                    track="academic_ref",
                    file=str(path),
                    line=m.line,
                    target=m.raw,
                    message=f"In-text citation {m.raw!r} has no matching entry in bibliography.",
                    expected=f"Reference entry for ({m.author_key}, {m.year})",
                    actual="missing from bibliography",
                    fix_hint="Add the verified reference entry or correct the author/year typo.",
                )
            )
        else:
            for h in hits:
                matched_ref_indices.add(h.index)

    for r in refs:
        if r.index not in matched_ref_indices:
            summary.issues.append(
                Issue(
                    code="UNCITED_REFERENCE",
                    severity="FAIL",
                    track="academic_ref",
                    file=str(path),
                    line=r.line,
                    target=f"{r.first_author_key} ({r.year})",
                    message=f"Bibliography entry [{r.index}] ({r.first_author_key}, {r.year}) is never cited in body or tables.",
                    expected="at least 1 matching in-text/table citation",
                    actual="0 in-text citations",
                    fix_hint="Cite the work in the body or remove unused entry from References.",
                )
            )

    # 3. Check APA 7th ordering inside parenthetical multi-citations
    for line_no, raw_block, author_parts in paren_blocks:
        sorted_parts = sorted(author_parts, key=_citation_sort_key)
        if [_citation_sort_key(x) for x in author_parts] != [_citation_sort_key(x) for x in sorted_parts]:
            summary.issues.append(
                Issue(
                    code="APA_INTEXT_ORDER",
                    severity="WARN",
                    track="academic_ref",
                    file=str(path),
                    line=line_no,
                    target=raw_block,
                    message="Parenthetical multi-citation block is not sorted (Korean 가나다 -> English A-Z).",
                    expected=" ; ".join(sorted_parts),
                    actual=raw_block,
                    fix_hint="Reorder citations inside the parentheses alphabetically.",
                )
            )

    return refs


def run_tier0_check(
    file_path: Path,
    check_rule_budget: bool | None = None,
) -> tuple[FileCheckSummary, list[ReferenceEntry]]:
    """Execute full Tier 0 offline verification on a single markdown/text file."""
    t0 = time.perf_counter()
    sha = compute_sha256(file_path)
    summary = FileCheckSummary(file=str(file_path), sha256=sha)
    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    check_local_file_references(file_path, lines, summary, check_rule_budget=check_rule_budget)
    refs = check_academic_citations_and_apa(file_path, lines, summary)
    summary.elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    return summary, refs
