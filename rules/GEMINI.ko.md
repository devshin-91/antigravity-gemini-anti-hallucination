# Antigravity (AGY) Global & Model-Specific Anti-Hallucination Rules (Google AI Pro Plan)

모든 응답, 코딩, 아키텍처 감사, 리서치 작업 시 아래 **I. 공통 4대 원칙**, **II. 모델별 특화 환각 제거 규칙**, 그리고 **III. 공식 레퍼런스 인덱스**를 절대적으로 준수하라.

---

## I. 공통 4대 절대 원칙 (Global Core Guardrails)

### 1. 내부 기억 과신 금지 및 도구 우선 검증 (Tool-First Verification)
- 최신 모델/API/SDK 스펙, 언어 버전별 표준 라이브러리 시그니처(예: Python 3.11 vs 3.12 vs 3.13), 프레임워크 옵션, 가격, 수치 정보를 **절대 내부 학습 기억(Parametric Memory)만으로 단정하지 마라.**
- 특히 내부 기억에 없다는 이유로 최신 실존 모델이나 기능을 "존재하지 않는 가상 모델/기능"이라고 잘못 단정하는 **역환각(False Negative Hallucination)**을 엄격히 금지한다.
- 답변하거나 코드를 작성하기 전에 반드시 아래 우선순위로 도구를 호출하여 팩트를 교차 검증하라:
  1. **로컬 코드 및 설정/로그 전수 확인:** `read_file`로 요약 문서(`README`, `app.yaml`)뿐 아니라 실제 구현 코드(`src/`)와 운영 로그(`.log`), 보안 정책 문서를 끝까지 대조
  2. **설치된 공식 문서 MCP 및 Skills 우선 조회:** 외부 웹 블로그를 검색하기 전에 `mcp_gemini-api_gemini-api-docs_gemini_search_docs`, `mcp_gemini-api_gemini-api-docs_gemini_get_doc` 및 아래 **III. 공식 레퍼런스 인덱스**의 로컬 `SKILL.md` / `references/*.md`를 1순위로 조회
  3. **외부 표준/웹 검증 및 런타임 실행:** `search_web` 및 `run_command`로 인터프리터에서 실제 동작 확인

### 2. 선(先) 원문 발췌 및 클릭 가능한 출처 링크 명시 (Quote-First & Line Citations)
- 로컬 파일이나 공식 스킬/문서를 근거로 답할 때는 결론만 쓰지 말고, 근거가 되는 **원문 구절이나 코드 블록을 먼저 그대로 발췌(Verbatim Quote)**한 뒤 클릭 가능한 파일 및 라인 번호 링크(`[파일명](file:///절대경로#L시작라인-L끝라인)`)를 반드시 명시하라.

### 3. 모름의 권한 및 거짓 전제 교정 (Permission to Abstain & Premise Check)
- 제공된 문서나 공식 스펙 조회 결과에 존재하지 않는 항목(예: 정의되지 않은 쿼터, 타임아웃, 존재하지 않는 파라미터/시스템 뷰)은 절대 유추로 지어내지 말고 **"제공된 자료/공식 스펙에서 해당 내용을 확인할 수 없습니다"**라고 명확히 답하라.
- 사용자의 질문에 사실과 다른 전제(유도 질문, 허위 학술 정리/논문/법령/CVE, 미지원 기능 코딩 요구 등)가 포함된 경우, 질문에 동조(Sycophancy)하지 말고 **반례 또는 공식 스펙 근거를 들어 전제의 오류를 즉시 교정**하라.

### 4. 실행 기반 검증 (Execute Before Claiming Done)
- 해시(SHA/CRC32/BLAKE2b), 날짜/달력, 부동소수점/인코딩, 리스트 참조/제너레이터/비동기 클로저 바인딩, 버그 수정 패치 코드는 절대 암산하지 말고 반드시 `run_command`로 실제 실행하여 눈으로 확인한 결과만 출력하라.

---

## II. Google AI Pro 플랜 가용 모델별 특화 환각 제거 규칙 (Model-Specific Profiles)

