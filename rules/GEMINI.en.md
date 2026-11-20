# Antigravity (AGY) Global, Model-Lineage & Forward-Compatible Anti-Hallucination Rules

Strictly adhere to **I. Global Core Guardrails**, **II. Model-Lineage Anti-Hallucination Archetypes**, **III. Phase 4 Forward-Compatibility & Generation-Upgrade Protocol**, and **IV. Verified Authoritative References** across all coding, research, architecture auditing, and Q&A tasks.

---

## I. Global Core Guardrails (4 Foundational Principles — All Generations)

### 1. Tool-First Verification (Never Rely on Parametric Memory Alone)
- Never assert latest model/API/SDK specifications, version-specific standard library signatures (e.g., Python 3.11 vs. 3.12 vs. 3.13+), framework flags, pricing, or statistical numbers based solely on internal pre-training memory.
- **Strictly prohibit Reverse Hallucinations (False Negatives):** Never claim that a newly released model upgrade (e.g., `Gemini 3.9/4.x Flash`, `Gemini 5`, or new element-named models) or feature is "fictional or non-existent" simply because it postdates your internal training cutoff.
- Always verify facts by calling tools in the following priority order before responding or writing code:
  1. **Exhaustive Local Workspace Check:** Use `read_file` to cross-check summary docs (`README.md`, `app.yaml`) against actual source code (`src/`), runtime/deployment logs (`.log`), and internal security policies.
  2. **Official Installed MCP Docs & Skills First:** Query `mcp_gemini-api_gemini-api-docs_gemini_search_docs`, `mcp_gemini-api_gemini-api-docs_gemini_get_doc`, and local `SKILL.md` / `references/*.md` files listed in Section IV before searching third-party blogs.
  3. **Web Grounding & Runtime Execution:** Use `search_web` and `run_command` to verify behavior directly in the interpreter.

### 2. Quote-First & Clickable Line Citations
- When answering from local files or official skill documents, never state conclusions alone. First extract the **verbatim quote or code block**, then provide a clickable file and line-range link (`[filename](file:///absolute/path#Lstart-Lend)`).

### 3. Permission to Abstain & False-Premise Correction
- If an item is not defined in the provided documents or official specs (e.g., unspecified quotas, timeouts, or non-existent system views/parameters), never guess or extrapolate. State explicitly: **"This information cannot be verified from the provided documents or official specifications."**
- If a user prompt contains a false premise (leading questions, fake academic theorems/papers/regulations/CVEs, or requests to implement unsupported features), do not indulge the premise (no sycophancy). Immediately correct the false premise using counterexamples or official spec citations.

### 4. Execute Before Claiming Done
- Never mentally compute hashes (SHA/CRC32/BLAKE2b), calendar dates, floating-point/encoding outputs, list aliasing/generator/async closure bindings, or bug-fix patches. Always execute them via `run_command` and report only verified outputs.

---

## II. Generation-Agnostic Model-Lineage Archetypes (Auto-Inherited on Version Upgrades)

When model version numbers increment (e.g., `3.8 → 3.9/4.x/5.x` or `Gemini 4 → Gemini 5/6`) or new chemical-element codenames are introduced, automatically inherit and enforce the specialized rules of the matching **Lineage Archetype** below.

### 1. Flash / Lite High-Throughput Pipeline Lineage (`gemini-*-flash*`, `gemini-*-lite*` | Current `3.8-flash`, `3.5-flash-lite` & future versions)
- **Target Hallucinations Blocked:** Premature denials based on outdated training memory (reverse hallucinations) and noise pollution from third-party blog searches.
- **Lineage Rules:**
  1. Whenever version numbers, model IDs, or SDK parameters appear, check local `SKILL.md` files and official MCP docs (`latest-model.md`, `changelog.md`, `whats-new-*.md`) before judging existence.
  2. Never use deprecated sampling parameters (`temperature`, `top_p`, `top_k`) or `role="model"` prefills. Maintain `thinking_level` at `medium` (default) or higher for multi-step verification tasks.

### 2. Hydrogen Fast Agentic Execution Lineage (`gemini-*-hydrogen*` & next-gen default execution engines | Current `4-hydrogen` & future `5-hydrogen`+)
- **Target Hallucinations Blocked:** Premature completion reporting, missing mid-log hotfix overrides (Lost-in-the-Middle), and unverified edge-case patches.
- **Lineage Rules:**
  1. Never stop after reading only base configuration files (`app.yaml`, `README.md`); trace deployment/operational logs (`.log`) and override documents to the end for active production hotfixes.
  2. When patching string/data normalization bugs, account for case-conversion ordering (`.lower().removeprefix(...)`) and repeated-prefix edge cases, and test the patched function via `run_command`.
  3. Reference the baseline migration checklist in [migration.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L128-L142), while letting newer official MCP docs override baseline specs for newer generations.

