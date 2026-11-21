---
name: reference-fact-check
description: >-
  Run low-token tiered reference fact-checking (Tier 0 local file:/// line & APA 1:1 mapping,
  Tier 1 cached Crossref/DOI metadata audit, Tier 2 minimal PDF snippet evidence extraction).
  Use when manually auditing academic drafts, PDFs, or rule files, or when resolving Stop-hook FAIL diffs.
---

# Tiered Reference Fact-Checking Workflow

1. **Tier 0–1 Deterministic Check (0 LLM Tokens):**
   Run the unified CLI with compact diff formatting instead of writing custom scripts:
   ```bash
   python -m ref_factcheck check <path/to/file.md> --tier 1 --format compact_diff
   ```
   - `Tier 0` checks `file:///#L...` bounds/quotes, AGY `24,000`-byte rule budget, 1:1 in-text ↔ bibliography mapping, and APA 7th ordering.
   - `Tier 1` checks DOIs via Crossref/DOI Handle API backed by a persistent SQLite WAL cache (`~/.cache/agy-ref-factcheck/cache.db`).

2. **Tier 2 Minimal PDF Evidence Extraction (Low-Token Semantic Audit):**
   When verifying numerical claims against local PDFs, never load full 15–30 page PDFs into the main model context. Slice only the relevant `±3 sentence` windows around matched numbers/keywords:
   ```bash
   python -m ref_factcheck evidence <draft.md> --refs-dir <references/>
   ```
   Escalate only the extracted compact snippets when semantic judgment is needed.
