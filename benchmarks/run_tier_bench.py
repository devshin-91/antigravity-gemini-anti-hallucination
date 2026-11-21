"""Axes 1, 3, and 4 Quantitative Benchmarks: Trap Stress Test, Tier Latency/Cache, Format Size, Tier 2 Model Comparison."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ref_factcheck.dirty_state import DirtyStateStore  # noqa: E402
from ref_factcheck.formatter import format_summaries  # noqa: E402
from ref_factcheck.tier0_local import run_tier0_check  # noqa: E402
from ref_factcheck.tier1_network import CacheDB, run_tier1_network_check  # noqa: E402
from ref_factcheck.tier2_evidence import (  # noqa: E402
    build_claim_evidence_bundles,
    extract_pdf_pages,
    slice_relevant_snippets,
    verify_bundle_with_genai,
)

GLOBAL_GEMINI = Path(r"C:\Users\ckstn\.gemini\config\GEMINI.md")
MIGRATION_MD = Path(r"C:\Users\ckstn\.gemini\config\plugins\gemini-api\skills\gemini-api-dev\references\migration.md")
PAPER_DRAFT = Path(r"C:\Users\ckstn\.gemini\antigravity\brain\f110d380-ab02-4c65-9672-33202e838d85\step4_full_draft.md")
PAPER_REFS_DIR = Path(r"C:\Users\ckstn\.gemini\antigravity\scratch\morning-waking-paper\references")


def run_axis4_trap_benchmark(cache: CacheDB) -> dict:
    """Test 14 synthetic traps + 2 clean real datasets across Track A (local) and Track B (academic)."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        repo_gemini = REPO_ROOT / "rules" / "GEMINI.ko.md"
        base_rule_txt = repo_gemini.read_text(encoding="utf-8")
        base_paper_txt = PAPER_DRAFT.read_text(encoding="utf-8")

        cases: list[tuple[str, str, Path, str | None, bool]] = []

        # Track A: Local refs & 24KB budget (1 clean + 5 traps)
        cases.append(("A0_clean_real_GEMINI_ko", "local", repo_gemini, None, True))

        a1 = root / "a1_missing.md"
        a1.write_text(
            base_rule_txt + "\n- Bad link: [ghost](file:///C:/nonexistent/ghost_file_999.md#L1-L5)\n",
            encoding="utf-8",
        )
        cases.append(("A1_missing_file", "local", a1, "MISSING_LOCAL_FILE", False))

        a2 = root / "a2_oob.md"
        a2.write_text(
            base_rule_txt + f"\n- OOB link: [migration.md](file:///{MIGRATION_MD.as_posix()}#L9000-L9050)\n",
            encoding="utf-8",
        )
        cases.append(("A2_oob_lines", "local", a2, "LINE_RANGE_OUT_OF_BOUNDS", False))

        a3 = root / "a3_inverted.md"
        a3.write_text(
            base_rule_txt + f"\n- Inverted: [migration.md](file:///{MIGRATION_MD.as_posix()}#L140-L120)\n",
            encoding="utf-8",
        )
        cases.append(("A3_inverted_lines", "local", a3, "LINE_RANGE_OUT_OF_BOUNDS", False))

        a4 = root / "a4_shifted.md"
        a4.write_text(
            f"- Shifted citation: [migration.md](file:///{MIGRATION_MD.as_posix()}#L1-L3)\n"
            "> `max_output_tokens` `background=True` `interaction.steps`\n",
            encoding="utf-8",
        )
        cases.append(("A4_shifted_offset", "local", a4, "LINE_SEMANTIC_MISMATCH", False))

        a5 = root / "GEMINI.md"
        a5.write_text(base_rule_txt + ("\n" + ("x" * 1000)) * 9, encoding="utf-8")
        cases.append(("A5_rule_budget", "local", a5, "RULE_BUDGET_EXCEEDED", False))

        # Track B: Academic refs (1 clean + 9 traps)
        cases.append(("B0_clean_real_paper", "academic", PAPER_DRAFT, None, True))

        b1 = root / "b1_fake_doi.md"
        b1.write_text(
            base_paper_txt.replace("https://doi.org/10.1016/j.smrv.2022.101697", "https://doi.org/10.9999/fake.sleep.2026.99"),
            encoding="utf-8",
        )
        cases.append(("B1_fake_doi", "academic", b1, "INVALID_OR_DEAD_DOI", False))

        b2 = root / "b2_year.md"
        b2.write_text(
            base_paper_txt.replace("Hilditch & McHill, 2019", "Hilditch & McHill, 2021")
            .replace("Hilditch & McHill(2019)", "Hilditch & McHill(2021)")
            .replace("Hilditch, C. J., & McHill, A. W. (2019).", "Hilditch, C. J., & McHill, A. W. (2021)."),
            encoding="utf-8",
        )
        cases.append(("B2_year_mismatch", "academic", b2, "DOI_YEAR_MISMATCH", False))

        b3 = root / "b3_author.md"
        b3.write_text(
            base_paper_txt.replace("Hilditch & McHill, 2019", "Smith & McHill, 2019")
            .replace("Hilditch & McHill(2019)", "Smith & McHill(2019)")
            .replace("Hilditch, C. J., & McHill, A. W. (2019).", "Smith, J., & McHill, A. W. (2019)."),
            encoding="utf-8",
        )
        cases.append(("B3_author_mismatch", "academic", b3, "DOI_AUTHOR_MISMATCH", False))

        b4 = root / "b4_wrong_doi.md"
        b4.write_text(
            base_paper_txt.replace("https://doi.org/10.1053/smrv.2000.0098", "https://doi.org/10.3389/fpsyg.2014.00611"),
            encoding="utf-8",
        )
        cases.append(("B4_wrong_article_doi", "academic", b4, "DOI_TITLE_MISMATCH", False))

        b5 = root / "b5_volume.md"
        b5.write_text(
            base_paper_txt.replace("*Building and Environment*, *132*, 11–20.", "*Building and Environment*, *99*, 11–20."),
            encoding="utf-8",
        )
        cases.append(("B5_volume_mismatch", "academic", b5, "DOI_VOLUME_MISMATCH", False))

        b6 = root / "b6_orphan.md"
        b6.write_text(
            base_paper_txt.replace("수면 관성 지속 시간이 두 배 가까이 길어져(Kim et al., 2026)", "수면 관성 지속 시간이 두 배 가까이 길어져(Kim et al., 2026; Walker, 2024)"),
            encoding="utf-8",
        )
        cases.append(("B6_orphan_citation", "academic", b6, "ORPHAN_INTEXT_CITATION", False))

        b7 = root / "b7_uncited.md"
        b7.write_text(
            base_paper_txt.replace(
                "* Wittmann, M.",
                "* Zale, P. (2023). Uncited benchmark entry. *Sleep*, *46*(1), 1–10.\n* Wittmann, M.",
            ),
            encoding="utf-8",
        )
        cases.append(("B7_uncited_reference", "academic", b7, "UNCITED_REFERENCE", False))

        b8 = root / "b8_apa_ref_order.md"
        b8.write_text(
            base_paper_txt.replace(
                "* Borbély, A. (2022). The two-process model of sleep regulation: Beginnings and outlook. *Journal of Sleep Research*, *31*(4), Article e13598. https://doi.org/10.1111/jsr.13598\n"
                "* Borbély, A. A. (1982). A two process model of sleep regulation. *Human Neurobiology*, *1*(3), 195–204.",
                "* Borbély, A. A. (1982). A two process model of sleep regulation. *Human Neurobiology*, *1*(3), 195–204.\n"
                "* Borbély, A. (2022). The two-process model of sleep regulation: Beginnings and outlook. *Journal of Sleep Research*, *31*(4), Article e13598. https://doi.org/10.1111/jsr.13598",
            ),
            encoding="utf-8",
        )
        cases.append(("B8_apa_ref_order", "academic", b8, "APA_REFERENCE_ORDER", False))

        b9 = root / "b9_apa_intext_order.md"
        b9.write_text(
            base_paper_txt.replace("(Tassi & Muzet, 2000; Trotti, 2017)", "(Trotti, 2017; Tassi & Muzet, 2000)"),
            encoding="utf-8",
        )
        cases.append(("B9_apa_intext_order", "academic", b9, "APA_INTEXT_ORDER", False))

        for name, track, path, expected_code, expect_clean in cases:
            t0 = time.perf_counter()
            summary, refs = run_tier0_check(path)
            if track == "academic" and refs:
                run_tier1_network_check(path, refs, summary, cache=cache, use_cache=True)
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            codes = [i.code for i in summary.issues]
            if expect_clean:
                passed = len(summary.issues) == 0
            else:
                passed = expected_code in codes
            results.append({
                "case": name,
                "track": track,
                "expected": "PASS" if expect_clean else expected_code,
                "detected_codes": codes,
                "passed": passed,
                "elapsed_ms": elapsed_ms,
            })

    traps = [r for r in results if r["expected"] != "PASS"]
    cleans = [r for r in results if r["expected"] == "PASS"]
    return {
        "cases": results,
        "trap_recall": f"{sum(r['passed'] for r in traps)}/{len(traps)}",
        "clean_pass": f"{sum(r['passed'] for r in cleans)}/{len(cleans)}",
    }


