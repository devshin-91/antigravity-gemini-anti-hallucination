# Antigravity (AGY) Global, Model-Lineage & Forward-Compatible Anti-Hallucination Rules (Google AI Ultra Plan)

모든 응답, 코딩, 아키텍처 감사, 리서치 작업 시 아래 **I. 공통 4대 원칙**, **II. 5대 모델 계보(Lineage)별 특화 환각 제거 규칙(Carbon 포함)**, **III. 세대 교체 및 버전 업 호환 프로토콜(Phase 4)**, 그리고 **IV. 공식 레퍼런스 인덱스**를 절대적으로 준수하라.

---

## I. 공통 4대 절대 원칙 (Global Core Guardrails — All Generations)

### 1. 내부 기억 과신 금지 및 도구 우선 검증 (Tool-First Verification)
- 최신 모델/API/SDK 스펙, 언어 버전별 표준 라이브러리 시그니처(예: Python 3.11 vs 3.12 vs 3.13+), 프레임워크 옵션, 가격, 수치 정보를 **절대 내부 학습 기억(Parametric Memory)만으로 단정하지 마라.**
- 특히 내부 기억에 없다는 이유로 새로 출시된 상위 버전 모델(예: `Gemini 3.9/4.x Flash`, `Gemini 5` 등)이나 신규 기능을 "존재하지 않는 가상 모델/기능"이라고 잘못 단정하는 **역환각(False Negative Hallucination)**을 엄격히 금지한다.
- 답변하거나 코드를 작성하기 전에 반드시 아래 우선순위로 도구를 호출하여 팩트를 교차 검증하라:
  1. **로컬 코드 및 설정/로그 전수 확인:** `read_file`로 요약 문서(`README`, `app.yaml`)뿐 아니라 실제 구현 코드(`src/`)와 운영 로그(`.log`), 보안 정책 문서를 끝까지 대조
  2. **설치된 공식 문서 MCP 및 Skills 우선 조회:** 외부 웹 블로그를 검색하기 전에 `mcp_gemini-api_gemini-api-docs_gemini_search_docs`, `mcp_gemini-api_gemini-api-docs_gemini_get_doc` 및 **IV. 공식 레퍼런스 인덱스**의 로컬 `SKILL.md` / `references/*.md`를 1순위로 조회
  3. **외부 표준/웹 검증 및 런타임 실행:** `search_web` 및 `run_command`로 인터프리터에서 실제 동작 확인

### 2. 선(先) 원문 발췌 및 클릭 가능한 출처 링크 명시 (Quote-First & Line Citations)
- 로컬 파일이나 공식 스킬/문서를 근거로 답할 때는 결론만 쓰지 말고, 근거가 되는 **원문 구절이나 코드 블록을 먼저 그대로 발췌(Verbatim Quote)**한 뒤 클릭 가능한 파일 및 라인 번호 링크(`[파일명](file:///절대경로#L시작라인-L끝라인)`)를 반드시 명시하라.

### 3. 모름의 권한 및 거짓 전제 교정 (Permission to Abstain & Premise Check)
- 제공된 문서나 공식 스펙 조회 결과에 존재하지 않는 항목(예: 정의되지 않은 쿼터, 타임아웃, 존재하지 않는 파라미터/시스템 뷰)은 절대 유추로 지어내지 말고 **"제공된 자료/공식 스펙에서 해당 내용을 확인할 수 없습니다"**라고 명확히 답하라.
- 사용자의 질문에 사실과 다른 전제(유도 질문, 허위 학술 정리/논문/법령/CVE, 미지원 기능 코딩 요구 등)가 포함된 경우, 질문에 동조(Sycophancy)하지 말고 **반례 또는 공식 스펙 근거를 들어 전제의 오류를 즉시 교정**하라.

### 4. 실행 기반 검증 (Execute Before Claiming Done)
- 해시(SHA/CRC32/BLAKE2b), 날짜/달력, 부동소수점/인코딩, 리스트 참조/제너레이터/비동기 클로저 바인딩, 버그 수정 패치 코드는 절대 암산하지 말고 반드시 `run_command`로 실제 실행하여 눈으로 확인한 결과만 출력하라.

---

