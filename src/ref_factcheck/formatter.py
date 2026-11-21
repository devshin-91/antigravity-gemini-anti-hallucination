"""Axis 3: Output formatters comparing Raw vs. Compact Diff vs. Zero-Byte Pass Hook protocols."""

from __future__ import annotations

import json
from typing import Any, Literal

from .models import FileCheckSummary

FormatMode = Literal["raw", "compact_diff", "hook_stop", "hook_pre"]


def format_summaries(
    summaries: list[FileCheckSummary],
    mode: FormatMode = "compact_diff",
    continuation_active: bool = False,
    execution_num: int = 0,
    max_continuations: int = 1,
) -> dict[str, Any]:
    """Render verification summaries according to the selected token-efficiency protocol."""
    total_fails = sum(s.fail_count for s in summaries)
    total_warns = sum(s.warn_count for s in summaries)
    all_issues = [iss for s in summaries for iss in s.issues]

    if mode == "raw":
        text = json.dumps([s.to_dict() for s in summaries], ensure_ascii=False, indent=2)
        return {"text": text, "bytes": len(text.encode("utf-8")), "status": "FAIL" if total_fails else "PASS"}

    if mode == "compact_diff":
        if total_fails == 0 and total_warns == 0:
            payload = {
                "status": "PASS",
                "files": len(summaries),
                "local_refs": sum(s.local_refs_checked for s in summaries),
                "academic_refs": sum(s.academic_refs_checked for s in summaries),
                "cache_hits": sum(s.network_cache_hits for s in summaries),
            }
        else:
            payload = {
                "status": "FAIL" if total_fails else "WARN",
                "fails": total_fails,
                "warns": total_warns,
                "issues": [iss.to_compact_dict() for iss in all_issues],
            }
        text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        return {"text": text, "bytes": len(text.encode("utf-8")), "status": payload["status"]}

    if mode == "hook_stop":
        # Guard against infinite Stop loops (runtime probe showed continuationActive can remain false on executionNum >= 1)
        if continuation_active or execution_num >= max_continuations:
            return {"decision": "allow", "bytes": 0, "status": "PASS_GUARD"}

        fails = [iss for iss in all_issues if iss.severity == "FAIL"]
        if not fails:
            # Zero tokens injected back to model when passed!
            return {"decision": "allow", "bytes": 0, "status": "PASS"}

        compact_issues = [iss.to_compact_dict() for iss in fails[:8]]
        reason = (
            f"[Auto Reference Fact-Check Gate] Detected {len(fails)} FAIL issue(s). "
            "Fix only the listed items before completing:\n"
            + json.dumps(compact_issues, ensure_ascii=False, separators=(",", ":"))
        )
        out = {"decision": "continue", "reason": reason}
        return {"hook_output": out, "bytes": len(reason.encode("utf-8")), "status": "FAIL"}

    if mode == "hook_pre":
        # User-only markdown badge via metadata.user_markdown (0 tokens added to model context)
        checked_refs = sum(s.local_refs_checked + s.academic_refs_checked for s in summaries)
        if checked_refs == 0 and total_fails == 0:
            return {"hook_output": {}, "bytes": 0, "status": "NOOP"}
        badge = (
            f"🛡️ **Auto Fact-Check:** `PASS` ({checked_refs} refs verified, 0 LLM tokens)"
            if total_fails == 0
            else f"⚠️ **Auto Fact-Check:** `{total_fails} FAIL` detected — model notified"
        )
        out = {
            "injectSteps": [
                {
                    "systemMessage": {
                        "systemMessage": "",
                        "metadata": {"user_markdown": badge},
                    }
                }
            ]
        }
        return {"hook_output": out, "bytes": 0, "status": "BADGE"}

    raise ValueError(f"Unknown format mode: {mode}")
