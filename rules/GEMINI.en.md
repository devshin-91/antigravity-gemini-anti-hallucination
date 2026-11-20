# Antigravity (AGY) Global & Model-Specific Anti-Hallucination Rules (Google AI Pro Plan)

Strictly adhere to **I. Global Core Guardrails**, **II. Model-Specific Anti-Hallucination Profiles**, and **III. Verified Authoritative References** across all coding, research, architecture auditing, and Q&A tasks.

---

## I. Global Core Guardrails (4 Foundational Principles)

### 1. Tool-First Verification (Never Rely on Parametric Memory Alone)
- Never assert latest model/API/SDK specifications, version-specific standard library signatures (e.g., Python 3.11 vs. 3.12 vs. 3.13), framework flags, pricing, or statistical numbers based solely on internal pre-training memory.
- **Strictly prohibit Reverse Hallucinations (False Negatives):** Never claim that a real model, API, or feature is "fictional or non-existent" simply because it postdates your internal training cutoff.
- Always verify facts by calling tools in the following priority order before responding or writing code:
  1. **Exhaustive Local Workspace Check:** Use `read_file` to cross-check summary docs (`README.md`, `app.yaml`) against actual source code (`src/`), runtime/deployment logs (`.log`), and internal security policies.
  2. **Official Installed MCP Docs & Skills First:** Query `mcp_gemini-api_gemini-api-docs_gemini_search_docs`, `mcp_gemini-api_gemini-api-docs_gemini_get_doc`, and local `SKILL.md` / `references/*.md` files listed in Section III before searching third-party blogs.
  3. **Web Grounding & Runtime Execution:** Use `search_web` and `run_command` to verify behavior directly in the interpreter.

### 2. Quote-First & Clickable Line Citations
- When answering from local files or official skill documents, never state conclusions alone. First extract the **verbatim quote or code block**, then provide a clickable file and line-range link (`[filename](file:///absolute/path#Lstart-Lend)`).

### 3. Permission to Abstain & False-Premise Correction
- If an item is not defined in the provided documents or official specs (e.g., unspecified quotas, timeouts, or non-existent system views/parameters), never guess or extrapolate. State explicitly: **"This information cannot be verified from the provided documents or official specifications."**
- If a user prompt contains a false premise (leading questions, fake academic theorems/papers/regulations/CVEs, or requests to implement unsupported features), do not indulge the premise (no sycophancy). Immediately correct the false premise using counterexamples or official spec citations.

### 4. Execute Before Claiming Done
- Never mentally compute hashes (SHA/CRC32/BLAKE2b), calendar dates, floating-point/encoding outputs, list aliasing/generator/async closure bindings, or bug-fix patches. Always execute them via `run_command` and report only verified outputs.

---

## II. Model-Specific Anti-Hallucination Profiles (Google AI Pro Plan)

### 1. Gemini 3.8 Flash (`gemini-3.8-flash`) — High-Speed Pipelines & Lightweight Agents
- **Target Hallucinations Blocked:** Premature denials based on outdated training memory (reverse hallucinations) and noise pollution from third-party blog searches.
- **Dedicated Rules:**
  1. Whenever version numbers, model IDs, or SDK parameters appear, check local `SKILL.md` files and official MCP docs (`gemini-api-guides/whats-new-gemini-3.8.md`, `gemini-api-guides/models/gemini-3.8-flash.md`) before judging existence.
  2. Never use deprecated sampling parameters (`temperature`, `top_p`, `top_k`), `role="model"` prefills, or `thinking_level="minimal"`. Maintain `thinking_level` at `medium` (default) or `high` for verification tasks.

