"""Unit and regression tests for Tier 0, Tier 1 cache, formatter, and hook runner."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
HOOK_RUNNER = Path(__file__).resolve().parents[1] / "plugins" / "ref-fact-checker" / "hooks" / "hook_runner.py"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ref_factcheck.dirty_state import DirtyStateStore  # noqa: E402
from ref_factcheck.formatter import format_summaries  # noqa: E402
from ref_factcheck.models import FileCheckSummary, Issue, ReferenceEntry  # noqa: E402
from ref_factcheck.tier0_local import run_tier0_check  # noqa: E402
from ref_factcheck.tier1_network import CacheDB, _compare_doi_metadata  # noqa: E402


class TestTier0AndFormatters(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_local_ref_bounds_and_semantic_mismatch(self) -> None:
        target = self.root / "sample.py"
        target.write_text("alpha = 1\nbeta = 2\ngamma = 3\ndelta = 4\nepsilon = 5\n", encoding="utf-8")

        doc = self.root / "GEMINI.md"
        doc.write_text(
            "# Test Rules\n"
            f"- Valid ref: [sample.py](file:///{target.as_posix()}#L4-L5)\n"
            f"> `delta` and `epsilon`\n\n"
            f"- Missing ref: [missing.md](file:///{(self.root / 'missing.md').as_posix()}#L1-L3)\n"
            f"- OOB ref: [sample.py](file:///{target.as_posix()}#L1-L99)\n"
            f"- Shifted ref: [sample.py](file:///{target.as_posix()}#L1-L2)\n"
            f"> `delta` and `epsilon`\n",
            encoding="utf-8",
        )
        summary, _ = run_tier0_check(doc)
        codes = {i.code for i in summary.issues}
        self.assertIn("MISSING_LOCAL_FILE", codes)
        self.assertIn("LINE_RANGE_OUT_OF_BOUNDS", codes)
        self.assertIn("LINE_SEMANTIC_MISMATCH", codes)
        self.assertEqual(summary.fail_count, 3)

    def test_rule_budget_exceeded(self) -> None:
        doc = self.root / "GEMINI.md"
        doc.write_text("a" * 24500, encoding="utf-8")
        summary, _ = run_tier0_check(doc)
        self.assertEqual([i.code for i in summary.issues], ["RULE_BUDGET_EXCEEDED"])

    def test_academic_mapping_and_apa_order(self) -> None:
        doc = self.root / "paper.md"
        doc.write_text(
            "## 본문\n"
            "김철수(2024)는 이를 보고했고 (Kim, 2020; 이영희, 2021) 및 (Ghost, 2025)도 언급된다.\n\n"
            "## 참고문헌\n"
            "* 김철수 (2024). 테스트 논문. *한국학술지*, *10*(1), 1–10.\n"
            "* 이영희 (2021). 또 다른 논문. *한국학술지*, *8*(2), 20–30.\n"
            "* Kim, A. A. (1999). Earlier work. *Journal*, *1*(1), 1–5.\n"
            "* Kim, A. (2022). Shorter initials should precede AA. *Journal*, *2*(1), 1–5.\n"
            "* Uncited, Z. (2023). Never cited. *Journal*, *3*(1), 1–5.\n",
            encoding="utf-8",
        )
        summary, refs = run_tier0_check(doc)
        self.assertEqual(len(refs), 5)
        codes = {i.code for i in summary.issues}
        self.assertIn("ORPHAN_INTEXT_CITATION", codes)
        self.assertIn("UNCITED_REFERENCE", codes)
        self.assertIn("APA_REFERENCE_ORDER", codes)
        self.assertIn("APA_INTEXT_ORDER", codes)

    def test_tier1_metadata_mismatches_and_cache(self) -> None:
        db = CacheDB(self.root / "cache.db")
        sample_payload = {
            "doi": "10.1000/test",
            "crossref_status": 200,
            "provider": "crossref",
            "meta": {
                "title": "Sleep inertia and circadian timing",
                "subtitle": "",
                "original_title": "",
                "authors": [{"family": "Hilditch", "given": "Cassie"}],
                "container": "Nature and Science of Sleep",
                "volume": "Volume 11",
                "issue": "",
                "page": "155-165",
                "article_number": "",
                "years": [2019],
            },
        }
        db.set("doi:10.1000/test", "crossref", sample_payload)
        cached = db.get("doi:10.1000/test", 3600)
        self.assertIsNotNone(cached)

        summary = FileCheckSummary(file="paper.md", sha256="abc")
        good_ref = ReferenceEntry(
            index=1,
            line=10,
            raw="Hilditch, C. (2019). Sleep inertia and circadian timing.",
            authors_raw="Hilditch, C.",
            first_author_key="hilditch",
            is_korean=False,
            is_solo=True,
            year="2019",
            doi="10.1000/test",
            title_hint="Sleep inertia and circadian timing",
            volume_hint="11",
        )
        _compare_doi_metadata(Path("paper.md"), good_ref, cached, summary)
        self.assertEqual(summary.fail_count, 0)

        bad_ref = ReferenceEntry(
            index=2,
            line=11,
            raw="Smith, J. (2021). Completely unrelated quantum mechanics title.",
            authors_raw="Smith, J.",
            first_author_key="smith",
            is_korean=False,
            is_solo=True,
            year="2021",
            doi="10.1000/test",
            title_hint="Completely unrelated quantum mechanics title",
            volume_hint="99",
        )
        _compare_doi_metadata(Path("paper.md"), bad_ref, cached, summary)
        codes = {i.code for i in summary.issues}
        self.assertEqual(
            codes,
            {"DOI_YEAR_MISMATCH", "DOI_AUTHOR_MISMATCH", "DOI_TITLE_MISMATCH", "DOI_VOLUME_MISMATCH"},
        )

    def test_formatter_zero_byte_pass_and_compact_diff(self) -> None:
        clean = FileCheckSummary(file="a.md", sha256="123", local_refs_checked=5)
        stop_pass = format_summaries([clean], mode="hook_stop", execution_num=0)
        self.assertEqual(stop_pass["decision"], "allow")
        self.assertEqual(stop_pass["bytes"], 0)

        pre_badge = format_summaries([clean], mode="hook_pre")
        self.assertEqual(pre_badge["bytes"], 0)
        self.assertIn("user_markdown", pre_badge["hook_output"]["injectSteps"][0]["systemMessage"]["metadata"])

        dirty = FileCheckSummary(
            file="b.md",
            sha256="456",
            issues=[
                Issue(
                    code="ORPHAN_INTEXT_CITATION",
                    severity="FAIL",
                    track="academic_ref",
                    file="b.md",
                    line=4,
                    target="(Fake, 2025)",
                    message="Missing entry",
                )
            ],
        )
        raw_sz = format_summaries([dirty], mode="raw")["bytes"]
        compact_sz = format_summaries([dirty], mode="compact_diff")["bytes"]
        stop_fail = format_summaries([dirty], mode="hook_stop", execution_num=0)
        self.assertLess(compact_sz, raw_sz)
        self.assertEqual(stop_fail["hook_output"]["decision"], "continue")

        # Execution guard: executionNum >= 1 must allow stop to prevent infinite loop
        stop_guard = format_summaries([dirty], mode="hook_stop", execution_num=1)
        self.assertEqual(stop_guard["decision"], "allow")

    def test_hook_runner_subprocess_cycle(self) -> None:
        bad_md = self.root / "bad_paper.md"
        bad_md.write_text("See (FakeAuthor, 2026).\n\n## 참고문헌\n* Real, A. (2020). Title.\n", encoding="utf-8")

        env = os.environ.copy()
        env["PLUGIN_DATA"] = str(self.root / "pdata")
        env["AGY_FACTCHECK_TIER"] = "0"

        post_payload = json.dumps({
            "conversationId": "test-conv-1",
            "workspacePaths": [str(self.root)],
            "toolCall": {"name": "edit_file", "args": {"Path": "bad_paper.md"}},
        })
        p1 = subprocess.run(
            [sys.executable, str(HOOK_RUNNER), "PostToolUse"],
            input=post_payload,
            text=True,
            capture_output=True,
            env=env,
            check=True,
        )
        self.assertEqual(json.loads(p1.stdout), {})

        stop_payload = json.dumps({
            "conversationId": "test-conv-1",
            "terminationReason": "NO_TOOL_CALL",
            "executionNum": 0,
            "continuationActive": False,
        })
        p2 = subprocess.run(
            [sys.executable, str(HOOK_RUNNER), "Stop"],
            input=stop_payload,
            text=True,
            capture_output=True,
            env=env,
            check=True,
        )
        res = json.loads(p2.stdout)
        self.assertEqual(res["decision"], "continue")
        self.assertIn("ORPHAN_INTEXT_CITATION", res["reason"])

        # Second Stop with executionNum=1 must safely allow
        stop_payload2 = json.dumps({
            "conversationId": "test-conv-1",
            "terminationReason": "NO_TOOL_CALL",
            "executionNum": 1,
            "continuationActive": False,
        })
        p3 = subprocess.run(
            [sys.executable, str(HOOK_RUNNER), "Stop"],
            input=stop_payload2,
            text=True,
            capture_output=True,
            env=env,
            check=True,
        )
        self.assertEqual(json.loads(p3.stdout)["decision"], "allow")


if __name__ == "__main__":
    unittest.main()
