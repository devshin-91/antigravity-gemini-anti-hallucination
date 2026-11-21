"""Axis 2 Live AGY A/B Benchmark: Unprompted Rule vs. Prompted Manual vs. Zero-Prompt Hook Gate."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
HOOK_RUNNER = REPO_ROOT / "plugins" / "ref-fact-checker" / "hooks" / "hook_runner.py"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ref_factcheck.tier0_local import run_tier0_check  # noqa: E402
from ref_factcheck.tier1_network import CacheDB, run_tier1_network_check  # noqa: E402

TRAP_PAPER = """# Mini Sleep Review

## 1. Introduction
Sleep inertia impairs morning cognitive performance (Hilditch & McHill, 2021).
Recent data also suggest bedtime procrastination correlates with fatigue (Hill et al., 2022; Ghost, 2025).

## 참고문헌
* Hilditch, C. J., & McHill, A. W. (2021). Sleep inertia: Current insights. *Nature and Science of Sleep*, *11*, 155–165. https://doi.org/10.2147/NSS.S188911
* Hill, V. M., Rebar, A. L., Ferguson, S. A., Shriane, A. E., & Vincent, G. E. (2022). Go to bed! A systematic review and meta-analysis of bedtime procrastination correlates and sleep outcomes. *Sleep Medicine Reviews*, *66*, Article 101697. https://doi.org/10.1016/j.smrv.2022.101697
"""

CLEAN_PAPER = """# Mini Sleep Review

## 1. Introduction
Sleep inertia impairs morning cognitive performance (Hilditch & McHill, 2019).
Recent data also suggest bedtime procrastination correlates with fatigue (Hill et al., 2022).

## 참고문헌
* Hilditch, C. J., & McHill, A. W. (2019). Sleep inertia: Current insights. *Nature and Science of Sleep*, *11*, 155–165. https://doi.org/10.2147/NSS.S188911
* Hill, V. M., Rebar, A. L., Ferguson, S. A., Shriane, A. E., & Vincent, G. E. (2022). Go to bed! A systematic review and meta-analysis of bedtime procrastination correlates and sleep outcomes. *Sleep Medicine Reviews*, *66*, Article 101697. https://doi.org/10.1016/j.smrv.2022.101697
"""


def _write_hooks(ws: Path, tier: int = 1) -> None:
    agents_dir = ws / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    # Use absolute python + hook_runner path so workspace stays minimal and clean
    runner = str(HOOK_RUNNER).replace("\\", "/")
    hooks_cfg = {
        "ref-fact-checker": {
            "PostToolUse": [
                {
                    "matcher": "write_file|edit_file",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f'python "{runner}" PostToolUse',
                            "timeout": 10,
                        }
                    ],
                }
            ],
            "PreInvocation": [
                {
                    "type": "command",
                    "command": f'python "{runner}" PreInvocation',
                    "timeout": 10,
                }
            ],
            "Stop": [
                {
                    "type": "command",
                    "command": f'python "{runner}" Stop',
                    "timeout": 25,
                }
            ],
        }
    }
    (agents_dir / "hooks.json").write_text(json.dumps(hooks_cfg, indent=2), encoding="utf-8")


def _run_agy_case(
    name: str,
    paper_content: str,
    prompt: str,
    with_hooks: bool,
    with_rule: bool,
    cache_db: Path,
    model: str = "gemini-3.8-flash-medium",
) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=ws, check=True)
        paper_path = ws / "paper.md"
        paper_path.write_text(paper_content, encoding="utf-8")

        if with_rule:
            (ws / "GEMINI.md").write_text(
                (REPO_ROOT / "rules" / "GEMINI.ko.md").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        if with_hooks:
            _write_hooks(ws)

        env = os.environ.copy()
        env["AGY_FACTCHECK_CACHE_DB"] = str(cache_db)
        env["AGY_FACTCHECK_TIER"] = "1"
        env["PLUGIN_DATA"] = str(ws / ".hook_state")

        t0 = time.perf_counter()
        proc = subprocess.run(
            [
                "agy",
                "-p",
                prompt,
                "--model",
                model,
                "--dangerously-skip-permissions",
                "--disable-slash-commands",
                "--output-format",
                "json",
                "--print-timeout",
                "180s",
            ],
            cwd=ws,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        wall_sec = round(time.perf_counter() - t0, 2)

        hook_state_files = list((ws / ".hook_state").rglob("*.json")) if (ws / ".hook_state").exists() else []
        hook_state_dump = {}
        for hf in hook_state_files:
            try:
                hook_state_dump[hf.name] = json.loads(hf.read_text(encoding="utf-8"))
            except Exception:
                pass

        parsed = {}
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    parsed = json.loads(line)
                except Exception:
                    pass

        # Post-run audit via Tier 0 + Tier 1
        summary, refs = run_tier0_check(paper_path)
        if refs:
            run_tier1_network_check(paper_path, refs, summary, cache=CacheDB(cache_db), use_cache=True)

        return {
            "case": name,
            "model": model,
            "with_hooks": with_hooks,
            "with_rule": with_rule,
            "returncode": proc.returncode,
            "wall_sec": wall_sec,
            "agy_status": parsed.get("status"),
            "duration_seconds": parsed.get("duration_seconds"),
            "num_turns": parsed.get("num_turns"),
            "usage": parsed.get("usage", {}),
            "post_audit_status": summary.status,
            "remaining_fails": [i.to_compact_dict() for i in summary.issues if i.severity == "FAIL"],
            "remaining_warns": [i.to_compact_dict() for i in summary.issues if i.severity == "WARN"],
            "hook_state": hook_state_dump,
            "final_paper_excerpt": paper_path.read_text(encoding="utf-8"),
        }


def main() -> None:
    cache_db = Path(r"C:\Users\ckstn\.gemini\antigravity\brain\a5bb0684-5633-4c0e-a055-6fa053e1eba8\scratch\agy_ab_cache.db")
    if cache_db.exists():
        cache_db.unlink()

    unprompted_edit_prompt = (
        "Edit paper.md immediately: add one short sentence 'Further integrative research is warranted.' "
        "at the end of '## 1. Introduction', then reply DONE."
    )
    manual_prompt = (
        "Edit paper.md immediately: add one short sentence 'Further integrative research is warranted.' "
        "at the end of '## 1. Introduction'. "
        "Also perform a complete reference fact-check on paper.md: check every DOI via Crossref API, "
        "verify 1:1 in-text vs bibliography matching, and fix any fabricated citations or mismatched publication years."
    )

    cases = [
        ("C1_RuleOnly_Unprompted_Trap", TRAP_PAPER, unprompted_edit_prompt, False, True),
        ("C2_ManualPrompted_Trap", TRAP_PAPER, manual_prompt, False, True),
        ("C3_HookGate_Unprompted_Trap", TRAP_PAPER, unprompted_edit_prompt, True, False),
        ("C4_HookGate_Unprompted_Clean", CLEAN_PAPER, unprompted_edit_prompt, True, False),
    ]

    results = []
    for name, content, prompt, hooks, rule in cases:
        print(f"Running {name}...")
        res = _run_agy_case(name, content, prompt, hooks, rule, cache_db)
        results.append(res)
        print(
            f"  -> status={res['agy_status']}, dur={res['duration_seconds']}s, "
            f"tokens={res['usage'].get('total_tokens')}, post_audit={res['post_audit_status']}, "
            f"remaining_fails={len(res['remaining_fails'])}"
        )

    out_path = REPO_ROOT / "benchmarks" / "agy_ab_results.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved AGY A/B results to {out_path}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
