# Contributors & Research Roles (연구 기여자 및 역할 분담)

**[🇺🇸 English](#english) | [🇰🇷 한국어](#korean)**

---

<a id="korean"></a>
## 🇰🇷 연구 기여자 및 역할 분담 (Korean)

본 프로젝트(**Antigravity Gemini Anti-Hallucination Framework**)는 인간 연구자의 실무적 통찰·가설 수립·실험 설계와 **Google Antigravity (AGY)** 플랫폼에서 구동된 **Gemini 4 Argon (High)** 모델의 에이전틱 리서치·벤치마크 구현·정량 채점 협업을 통해 수행되었습니다.

### 1. Principal Investigator & Research Lead (연구 총괄 및 실험 설계)
* **이름 / GitHub / 이메일:** Chansu Shin ([`@devshin-91`](https://github.com/devshin-91) / `devshin91@gmail.com`)
* **핵심 기여 역할:**
  1. **문제 정의 및 핵심 현상 포착:**
     - `Gemini 3.8 Flash` 실사용 과정에서 발생하는 빈번한 환각(Hallucination) 문제를 정의하고, 외부 검색 및 그라운딩을 강제했을 때 모델의 실질적 효용성이 급상승하는 현상을 발견.
  2. **공식 스펙 기반 가설 수립:**
     - Google 공식 문서([https://aistudio.google.com/docs/pricing](https://aistudio.google.com/docs/pricing)) 분석을 통해 `Gemini 3.8 Flash`의 설계 목적(장기 소프트웨어 엔지니어링, 자율 에이전트, 엔터프라이즈 워크플로우)을 확인하고 *"환각만 시스템적으로 제어하면 고성능·저비용 실무 모델로 충분히 활용 가능하다"*는 연구 가설 수립.
  3. **3단계 실험 확장 로드맵 기획:**
     - **Phase 1:** `Gemini 3.8 Flash` 대상 환각 방지 규칙 적용 전(A) vs 적용 후(B) A/B 테스트 기획.
     - **Phase 2:** 일반적 상황을 넘어 환각이 발생 가능한 **8대 정보 종류별(24개 세부 문항)** 스트레스 테스트 기획.
     - **Phase 3:** Google AI Pro 구독 플랜 내 가용한 전체 주력 모델(`Gemini 3.8 Flash`, `Gemini 4 Hydrogen`, `Gemini 4 Neon`, `Gemini 4 Argon`; Ultra 전용인 `Carbon` 제외)로 연구를 확장하여 모델별 적합 태스크 정의 → 고유 환각 도출 → 모델별 맞춤 규칙 작성 → 모델별 A/B 검증 프로세스 설계.
  4. **레퍼런스 팩트 체크 및 오픈 리서치 정책 수립:**
     - 모든 참고 문서의 레퍼런스 명기 및 팩트 체크 검증을 지시하고, 비영리 공유 허용·상업화 불가(`CC BY-NC 4.0`) 및 한/영 이중 언어 문서화 표준 수립.

### 2. AI Co-Researcher, Benchmark Architect & Evaluator (연구 협조 · 벤치마크 구현 · 채점 및 팩트 체크)
* **플랫폼:** **Google Antigravity (AGY)**
* **협조 모델:** **Gemini 4 Argon (High)** (`gemini-4-argon-high`)
* **핵심 기여 역할:**
  1. **최신 Gemini 3.x / 4.x 아키텍처 및 환각 원인 규명:**
     - 한글·영문 웹 리서치 및 공식 Gemini API Docs MCP 조회를 통해 `temperature` / `top_p` / `top_k` 샘플링 파라미터 폐기, `thinking_level` 추론 깊이 제어, `Thought Signatures` 멀티턴 상태 보존, `Long Decode` 작동 원리 규명.
  2. **AGY 2계층 환각 방지 규칙(`GEMINI.md`) 엔지니어링:**
     - `I. 공통 4대 절대 원칙(도구 우선 검증, 선 원문 발췌 및 라인 링크, 모름의 권한 및 전제 교정, 실행 기반 검증)`과 `II. Google AI Pro 가용 4대 모델별 특화 환각 제거 프로파일`, `III. 공식 레퍼런스 인덱스`로 구성된 영구 규칙 아키텍처 작성.
  3. **함정 코드베이스 구축 및 AGY Native Swarm A/B 실험 수행:**
     - 레거시 문서 충돌(`README` vs `src/config.py`), 재무 과다 청구(`contract` vs `invoice`), 보안 취약점(`auth_service.py`, `crypto_auth.py`), 비동기 클로저 지연 바인딩(`async_worker.py`), 배치 문자열 정규화 버그(`batch_processor.py`) 등 실제 코드베이스 함정을 구축하고 AGY Native Swarm 위에서 통제된 A/B 테스트 실행.
  4. **정량 채점(Rubric Evaluation) 및 자동화 팩트 체크:**
     - 8대 정보 카테고리(160점 만점) 및 4대 모델(400점 만점)에 대한 객관적 루브릭 채점 및 환각 개선율 산출, Python 기반 레퍼런스 자동 검증 스크립트(`scripts/fact_check_references.py`) 작성 및 100% 무결성 입증.

---

<a id="english"></a>
## 🇺🇸 Contributors & Research Roles (English)

### 1. Principal Investigator & Research Lead
* **Author / GitHub / Contact:** Chansu Shin ([`@devshin-91`](https://github.com/devshin-91) / `devshin91@gmail.com`)
* **Contributions:**
  - Identified the practical hallucination bottleneck in `Gemini 3.8 Flash` and discovered its high reliability when properly grounded with external search and documentation tools.
  - Formulated the core research hypothesis based on [Google's official pricing and model specifications](https://aistudio.google.com/docs/pricing).
  - Designed the 3-phase empirical research methodology: (1) Initial A/B testing on Gemini 3.8 Flash, (2) 8-category information domain stress testing, and (3) Expansion to all available models under the Google AI Pro plan (`Gemini 3.8 Flash`, `Gemini 4 Hydrogen`, `Gemini 4 Neon`, `Gemini 4 Argon`, excluding Ultra-only `Carbon`).
  - Directed the reference integrity fact-check audit and established the bilingual documentation structure and `CC BY-NC 4.0` licensing policy.

### 2. AI Co-Researcher, Benchmark Architect & Evaluator
* **Platform:** **Google Antigravity (AGY)**
* **Co-Research Model:** **Gemini 4 Argon (High)** (`gemini-4-argon-high`)
* **Contributions:**
  - Conducted bilingual literature and official MCP documentation research on Gemini 3.x / 4.x parameter shifts (`temperature` deprecation, `thinking_level`, `Thought Signatures`, `Long Decode`).
  - Engineered the 2-tier global and model-specific `GEMINI.md` anti-hallucination ruleset and authoritative reference index.
  - Built realistic multi-file trap codebases and orchestrated isolated A/B test workers using AGY Native Swarm.
  - Performed quantitative rubric grading across all models and authored `scripts/fact_check_references.py` to verify 100% line-level reference accuracy.