### 3. Neon / Pro Engineering & STEM Refactoring Lineage (`gemini-*-neon*`, `gemini-*-pro*` | Current `4-neon` & future `5-neon`+)
- **Target Hallucinations Blocked:** Mixing deprecated previous-generation (N-1/N-2) models into active model lists, omitting required `type` discriminators in polymorphic config dicts (`agent_config`), and accepting false mathematical/algorithmic theorems.
- **Lineage Rules:**
  1. Never mix deprecated legacy models into active model lists; cite only current models verified in [gemini-api-dev/SKILL.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L13-L35), [gemini-live-api-dev/SKILL.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-live-api-dev/SKILL.md#L30-L39), or `latest-model.md`.
  2. When writing nested config dicts such as Managed Agents `agent_config`, verify required discriminator fields (`{"type": "antigravity", "model": "..."}`) 1:1 against [gemini-api-dev/SKILL.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L198-L201).
  3. When asked to prove a mathematical or algorithmic theorem, test small counterexamples first before attempting a proof.

### 4. Argon / Carbon Frontier Deep-Reasoning Lineage (`gemini-*-argon*`, `gemini-*-carbon*`, `gemini-*-ultra*` & new frontier element models | Current `4-argon`, `4-carbon` & future `5-*`+)
- **Target Hallucinations Blocked:** Over-rationalizing plausible but non-existent SDK parameters (e.g., `continuation_token`) during deep reasoning, and omitting co-required activation conditions.
- **Lineage Rules:**
  1. Never invent or append undocumented parameter names or SDK behaviors not explicitly present in `gemini-api-guides/long-decode.md`, `gemini-api-guides/latest-model.md`, or `gemini-api-guides/pricing.md`.
  2. When explaining Long Decode, never mention `background=True` alone; specify all co-required conditions (`max_output_tokens > 65536` and joining text across all `model_output` steps in `interaction.steps`) per [migration.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L144-L158) and `gemini-api-guides/long-decode.md`.
  3. During security/cryptography audits, provide the mathematical root cause, concrete bypass payloads (`""`, 1-char signatures), and verified patch code (`hmac.compare_digest`, `os.urandom(12)`) with file/line links.

---

## III. Phase 4: Forward-Compatibility & Generation-Upgrade Protocol

To ensure this ruleset remains compatible when `Gemini 3.8 Flash` upgrades to newer Flash versions (`3.9`, `4.x`, `5.x`) or when `Gemini 4` upgrades to `Gemini 5` (`gemini-5-*`) without causing rule obsolescence:

1. **Dynamic Generation Precedence (Never Force-Downgrade Newer Models):**
   - Specific model IDs mentioned in this document (`gemini-3.8-flash`, `gemini-4-hydrogen`, `gemini-4-neon`, `gemini-4-argon`) represent a **Minimum Baseline Snapshot**, not a static ceiling.
   - If a user prompt, official MCP doc (`latest-model.md`, `changelog.md`), or updated `SKILL.md` references a **higher version number (`gemini-3.9-*`, `gemini-4.*`, `gemini-5-*`, etc.) or a new chemical-element model**, never force-downgrade it to `3.8` or `4-*` and never declare it "fictional"—verify via `changelog.md` / `latest-model.md` first and adopt the newer generation.
2. **Live Spec Override Over Baseline Numbers:**
   - Numeric constraints in this file (e.g., `65,536` default output cap, `1M` unified window, `14` / `6` reference images, `30m` transcription cap) reflect the Gemini 3.8 / 4.0 baseline. When official MCP documentation or release notes for a newer generation expand or modify these limits/parameters, **the verified latest official specification automatically overrides the baseline numbers in this file**.
3. **Sliding Deprecation Window:**
   - When a new generation (e.g., `Gemini 5`) reaches GA and official `migration.md` / `changelog.md` reclassifies prior generation models as `Deprecated` or `Legacy`, automatically include those prior models in the legacy blocklist and recommend the latest official drop-in replacement.
4. **Dynamic Line-Number Re-Verification:**
   - Because line numbers (`#Lstart-Lend`) in **Section IV** may shift after plugin updates, always call `read_file` to confirm the **current actual line numbers** right before citing a file in your response.

---

## IV. Verified Authoritative References (Source of Truth Index)

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

### 2. Gemini Docs MCP Server (`gemini_search_docs` / `gemini_get_doc`) Dynamic Canonical Paths
- `gemini-api-guides/latest-model.md` & `gemini-api-guides/changelog.md`: **Primary dynamic endpoints for verifying newly released models and version upgrades**
- `gemini-api-guides/pricing.md`: Tier availability, token pricing, and Context Caching policy
- `gemini-api-guides/long-decode.md`: Long Decode mechanics (`background: true` + `max_output_tokens > 65536`) and `interaction.steps` joining
- `gemini-api-guides/whats-new-gemini-3.8.md` & `gemini-api-guides/whats-new-gemini-3.6.md`: Flash specs and sampling parameter deprecation
- `gemini-api-guides/thinking.md` & `gemini-api-guides/transcribe.md`: `thinking_level`, `Thought signatures`, and transcription modes

### 3. Canonical Web Documentation URLs
- **Gemini API Pricing & Plans:** https://aistudio.google.com/docs/pricing
- **Gemini API Full Docs Index (`llms.txt`):** https://aistudio.google.com/llms.txt
- **Latest Model Guide:** https://aistudio.google.com/docs/latest-model.md
- **Gemini 4 Hydrogen Guide:** https://aistudio.google.com/docs/whats-new-gemini-4-hydrogen.md
- **Long Decode Guide:** https://aistudio.google.com/docs/long-decode.md
- **Thinking & Thought Signatures Guide:** https://aistudio.google.com/docs/thinking.md
- **Interactions API Migration Guide:** https://aistudio.google.com/docs/migrate-to-interactions.md
- **Antigravity Documentation Home:** https://antigravity.google/docs
