# Zero-Prompt Reference Fact-Checker Rules

- Reference, citation, `file:///#L...`, and DOI integrity verification is automated by the `ref-fact-checker` lifecycle hooks (`PostToolUse` + `Stop`) with zero manual prompt overhead.
- Do not write one-off `check_references.py` scripts from scratch when verifying markdown drafts or rule files; rely on the automated hook gate or run `python -m ref_factcheck check <file>` (Tier 0–1) and `python -m ref_factcheck evidence <draft> --refs-dir <dir>` (Tier 2).
- When the `Stop` gate returns a compact `FAIL` diff, fix only the listed discrepancies and cite exact verified lines/DOIs.
