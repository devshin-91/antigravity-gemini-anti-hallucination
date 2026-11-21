"""Antigravity Lifecycle Hook Runner for Zero-Prompt Reference Fact-Checking."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import time

# Resolve ref_factcheck package from either bundled ./ref_factcheck or repo ../../src
HOOK_DIR = Path(__file__).resolve().parent
PLUGIN_DIR = HOOK_DIR.parent
CANDIDATE_ROOTS = [
    HOOK_DIR,
    PLUGIN_DIR.parent.parent / "src",
]
for root in CANDIDATE_ROOTS:
    if (root / "ref_factcheck").is_dir() and str(root) not in sys.path:
        sys.path.insert(0, str(root))
        break

from ref_factcheck.cli import check_files  # noqa: E402
from ref_factcheck.dirty_state import DirtyStateStore  # noqa: E402
from ref_factcheck.formatter import format_summaries  # noqa: E402
from ref_factcheck.tier1_network import CacheDB  # noqa: E402

DOC_EXTENSIONS = {".md", ".markdown", ".txt", ".tex"}


def _state_dir(payload: dict) -> Path:
    plugin_data = os.environ.get("PLUGIN_DATA")
    if plugin_data:
        base = Path(plugin_data)
    else:
        base = Path.home() / ".cache" / "agy-ref-factcheck"
    conv_id = payload.get("conversationId") or "default"
    safe_conv = hashlib.sha1(str(conv_id).encode("utf-8")).hexdigest()[:12]
    d = base / "sessions" / safe_conv
    d.mkdir(parents=True, exist_ok=True)
    return d


def _extract_edited_path(tool_call: dict, payload: dict) -> Path | None:
    args = tool_call.get("args") or {}
    ws_list = payload.get("workspacePaths") or []
    ws_root = Path(ws_list[0]) if ws_list else None
    for key in ("Path", "TargetFile", "path", "file_path"):
        val = args.get(key)
        if isinstance(val, str) and val.strip():
            p = Path(val.strip())
            if not p.is_absolute() and ws_root is not None:
                p = ws_root / p
            return p
    return None


def main() -> int:
    event = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    sdir = _state_dir(payload)
    dirty_store = DirtyStateStore(sdir / "dirty_state.json")
    badge_file = sdir / "last_badge.json"

    if event == "PostToolUse":
        tc = payload.get("toolCall") or {}
        if not payload.get("error"):
            target = _extract_edited_path(tc, payload)
            if target and target.suffix.lower() in DOC_EXTENSIONS and target.exists():
                dirty_store.mark_dirty(target, tool_name=str(tc.get("name", "")))
        print("{}")
        return 0

    if event == "PreInvocation":
        # Emit user-only markdown badge (0 model tokens) if a previous Stop pass verified files
        if badge_file.exists():
            try:
                out = json.loads(badge_file.read_text(encoding="utf-8"))
                badge_file.unlink(missing_ok=True)
                print(json.dumps(out, ensure_ascii=False))
                return 0
            except Exception:
                pass
        print("{}")
        return 0

    if event == "Stop":
        term_reason = str(payload.get("terminationReason", ""))
        cont_active = bool(payload.get("continuationActive", False))
        exec_num = int(payload.get("executionNum") or 0)
        if cont_active or exec_num >= 2 or term_reason in ("USER_CANCELED", "ERROR", "MAX_INVOCATIONS"):
            print(json.dumps({"decision": "allow"}))
            return 0

        dirty_paths = dirty_store.pop_dirty_queue()
        if not dirty_paths:
            print(json.dumps({"decision": "allow"}))
            return 0

        tier = int(os.environ.get("AGY_FACTCHECK_TIER", "1"))
        cache_db = CacheDB() if tier >= 1 else None
        summaries = check_files(
            dirty_paths,
            tier=tier,
            use_cache=True,
            dirty_store=dirty_store,
            cache_db=cache_db,
        )

        # Store a 0-token user badge for the next PreInvocation if desired
        badge_res = format_summaries(summaries, mode="hook_pre")
        if badge_res.get("hook_output"):
            badge_file.write_text(
                json.dumps(badge_res["hook_output"], ensure_ascii=False),
                encoding="utf-8",
            )

        stop_res = format_summaries(
            summaries,
            mode="hook_stop",
            continuation_active=cont_active,
            execution_num=exec_num,
            max_continuations=2,
        )
        out = stop_res.get("hook_output") or {"decision": stop_res.get("decision", "allow")}
        print(json.dumps(out, ensure_ascii=False))
        return 0

    print("{}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
