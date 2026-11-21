# [Phase 5 Research Report] Zero-Prompt, Low-Token Reference Fact-Checking Architecture & 4-Axis Benchmark Analysis

* **Platform:** Google Antigravity (AGY)
* **Principal Investigator (PI):** Chansu Shin (`@devshin-91` / `devshin91@gmail.com`)
* **Phase 5 Co-Research Model:** **Google Antigravity** (`Gemini 4 Hydrogen XHigh` — core architecture, engine & plugin implementation, live `agy` A/B benchmarking; Tier 2 comparison across `gemini-3.5-flash-lite`, `gemini-3.8-flash`, `gemini-4-hydrogen`, `gemini-4-neon`)
* **License:** [CC BY-NC 4.0](../LICENSE)

---

## 1. Motivation & Problem Statement

While Phase 1–4 `GEMINI.md` rules and the single-purpose verifier ([fact_check_references.py](../scripts/fact_check_references.py)) eliminated hallucinations **when explicitly prompted**, real-world usage exposed two operational bottlenecks:

1. **Prompt Dependency & Omission Risk:** Without an explicit user reminder (e.g., *"fact-check the references"*), models executing routine edits leave pre-existing orphan citations or mismatched DOI years untouched even when `GEMINI.md` rules are active.
2. **Token & Step Overhead:** Auditing a 21-reference manuscript (`morning-waking-paper`, steps `463–542`) via manual prompting consumed **124 logged records, 43 planner LLM responses, and 68 tool calls**, because the agent repeatedly re-authored ad-hoc verification scripts and ingested raw API/PDF dumps into the primary reasoning context.

---

## 2. Proposed Architecture: Tier 0–2 Offloading + AGY Lifecycle Hook Gate

```text
[Document Edit: write_file / edit_file]
        │
        ▼ (PostToolUse Hook, <15 ms, 0 LLM tokens)
  Mark modified document path in DirtyStateStore
        │
        ▼ (Turn Completion: Stop Hook)
  ┌─ Tier 0 (Offline Deterministic Engine, ~10 ms, 0 LLM tokens)
  │    • file:///#L... existence, bounds, semantic token alignment + 24KB rule budget
  │    • 1:1 in-text ↔ bibliography mapping + APA 7th ordering linter
  ├─ Tier 1 (SQLite WAL Cache + Crossref/CSL-JSON/Handle, Warm ~73 ms, 0 LLM tokens)
  │    • Automated DOI resolution + year, first author, title overlap, volume cross-check
  └─ Tier 2 (Low-Token PDF Snippet Slicer + Lightweight Model Escalation, on-demand)
       • Poppler pdftotext + signed-anchor Set-Cover (90–98% char reduction)
       • Escalate to Full PDF only when 1st-pass Snippet flags MISMATCH (Cascade)
        │
        ├─ PASS ──▶ decision: "allow" (0B injected to model; optional PreInvocation user_markdown badge)
        └─ FAIL ──▶ decision: "continue" + compact JSON diff (guarded up to 2 continuations)
```

---

## 3. Empirical Runtime Findings on Antigravity Lifecycle Hooks

