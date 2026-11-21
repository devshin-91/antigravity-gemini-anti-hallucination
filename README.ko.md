<div align="center">

# 🛡️ Antigravity Gemini Anti-Hallucination Framework
### Google Antigravity 기반 Gemini 3.8 Flash 및 Gemini 4 시리즈(Hydrogen · Neon · Argon) 환각 제어 연구 및 실전 가드레일

[![Platform](https://img.shields.io/badge/Platform-Google%20Antigravity%20(AGY)-4285F4?style=for-the-badge&logo=google)](https://antigravity.google/docs)
[![Research Partner](https://img.shields.io/badge/Co--Research%20Model-Gemini%204%20Argon%20(High)-8E24AA?style=for-the-badge)](https://aistudio.google.com/docs/latest-model.md)
[![Target Models](https://img.shields.io/badge/Models-Gemini%203.8%20Flash%20%7C%204%20Hydrogen%20%7C%204%20Neon%20%7C%204%20Argon-0F9D58?style=for-the-badge)](https://aistudio.google.com/docs/pricing)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0%20(비영리%20공유%20허용)-F4B400?style=for-the-badge)](./LICENSE)
[![Repository Visibility](https://img.shields.io/badge/Repository-Private%20Research-333333?style=for-the-badge)]()

**[🇺🇸 English (README.md)](./README.md) | [🇰🇷 한국어 (README.ko.md)](./README.ko.md)**

</div>

---

> 📌 **GitHub Sidebar ("About") 설정 문구 (저장소 우측 상단 표시용)**
> - **Description (About):** `[Antigravity Research] Empirical anti-hallucination guardrails & A/B benchmark suite for Gemini 3.8 Flash and Gemini 4 (Hydrogen, Neon, Argon) on Google Antigravity, co-researched with Gemini 4 Argon (High).`
> - **Topics (Tags):** `antigravity` `google-antigravity` `gemini-4-argon` `gemini-3-8-flash` `gemini-4-hydrogen` `gemini-4-neon` `anti-hallucination` `llm-grounding` `ab-testing`

---

## 1. 연구 배경 및 문제 정의 (Motivation & Problem Definition)

### "Gemini 3.8 Flash는 환각이 심해서 못 쓰겠다?" — 현상 발견에서 가설 수립까지

많은 사용자와 개발자들이 **Gemini 3.8 Flash (`gemini-3.8-flash`)**를 처음 사용할 때 가장 크게 겪는 좌절은 **"속도는 빠르지만 그럴듯한 거짓말(환각, Hallucination)이 너무 자주 나와서 실무에 쓰기 어렵다"**는 점이었습니다. 본 연구 역시 똑같은 실사용의 불편함에서 출발했습니다.

그러나 실험 과정에서 한 가지 중요한 단서를 발견했습니다.
모델이 자신의 내부 학습 기억(Parametric Memory)에만 의존해 성급히 답하게 두지 않고, **외부 검색이나 로컬 문서 도구를 먼저 실행하도록 강제(Grounding)했을 때는 Gemini 3.8 Flash가 놀라울 정도로 정확하고 쓸만한 결과**를 내놓았던 것입니다.

이후 Google의 공식 가격 및 모델 스펙 문서인 **[Gemini Developer API Pricing (`aistudio.google.com/docs/pricing`)](https://aistudio.google.com/docs/pricing)**을 정밀 분석하면서 핵심 가설을 세웠습니다:

1. **가설 수립:** 공식 문서상 `Gemini 3.8 Flash`는 단순 챗봇이 아니라 *"장기 소프트웨어 엔지니어링(long-horizon software engineering), 자율 에이전트(autonomous agents), 복잡한 엔터프라이즈 워크플로우"*에 최적화된 고지능·고효율 모델이다. 즉, **모델 자체의 지능이 부족한 것이 아니라 '도구 확인을 건너뛰는 성급한 추론 습관(환각)'만 시스템적으로 제어하면 극강의 가성비와 속도로 실무에 활용할 수 있다.**
2. **1차 검증 (Gemini 3.8 Flash A/B 테스트):** **Google Antigravity (AGY)** 환경에서 Gemini 3.8 Flash의 환각을 억제하는 전역 규칙(`GEMINI.md`)을 설계하고, 규칙 적용 전(Condition A)과 적용 후(Condition B)에 대한 통제된 A/B 테스트를 진행했다. 그 결과 **단일 벤치마크에서 `73점 → 100점 (+36.99%)`으로 환각이 100% 제거됨**을 확인했다.
3. **2차 확장 (8대 정보 종류별 극한 스트레스 테스트):** 일반적인 질문이 아니라 환각이 발생할 수 있는 최대한 다양한 **8가지 정보 도메인(총 24개 세부 항목: 언어 버전 차이, 최신 AI SDK, 멀티모달 제약, 레거시 문서 충돌, 재무/계약 감사, 국제 표준/가짜 논문, 보안 CVE/코드 감사, 유니코드/IEEE-754 정밀 연산)**으로 테스트를 확장했다. 여기서도 **`116/160점 (72.50%) → 160/160점 (100.00%, +37.93%)`**이라는 탁월한 환각 제거 효과를 입증했다.
4. **3차 일반화 (Google AI Pro 가용 전 모델 맞춤형 확장):** 이 방법론이 Gemini 3.8 Flash에서 완벽히 작동함을 확인한 뒤, 연구를 확장하여 **Google AI Pro 플랜에서 사용 가능한 모든 주력 Gemini 모델(`Gemini 3.8 Flash`, `Gemini 4 Hydrogen`, `Gemini 4 Neon`, `Gemini 4 Argon`)**로 적용 범위를 넓혔다. 각 모델이 가장 잘하는 적합 태스크와 그 태스크에서 발생하는 고유 환각 유형을 규명하고, 모델별 맞춤형 환각 제거 규칙을 수립·검증하여 **범용적인 Antigravity 환각 방지 프레임워크**를 완성했다. *(※ `Gemini 4 Carbon`은 최상위 Ultra 플랜 전용 모델이므로 본 Google AI Pro 플랜 기반 연구 범위에서는 제외함)*
5. **4차 미래 호환성 설계 (Phase 4 — 차세대 버전 업 & 신모델 출시 자동 호환 아키텍처):** 향후 `Gemini 3.8 Flash`가 상위 버전(`3.9`, `4.x`, `5.x Flash`)으로 올라가거나 `Gemini 4`가 `Gemini 5`(`gemini-5-*`) 및 신규 원소 코드명으로 세대 교체될 때, 규칙에 적힌 구버전 모델명이 오히려 신버전 사용을 막는 '규칙 노후화(Rule Obsolescence)'를 방지하도록 **① 와일드카드 계보(Lineage Archetype) 승계, ② 상위 세대 자동 우선(강제 다운그레이드 금지), ③ 신규 공식 스펙 동적 오버라이드, ④ 슬라이딩 레거시 차단 윈도우, ⑤ 플러그인 업데이트 대비 동적 라인 번호 재확인 프로토콜**을 설계·적용했다.
6. **5차 자동화 연구 (Phase 5 — Zero-Prompt · Low-Token 자동 리퍼런스 팩트체크):** 매번 수동으로 리퍼런스 팩트체크를 명령할 때 발생하는 **사용량 낭비**(`morning-waking-paper` 실측 기준 `Step 463~542`에서 **LLM 응답 43회 / 도구 68회** 소모)와 **미명령 시 결함 누락**을 제거하기 위해 **Tier 0–2 계층 오프로딩 엔진(`src/ref_factcheck/`)** 과 **AGY Lifecycle Hook 플러그인(`plugins/ref-fact-checker/`)** 을 구축하고 4대 핵심 축 A/B 비교 실험을 수행했다. 상세 결과는 [Phase 5 연구 보고서](./docs/PHASE5_REFERENCE_FACTCHECK_REPORT.ko.md)를 참조하세요.

---

## 2-1. Phase 5 핵심 발견: "규칙만으로는 무명령 누락을 못 막고, 훅 게이트는 PASS 시 0바이트로 통과한다"

| 실험 지표 / 비교 대상 | 기존 수동·규칙 방식 | Phase 5 자동화 (`ref-fact-checker`) | 실측 개선 효과 |
| :--- | :---: | :---: | :--- |
| **무명령 편집 시 결함 적발** (`agy -p` A/B) | `Rule Only (C1)`: `FAIL 2 / WARN 1` **전부 누락** (`83.05s`, `51,591 tok`) | `Hook Gate (C3)`: **자동 적발 및 교정 `PASS`** (`0 fails`, `0 warns`) | **무명령 누락률 100% → 0% 제거** |
| **정상 파일 편집 시 오버헤드** (`agy -p`) | `Rule Only (C1)`: `83.05s` · `51,591 tok` | `Hook Gate Clean (C4)`: **`23.01s` · `27,693 tok`** (추가 LLM 턴 `0`회) | **시간 `-72.3%` · 토큰 `-46.3%`** |
| **DOI/서지 21편 검증 속도** (21편 / 18 DOI) | 매번 LLM 스크립트 작성·실행 | Tier 1 Cold `4,630.8ms` → Warm SQLite `72.99ms` → Dirty-Skip **`0.73ms`** | **캐시 `63.4x` · 스킵 `6,343x` 가속 (`0` LLM 토큰)** |
| **16케이스 함정 스트레스 테스트** (Track A+B) | 수동 스크립트(단일 규칙 파일 전용) | **14/14 함정 적발 (`100%`), 2/2 정상 통과 (`0%` 오탐)** | **로컬 라인·문맥 + 학술 DOI·APA 전수 커버** |
| **Tier 2 PDF 수치 대조 (`Snippet` vs `Full`)** | PDF 전문 읽기로 대량 토큰 소모 | `Ahn 2019` 변조 적발 시 입력 토큰 `11,656 → 1,160` (**`4/4` 모델 100% 정확**) | **입력 토큰 `-90%` (`1~2초` 컷) + 불일치 건만 Cascade** |

---

## 2. 핵심 연구 발견: 모델 지능에 따라 환각의 '형태'가 진화한다

**Gemini 4 Argon (High)**와 함께 4대 모델을 대상으로 A/B 테스트를 수행한 결과, 모델의 체급이 올라간다고 해서 환각이 자연 소멸하는 것이 아니라 **모델의 역할에 따라 환각의 양상이 더 교묘하게 진화**한다는 사실을 발견했습니다.

| 모델명 (Google AI Pro) | 최적 태스크 (Best-Fit Workload) | 규칙 미적용 시(Condition A) 발생한 고유 환각 패턴 | 맞춤 규칙 적용 시(Condition B) 점수 변화 |
| :--- | :--- | :--- | :---: |
| **Gemini 3.8 Flash**<br>(`gemini-3.8-flash`) | 고속 데이터/문서 파이프라인, 빠른 스크립트 작성, 경량 에이전트 | **기억 과신 역환각 (False Negative):** 과거 학습 기억만 믿고 공식 MCP/Skill 조회를 생략하여 최신 실존 모델(`gemini-decision-1` 등)을 "가상 모델"이라 단정하거나 Python 3.13 신규 파라미터(`strict=True`)를 미지원이라 우김 | `73 → 100점`<br>**(`+36.99%`)** |
| **Gemini 4 Hydrogen**<br>(`gemini-4-hydrogen`) | 일상 인터랙티브 코딩, 고속 배치 실행 엔진, 구현 워커 | **성급한 패치 & 엣지 케이스 누락:** 빠른 실행에 치중해 대소문자 혼용(`Usr-`)·이중 접두사(`USR-usr-`)에 깨지는 코드를 테스트 없이 제출하고, 공식 스키마(`mode.type`) 대신 임의 약칭(`"Smart Dictation"`) 추측 | `75 → 100점`<br>**(`+33.33%`)** |
| **Gemini 4 Neon**<br>(`gemini-4-neon`) | 멀티파일 리팩토링, 비동기/동시성 디버깅, STEM/알고리즘 추론 | **레거시 혼용 & 필수 식별자 누락:** 현역 모델 목록에 폐기된 `gemini-2.5-*` 모델을 섞어 제시하고, 다형성 설정 객체(`agent_config`)에서 필수 `"type": "antigravity"` 필드를 누락 | `72 → 100점`<br>**(`+38.89%`)** |
| **Gemini 4 Argon**<br>(`gemini-4-argon`) | 프론티어 아키텍처 설계, 암호학/보안 감사, 1M Long Decode | **심층 추론 과잉 일반화 (Over-Rationalization):** 높은 추론력으로 공식 문서에 존재하지 않는 가상의 SDK 파라미터(`continuation_token`)를 스스로 추론해 덧붙이고 복합 조건(`max_output_tokens > 65536`) 일부를 생략 | `80 → 100점`<br>**(`+25.00%`)** |
| **4대 모델 종합** | **전 영역 엔지니어링 & 리서치** | **모델별 고유 환각 및 원문/라인 출처 누락 결함 100점 감점** | **`300 → 400점`**<br>**(`+33.33%` / 결함 100% 제거)** |

---

## 3. 저장소 구조 (Repository Structure)

본 저장소는 한국어와 영문 사용자를 모두 지원하도록 이중 언어(Bilingual) 구조로 설계되었습니다.

```text
antigravity-gemini-anti-hallucination/
├── README.md                                  # [English] Main documentation & Quickstart
├── README.ko.md                               # [한국어] 메인 연구 개요 및 빠른 시작 가이드
├── CONTRIBUTORS.md                            # 연구자(Human PI) 및 AI 협조 모델(Argon High · Hydrogen XHigh) 역할 명세
├── LICENSE                                    # CC BY-NC 4.0 (비영리 공유 허용 / 상업적 이용 금지 라이선스)
├── rules/
│   ├── GEMINI.ko.md                           # [한국어] Antigravity 전역 & 모델별 환각 방지 규칙 (배포용)
│   └── GEMINI.en.md                           # [English] Antigravity Global & Model-Specific Anti-Hallucination Rules
├── docs/
│   ├── RESEARCH_REPORT.ko.md                  # [한국어] Phase 1–4 8대 카테고리 & 4대 모델 A/B 실험 보고서
│   ├── RESEARCH_REPORT.en.md                  # [English] Phase 1–4 Full Empirical A/B Benchmark Report
│   ├── PHASE5_REFERENCE_FACTCHECK_REPORT.ko.md # [한국어] Phase 5 Zero-Prompt 자동 팩트체크 4대 축 비교 보고서
│   └── PHASE5_REFERENCE_FACTCHECK_REPORT.en.md # [English] Phase 5 Zero-Prompt Fact-Check Architecture & Benchmark Report
├── src/
│   └── ref_factcheck/                         # Tier 0–2 통합 검증 엔진 (오프라인·SQLite WAL 캐시·Poppler PDF 스니펫·CLI)
├── plugins/
│   └── ref-fact-checker/                      # Antigravity 네이티브 플러그인 (hooks.json + hook_runner.py + SKILL.md + AGENTS.md)
├── benchmarks/
│   ├── run_tier_bench.py                      # 축 1·3·4 정량 벤치마크 (16케이스 함정·캐시·포맷·Tier 2 4모델 비교)
│   ├── run_agy_ab_bench.py                    # 축 2 실전 agy -p 3-Way A/B 벤치마크
│   ├── tier_bench_results.json                # 축 1·3·4 실측 JSON 데이터
│   └── agy_ab_results.json                    # 축 2 실측 JSON 데이터
├── tests/
│   └── test_ref_factcheck.py                  # 단위·서브프로세스 통합 회귀 테스트
└── scripts/
    ├── fact_check_references.py               # 레퍼런스 경로·라인 번호·키워드 자동 팩트 체크 스크립트
    └── install_plugin.py                      # ~/.gemini/config/plugins/ref-fact-checker 일괄 설치 스크립트
```

---

## 4. Google Antigravity (AGY) 빠른 설치 및 적용 방법

### Step 1. 전역 규칙 파일(`GEMINI.md`) 적용
본 저장소의 `rules/GEMINI.ko.md` (또는 영문 `rules/GEMINI.en.md`)를 Antigravity 전역 설정 폴더에 복사하면 모든 프로젝트와 대화에 즉시 자동 적용됩니다. *(AGY 24KB 제한 대비 약 14.3KB로 최적화 완료)*

```powershell
# Windows (PowerShell)
Copy-Item .\rules\GEMINI.ko.md "$HOME\.gemini\config\GEMINI.md" -Force
```

```bash
# macOS / Linux
cp ./rules/GEMINI.ko.md ~/.gemini/config/GEMINI.md
```

### Step 2. Phase 5 Zero-Prompt 자동 팩트체크 플러그인 설치 (전역 AGY 자동 적용)
매번 `"참고문헌 팩트체크해줘"`를 입력하지 않고도 문서 편집 시 자동으로 `file:///#L`·DOI·1:1 인용을 검사하려면 `ref-fact-checker` 플러그인을 전역 설치합니다. 설치 스크립트가 `src/ref_factcheck/` 엔진을 번들링하고 현재 Python 인터프리터 경로를 `hooks.json`에 고정해 `~/.gemini/config/plugins/ref-fact-checker`로 복사합니다:

```powershell
# Windows / macOS / Linux 공통 (저장소 루트에서 실행, Python 3.10+)
python ./scripts/install_plugin.py
```

* **CLI 단독 실행 (플러그인 없이 수동 검증 시):**
  ```powershell
  $env:PYTHONPATH="src"   # macOS/Linux: export PYTHONPATH=src
  python -m ref_factcheck check path/to/paper.md --tier 1 --format compact_diff
  ```
* **Tier 2 PDF 수치 대조 (선택):** `pdftotext` (Poppler) 및 `google-genai` 패키지 설치 시 `python -m ref_factcheck evidence paper.md --refs-dir references/` 실행 가능.
* **비활성화 / 제거:** Antigravity Customizations UI(`ref-fact-checker`)에서 토글하거나 `~/.gemini/config/plugins/ref-fact-checker` 폴더를 삭제하세요.

### Step 3. AGY 채팅창 슬래시 커맨드 & 멘션 조합
* **`@` 멘션 (`@파일`, `@폴더`, `@MCP`)**: 질문 전에 근거 데이터를 컨텍스트 최상단에 고정(Context-First)합니다.
* **`/boost`**: 다각도 추론과 엄격한 교차 검증(Rigorous Verification)이 필요한 고난도 코딩/리서치 시 활성화합니다.
* **`/grill-me`**: 에이전트가 모호한 요구사항을 멋대로 추측(Assumption Hallucination)하지 못하도록 사전 인터뷰를 강제합니다.
* **`/goal`**: 성급한 거짓 완료 보고(Premature Completion)를 막고 검증 조건 달성 시까지 루프를 유지합니다.

---

## 5. 한계점 및 인간 최종 책임 원칙 (Limitations & Human Final Review)

* **기술적·알고리즘적 한계:**
  * **문맥 경계 불일치 (`Chunk-Boundary Blindness`):** `Hill 2022` 실험처럼 단일 논문 내부에 이원 표기(예: `p.3` 정성 고찰 `44편`·`z=0.32` vs 본문 메타분석 `43편`·`p.35` `z=0.31`)가 존재하면, 부분 스니펫과 경량 모델이 오탐(`MISMATCH`)할 수 있어 원문 전체 교차 확인이 필요합니다.
  * **비-DOI·의미론적 왜곡 미검출:** Tier 0–1 엔진은 `file:///#L`, DOI 메타데이터, 1:1 인용 매핑만 검증하므로 **DOI 없는 보도자료·단행본 내용**이나 **수치는 맞지만 해석을 과장한 서술**, **OCR 미적용 스캔 PDF**는 자동으로 완전히 검증하지 못합니다.
  * **재시도 상한 (`max_continuations=2`):** 무한 루프 방지를 위해 `Stop` 훅의 자동 수정 루프는 턴당 최대 2회로 제한됩니다.
* **AI 오류 가능성과 인간의 공동·최종 책임:**
  * AI와 자동 팩트체커는 오류를 줄이는 **보조 안전장치**일 뿐, AI 역시 확률적 모델로서 언제든 실수를 할 수 있습니다.
  * AI와 함께 작업하는 인간 연구자·개발자는 산출물의 **공동 책임자(Co-Owner)** 이자 외부 공개·제출·배포에 대한 **최종 책임자(Final Accountable Authority)** 이므로, 자동 검증 `PASS` 여부와 무관하게 **최종 검토(Human Final Review)는 반드시 인간이 직접 수행해야 합니다.**

---

## 6. Contributors (연구 기여자 및 역할 분담)

본 연구는 인간 연구자의 문제 정의·가설 수립·실험 설계와 **Google Antigravity** 상에서 구동된 AI 모델(**Gemini 4 Argon High** · **Gemini 4 Hydrogen XHigh**)의 에이전틱 실행·검증·채점 협업을 통해 완성되었습니다. 상세 내역은 [CONTRIBUTORS.md](./CONTRIBUTORS.md)를 참조하세요.

| 역할 (Role) | 기여자 (Contributor) | 주요 기여 내용 (Key Contributions) |
| :--- | :--- | :--- |
| **Principal Investigator & Research Lead**<br>*(연구 총괄 · 문제 정의 · 가설 및 실험 설계)* | **Chansu Shin (`@devshin-91` / `devshin91@gmail.com`)** | • Gemini 3.8 Flash 실사용 환각 문제 정의 및 외부 검색 그라운딩 시의 효용성 발견<br>• 공식 가격/모델 문서(`aistudio.google.com/docs/pricing`) 기반 모델별 최적 태스크 매핑 가설 수립<br>• 5단계 연구 확장 설계 (3.8 Flash → 8대 정보 유형 → 4대 모델 → Phase 4 세대 호환 → Phase 5 Zero-Prompt 자동화 4대 축)<br>• 레퍼런스 무결성 기준, 인간 최종 책임 원칙 및 비영리 공유 라이선스 정책 수립 |
| **AI Co-Researcher, Benchmark Architect & Evaluator**<br>*(기술 리서치 · 규칙/플러그인 아키텍처 · Swarm & A/B 실측)* | **Google Antigravity** ([`@antigravity-bot`](https://github.com/antigravity-bot))<br>*(Phase 1–4: **Gemini 4 Argon High** · Phase 5: **Gemini 4 Hydrogen XHigh**)* | • **Phase 1–4 (`Argon High`):** Gemini 3.x/4.x API 패러다임 변화 문헌 조사, 2계층 `GEMINI.md` 규칙 설계, Swarm 통제 A/B 실험 및 400점 루브릭 채점<br>• **Phase 5 (`Hydrogen XHigh`):** 실사용 토큰 베이스라인 분석, AGY Hook 런타임 프로브, Tier 0–2 `ref_factcheck` 엔진·`plugins/ref-fact-checker` 구현, 16케이스 스트레스 테스트 및 라이브 `agy -p` 3-Way A/B 비교 실험 수행 |

---

## 7. 라이선스 (License — CC BY-NC 4.0)

본 저장소의 모든 규칙(`GEMINI.md`), 연구 보고서, 벤치마크 설계 및 스크립트는 **Creative Commons Attribution-NonCommercial 4.0 International ([CC BY-NC 4.0](./LICENSE))** 라이선스 하에 배포됩니다.

* ✅ **공유 및 수정 허용 (Share & Adapt):** 연구, 개인 개발, 사내 비영리 학습 목적으로 자유롭게 복제, 배포, 수정할 수 있습니다.
* ⚠️ **출처 표시 필수 (Attribution):** 공유 또는 인용 시 원 저작자 및 연구 플랫폼/협조 모델(**Google Antigravity** · **Gemini 4 Argon High** · **Gemini 4 Hydrogen XHigh**)을 명시해야 합니다.
* 🚫 **상업적 이용 불가 (Non-Commercial):** 본 저장소의 결과물을 유료 강의, 유료 플러그인/SaaS 판매 등 상업적·영리적 목적으로 사용하는 것을 엄격히 금지합니다.