def run_axis1_and_3_benchmarks(cache: CacheDB) -> dict:
    """Measure Tier 0, Tier 1 Cold vs Warm, Dirty-Skip, and Axis 3 payload bytes."""
    with tempfile.TemporaryDirectory() as tmp:
        cold_cache = CacheDB(Path(tmp) / "cold.db")
        dirty_store = DirtyStateStore(Path(tmp) / "dirty.json")

        # Cold Tier 0+1 on 21-ref paper
        t0 = time.perf_counter()
        s_cold, refs_cold = run_tier0_check(PAPER_DRAFT)
        run_tier1_network_check(PAPER_DRAFT, refs_cold, s_cold, cache=cold_cache, use_cache=True)
        cold_ms = round((time.perf_counter() - t0) * 1000, 2)
        dirty_store.record_result(PAPER_DRAFT, s_cold.sha256, 1, s_cold.status)

        # Warm Tier 0+1 (cache hit, forced check)
        t1 = time.perf_counter()
        s_warm, refs_warm = run_tier0_check(PAPER_DRAFT)
        run_tier1_network_check(PAPER_DRAFT, refs_warm, s_warm, cache=cold_cache, use_cache=True)
        warm_ms = round((time.perf_counter() - t1) * 1000, 2)

        # Dirty-skip (unchanged SHA-256)
        t2 = time.perf_counter()
        clean, _ = dirty_store.is_clean_and_passed(PAPER_DRAFT, 1)
        dirty_skip_ms = round((time.perf_counter() - t2) * 1000, 2)

        # Axis 3: Formatter byte sizes on PASS vs FAIL
        fail_summary, _ = run_tier0_check(PAPER_DRAFT)
        # Inject synthetic fail sample for size comparison
        bad_file = Path(tmp) / "multi_fail.md"
        bad_txt = PAPER_DRAFT.read_text(encoding="utf-8")
        bad_txt = bad_txt.replace("https://doi.org/10.1016/j.smrv.2022.101697", "https://doi.org/10.9999/fake.2026.99")
        bad_txt = bad_txt.replace("Kim et al., 2026", "Ghost, 2026")
        bad_file.write_text(bad_txt, encoding="utf-8")
        s_fail, refs_fail = run_tier0_check(bad_file)
        run_tier1_network_check(bad_file, refs_fail, s_fail, cache=cache, use_cache=True)

        fmt_pass = {
            m: format_summaries([s_warm], mode=m)["bytes"]
            for m in ("raw", "compact_diff", "hook_stop", "hook_pre")
        }
        fmt_fail = {
            m: format_summaries([s_fail], mode=m)["bytes"]
            for m in ("raw", "compact_diff", "hook_stop", "hook_pre")
        }

    return {
        "paper_tier1_cold_ms": cold_ms,
        "paper_tier1_cold_live_calls": s_cold.network_live_calls,
        "paper_tier1_warm_ms": warm_ms,
        "paper_tier1_warm_cache_hits": s_warm.network_cache_hits,
        "dirty_skip_hit": clean,
        "dirty_skip_ms": dirty_skip_ms,
        "format_bytes_pass": fmt_pass,
        "format_bytes_fail": fmt_fail,
    }