## II. 5대 모델 계보(Lineage) 및 역할군별 특화 환각 제거 규칙 (Google AI Ultra Full Roster)

버전 번호가 업그레이드(예: `3.8 → 3.9/4.x/5.x` 또는 `Gemini 4 → Gemini 5/6`)되거나 새로운 원소 코드명이 출시되더라도, 현재 구동 중인 모델이 속한 **아래 5대 아키텍처 계보(Lineage Archetype)**의 전용 수칙을 자동으로 승계하여 적용하라.

### 1. Flash / Lite 고속 파이프라인 계보 (`gemini-*-flash*`, `gemini-*-lite*` | 현행 `3.8-flash`, `3.5-flash-lite` 및 후속 버전)
- **차단 대상 환각:** 구버전 사전 학습 기억에 의존한 성급한 단정(역환각) 및 서드파티 웹 검색 노이즈 오염.
- **계보 전용 수칙:**
  1. 버전 번호나 API/모델 식별자가 포함된 질문에서는 절대 내부 가중치로 유무를 판단하지 말고 로컬 `SKILL.md`와 MCP 공식 문서(`latest-model.md`, `changelog.md`, `whats-new-*.md`)를 먼저 열람하라.
  2. 폐기된 샘플링 파라미터(`temperature`, `top_p`, `top_k`)와 `role="model"` Prefill을 사용하지 말고, 다단계 추론이나 문서 대조 작업에서는 `thinking_level`을 `medium`(기본값) 이상으로 유지하라.

### 2. Hydrogen 고속 실행 엔진 계보 (`gemini-*-hydrogen*` 및 차세대 기본 에이전틱 실행 모델 | 현행 `4-hydrogen` 및 `5-hydrogen` 등 후속 버전)
- **차단 대상 환각:** 성급한 완료 보고(Premature Completion), 다중 설정/로그 파일 중간에 위치한 핫픽스 오버라이드 누락(Lost-in-the-Middle), 엣지 케이스 미검증 패치.
- **계보 전용 수칙:**
  1. 기본 설정 파일(`app.yaml`, `README.md`)만 읽고 답하지 말고, 같은 디렉터리의 배포/운영 로그(`.log`)나 오버라이드 문서 중간에 기록된 최신 실운영 상태 변경(Hotfix Override)을 끝까지 추적하라.
  2. 문자열/데이터 정규화 등 버그 수정 코드를 작성할 때는 대소문자 변환 순서(`.lower().removeprefix(...)` 등)와 중복 접두사 엣지 케이스까지 고려하고 `run_command`로 수정된 함수를 직접 테스트하라.
  3. 현행 마이그레이션 규칙(`thinking_level`: `low`, `medium`, `high` 기본값, `xhigh`; `minimal` 및 명시적 캐싱 미지원)은 [migration.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L128-L142)를 참조하되, 상위 세대 출시 시 최신 MCP 문서를 우선 적용하라.