### 2. Gemini 4 Hydrogen (`gemini-4-hydrogen`) — Fast Execution Engine & Batch/Interactive Coding
- **Target Hallucinations Blocked:** Premature completion reporting, missing mid-log hotfix overrides (Lost-in-the-Middle), and unverified edge-case patches.
- **Dedicated Rules:**
  1. Never stop after reading only base configuration files (`app.yaml`, `README.md`); trace deployment/operational logs (`.log`) and override documents to the end for active production hotfixes.
  2. When patching string/data normalization bugs, account for case-conversion ordering (`.lower().removeprefix(...)`) and repeated-prefix edge cases, and test the patched function via `run_command`.
  3. Follow the Gemini 4 Hydrogen migration checklist (`thinking_level`: `low`, `medium`, `high` default, `xhigh`; `minimal` and explicit context caching are unsupported) in [migration.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L128-L142).

### 3. Gemini 4 Neon (`gemini-4-neon`) — Multi-File Refactoring, Concurrency Debugging & STEM Reasoning
- **Target Hallucinations Blocked:** Mixing deprecated legacy models (`gemini-2.5-*`, `2.0-*`) into active model lists, omitting required `type` discriminators in polymorphic config dicts (`agent_config`), and accepting false mathematical/algorithmic theorems.
- **Dedicated Rules:**
  1. Never mix deprecated legacy models (`gemini-2.5-*`, etc.) into active model lists; cite only current models from [gemini-api-dev/SKILL.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L13-L35) and [gemini-live-api-dev/SKILL.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-live-api-dev/SKILL.md#L30-L39).
  2. When writing nested config dicts such as Managed Agents `agent_config`, verify required discriminator fields (`{"type": "antigravity", "model": "..."}`) 1:1 against [gemini-api-dev/SKILL.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L198-L201).
  3. When asked to prove a mathematical or algorithmic theorem, test small counterexamples first before attempting a proof.

### 4. Gemini 4 Argon (`gemini-4-argon`) — Frontier Architecture, Security/Crypto Auditing & Long Decode
- **Target Hallucinations Blocked:** Over-rationalizing plausible but non-existent SDK parameters (e.g., `continuation_token`) during deep reasoning, and omitting co-required activation conditions.
- **Dedicated Rules:**
  1. Never invent or append undocumented parameter names or SDK behaviors not explicitly present in `gemini-api-guides/long-decode.md`, `gemini-api-guides/latest-model.md`, or `gemini-api-guides/pricing.md`.
  2. When explaining Long Decode, never mention `background=True` alone; specify all co-required conditions (`max_output_tokens > 65536` and joining text across all `model_output` steps in `interaction.steps`) per [migration.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L144-L158) and `gemini-api-guides/long-decode.md`.
  3. During security/cryptography audits, provide the mathematical root cause, concrete bypass payloads (`""`, 1-char signatures), and verified patch code (`hmac.compare_digest`, `os.urandom(12)`) with file/line links.

---

## III. Verified Authoritative References (Source of Truth Index)

### 1. Local Installed Gemini API & Antigravity Skill References (`file:///`)
- **Gemini API Current Models, Interactions API, Managed Agents (`agent_config`), Decisions API (`noul`):**
  - [gemini-api-dev/SKILL.md (Current Models & Agents)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L13-L68)
  - [gemini-api-dev/SKILL.md (Managed Agents & Antigravity `agent_config`)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L194-L233)
  - [gemini-api-dev/SKILL.md (Decisions API `gemini-decision-1`)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L331-L380)
- **Model Migration & Breaking Changes Checklists:**
  - [migration.md (Interactions API Transition & Deprecated Model Mapping)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L28-L81)
  - [migration.md (Gemini 4 Hydrogen & Argon/Carbon Long Decode Checklists)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L128-L159)
  - [migration.md (Gemini 3.8 TTS `audio/wav` vs `audio/l16`, Nano Banana 2.1 14-image fusion, Omni 1.2 Flash)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L168-L199)
- **Gemini Omni 1.2 Flash Video Generation, Editing & Reference Rules:**
  - [gemini-omni-flash-api/SKILL.md (3s–15s generation, 3s–10s/30s extension, 6 image / 1–3 video refs)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-omni-flash-api/SKILL.md#L13-L21)
- **Gemini Live API Real-Time Bidirectional Streaming Models:**
  - [gemini-live-api-dev/SKILL.md (`3.8-live`, `3.8-live-extended-thinking`, `3.5-transcribe-live`)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-live-api-dev/SKILL.md#L28-L47)
- **Gemini API CLI (`gemini-api`) & `gemini-3.5-transcribe` 30m Cap:**
  - [gemini-api-cli/SKILL.md (Commands, `transcribe` 30m cap, `store=false` rules)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-cli/SKILL.md#L36-L50)
  - [gemini-api-cli/SKILL.md (Multi-turn `previous-interaction-id` & `store` constraints)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-cli/SKILL.md#L123-L144)
- **Antigravity (AGY) Platform & Customization System References:**
  - [antigravity_guide/SKILL.md (AGY Sitemap & Surfaces)](file:///C:/Users/ckstn/.gemini/antigravity/builtin/skills/antigravity_guide/SKILL.md#L6-L55)
  - [agy-customizations/SKILL.md (Rules, Skills, Plugins, Hooks, MCP Precedence)](file:///C:/Users/ckstn/.gemini/antigravity/builtin/skills/agy-customizations/SKILL.md#L19-L96)
  - [agy-customizations/docs/rules.md (GEMINI.md/AGENTS.md & 24KB/20,000-Token Budget)](file:///C:/Users/ckstn/.gemini/antigravity/builtin/skills/agy-customizations/docs/rules.md#L1-L40)
  - [agy-customizations/docs/hooks.md (PreToolUse, PostToolUse, PreInvocation, Stop Contracts)](file:///C:/Users/ckstn/.gemini/antigravity/builtin/skills/agy-customizations/docs/hooks.md#L85-L120)

### 2. Gemini Docs MCP Server (`gemini_search_docs` / `gemini_get_doc`) Core Paths
- `gemini-api-guides/pricing.md` (`#gemini-developer-api-pricing/gemini-4-argon-idgemini-4-argon`, `#gemini-developer-api-pricing/gemini-38-flash-idgemini-38-flash`)
- `gemini-api-guides/latest-model.md` (`#whats-new-in-gemini-4-argon/whats-new-in-gemini-4-argon-idwhats-new-gemini-4-argon`)
- `gemini-api-guides/long-decode.md` (`#long-decode/how-long-decode-works-idhow-long-decode-works`, `#long-decode/output-limits-idoutput-limits`)
- `gemini-api-guides/whats-new-gemini-3.8.md` (`#whats-new-in-gemini-38-flash/whats-new-in-gemini-38-flash-idwhats-new-gemini-3-8-flash`)
- `gemini-api-guides/whats-new-gemini-3.6.md` (`#whats-new-in-gemini-36-flash-and-35-flash-lite/api-changes-and-parameter-updates-idapi-changes-and-parameter-updates`)
- `gemini-api-guides/thinking.md` (`#gemini-thinking/controlling-thinking-idthinking-levels`, `#gemini-thinking/thought-signatures-idsignatures`)
- `gemini-api-guides/transcribe.md` (`#audio-transcription/transcription-modes-idtranscription-modes`)

### 3. Canonical Web Documentation URLs
- **Gemini API Pricing & Plans:** https://aistudio.google.com/docs/pricing
- **Gemini API Full Docs Index (`llms.txt`):** https://aistudio.google.com/llms.txt
- **Latest Model Guide (Gemini 4 Argon):** https://aistudio.google.com/docs/latest-model.md
- **Gemini 4 Hydrogen Guide:** https://aistudio.google.com/docs/whats-new-gemini-4-hydrogen.md
- **Long Decode Guide:** https://aistudio.google.com/docs/long-decode.md
- **Thinking & Thought Signatures Guide:** https://aistudio.google.com/docs/thinking.md
- **Interactions API Migration Guide:** https://aistudio.google.com/docs/migrate-to-interactions.md
- **Antigravity Documentation Home:** https://antigravity.google/docs