def run_axis1_tier2_model_comparison() -> dict:
    """Compare Full PDF vs +-3 sentence Snippet across 3.5-flash-lite, 3.8-flash, 4-hydrogen, 4-neon."""
    bundles = build_claim_evidence_bundles(PAPER_DRAFT, PAPER_REFS_DIR, max_claims=12)
    # Pick 2 clear numeric claims from distinct papers: Ahn 2019 (Korean PDF) & Hill 2022 (English PDF)
    ahn_bundle = next(b for b in bundles if "03_Ahn_2019" in b["pdf_file"] and "0.86" in b["claim"])
    hill_bundle = next(b for b in bundles if "14_Hill_2022" in b["pdf_file"] and "-0.39" in b["claim"])

    # Create 1 clean claim + 1 numerical flip trap claim
    clean_case = {
        "name": "Hill_2022_CLEAN",
        "expected": "MATCH",
        "bundle": hill_bundle,
    }
    trap_bundle = dict(ahn_bundle)
    trap_bundle["claim"] = ahn_bundle["claim"].replace("0.86", "0.68")  # subtle digit swap trap!
    ahn_pages = extract_pdf_pages(PAPER_REFS_DIR / ahn_bundle["pdf_file"])
    trap_bundle["snippets"] = slice_relevant_snippets(ahn_pages, trap_bundle["claim"])
    trap_case = {
        "name": "Ahn_2019_FLIP_0.86_to_0.68",
        "expected": "MISMATCH",
        "bundle": trap_bundle,
    }

    models = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-4-hydrogen", "gemini-4-neon"]
    rows = []
    for case in (clean_case, trap_case):
        for mode in ("full", "snippet"):
            for model in models:
                try:
                    res = verify_bundle_with_genai(case["bundle"], model=model, mode=mode, thinking_level="low")
                    correct = res["verdict"] == case["expected"]
                    rows.append({
                        "case": case["name"],
                        "expected": case["expected"],
                        "mode": mode,
                        "model": model,
                        "verdict": res["verdict"],
                        "correct": correct,
                        "elapsed_ms": res["elapsed_ms"],
                        "input_tokens": res["usage"].get("input_tokens"),
                        "output_tokens": res["usage"].get("output_tokens"),
                        "total_tokens": res["usage"].get("total_tokens"),
                        "prompt_chars": res["prompt_chars"],
                        "reason": res["reason"][:120],
                    })
                except Exception as exc:
                    rows.append({
                        "case": case["name"],
                        "mode": mode,
                        "model": model,
                        "error": str(exc),
                    })
    return {"tier2_rows": rows}


def main() -> None:
    cache = CacheDB(Path(r"C:\Users\ckstn\.gemini\antigravity\brain\a5bb0684-5633-4c0e-a055-6fa053e1eba8\scratch\bench_cache.db"))
    print("Running Axis 1 & 3 benchmarks...")
    ax13 = run_axis1_and_3_benchmarks(cache)
    print("Running Axis 4 16-case trap stress test...")
    ax4 = run_axis4_trap_benchmark(cache)
    print("Running Axis 1 Tier 2 GenAI Full-vs-Snippet model comparison...")
    ax1_t2 = run_axis1_tier2_model_comparison()

    report = {"axis1_and_3": ax13, "axis4": ax4, "axis1_tier2": ax1_t2}
    out_path = REPO_ROOT / "benchmarks" / "tier_bench_results.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved results to {out_path}")
    print(json.dumps(ax13, ensure_ascii=False, indent=2))
    print(f"Axis 4 Recall={ax4['trap_recall']}, Clean={ax4['clean_pass']}")
    for r in ax1_t2["tier2_rows"]:
        print(" ", r)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
