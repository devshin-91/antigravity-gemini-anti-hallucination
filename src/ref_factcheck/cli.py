"""CLI entry point for Zero-Prompt & Low-Token Reference Fact-Checking."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from .dirty_state import DirtyStateStore
from .formatter import format_summaries
from .models import FileCheckSummary
from .tier0_local import run_tier0_check
from .tier1_network import CacheDB, run_tier1_network_check
from .tier2_evidence import build_claim_evidence_bundles, verify_bundle_with_genai


def check_files(
    paths: list[Path],
    tier: int = 1,
    use_cache: bool = True,
    dirty_store: DirtyStateStore | None = None,
    cache_db: CacheDB | None = None,
    force: bool = False,
) -> list[FileCheckSummary]:
    """Run Tier 0 (and optional Tier 1) checks across target files."""
    summaries: list[FileCheckSummary] = []
    cache = cache_db or (CacheDB() if tier >= 1 else None)

    for p in paths:
        if not p.exists() or not p.is_file():
            continue
        if dirty_store is not None and not force:
            clean, sha = dirty_store.is_clean_and_passed(p, tier)
            if clean:
                summaries.append(
                    FileCheckSummary(
                        file=str(p),
                        sha256=sha,
                        skipped_clean=True,
                    )
                )
                continue

        summary, refs = run_tier0_check(p)
        if tier >= 1 and refs:
            run_tier1_network_check(p, refs, summary, cache=cache, use_cache=use_cache)
        if dirty_store is not None:
            dirty_store.record_result(p, summary.sha256, tier, summary.status)
        summaries.append(summary)
    return summaries


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ref-factcheck", description="Zero-Prompt Reference Fact-Checker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_chk = sub.add_parser("check", help="Verify local file:/// and academic references")
    p_chk.add_argument("paths", nargs="*", type=Path, help="Files to verify")
    p_chk.add_argument("--tier", type=int, choices=[0, 1], default=1)
    p_chk.add_argument("--format", choices=["raw", "compact_diff", "hook_stop", "hook_pre"], default="compact_diff")
    p_chk.add_argument("--no-cache", action="store_true")
    p_chk.add_argument("--dirty-state", type=Path, default=None)
    p_chk.add_argument("--only-dirty", action="store_true")
    p_chk.add_argument("--force", action="store_true")

    p_ev = sub.add_parser("evidence", help="Tier 2 minimal PDF snippet extraction & optional GenAI check")
    p_ev.add_argument("draft", type=Path)
    p_ev.add_argument("--refs-dir", type=Path, required=True)
    p_ev.add_argument("--max-claims", type=int, default=5)
    p_ev.add_argument("--model", type=str, default=None, help="Optional GenAI model (e.g. gemini-3.8-flash)")
    p_ev.add_argument("--mode", choices=["snippet", "full"], default="snippet")

    args = parser.parse_args(argv)

    if args.cmd == "check":
        dirty_store = DirtyStateStore(args.dirty_state) if args.dirty_state else None
        targets = list(args.paths)
        if args.only_dirty and dirty_store is not None:
            targets.extend(dirty_store.pop_dirty_queue())
        summaries = check_files(
            targets,
            tier=args.tier,
            use_cache=not args.no_cache,
            dirty_store=dirty_store,
            force=args.force,
        )
        rendered = format_summaries(summaries, mode=args.format)
        if "text" in rendered:
            print(rendered["text"])
        else:
            print(json.dumps(rendered.get("hook_output", {"decision": rendered.get("decision", "allow")}), ensure_ascii=False))
        return 1 if any(s.fail_count > 0 for s in summaries) else 0

    if args.cmd == "evidence":
        bundles = build_claim_evidence_bundles(args.draft, args.refs_dir, max_claims=args.max_claims)
        out: list[dict] = []
        for b in bundles:
            item = {k: v for k, v in b.items() if k != "full_text"}
            if args.model:
                item["eval"] = verify_bundle_with_genai(b, model=args.model, mode=args.mode)
            out.append(item)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
