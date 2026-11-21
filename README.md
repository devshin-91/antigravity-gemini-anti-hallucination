<div align="center">

# 🛡️ Antigravity Gemini Anti-Hallucination Framework
### Empirical Anti-Hallucination Guardrails & A/B Benchmark Suite for Gemini 3.8 Flash & Gemini 4 Series (Hydrogen · Neon · Argon) on Google Antigravity

[![Platform](https://img.shields.io/badge/Platform-Google%20Antigravity%20(AGY)-4285F4?style=for-the-badge&logo=google)](https://antigravity.google/docs)
[![Research Partner](https://img.shields.io/badge/Co--Research%20Model-Gemini%204%20Argon%20(High)-8E24AA?style=for-the-badge)](https://aistudio.google.com/docs/latest-model.md)
[![Target Models](https://img.shields.io/badge/Models-Gemini%203.8%20Flash%20%7C%204%20Hydrogen%20%7C%204%20Neon%20%7C%204%20Argon-0F9D58?style=for-the-badge)](https://aistudio.google.com/docs/pricing)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0%20(Non--Commercial)-F4B400?style=for-the-badge)](./LICENSE)
[![Repository Visibility](https://img.shields.io/badge/Repository-Private%20Research-333333?style=for-the-badge)]()

**[🇺🇸 English (README.md)](./README.md) | [🇰🇷 한국어 (README.ko.md)](./README.ko.md)**

</div>

---

> 📌 **GitHub Sidebar ("About") Metadata (For Top-Right Repository Sidebar)**
> - **Description (About):** `[Antigravity Research] Empirical anti-hallucination guardrails & A/B benchmark suite for Gemini 3.8 Flash and Gemini 4 (Hydrogen, Neon, Argon) on Google Antigravity, co-researched with Gemini 4 Argon (High).`
> - **Topics (Tags):** `antigravity` `google-antigravity` `gemini-4-argon` `gemini-3-8-flash` `gemini-4-hydrogen` `gemini-4-neon` `anti-hallucination` `llm-grounding` `ab-testing`

---

## 1. Motivation & Problem Definition

### "Is Gemini 3.8 Flash too prone to hallucination for production?" — From Frustration to Hypothesis

Many developers and everyday users initially found **Gemini 3.8 Flash (`gemini-3.8-flash`)** frustrating to use due to frequent, confident hallucinations when relying solely on its parametric memory. This research began from that exact real-world pain point.

However, an important observation emerged during practical testing: **when Gemini 3.8 Flash was forced to ground its claims via external search or local documentation tools before answering, its reliability improved dramatically.**

By cross-referencing the official **[Gemini Developer API Pricing & Model Specifications (`aistudio.google.com/docs/pricing`)](https://aistudio.google.com/docs/pricing)**, we formulated the core hypothesis of this study:

1. **Core Hypothesis:** According to official specifications, `Gemini 3.8 Flash` is specifically engineered for *"long-horizon software engineering, autonomous agents, and complex enterprise workflows."* Its baseline failures are not due to a lack of reasoning capacity, but rather **a tendency to skip tool verification when internal parametric confidence is high**. If we systematically eliminate these hallucinations, Gemini 3.8 Flash becomes an extraordinarily cost-effective, high-speed workhorse.
2. **Phase 1 (Gemini 3.8 Flash Initial A/B Test):** We designed a global anti-hallucination rule architecture (`GEMINI.md`) for **Google Antigravity (AGY)** and conducted a controlled A/B test (`Condition A: Without rules` vs. `Condition B: With rules`). Accuracy jumped from **`73/100 to 100/100 (+36.99%)`**, eliminating 100% of factual and reverse hallucinations.
3. **Phase 2 (8-Category Information Stress Test):** Rather than testing only simple cases, we expanded the benchmark across **8 distinct information domains (24 sub-tasks: language version deltas, bleeding-edge AI SDKs, multimodal constraints, legacy vs. production doc conflicts, financial/contract audits, RFC standards & fake academic papers, cybersecurity CVEs & code audits, and Unicode/IEEE-754 precision computation)**. Condition B achieved **`160/160 (100.00%)` vs. Condition A's `116/160 (72.50%)` (`+37.93%` improvement)**.
4. **Phase 3 (Generalization Across All Google AI Pro Models):** Having proven the methodology on Gemini 3.8 Flash, we expanded the framework to every core Gemini model available under the **Google AI Pro** subscription plan inside Antigravity: **`Gemini 3.8 Flash`**, **`Gemini 4 Hydrogen`**, **`Gemini 4 Neon`**, and **`Gemini 4 Argon`**. *(Note: `Gemini 4 Carbon` is excluded both because it is reserved for the Google AI Ultra plan and because it serves as the top-end heavyweight model).*
5. **Phase 4 (Forward-Compatibility & Next-Generation Upgrade Architecture):** To guarantee that our global rules remain compatible when `Gemini 3.8 Flash` upgrades to higher versions (`3.9`, `4.x`, `5.x Flash`) or when `Gemini 4` transitions to `Gemini 5` (`gemini-5-*`) and new chemical-element models without causing rule obsolescence, we engineered a **Generation-Agnostic Forward-Compatibility Protocol** featuring: (1) Wildcard Model-Lineage Archetypes (`gemini-*-flash*`, `gemini-*-hydrogen*`, `gemini-*-neon*`, `gemini-*-argon*`), (2) Dynamic Generation Precedence (never force-downgrading newer generations), (3) Live Official Spec Override over baseline numbers, (4) Sliding Deprecation Windows, and (5) Dynamic Line-Number Re-Verification across plugin updates.
6. **Phase 5 (Zero-Prompt, Low-Token Automated Reference Fact-Checking):** Manual fact-checking prompts incur high token/step overhead (`43 LLM responses / 68 tool calls` observed in `morning-waking-paper` steps `463–542`), while unprompted edits miss errors. We engineered a **Tier 0–2 Verification Engine (`src/ref_factcheck/`)** and an **AGY Lifecycle Hook Plugin (`plugins/ref-fact-checker/`)** and evaluated them across a 4-axis benchmark ([Phase 5 Research Report](./docs/PHASE5_REFERENCE_FACTCHECK_REPORT.en.md)).

---

## 2-1. Phase 5 Highlights: Eliminating Omissions & Unnecessary Token Spend

| Metric / Evaluation Axis | Baseline (Rules / Manual) | Phase 5 (`ref-fact-checker`) | Measured Gain |
| :--- | :---: | :---: | :--- |
| **Unprompted Trap Detection** (`agy -p`) | `Rule Only (C1)`: `2 FAIL / 1 WARN` **missed** (`83.05s`, `51,591 tok`) | `Hook Gate (C3)`: **Auto-fixed to `PASS`** (`0 fails`, `0 warns`) | **100% → 0% omission rate** |
| **Clean Edit Overhead** (`agy -p`) | `Rule Only (C1)`: `83.05s` · `51,591 tok` | `Hook Gate Clean (C4)`: **`23.01s` · `27,693 tok`** (`0` extra turns) | **`-72.3%` latency · `-46.3%` tokens** |
| **21-Ref / 18-DOI Verification Speed** | Ad-hoc LLM scripts | Cold `4,630.8ms` → Warm SQLite `72.99ms` → Dirty-Skip **`0.73ms`** | **`63.4x` cached · `6,343x` dirty-skip (`0` LLM tok)** |
| **16-Case Stress Test** (Track A + B) | Rule-file-only checker | **14/14 traps caught (`100%`), 2/2 clean (`0%` FP)** | **Full local link + academic DOI/APA coverage** |
| **Tier 2 PDF Slicing (`Snippet` vs `Full`)** | Full PDF context ingestion | `Ahn 2019` flip trap: `11,656 → 1,160` input tok (**`4/4` models 100%**) | **`-90%` input tokens (`1–2s`) + Cascade fallback** |

---

## 2. Key Findings: Hallucinations Don't Disappear in Larger Models — They Change Shape

Through controlled A/B experiments evaluated by **Gemini 4 Argon (High)**, we discovered that each model tier exhibits its own **characteristic hallucination failure mode** tied to its primary workload:

| Model (Google AI Pro) | Optimal Workload | Characteristic Hallucination in Condition A (Unguarded) | A/B Score Improvement (Condition A → B) |
| :--- | :--- | :--- | :---: |
| **Gemini 3.8 Flash**<br>(`gemini-3.8-flash`) | High-speed data/doc pipelines, rapid scripting, lightweight agent loops | **Parametric Overconfidence & Reverse Hallucination:** Skips local MCP/Skill lookup and declares real 2026 models (`gemini-decision-1`, `3.8-flash-tts`) "fictional" or denies Python 3.13 `strict=True` support | `73 → 100`<br>**(`+36.99%`)** |
| **Gemini 4 Hydrogen**<br>(`gemini-4-hydrogen`) | Fast interactive coding, batch tool execution, implementation worker | **Premature Patching & Edge-Case Omission:** Submits patches without testing mixed-case (`Usr-`) or repeated-prefix (`USR-usr-`) edge cases; guesses informal names (`"Smart Dictation"`) instead of exact API schemas | `75 → 100`<br>**(`+33.33%`)** |
| **Gemini 4 Neon**<br>(`gemini-4-neon`) | Multi-file refactoring, async/concurrency debugging, STEM reasoning | **Legacy/Current API Mixing & Missing Discriminators:** Mixes deprecated `gemini-2.5-*` models into active Live API lists and omits required `"type": "antigravity"` discriminator in `agent_config` | `72 → 100`<br>**(`+38.89%`)** |
| **Gemini 4 Argon**<br>(`gemini-4-argon`) | Frontier architecture design, cryptographic/security audit, 1M Long Decode | **Over-Rationalization in Deep Reasoning:** Invents plausible-sounding but non-existent SDK parameters (`continuation_token`) and omits co-required flags (`max_output_tokens > 65536` + joining `interaction.steps`) | `80 → 100`<br>**(`+25.00%`)** |
| **Combined Total** | **Full-Stack Engineering & Research** | **100 points lost to model-specific hallucinations & missing line citations** | **`300 → 400`**<br>**(`+33.33%` / 100% defect elimination)** |

---

## 3. Repository Structure

```text
antigravity-gemini-anti-hallucination/
├── README.md                                  # [English] Main documentation & Quickstart
├── README.ko.md                               # [한국어] Korean Main documentation & Quickstart
├── CONTRIBUTORS.md                            # Role breakdown between Human PI and AI Partners (Argon High · Hydrogen XHigh)
├── LICENSE                                    # CC BY-NC 4.0 (Non-Commercial Shareable License)
├── rules/
│   ├── GEMINI.ko.md                           # [한국어] Production GEMINI.md rules (Global + Model-Specific)
│   └── GEMINI.en.md                           # [English] Production GEMINI.md rules (Global + Model-Specific)
├── docs/
│   ├── RESEARCH_REPORT.ko.md                  # [한국어] Phase 1–4 A/B Test & Fact-Check Research Report
│   ├── RESEARCH_REPORT.en.md                  # [English] Phase 1–4 A/B Test & Fact-Check Research Report
│   ├── PHASE5_REFERENCE_FACTCHECK_REPORT.ko.md # [한국어] Phase 5 Zero-Prompt Fact-Check 4-Axis Report
│   └── PHASE5_REFERENCE_FACTCHECK_REPORT.en.md # [English] Phase 5 Zero-Prompt Fact-Check 4-Axis Report
├── src/
│   └── ref_factcheck/                         # Tier 0–2 verification engine (offline, SQLite WAL cache, Poppler PDF slicer, CLI)
├── plugins/
│   └── ref-fact-checker/                      # Native Antigravity plugin bundle (hooks.json + hook_runner.py + SKILL.md + AGENTS.md)
├── benchmarks/
│   ├── run_tier_bench.py                      # Axes 1, 3, 4 benchmarks (16 traps, cache, format sizes, Tier 2 4-model eval)
│   ├── run_agy_ab_bench.py                    # Axis 2 live agy -p 3-way A/B benchmark
│   ├── tier_bench_results.json                # Measured Axes 1, 3, 4 results
│   └── agy_ab_results.json                    # Measured Axis 2 results
├── tests/
│   └── test_ref_factcheck.py                  # Unit & subprocess hook integration tests
└── scripts/
    ├── fact_check_references.py               # Automated verifier for file paths, line ranges, and semantic keywords
    └── install_plugin.py                      # Self-contained installer to ~/.gemini/config/plugins/ref-fact-checker
```

---

## 4. Quick Installation on Google Antigravity (AGY)

Copy either the English (`rules/GEMINI.en.md`) or Korean (`rules/GEMINI.ko.md`) ruleset to your global Antigravity configuration path (`~/.gemini/config/GEMINI.md`):

```powershell
# Windows (PowerShell) - English or Korean
Copy-Item .\rules\GEMINI.en.md "$HOME\.gemini\config\GEMINI.md" -Force
# Or for Korean:
Copy-Item .\rules\GEMINI.ko.md "$HOME\.gemini\config\GEMINI.md" -Force
```

```bash
# macOS / Linux
cp ./rules/GEMINI.en.md ~/.gemini/config/GEMINI.md
```

### Step 2. Install the Phase 5 Zero-Prompt Fact-Checker Plugin (Global AGY Automation)
To enforce automatic verification on markdown/rule edits without manual prompts (and zero extra tokens on clean edits), run the installer from the repository root. It bundles `src/ref_factcheck/` into a self-contained plugin and pins your active Python interpreter path inside `~/.gemini/config/plugins/ref-fact-checker/hooks.json`:

```bash
# Windows / macOS / Linux (Python 3.10+)
python ./scripts/install_plugin.py
```

* **Standalone CLI Usage:**
  ```bash
  PYTHONPATH=src python -m ref_factcheck check path/to/paper.md --tier 1 --format compact_diff
  ```
* **Tier 2 PDF Evidence Slicing (Optional):** Requires Poppler (`pdftotext`) and `google-genai` (`python -m ref_factcheck evidence paper.md --refs-dir references/`).
* **Disable / Uninstall:** Toggle off in the Antigravity Customizations UI (`ref-fact-checker`) or remove `~/.gemini/config/plugins/ref-fact-checker`.

---

## 5. Limitations & Human Final Responsibility

* **Technical & Algorithmic Boundaries:**
  * **Chunk-Boundary Context Blindness:** As observed in the `Hill 2022` benchmark, when a single paper reports dual figures across distant sections (`44` qualitative studies / `z=0.32` on p.3 vs. `43` meta-analyzed studies / `z=0.31` on p.35), localized snippets and lightweight models can emit false-positive `MISMATCH` flags unless escalated to the full source.
  * **Non-DOI & Semantic Coverage Limits:** Deterministic Tier 0–1 checks verify `file:///#L...` bounds, DOI metadata, 1:1 citation mapping, and APA ordering—they do **not** validate **non-DOI sources** (press releases, books), **overstated causal interpretations** of accurate numbers, or **un-OCR'd scanned PDFs**.
  * **Bounded Retry Guard (`max_continuations=2`):** The `Stop` hook limits automatic continuation loops to 2 retries per turn to avoid runaway token usage.
* **AI Fallibility & Human Co-Responsibility / Final Sign-Off:**
  * Automated hooks and LLMs are **risk-reduction guardrails**, not infallible oracles—**AI can still make mistakes, overlook context, or introduce faulty edits.**
  * Anyone working alongside AI is both a **co-responsible collaborator (Co-Owner)** and the **final accountable authority (Final Sign-Off)** for academic publication, production release, or external decisions. **Final human verification of primary sources and conclusions remains mandatory.**

---

## 6. Contributors

See [CONTRIBUTORS.md](./CONTRIBUTORS.md) for the complete division of roles:

* **Principal Investigator & Research Lead — Chansu Shin (`@devshin-91` / `devshin91@gmail.com`)**: Problem definition, empirical observation of Gemini 3.8 Flash grounding behavior, official pricing/task hypothesis formulation (`aistudio.google.com/docs/pricing`), 5-phase experimental design (including Zero-Prompt Phase 5 and Human-in-the-Loop governance), and licensing policy.
* **AI Co-Researcher, Benchmark Architect & Evaluator (`Google Antigravity` — [`@antigravity-bot`](https://github.com/antigravity-bot))**:
  - **Phase 1–4 (`Gemini 4 Argon High`):** Literature & API documentation synthesis, 2-tier `GEMINI.md` guardrail engineering, trap codebase construction, AGY Native Swarm A/B execution, quantitative rubric grading, and initial reference fact-checking.
  - **Phase 5 (`Gemini 4 Hydrogen XHigh`):** Baseline session profiling, live AGY `hooks.json` runtime probing, Tier 0–2 `ref_factcheck` engine & `plugins/ref-fact-checker` implementation, 16-case trap stress testing, live `agy -p` 3-way A/B evaluation, and 4-model Tier 2 PDF comparison.

---

## 7. License (CC BY-NC 4.0)

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License ([CC BY-NC 4.0](./LICENSE))**.
* **Share & Adapt:** You may freely copy, share, and adapt this work for personal, academic, or non-commercial research use.
* **Attribution Required:** You must give appropriate credit to the author and the co-research platform/models (**Google Antigravity** · **Gemini 4 Argon High** · **Gemini 4 Hydrogen XHigh**).
* **Non-Commercial Only:** Commercial use, resale, or bundling into paid commercial products/courses is strictly prohibited.
