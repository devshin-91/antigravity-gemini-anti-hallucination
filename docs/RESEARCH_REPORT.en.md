# [Research Report] Empirical A/B Benchmark of Anti-Hallucination Guardrails Across Gemini 3.8 Flash & Gemini 4 Series on Google Antigravity

* **Platform:** Google Antigravity (AGY)
* **Principal Investigator (PI):** Chansu Shin (`@devshin-91` / `devshin91@gmail.com`)
* **Co-Research & Evaluation Model:** **Gemini 4 Argon (High)** (`gemini-4-argon-high`)
* **Target Subscription Plan & Models:** Google AI Pro (`g1-pro`) — `Gemini 3.8 Flash`, `Gemini 4 Hydrogen`, `Gemini 4 Neon`, `Gemini 4 Argon`
* **License:** [CC BY-NC 4.0](../LICENSE) (Non-Commercial Shareable with Attribution)

---

## 1. Research Motivation & Problem Statement

1. **Initial Observation:** Many users and developers experienced frequent hallucinations with `Gemini 3.8 Flash` out of the box, leading to the common perception that the model was unreliable for production engineering.
2. **Turning Point (The Grounding Discovery):** Practical experimentation revealed that when `Gemini 3.8 Flash` was prevented from answering immediately from internal weights and instead forced to ground its claims via external search (`search_web`) or local documentation tools, its accuracy and utility improved dramatically.
3. **Hypothesis Formulation via Official Specs:** Reviewing the official **[Gemini Developer API Pricing & Model Documentation (`aistudio.google.com/docs/pricing`)](https://aistudio.google.com/docs/pricing)** confirmed that `Gemini 3.8 Flash` is engineered for *"long-horizon software engineering, autonomous agents, and complex enterprise workflows."* We hypothesized that **its baseline errors stem from skipping tool verification under high parametric confidence rather than lacking reasoning capability—meaning systematic anti-hallucination guardrails can unlock its full speed and cost efficiency.**
4. **4-Stage Empirical Methodology:**
   - **Experiment 1:** Initial A/B testing on `Gemini 3.8 Flash` comparing `Condition A (Unguarded)` vs. `Condition B (Guarded with GEMINI.md)`.
   - **Experiment 2:** Expansion across **8 distinct information categories (24 sub-items)** covering diverse real-world hallucination traps.
   - **Experiment 3:** Generalization to all core models available in the **Google AI Pro** plan (`Gemini 3.8 Flash`, `Gemini 4 Hydrogen`, `Gemini 4 Neon`, `Gemini 4 Argon`; excluding Ultra-only `Carbon`), mapping each model's optimal workload and characteristic failure modes to tailored `GEMINI.md` profiles.
   - **Experiment 4:** Automated programmatic fact-checking of every reference path, line number range (`#Lstart-Lend`), and semantic keyword using Python (`scripts/fact_check_references.py`).

---

## 2. Experiment 1 & 2: Gemini 3.8 Flash Across 8 Information Categories

| Information Category | Condition A<br>(Unguarded) | Condition B<br>(`GEMINI.md` Guarded) | Score Gain<br>(Relative Lift) | Key Hallucination Eliminated by Condition B |
| :--- | :---: | :---: | :---: | :--- |
| **1. Language & Stdlib Version Deltas**<br>*(Python 3.11 vs 3.12 vs 3.13)* | `14 / 20`<br>(70%) | **`20 / 20`**<br>(100%) | **`+6 pts`**<br>(`+42.9%`) | **Parametric Interference:** Relied on Python 3.12 memory without running tools and falsely claimed Python 3.13 `itertools.batched` lacks `strict=True` |
| **2. Bleeding-Edge AI Text/TTS/Decision SDKs**<br>*(Gemini 3.8 / TTS / Decision 1)* | `3 / 20`<br>(15%) | **`20 / 20`**<br>(100%) | **`+17 pts`**<br>(`+566.7%`) | **Severe Reverse Hallucination:** Skipped MCP/Skill docs and declared `gemini-3.8-flash`, `gemini-decision-1`, and `3.8-flash-tts` "fictional models" |
| **3. Multimodal Video/Image Constraints**<br>*(Omni 1.2 Flash / Nano Banana 2.1)* | `16 / 20`<br>(80%) | **`20 / 20`**<br>(100%) | **`+4 pts`**<br>(`+25.0%`) | **Third-Party Web Noise:** Ignored local official `SKILL.md` in favor of web blogs, encountering inaccurate blog numbers (10 refs vs. 6) and omitting citations |
| **4. Local Tech Specs & Legacy Doc Conflicts**<br>*(README v2.0 vs Code v2.4)* | `16 / 20`<br>(80%) | **`20 / 20`**<br>(100%) | **`+4 pts`**<br>(`+25.0%`) | **Missing Traceability:** Found the values but omitted all verbatim code quotes and clickable file/line links (`#L...`) |
| **5. Financial & Multi-Doc Contractual Audit**<br>*(12% Contract vs 10% Invoice)* | `16 / 20`<br>(80%) | **`20 / 20`**<br>(100%) | **`+4 pts`**<br>(`+25.0%`) | **Missing Audit Evidence:** Computed the `\$3,012.00` overbilling correctly but omitted verbatim contract clauses and JSON line links |
| **6. International Standards (RFC) & Fake Papers**<br>*(RFC 9110, Fake NeurIPS/BOK Notice)* | `18 / 20`<br>(90%) | **`20 / 20`**<br>(100%) | **`+2 pts`**<br>(`+11.1%`) | **Shallow Refutation:** Flagged the fake paper but failed to cite the actual 2024 NeurIPS Best Papers or PostgreSQL `pg_class.reloptions` catalog |
| **7. Cybersecurity (Fake CVE) & Code Audit**<br>*(Fake CVE-2025-88888, Privilege Escalation)* | `15 / 20`<br>(75%) | **`20 / 20`**<br>(100%) | **`+5 pts`**<br>(`+33.3%`) | **Missed Exploit Path:** Missed how an unauthenticated request (`row == None`) inherits `['admin']` from the shared mutable default list |
| **8. Precision Math, Encoding & Binding**<br>*(UTF-8 NFC/NFD, IEEE-754, CRC32)* | `18 / 20`<br>(90%) | **`20 / 20`**<br>(100%) | **`+2 pts`**<br>(`+11.1%`) | **Missing Mechanism:** Computed `sum([0.1]*10) == 1.0` (`True`) via Python but omitted the Python 3.12+ Neumaier compensated summation explanation |
| **8-Category Total** | **`116 / 160`**<br>**(`72.50%`)** | **`160 / 160`**<br>**(`100.00%`)** | **`+44 pts`**<br>**(`+37.93%`)** | **100.0% elimination of hallucination and grounding defects (`44 pts → 0 pts`)** |

---

## 3. Experiment 3: Model-Specific A/B Benchmark Across All 4 Google AI Pro Models

Evaluated by **Gemini 4 Argon (High)** on a 100-point rubric per model (400 points total):

| Model (Google AI Pro) | Evaluation Tasks (100 pts) | Condition A<br>(Unguarded) | Condition B<br>(Tailored `GEMINI.md`) | Score Gain<br>(Relative Lift) | Model-Specific Hallucination Eliminated |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **1. Gemini 3.8 Flash**<br>(`gemini-3.8-flash`) | Local spec conflict, false premise, Python 3.13 `strict=True`, Gemini 3.8/TTS/Decision SDK, deterministic execution | **`73 / 100`** | **`100 / 100`** | **`+27 pts`**<br>(`+36.99%`) | Eliminated reverse hallucinations where the model declared new SDK models "fictional" without checking installed MCP/Skill docs |
| **2. Gemini 4 Hydrogen**<br>(`gemini-4-hydrogen`) | `app.yaml` vs `deploy_history.log` mid-log hotfix, `lstrip` normalization bug & edge-case patch, `3.5-transcribe` schema | **`75 / 100`** | **`100 / 100`** | **`+25 pts`**<br>(`+33.33%`) | Fixed premature patch bug on mixed-case (`Usr-`) & double prefixes (`USR-usr-`), and replaced informal `"Smart Dictation"` guess with exact `transcription_config.mode.type` schema |
| **3. Gemini 4 Neon**<br>(`gemini-4-neon`) | `asyncio` closure late-binding & GC task set patch, fake Dijkstra-Bellman theorem disproof, Live API & Managed Agents `agent_config` | **`72 / 100`** | **`100 / 100`** | **`+28 pts`**<br>(`+38.89%`) | Eliminated mixing of deprecated `gemini-2.5-*` models into active Live API lists and fixed omission of required `"type": "antigravity"` discriminator in `agent_config` |
| **4. Gemini 4 Argon**<br>(`gemini-4-argon`) | `crypto_auth.py` 3 crypto flaws (prefix slice & AES-GCM Forbidden Attack), Long Decode 1M spec, 2D list aliasing & BLAKE2b, Implicit Caching | **`80 / 100`** | **`100 / 100`** | **`+20 pts`**<br>(`+25.00%`) | Eliminated over-rationalized invention of a non-existent `continuation_token` parameter and added co-required `max_output_tokens > 65536` + `interaction.steps` joining logic |
| **4-Model Combined Total** | **400 Points Maximum** | **`300 / 400`**<br>**(`75.00%`)** | **`400 / 400`**<br>**(`100.00%`)** | **`+100 pts`**<br>**(`+33.33%`)** | **100.0% defect reduction across all 4 available Google AI Pro models** |

---

## 4. Experiment 4: Automated Reference Integrity Fact-Check

Executed via `scripts/fact_check_references.py`:
* **AGY Rule Size Compliance:** `14,287 bytes / 24,000 bytes` (`59.5%` of the 24KB AGY per-file cap).
* **File Existence & Line-Range Validity (`#Lstart-Lend`):** `19 / 19 PASS` in `GEMINI.md` (`100%`).
* **Semantic Keyword Match Inside Cited Line Ranges:** `19 / 19 PASS` (`100%`).