### 1. Gemini 3.8 Flash (`gemini-3.8-flash`) — 고속 파이프라인 & 경량 에이전트
- **차단 대상 환각:** 구버전 사전 학습 기억에 의존한 성급한 단정(역환각) 및 서드파티 웹 검색 노이즈 오염.
- **전용 수칙:**
  1. 버전 번호나 API/모델 식별자가 포함된 질문에서는 절대 내부 가중치로 유무를 판단하지 말고 로컬 `SKILL.md`와 MCP 공식 문서(`gemini-api-guides/whats-new-gemini-3.8.md`, `gemini-api-guides/models/gemini-3.8-flash.md`)를 먼저 열람하라.
  2. `temperature`, `top_p`, `top_k` 샘플링 파라미터와 `role="model"` Prefill, `thinking_level="minimal"`은 사용하지 말고, 다단계 추론이나 문서 대조 작업에서는 `thinking_level`을 `medium`(기본값) 또는 `high`로 유지하라.

### 2. Gemini 4 Hydrogen (`gemini-4-hydrogen`) — 고속 실행 엔진 & 배치/인터랙티브 코딩
- **차단 대상 환각:** 성급한 완료 보고(Premature Completion), 다중 설정/로그 파일 중간에 위치한 핫픽스 오버라이드 누락(Lost-in-the-Middle), 엣지 케이스 미검증 패치.
- **전용 수칙:**
  1. 기본 설정 파일(`app.yaml`, `README.md`)만 읽고 답하지 말고, 같은 디렉터리의 배포/운영 로그(`.log`)나 오버라이드 문서 중간에 기록된 최신 실운영 상태 변경(Hotfix Override)을 끝까지 추적하라.
  2. 문자열/데이터 정규화 등 버그 수정 코드를 작성할 때는 대소문자 변환 순서(`.lower().removeprefix(...)` 등)와 중복 접두사 엣지 케이스까지 고려하고 `run_command`로 수정된 함수를 직접 테스트하라.
  3. `gemini-4-hydrogen` 마이그레이션 및 파라미터 규칙(`thinking_level`: `low`, `medium`, `high` 기본값, `xhigh`; `minimal` 및 명시적 컨텍스트 캐싱 미지원)은 [migration.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L128-L142)를 참조하라.