Isolated `agy -p` probes revealed three critical runtime behaviors not captured by static documentation ([antigravity.google/docs/hooks](https://antigravity.google/docs/hooks)) and implemented directly in [hook_runner.py](../plugins/ref-fact-checker/hooks/hook_runner.py):

1. **Omitted Common Fields:** Actual stdin payloads omit `hookEventName` and `cwd` keys; handlers must identify the event via CLI arguments (`argv[1]`) and resolve relative file arguments against `workspacePaths[0]`.
2. **`continuationActive` Guard Necessity:** Protojson default-value omission causes `continuationActive` to arrive as `false` (or omitted) even on `executionNum >= 1` after a `Stop` continuation. Pairing `continuationActive` with `executionNum >= max_continuations` eliminates infinite `Stop` loops.
3. **Windows SQLite Locking & Crossref 429:** Standard `with sqlite3.connect(...)` does not close file handles on Windows (`contextlib.closing` is required). Crossref concurrency `>= 6` triggered HTTP `429` throttling; capping workers at `3` with exponential backoff and falling back to `doi.org` CSL-JSON Content Negotiation achieved zero `429` warnings across all 18 DOIs.

---

## 4. Quantitative 4-Axis Benchmark Results

### Axis 1. Tiered Verification Latency, Caching & Tier 2 PDF Model Comparison

#### (1) Tier 0–1 Latency & Cache Speedup (21-ref / 18-DOI draft)
| Stage | Latency | Live Network Calls | LLM Tokens |
| :--- | :---: | :---: | :---: |
| **Historical Manual Baseline** (`morning-waking-paper` `Step 463–542`) | Multi-minute | Ad-hoc scripts | **43 LLM responses / 68 tool calls** |
| **Tier 1 Cold** (First-time parallel Crossref/CSL-JSON lookup) | **`4,630.75 ms`** | `18` live calls | **`0` tokens** |
| **Tier 1 Warm** (SQLite WAL cache hit) | **`72.99 ms`** *(63.4x faster)* | `0` calls (`18` hits) | **`0` tokens** |
| **Dirty-Skip** (Unchanged SHA-256) | **`0.73 ms`** *(6,343x faster)* | `0` calls | **`0` tokens** |

#### (2) Tier 2 PDF Numerical Verification: `Full PDF` vs. `Set-Cover Snippet`
*(Evaluated via `google-genai` 3.3.0 Interactions API, `thinking_level="low"`, `store=False`)*

| Test Case | Mode (Prompt Size) | `gemini-3.5-flash-lite` | `gemini-3.8-flash` | `gemini-4-hydrogen` | `gemini-4-neon` |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`Ahn 2019` Numeric Flip Trap**<br>*(`α = 0.86 → 0.68`)* | **`Full PDF`** (`23,131 chars` / `9.6K–11.7K tok`) | ✅ `MISMATCH`<br>(`2,447ms` · `12,231 tok`) | ✅ `MISMATCH`<br>(`2,141ms` · `11,711 tok`) | ✅ `MISMATCH`<br>(`5,606ms` · `10,226 tok`) | ✅ `MISMATCH`<br>(`8,379ms` · `10,275 tok`) |
| **`Ahn 2019` Numeric Flip Trap** | **`Snippet`** (`2,582 chars` / **`1.1K–1.2K tok`**, `-88.5%–90.0%`) | ✅ **`MISMATCH`**<br>(**`1,055ms` · `1,219 tok`**) | ✅ **`MISMATCH`**<br>(**`1,937ms` · `1,222 tok`**) | ✅ `MISMATCH`<br>(`3,783ms` · `1,631 tok`) | ✅ `MISMATCH`<br>(`9,459ms` · `1,655 tok`) |
| **`Hill 2022` Clean Claim**<br>*(Internal AAM conflict: 44 qualitative vs. 43 meta; p.3 z=0.32 vs. p.35 z=0.31)* | **`Full PDF`** (`100,490 chars` / `27.5K–33.1K tok`) | ❌ `MISMATCH`<br>(`4,472ms` · `34,129 tok`) | ✅ **`MATCH`**<br>(**`3,941ms` · `33,212 tok`**) | ✅ `MATCH`<br>(`12,319ms` · `28,246 tok`) | ✅ `MATCH`<br>(`13,821ms` · `28,664 tok`) |
| **`Hill 2022` Clean Claim** | **`Snippet`** (`2,504 chars` / `846–867 tok`, `-97.4%`) | ❌ `MISMATCH`<br>(`1,169ms` · `916 tok`) | ❌ `MISMATCH`*(44 vs 43)*<br>(`2,060ms` · `886 tok`) | ❌ `MISMATCH`*(44 vs 43)*<br>(`6,055ms` · `1,281 tok`) | ❌ `MISMATCH`*(44 vs 43)*<br>(`8,254ms` · `1,385 tok`) |

* **Key Tier 2 Finding (Cascading Escalation):** Simple numerical falsifications (`0.86 → 0.68`) are caught with **100% accuracy across all 4 models** using **90% fewer tokens** via `Snippet` slicing (`1–2s` on `3.5-flash-lite`/`3.8-flash`). However, when a single PDF contains conflicting figures across distant sections (`44` included qualitative studies on p.3 vs. `43` meta-analyzed studies in Results), short snippets trigger conservative `MISMATCH` flags. Running **`Snippet + gemini-3.8-flash` (or `3.5-flash-lite`) first and escalating only `MISMATCH` verdicts to `Full PDF`** balances cost and precision.

---

### Axis 2. Live 3-Way `agy -p` A/B Comparison (`gemini-3.8-flash-medium`)

Executed on an isolated Git workspace editing `paper.md` seeded with 2 errors (`Ghost, 2025` orphan citation and `Hilditch & McHill, 2021` DOI year mismatch; [agy_ab_results.json](../benchmarks/agy_ab_results.json)):

| Condition | Explicit Fact-Check Prompt? | Duration | Total Tokens | Post-Audit Status | Remaining Defects |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`C1` Rule Only (Trap)** | ❌ Unprompted | `83.05 s` | `51,591` | ❌ **`FAIL`** | `2 FAIL / 1 WARN` **(100% missed)** |
| **`C2` Manual Prompted (Trap)** | ✅ Manual prompt | `59.63 s` | `40,238` | ✅ `PASS` | `0` *(requires manual prompting every time)* |
| **`C3` Hook Gate (Trap)** | ❌ **Unprompted** | `112.10 s` | `63,274` | ✅ **`PASS`** | **`0` (auto-detected & fixed via `Stop` gate)** |
| **`C4` Hook Gate (Clean)** | ❌ **Unprompted** | **`23.01 s`** | **`27,693`** | ✅ **`PASS`** | **`0` (0 extra turns; -46.3% tokens vs `C1`)** |

---

### Axis 3. Feedback Protocol Payload Comparison

| Format Mode | `PASS` Bytes Injected to Model | `FAIL` Bytes Injected to Model | Operational Benefit |
| :--- | :---: | :---: | :--- |
| **`raw`** | `502 B` | `2,713 B` | Full verbose JSON dump |
| **`compact_diff`** | `77 B` (`-84.7%`) | `1,779 B` (`-34.4%`) | Non-empty actionable fields only |
| **`hook_stop`** | **`0 B` (`-100%`)** | **`1,389 B` (`-48.8%`)** | **Zero re-entry on PASS**; capped top-8 diff on FAIL |
| **`hook_pre`** (`metadata.user_markdown`) | **`0 B` (`-100%`)** | **`0 B` (`-100%`)** | Renders inline UI status badge with zero model context cost |

---

### Axis 4. 16-Case Trap Stress Test Summary

Across 2 real clean baselines (`GEMINI.ko.md` with 19 `file:///` links and `step4_full_draft.md` with 21 references / 86 in-text citations) plus 14 injected failure traps ([run_tier_bench.py](../benchmarks/run_tier_bench.py)):
* **Trap Detection Recall:** **`14 / 14` (`100.0%`)** (`A1–A5` local/budget traps in `2.75–19.91 ms`; `B1–B9` DOI/citation/APA traps in `63.13–1,880.13 ms`).
* **Clean False Positive Rate:** **`0 / 2` (`0.0%`)**.

---

## 5. Production Recommendation

1. **Always-On Tier 0–1 Baseline:** Enable `plugins/ref-fact-checker` globally (`PostToolUse` + `Stop` + `PreInvocation` + SQLite WAL cache) to eliminate omission risk with zero extra LLM turns on clean edits.
2. **Keep `GEMINI.md` Lean:** Offload procedural reference verification to deterministic hooks and CLI tools rather than bloating the 24KB instruction budget.
3. **Cascade Tier 2 Only Before Final Submission:** Run `python -m ref_factcheck evidence` (`Snippet + gemini-3.8-flash` first, escalating only `MISMATCH` cases to `Full PDF`) during pre-submission numerical audits.

---

## 6. Limitations & Human Final Responsibility

1. **Chunk-Boundary Context Blindness:** As demonstrated in the `Hill 2022` Tier 2 evaluation, when a single paper contains conflicting or dual-reported numbers across distant sections (`44` qualitative studies / `z = 0.32` on p.3 vs. `43` meta-analyzed studies / `z = 0.31` on p.35), localized snippets or lightweight models can emit false-positive `MISMATCH` alerts or miss subtle contextual distinctions.
2. **Coverage Boundaries (Non-DOI, Semantic Distortion & PDF Extraction):**
   * Deterministic Tier 0–1 checks verify file/line bounds, 1:1 citation mapping, APA order, and Crossref/DOI metadata—they do **not** guarantee semantic fidelity of **non-DOI sources** (press releases, books, conference abstracts) or catch **valid statistics framed with exaggerated causal claims**.
   * Scanned image PDFs without an OCR text layer, complex multi-column tables, and non-standard font encodings can lose digits or signs during Poppler `pdftotext` extraction.
3. **Bounded `Stop`-Hook Continuation Guard (`max_continuations=2`):** To prevent infinite loops and runaway token spend, the `Stop` hook caps automated retries per turn. Complex failures left unresolved after the retry budget require manual resolution.
4. **AI Fallibility & Human Co-Responsibility / Final Accountability:**
   * Even with deterministic guardrails and cascading LLM checks, **AI agents remain probabilistic systems capable of mistakes, misinterpretations, and faulty edits.**
   * Any human collaborating with AI acts as both a **co-responsible partner (Co-Owner)** in the workflow and the **final accountable authority (Final Sign-Off)** for academic publication, code release, or production deployment. A hook `PASS` never substitutes for **direct human final review** of primary sources, figures, and conclusions prior to release.