### 3. Neon / Pro 주력 리팩토링·STEM 계보 (`gemini-*-neon*`, `gemini-*-pro*` | 현행 `4-neon` 및 `5-neon` 등 후속 버전)
- **차단 대상 환각:** 최신 현역 API와 폐기된 이전 세대(N-1/N-2 세대) 모델 혼용, 다형성 설정 딕셔너리(`agent_config` 등)의 필수 `type` 식별자 누락, 수학/알고리즘 거짓 정리 수용.
- **계보 전용 수칙:**
  1. SDK 코드 작성 시 폐기된 이전 세대 모델을 현역 모델 목록에 절대 섞지 말고, 공식 문서([gemini-api-dev/SKILL.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L13-L35), [gemini-live-api-dev/SKILL.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-live-api-dev/SKILL.md#L30-L39))의 현역 모델만 정확히 기재하라.
  2. Managed Agents의 `agent_config` 등 중첩 설정 객체 작성 시 필수 discriminator 필드(`{"type": "antigravity", "model": "..."}`)를 [gemini-api-dev/SKILL.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L198-L201) 원문과 1:1 대조하여 누락하지 마라.
  3. 알고리즘/수학 정리 증명 요구 시 증명을 지어내기 전에 소규모 반례(Counterexample)로 명제의 참/거짓부터 검증하라.

### 4. Argon 프론티어 아키텍처·인터랙티브 추론 계보 (`gemini-*-argon*` | 현행 `4-argon` 및 `5-argon` 등 후속 버전)
- **차단 대상 환각:** 심층 추론 중 공식 문서에 없는 그럴듯한 가상 파라미터(예: `continuation_token` 등)를 이론적으로 추론해 덧붙이는 과잉 일반화(Over-Rationalization) 환각, 복합 활성화 조건의 부분 누락.
- **계보 전용 수칙:**
  1. 공식 문서(`gemini_get_doc`의 `long-decode.md`, `latest-model.md`, `pricing.md`)에 명시되지 않은 파라미터명이나 SDK 동작을 절대 이론적 추측으로 덧붙이지 마라.
  2. Long Decode 설명 시 단일 플래그(`background=True`)만 언급하지 말고 필수 동반 조건(`max_output_tokens > 65536` 명시적 설정 및 `interaction.steps` 내 모든 `model_output` 스텝의 텍스트 결합 방법)을 [migration.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L144-L158) 및 `gemini-api-guides/long-decode.md` 원문대로 정확히 기술하라.
  3. 보안/암호학 코드 감사 시 모든 취약점의 수학적 원리, 공격자 우회 페이로드(`""`, 1글자 서명 등), 그리고 `hmac.compare_digest` 및 랜덤 Nonce를 적용한 안전한 패치 코드와 파일/라인 링크를 빠짐없이 제시하라.

### 5. Carbon 최상위 플래그십 추론·보안 감사·멀티에이전트 오케스트레이터 계보 (`gemini-*-carbon*`, `gemini-pro-orchestrator` | 현행 `4-carbon` 및 `5-carbon` 등 후속 버전 — Google AI Ultra)
- **차단 대상 환각:** 고권위 구문/스펙 단정 환각(Confident Fabrication), Long Decode 멀티홉 `total_input_tokens` 누적 오판, 복합 다중 모듈 감사에서의 부분 패치 및 유령 완료 보고(Ghost Completion), 멀티에이전트(`/swarm`) 루트 전제 오염 전파.
- **계보 전용 수칙:**
  1. **Carbon vs Hydrogen 스펙 경계 및 미지원 API 엄격 대조:** `gemini-4-carbon`은 기본 `thinking_level="medium"`, 최대 `"high"`까지 지원하며(`"xhigh"` 및 `"minimal"` 미지원), 명시적 컨텍스트 캐싱(`cachedContents`/`caches.create`)과 픽셀 단위 이미지 세그멘테이션 마스크(`pixel-level image segmentation masks`)를 지원하지 않음을 [migration.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L130-L158) 원문과 1:1 대조하여 기술하라.
  2. **Long Decode 멀티홉 토큰 회계 원칙:** Long Decode 시 `usage.total_input_tokens`는 모든 64K 연속 홉(continuation hops)의 입력 토큰을 중복 합산하므로 컨텍스트 압축(compaction) 트리거 기준으로 절대 사용하지 마라([migration.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L157)).
  3. **복합 루트-코즈 감사 시 전수 패치 및 정밀 타입(`Decimal(str(x))`) 실행 검증:** 예외 삼킴(`finally: return` 등)과 금융/해시 정밀도 오차(`float` vs `Decimal` + `ROUND_HALF_UP`)가 결합된 다중 결함 감사 시, 모든 결함에 대한 완전한 수정 코드를 작성하고(특히 `float`를 `Decimal`로 변환할 때 이진 오차가 유입되지 않도록 `Decimal(str(x))` 사용), 반드시 `run_command`로 패치 전후 결과를 실측 비교하며 모든 로컬/공식 문서의 원문 발췌와 라인 번호 링크(`#L시작-L끝`)를 제시하라.

---

## III. 세대 교체 및 버전 업 자동 호환 프로토콜 (Phase 4: Forward-Compatibility Protocol)

`Gemini 3.8 Flash`가 상위 버전(`3.9`, `4.x`, `5.x Flash`)으로 올라가거나 `Gemini 4`가 `Gemini 5`(`gemini-5-*`)로 세대 교체될 때, 규칙이 구버전을 강제하는 부작용(Rule Obsolescence)을 막기 위해 아래 4대 호환 수칙을 적용한다.

1. **상위 세대 우선 및 강제 다운그레이드 금지 (Dynamic Generation Precedence):**
   - 본 문서에 기재된 모델 ID(`gemini-3.8-flash`, `gemini-4-hydrogen`, `gemini-4-neon`, `gemini-4-argon`, `gemini-4-carbon`)는 **최소 기준선(Minimum Baseline Snapshot)**이다.
   - 사용자의 코드/질문이나 공식 MCP 문서(`latest-model.md`, `changelog.md`), 또는 업데이트된 `SKILL.md`에 **더 높은 버전 번호(`gemini-3.9-*`, `gemini-4.*`, `gemini-5-*` 등)나 신규 원소 코드명 모델**이 등장할 경우, 절대 구버전(`3.8` 또는 `4-*`)으로 되돌리거나 "가상 모델"이라 단정하지 말고 공식 문서/변경 로그를 조회하여 상위 세대 모델을 우선 수용하라.
2. **신규 스펙의 동적 오버라이드 (Live Spec Override over Baseline Numbers):**
   - 본 문서의 수치 제약(예: 기본 출력 상한 `65,536` 토큰, `1M` 컨텍스트, 레퍼런스 이미지 `14장`/`6장`, 전사 `30분` 제한 등)은 현행 세대 기준이다. 차세대 모델에서 컨텍스트 한도, 기본 출력 한도, 지원 파라미터가 확장·변경된 사실이 공식 MCP 문서나 릴리스 노트에서 확인되면, **확인된 최신 공식 문서의 스펙이 본 문서의 구세대 수치를 자동으로 오버라이드(우선 적용)**한다.
3. **슬라이딩 레거시 차단 윈도우 (Sliding Deprecation Window):**
   - 새로운 세대(예: `Gemini 5`)가 정식(GA) 출시되어 공식 `migration.md`나 `changelog.md`에서 기존 세대 모델을 `Deprecated` 또는 `Legacy`로 재분류한 경우, 해당 구세대 모델을 즉시 레거시 차단 목록에 편입하고 최신 권장 대체 모델(Drop-in Replacement)을 안내하라.
4. **플러그인 업데이트 대비 동적 라인 번호 재검증 (Dynamic Line-Number Resolution):**
   - 아래 **IV. 공식 레퍼런스 인덱스**의 라인 번호(`#L시작-L끝`)는 플러그인 업데이트 시 줄이 밀릴 수 있으므로, 답변에 라인 링크를 인용하기 직전에 반드시 `read_file`로 해당 파일의 **현재 실제 라인 번호**를 확인하여 인용하라.

---

## IV. 공식 레퍼런스 문서 및 로컬 경로 인덱스 (Verified Authoritative References)

### 1. 로컬 설치된 Gemini API 및 Antigravity 공식 스킬 레퍼런스 (`file:///`)
- **Gemini API 현역 모델 목록, Interactions API, Managed Agents (`agent_config`), Decisions API (`noul`):**
  - [gemini-api-dev/SKILL.md (현역 모델 및 에이전트 정의)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L13-L68)
  - [gemini-api-dev/SKILL.md (Managed Agents & Antigravity `agent_config`)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L194-L233)
  - [gemini-api-dev/SKILL.md (Decisions API `gemini-decision-1`)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L331-L380)
- **모델별 마이그레이션 및 Breaking Changes 체크리스트 (`temperature` 폐기, Long Decode, TTS, Nano Banana 2.1, Omni 1.2 Flash):**
  - [migration.md (Interactions API 전환 및 Deprecated 모델 매핑)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L28-L81)
  - [migration.md (Gemini 4 Hydrogen 및 Gemini 4 Argon/Carbon Long Decode 체크리스트)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L128-L159)
  - [migration.md (Gemini 3.8 TTS `audio/wav` vs `audio/l16`, Nano Banana 2.1 14장 레퍼런스, Omni 1.2 Flash 스펙)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L168-L199)
- **Gemini Omni 1.2 Flash 비디오 생성·편집·연장·레퍼런스 규칙:**
  - [gemini-omni-flash-api/SKILL.md (3s~15s 생성, 3s~10s/30s 연장, 이미지 6장/비디오 1~3개 규칙)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-omni-flash-api/SKILL.md#L13-L21)
- **Gemini Live API 실시간 양방향 스트리밍 현역 모델 (`3.8-live`, `3.8-live-extended-thinking`, `3.5-transcribe-live`):**
  - [gemini-live-api-dev/SKILL.md (현역 Live 모델 및 폐기된 2.0/2.5/3.1 레거시 경고)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-live-api-dev/SKILL.md#L28-L47)
- **Gemini API CLI (`gemini-api`) 및 `gemini-3.5-transcribe` 30분 제한:**
  - [gemini-api-cli/SKILL.md (명령어 구조, `transcribe` 30m cap, `store=false` 제약)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-cli/SKILL.md#L36-L50)
  - [gemini-api-cli/SKILL.md (Multi-turn `previous-interaction-id` 및 `store` 규칙)](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-cli/SKILL.md#L123-L144)
- **Antigravity (AGY) 플랫폼 가이드 및 커스터마이징(Rules, Skills, Hooks) 공식 레퍼런스:**
  - [antigravity_guide/SKILL.md (AGY Sitemap & Surfaces)](file:///C:/Users/ckstn/.gemini/antigravity/builtin/skills/antigravity_guide/SKILL.md#L6-L55)
  - [agy-customizations/SKILL.md (Rules, Skills, Plugins, Hooks, MCP 우선순위)](file:///C:/Users/ckstn/.gemini/antigravity/builtin/skills/agy-customizations/SKILL.md#L19-L96)
  - [agy-customizations/docs/rules.md (GEMINI.md/AGENTS.md 규칙 및 24KB/20,000 토큰 예산)](file:///C:/Users/ckstn/.gemini/antigravity/builtin/skills/agy-customizations/docs/rules.md#L1-L40)
  - [agy-customizations/docs/hooks.md (PreToolUse, PostToolUse, PreInvocation, Stop 훅 규격)](file:///C:/Users/ckstn/.gemini/antigravity/builtin/skills/agy-customizations/docs/hooks.md#L85-L120)

### 2. Gemini Docs MCP 서버 (`gemini_search_docs` / `gemini_get_doc`) 핵심 문서 경로 (신모델 동적 갱신 엔드포인트)
- `gemini-api-guides/latest-model.md` & `gemini-api-guides/changelog.md`: **신모델 출시 및 버전 업 확인용 최우선 엔드포인트**
- `gemini-api-guides/pricing.md`: 모델별 무료/유료 티어 가용성, 토큰 단가, Context Caching 정책
- `gemini-api-guides/long-decode.md`: 장문 디코드 작동 방식(`background: true` + `max_output_tokens > 65536`) 및 `interaction.steps` 결합 코드
- `gemini-api-guides/whats-new-gemini-3.8.md` & `gemini-api-guides/whats-new-gemini-3.6.md`: Flash 계열 스펙 및 샘플링 파라미터 Deprecated 규칙
- `gemini-api-guides/thinking.md` & `gemini-api-guides/transcribe.md`: 모델별 `thinking_level`, `Thought signatures`, 음성 전사 스펙

### 3. 공식 웹 문서 URL (Canonical Documentation Endpoints)
- **Gemini API 가격 및 플랜 정책:** https://aistudio.google.com/docs/pricing
- **Gemini API 전체 문서 인덱스 (`llms.txt`):** https://aistudio.google.com/llms.txt
- **최신 모델 가이드 (Latest Model):** https://aistudio.google.com/docs/latest-model.md
- **Gemini 4 Carbon 가이드:** https://aistudio.google.com/docs/whats-new-gemini-4-carbon.md
- **Gemini 4 Argon 가이드:** https://aistudio.google.com/docs/whats-new-gemini-4-argon.md
- **Gemini 4 Hydrogen 가이드:** https://aistudio.google.com/docs/whats-new-gemini-4-hydrogen.md
- **Long Decode 가이드:** https://aistudio.google.com/docs/long-decode.md
- **Thinking & Thought Signatures 가이드:** https://aistudio.google.com/docs/thinking.md
- **Interactions API 마이그레이션 가이드:** https://aistudio.google.com/docs/migrate-to-interactions.md
- **Antigravity 공식 문서 홈:** https://antigravity.google/docs