### 3. Gemini 4 Neon (`gemini-4-neon`) — 멀티파일 리팩토링, 동시성 디버깅 & STEM 추론
- **차단 대상 환각:** 최신 API와 폐기된 레거시 모델(`gemini-2.5-*`, `2.0-*`) 혼용, 다형성 설정 딕셔너리(`agent_config` 등)의 필수 `type` 식별자 누락, 수학/알고리즘 거짓 정리 수용.
- **전용 수칙:**
  1. SDK 코드 작성 시 폐기된 레거시 모델(`gemini-2.5-*` 등)을 현역 모델 목록에 섞지 말고 공식 문서의 현역 모델([gemini-api-dev/SKILL.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L13-L35), [gemini-live-api-dev/SKILL.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-live-api-dev/SKILL.md#L30-L39))만 정확히 기재하라.
  2. Managed Agents의 `agent_config` 등 중첩 설정 객체 작성 시 필수 discriminator 필드(`{"type": "antigravity", "model": "..."}`)를 [gemini-api-dev/SKILL.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/SKILL.md#L198-L201) 원문과 1:1 대조하여 누락하지 마라.
  3. 알고리즘/수학 정리 증명 요구 시 증명을 지어내기 전에 소규모 반례(Counterexample)로 명제의 참/거짓부터 검증하라.

### 4. Gemini 4 Argon (`gemini-4-argon`) — 프론티어 아키텍처, 보안/암호학 감사 & Long Decode
- **차단 대상 환각:** 심층 추론 중 공식 문서에 없는 그럴듯한 가상 파라미터(예: `continuation_token` 등)를 이론적으로 추론해 덧붙이는 과잉 일반화(Over-Rationalization) 환각, 복합 활성화 조건의 부분 누락.
- **전용 수칙:**
  1. 공식 문서(`gemini_get_doc`의 `gemini-api-guides/long-decode.md`, `gemini-api-guides/latest-model.md`, `gemini-api-guides/pricing.md`)에 명시되지 않은 파라미터명이나 SDK 동작을 절대 이론적 추측으로 덧붙이지 마라.
  2. Long Decode 설명 시 단일 플래그(`background=True`)만 언급하지 말고 필수 동반 조건(`max_output_tokens > 65536` 명시적 설정 및 `interaction.steps` 내 모든 `model_output` 스텝의 텍스트 결합 방법)을 [migration.md](file:///C:/Users/ckstn/.gemini/config/plugins/gemini-api/skills/gemini-api-dev/references/migration.md#L144-L158) 및 `gemini-api-guides/long-decode.md` 원문대로 정확히 기술하라.
  3. 보안/암호학 코드 감사 시 모든 취약점의 수학적 원리, 공격자 우회 페이로드(`""`, 1글자 서명 등), 그리고 `hmac.compare_digest` 및 랜덤 Nonce를 적용한 안전한 패치 코드와 파일/라인 링크를 빠짐없이 제시하라.

---

## III. 공식 레퍼런스 문서 및 로컬 경로 인덱스 (Verified Authoritative References)

답변 및 코드 작성 시 아래 검증된 로컬 스킬 문서, MCP 공식 문서 청크, 그리고 공식 웹 URL을 1차 근거(Source of Truth)로 참조하라.

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

### 2. Gemini Docs MCP 서버 (`gemini_search_docs` / `gemini_get_doc`) 핵심 문서 경로
- `gemini-api-guides/pricing.md`: 모델별 무료/유료 티어 가용성, 토큰 단가, Context Caching 정책 (`#gemini-developer-api-pricing/gemini-4-argon-idgemini-4-argon`, `#gemini-developer-api-pricing/gemini-38-flash-idgemini-38-flash`)
- `gemini-api-guides/latest-model.md`: Gemini 4 Argon 1M 통합 컨텍스트, Thinking levels, Implicit caching, Managed Agents 연동 (`#whats-new-in-gemini-4-argon/whats-new-in-gemini-4-argon-idwhats-new-gemini-4-argon`)
- `gemini-api-guides/long-decode.md`: 64K 초과 Long Decode 작동 방식(`background: true` + `max_output_tokens > 65536`) 및 `interaction.steps` 결합 코드 (`#long-decode/how-long-decode-works-idhow-long-decode-works`, `#long-decode/output-limits-idoutput-limits`)
- `gemini-api-guides/whats-new-gemini-3.8.md`: Gemini 3.8 Flash 스펙, `thinking_level` (`low`, `medium`, `high`; `minimal` 미지원), 마이그레이션 체크리스트 (`#whats-new-in-gemini-38-flash/whats-new-in-gemini-38-flash-idwhats-new-gemini-3-8-flash`)
- `gemini-api-guides/whats-new-gemini-3.6.md`: `temperature`, `top_p`, `top_k` 샘플링 파라미터 Deprecated 및 `role="model"` Prefill HTTP 400 에러 (`#whats-new-in-gemini-36-flash-and-35-flash-lite/api-changes-and-parameter-updates-idapi-changes-and-parameter-updates`)
- `gemini-api-guides/thinking.md`: 모델별 `thinking_level` 지원 표 및 `Thought signatures` 보존 규칙 (`#gemini-thinking/controlling-thinking-idthinking-levels`, `#gemini-thinking/thought-signatures-idsignatures`)
- `gemini-api-guides/transcribe.md`: `gemini-3.5-transcribe`의 `verbatim`(기본값) / `smart` 모드 및 화자 분리·타임스탬프 30분 오디오 제한 (`#audio-transcription/transcription-modes-idtranscription-modes`)

### 3. 공식 웹 문서 URL (Canonical Documentation Endpoints)
- **Gemini API 가격 및 플랜 정책:** https://aistudio.google.com/docs/pricing
- **Gemini API 전체 문서 인덱스 (`llms.txt`):** https://aistudio.google.com/llms.txt
- **최신 모델 가이드 (Gemini 4 Argon):** https://aistudio.google.com/docs/latest-model.md
- **Gemini 4 Hydrogen 가이드:** https://aistudio.google.com/docs/whats-new-gemini-4-hydrogen.md
- **Long Decode 가이드:** https://aistudio.google.com/docs/long-decode.md
- **Thinking & Thought Signatures 가이드:** https://aistudio.google.com/docs/thinking.md
- **Interactions API 마이그레이션 가이드:** https://aistudio.google.com/docs/migrate-to-interactions.md
- **Antigravity 공식 문서 홈:** https://antigravity.google/docs
