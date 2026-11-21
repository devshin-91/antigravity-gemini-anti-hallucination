# Contributors & Research Roles (연구 기여자 및 역할 분담)

**[🇺🇸 English](#english) | [🇰🇷 한국어](#korean)**

---

<a id="korean"></a>
## 🇰🇷 연구 기여자 및 역할 분담 (Korean)

본 프로젝트(**Antigravity Gemini Anti-Hallucination Framework**)는 인간 연구자의 실무적 통찰·가설 수립·실험 설계와 **Google Antigravity (AGY)** 플랫폼에서 구동된 AI 모델들의 에이전틱 리서치·엔진 구현·벤치마크 검증 협업을 통해 수행되었습니다.

### 1. Principal Investigator & Research Lead (연구 총괄 및 실험 설계)
* **이름 / GitHub / 이메일:** Chansu Shin ([`@devshin-91`](https://github.com/devshin-91) / `devshin91@gmail.com`)
* **핵심 기여 역할:**
  1. **Phase 1–4 문제 정의 및 5대 모델(Google AI Ultra) 아키텍처 설계:**
     - `Gemini 3.8 Flash` 실사용 환각 문제 정의 및 외부 검색 그라운딩 효용성 발견, 공식 가격/모델 스펙 기반 가설 수립.
     - 8대 정보 카테고리 및 Google AI Pro/Ultra 가용 5대 모델(`3.8 Flash`, `4 Hydrogen`, `4 Neon`, `4 Argon`, `4 Carbon`) 맞춤 A/B 실험 및 세대 교체 호환 프로토콜(Phase 4) 설계.
  2. **Phase 5 Zero-Prompt 자동화 문제 제기 및 4대 축 비교 설계:**
     - 수동 리퍼런스 팩트체크 지시의 반복 피로·토큰 낭비와 지시 누락 리스크를 핵심 병목으로 정의하고, 4대 핵심 축(계층 오프로딩·AGY 자동 발화·압축 피드백·함정 벤치마크) 및 기존 저장소 확장 연구 방향 수립.
     - 부분적 Re-warming 손실 방지를 위한 단일 맥락 일관 실행 원칙 및 `CC BY-NC 4.0` 오픈 리서치 정책 수립.

### 2. AI Engineering & Co-Research Partner (`Google Antigravity`)
* **플랫폼 & 계정:** **Google Antigravity (AGY)** ([`@antigravity-bot`](https://github.com/antigravity-bot))
* **참여 모델 계보 및 역할 분담:**
  * **Phase 1–4 — `Gemini 4 Argon (High)` (`gemini-4-argon-high`):**
    - Gemini 3.x/4.x API 패러다임 변화 문헌 조사 및 2계층 `GEMINI.md` 환각 방지 규칙(Phase 1–4, 5대 모델 계보) 엔지니어링.
    - 8대 정보 카테고리 및 5대 모델별(`3.8 Flash`, `4 Hydrogen`, `4 Neon`, `4 Argon`, `4 Carbon`) 함정 코드베이스 구축, AGY Native Swarm 통제 A/B 실험, 500점 루브릭 채점 및 초기 `fact_check_references.py` 작성.
  * **Phase 5 — `Gemini 4 Hydrogen (XHigh)` (`gemini-4-hydrogen-xhigh`):**
    - 실사용 세션(`morning-waking-paper` `Step 463~542`) 토큰·스텝 베이스라인 측정 및 AGY Lifecycle Hooks(`hooks.json`) 런타임 프로브로 문서 대비 실측 차이(`hookEventName`/`cwd` 생략, `continuationActive` protojson 생략) 규명.
    - Tier 0(`file:///#L...`·1:1 인용·APA 7판), Tier 1(SQLite WAL 캐시 + Crossref/CSL-JSON/Handle), Tier 2(Poppler `pdftotext` + 부호 보존 Set-Cover 스니펫 슬라이서) 파이프라인 및 `plugins/ref-fact-checker` 번들 구현.
    - 16케이스 함정 스트레스 테스트(14/14 적발), `agy -p` 3-Way A/B 벤치마크(`C1~C4`), Tier 2 4개 모델(`3.5-flash-lite`, `3.8-flash`, `4-hydrogen`, `4-neon`) Full vs Snippet 라이브 비교 실험 및 Phase 5 보고서 작성.

---

<a id="english"></a>
## 🇺🇸 Contributors & Research Roles (English)

### 1. Principal Investigator & Research Lead
* **Author / GitHub / Contact:** Chansu Shin ([`@devshin-91`](https://github.com/devshin-91) / `devshin91@gmail.com`)
* **Contributions:**
  - **Phase 1–4:** Identified `Gemini 3.8 Flash` grounding behavior, formulated the official pricing/spec hypothesis, and designed the 8-category, 5-model (`3.8 Flash`, `4 Hydrogen`, `4 Neon`, `4 Argon`, `4 Carbon` on Google AI Ultra), and Phase 4 forward-compatibility research methodology.
  - **Phase 5:** Diagnosed the operational bottleneck of manual reference fact-checking (prompt fatigue, token/step waste, and omission risk), defined the 4-axis Zero-Prompt / Low-Token evaluation framework, enforced single-context execution to prevent partial re-warming degradation, and established the `CC BY-NC 4.0` licensing policy.

### 2. AI Engineering & Co-Research Partner (`Google Antigravity`)
* **Platform & Attribution:** **Google Antigravity (AGY)** ([`@antigravity-bot`](https://github.com/antigravity-bot))
* **Model Contributions:**
  - **Phase 1–4 (`Gemini 4 Argon High`):** Literature & MCP docs synthesis, 2-tier `GEMINI.md` anti-hallucination ruleset engineering, trap codebase construction, AGY Native Swarm A/B evaluation, quantitative rubric scoring, and initial `scripts/fact_check_references.py`.
  - **Phase 5 (`Gemini 4 Hydrogen XHigh`):** Empirical baseline profiling (`morning-waking-paper` `Step 463–542`), live AGY `hooks.json` runtime probing (identifying `hookEventName`/`cwd` omission and `continuationActive` protojson guard requirements), implementation of the Tier 0–2 `ref_factcheck` engine and `plugins/ref-fact-checker` bundle, 16-case stress testing (`14/14` recall), live `agy -p` 3-way A/B runs (`C1–C4`), 4-model Tier 2 Full-vs-Snippet GenAI evaluations, and Phase 5 reporting.
