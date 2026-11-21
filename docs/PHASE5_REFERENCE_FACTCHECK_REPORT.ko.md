# [Phase 5 연구 보고서] Zero-Prompt · Low-Token 자동 리퍼런스 팩트체크 아키텍처 및 4대 핵심 축 A/B 비교 분석

* **연구 플랫폼:** Google Antigravity (AGY)
* **연구 총괄 (PI):** Chansu Shin (`@devshin-91` / `devshin91@gmail.com`)
* **Phase 5 협조 모델:** **Google Antigravity** (`Gemini 4 Hydrogen XHigh` — 전체 아키텍처·엔진 구현·라이브 `agy` 벤치마크 및 비교 분석; Tier 2 교차 비교: `gemini-3.5-flash-lite`, `gemini-3.8-flash`, `gemini-4-hydrogen`, `gemini-4-neon`)
* **라이선스:** [CC BY-NC 4.0](../LICENSE)

---

## 1. 연구 동기 및 문제 정의

1차 연구(Phase 1~4)의 `GEMINI.md` 환각 방지 규칙과 단일 검증 스크립트([fact_check_references.py](../scripts/fact_check_references.py))는 **명시적으로 검증을 지시했을 때** 환각을 제거하는 데 성공했으나, 실전 사용에서 다음 두 가지 구조적 한계가 드러났다.

1. **수동 명령 의존 및 누락 리스크:** 사용자가 매번 `"참고문헌 팩트체크해줘"`라고 지시하지 않으면, 규칙 파일(`GEMINI.md`)이 로드되어 있더라도 일반 편집 요청 시 기존 문서 내 깨진 인용이나 틀린 DOI 연도를 놓친다.
2. **사용량(토큰·스텝) 낭비:** 실제 21편 문헌고찰 작업(`morning-waking-paper` 세션 `Step 463~542`)에서 단 한 번의 `"야 참고 문헌 팩트 체크해보자"` 요청을 처리하는 데 **기록 124건 · LLM 추론 응답 43회 · 도구 호출 68회**가 소모되었다. 매 프로젝트마다 에이전트가 1회성 파이썬 스크립트를 새로 짜고, 전체 API 응답과 PDF 본문을 LLM 컨텍스트로 읽는 비용이 지나치게 컸다.

---

## 2. 제안 아키텍처: Tier 0–2 계층 오프로딩 + AGY Lifecycle Hook Gate

```text
[문서 편집: write_file / edit_file]
        │
        ▼ (PostToolUse Hook, <15 ms, 0 LLM 토큰)
  DirtyStateStore에 수정 문서 경로 기록
        │
        ▼ (에이전트 응답 종료 직전: Stop Hook)
  ┌─ Tier 0 (오프라인 결정론적 엔진, ~10 ms, 0 LLM 토큰)
  │    • file:///#L... 존재·라인 범위·문맥 키워드 검증 + 24KB 규칙 예산 검사
  │    • 본문↔참고문헌 1:1 매핑(고아 인용/미인용 문헌) + APA 7판 순서 린트
  ├─ Tier 1 (SQLite WAL 캐시 + Crossref/CSL-JSON/Handle, Warm ~73 ms, 0 LLM 토큰)
  │    • DOI 실존, 출판 연도, 제1저자 성, 제목 유사도, 권(Volume) 자동 교차대조
  └─ Tier 2 (Low-Token PDF 스니펫 슬라이서 + 경량 모델 에스컬레이션, 선택 실행)
       • Poppler pdftotext + 부호 보존 Set-Cover로 원문 90~98% 축소
       • MISMATCH 판정 건에 한해 Full PDF 2차 교차확인(Cascade)
        │
        ├─ PASS ──▶ decision: "allow" (0B 추가 전달, PreInvocation user_markdown 배지)
        └─ FAIL ──▶ decision: "continue" + 압축 Diff만 주입 (최대 2회 가드)
```

---

## 3. Antigravity Hook 런타임 실측 검증 결과 (문서 대비 핵심 발견)

격리된 `agy -p` 프로브 실행을 통해 Antigravity 공식 Hooks 문서([antigravity.google/docs/hooks](https://antigravity.google/docs/hooks)) 및 로컬 스킬 명세와 실제 Windows AGY 런타임 간 핵심 차이를 사전에 규명해 [hook_runner.py](../plugins/ref-fact-checker/hooks/hook_runner.py)에 반영했다.

1. **Protojson 필드 생략:** 실제 stdin JSON에는 `hookEventName`과 `cwd` 키가 포함되지 않고 전달되므로 CLI 인자(`argv[1]`)와 `workspacePaths`로 판별해야 한다.
2. **`continuationActive` 무한 루프 함정:** `Stop` 재진입 후 `executionNum >= 1` 시점에서도 `continuationActive`가 `false`로 전달되는 케이스가 실측되어, `continuationActive`뿐 아니라 `executionNum >= max_continuations` 이중 가드를 적용해야 무한 루프를 방지할 수 있다.
3. **Windows SQLite 핸들 잠금 & Crossref 429:** Windows에서는 `with sqlite3.connect(...)`가 커넥션을 닫지 않으므로 `contextlib.closing`이 필수이며, Crossref API 동시성 6 이상에서는 HTTP 429가 다수 발생해 `max_workers=3` + 백오프 + `doi.org` CSL-JSON Content Negotiation 폴백으로 429 0건을 달성했다.

---

## 4. 4대 핵심 축 정량 비교 실험 결과

### 축 1. 계층적 검증 속도·캐시 & Tier 2 모델별 PDF 대조 비교

#### (1) Tier 0–1 속도 및 캐시 효과 (`step4_full_draft.md` 21편 / 18 DOI 기준)
| 실행 단계 | 소요 시간 | 외부 네트워크 호출 | LLM 토큰 소모 |
| :--- | :---: | :---: | :---: |
| **기존 수동 방식** (`morning-waking-paper` 실측) | 수 분 (`Step 463~542`) | 매번 스크립트 작성·실행 | **LLM 응답 43회 / 도구 68회** |
| **Tier 1 Cold** (최초 Crossref/CSL-JSON 병렬 조회) | **`4,630.75 ms`** | `18` live calls | **`0` 토큰** |
| **Tier 1 Warm** (SQLite WAL 캐시 히트) | **`72.99 ms`** *(63.4x 가속)* | `0` calls (`18` cache hits) | **`0` 토큰** |
| **Dirty-Skip** (SHA-256 미변경 파일 스킵) | **`0.73 ms`** *(6,343x 가속)* | `0` calls | **`0` 토큰** |

#### (2) Tier 2 PDF 원문 수치 대조: `Full PDF` vs `Set-Cover Snippet` (4개 모델 라이브 비교)
*(설정: `google-genai` 3.3.0 Interactions API, `thinking_level="low"`, `store=False`)*

| 테스트 케이스 | 모드 (평균 프롬프트 크기) | `gemini-3.5-flash-lite` | `gemini-3.8-flash` | `gemini-4-hydrogen` | `gemini-4-neon` |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`Ahn 2019` 수치 변조 함정**<br>*(`α = 0.86 → 0.68` 조작)* | **`Full PDF`** (`23,131자` / `9.6K~11.7K tok`) | ✅ `MISMATCH`<br>(`2,447ms` · `12,231 tok`) | ✅ `MISMATCH`<br>(`2,141ms` · `11,711 tok`) | ✅ `MISMATCH`<br>(`5,606ms` · `10,226 tok`) | ✅ `MISMATCH`<br>(`8,379ms` · `10,275 tok`) |
| **`Ahn 2019` 수치 변조 함정** | **`Snippet`** (`2,582자` / **`1.1K~1.2K tok`**, `-88.5%~90.0%`) | ✅ **`MISMATCH`**<br>(**`1,055ms` · `1,219 tok`**) | ✅ **`MISMATCH`**<br>(**`1,937ms` · `1,222 tok`**) | ✅ `MISMATCH`<br>(`3,783ms` · `1,631 tok`) | ✅ `MISMATCH`<br>(`9,459ms` · `1,655 tok`) |
| **`Hill 2022` 정상 문장**<br>*(원문 내부 44 vs 43, 0.32 vs 0.31 이원 표기)* | **`Full PDF`** (`100,490자` / `27.5K~33.1K tok`) | ❌ `MISMATCH`<br>(`4,472ms` · `34,129 tok`) | ✅ **`MATCH`**<br>(**`3,941ms` · `33,212 tok`**) | ✅ `MATCH`<br>(`12,319ms` · `28,246 tok`) | ✅ `MATCH`<br>(`13,821ms` · `28,664 tok`) |
| **`Hill 2022` 정상 문장** | **`Snippet`** (`2,504자` / `846~867 tok`, `-97.4%`) | ❌ `MISMATCH`<br>(`1,169ms` · `916 tok`) | ❌ `MISMATCH`*(44 vs 43)*<br>(`2,060ms` · `886 tok`) | ❌ `MISMATCH`*(44 vs 43)*<br>(`6,055ms` · `1,281 tok`) | ❌ `MISMATCH`*(44 vs 43)*<br>(`8,254ms` · `1,385 tok`) |

* **핵심 인사이트 (Tier 2 최적 전략):**
  1. 단순 수치 변조(`0.86 → 0.68`)는 `Snippet` 모드(`1.2K` 토큰)만으로 4개 모델 모두 100% 적발하며 토큰을 **90%** 절감했다. 특히 `gemini-3.5-flash-lite`와 `gemini-3.8-flash`가 **1~2초대**로 가장 빠르고 경제적이었다.
  2. 반면 `Hill 2022`처럼 단일 논문 내부에 서로 다른 맥락(`p.3` 정성 고찰 `44편` / `z=0.32` vs 본문 메타분석 `43편` / `p.35` `z=0.31`)이 공존하는 경우 소형 스니펫만 보면 오탐 위험이 존재한다. 따라서 **1차는 `Snippet + 3.8 Flash`(또는 `3.5 Flash-Lite`), `MISMATCH`가 반환된 항목만 `Full PDF + 3.8 Flash / 4 Hydrogen`으로 에스컬레이션하는 2단 캐스케이드**가 정확도와 비용 면에서 최적이다.

---

### 축 2. AGY 자동 발화 방식 실전 3-Way A/B 비교 (`agy -p` + `gemini-3.8-flash-medium`)

동일한 2편 미니 논문 편집 과제(`paper.md`에 의도적 오류 2건: `Ghost, 2025` 고아 인용 + `Hilditch & McHill, 2021` DOI 연도 불일치)를 격리된 Git 워크스페이스에서 4개 조건으로 실행했다([agy_ab_results.json](../benchmarks/agy_ab_results.json)).

| 실험 조건 | 사용자 팩트체크 명령 여부 | 소요 시간 | 총 토큰 (`input+output`) | 사후 감사 결과 | 남은 결함 (`FAIL`/`WARN`) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`C1` Rule Only (Trap)** | ❌ 무명령 | `83.05 s` | `51,591` | ❌ **`FAIL`** | `FAIL 2` / `WARN 1` **(100% 누락)** |
| **`C2` Manual Prompted (Trap)** | ✅ 수동 명령 | `59.63 s` | `40,238` | ✅ `PASS` | `0` *(매번 사람이 명령해야 함)* |
| **`C3` Hook Gate (Trap)** | ❌ **무명령** | `112.10 s` | `63,274` | ✅ **`PASS`** | **`0` (자동 적발 및 교정 완료)** |
| **`C4` Hook Gate (Clean)** | ❌ **무명령** | **`23.01 s`** | **`27,693`** | ✅ **`PASS`** | **`0` (추가 LLM 턴 0회, `C1` 대비 -46.3% 토큰)** |

* **비교 결론:**
  * `GEMINI.md` 규칙만 믿고 사용자가 명령을 빼먹으면(`C1`), 모델은 편집만 마친 채 오류 2건을 그대로 남긴다.
  * 반면 `ref-fact-checker` Hook Gate를 켜두면, 사용자가 아무 말도 하지 않아도 **오류가 있는 파일(`C3`)은 `Stop` 훅이 자동 교정(`PASS`)**하고, **대다수의 정상 편집(`C4`)은 추가 LLM 턴 없이 `23.01s / 27,693 tokens`로 초고속 통과**하며 사용자에게만 무토큰 배지(`metadata.user_markdown`)를 띄운다.

---

### 축 3. 피드백 프로토콜별 컨텍스트 크기 비교

| 출력 모드 | `PASS` 시 모델 주입 크기 | `FAIL` 시 모델 주입 크기 | 절감 효과 및 특징 |
| :--- | :---: | :---: | :--- |
| **`raw`** (기존 상세 JSON/로그) | `502 bytes` | `2,713 bytes` | 통과 여부·세부 항목까지 컨텍스트에 전부 적재 |
| **`compact_diff`** (압축 Diff CLI) | `77 bytes` (`-84.7%`) | `1,779 bytes` (`-34.4%`) | PASS 시 요약 1줄, FAIL 시 비어 있지 않은 수정 필드만 출력 |
| **`hook_stop`** (`Stop` 훅 게이트) | **`0 bytes` (`-100%`)** | **`1,389 bytes` (`-48.8%`)** | **PASS 시 모델 재호출 0회**, FAIL 시 상위 8개 오류만 압축 주입 |
| **`hook_pre`** (`metadata.user_markdown`) | **`0 bytes` (`-100%`)** | **`0 bytes` (`-100%`)** | 모델 컨텍스트 `0` 소비로 UI에 검증 배지만 인라인 표시 |

---

### 축 4. 16케이스 함정 스트레스 테스트 결과

실제 데이터 2종(`GEMINI.ko.md` 19개 링크, `step4_full_draft.md` 21편/86개 본문 인용)과 인위적 함정 14종([run_tier_bench.py](../benchmarks/run_tier_bench.py))에 대해 Tier 0+1 엔진을 실행한 결과:

* **Track A (로컬 `file:///#L...` & 24KB 규칙 예산, 6건):** 정상 `1/1 PASS`, 함정 `5/5` 적발 (`2.75ms ~ 19.91ms`)
  * *적발 항목:* 존재하지 않는 파일(`MISSING_LOCAL_FILE`), 라인 상한 초과(`LINE_RANGE_OUT_OF_BOUNDS`), 역전된 범위(`#L140-L120`), 오프셋 밀림으로 인한 인접 코드/인용문 불일치(`LINE_SEMANTIC_MISMATCH`), `24KB` 예산 초과(`RULE_BUDGET_EXCEEDED`).
* **Track B (학술 DOI & 1:1 인용 & APA 7판, 10건):** 정상 `1/1 PASS`, 함정 `9/9` 적발 (`63.13ms ~ 1,880.13ms`)
  * *적발 항목:* 가짜 DOI(`INVALID_OR_DEAD_DOI`), 연도 불일치(`DOI_YEAR_MISMATCH`), 저자 불일치(`DOI_AUTHOR_MISMATCH`), 다른 논문 DOI 오매핑(`DOI_TITLE_MISMATCH`), 권 번호 오기(`DOI_VOLUME_MISMATCH`), 본문 고아 인용(`ORPHAN_INTEXT_CITATION`), 미인용 참고문헌(`UNCITED_REFERENCE`), 참고문헌 APA 정렬 역전(`APA_REFERENCE_ORDER`), 괄호 내 다중 인용 정렬 위반(`APA_INTEXT_ORDER`).
* **종합 지표:** **Trap Recall `14 / 14 (100.0%)`**, **Clean False Positive Rate `0 / 2 (0.0%)`**.

---

## 5. 최종 권장 구성 (Production Recommendation)

1. **기본 상시 방어선:** `plugins/ref-fact-checker` (`PostToolUse` + `Stop` + `PreInvocation` + Tier 0–1 SQLite 캐시)를 전역 플러그인으로 활성화해 **무명령 자동 팩트체크 & PASS 시 0 추가 토큰** 환경을 상시 유지한다.
2. **규칙 파일(`GEMINI.md`) 다이어트:** 검증 절차를 장황한 자연어 규칙으로 `24KB` 예산 안에 밀어 넣지 않고, 결정론적 훅과 CLI로 오프로딩한다.
3. **고비용 PDF 수치 대조:** 일상 편집에는 Tier 0–1만 자동 실행하고, 논문 최종 제출 전 PDF 수치 감사가 필요할 때만 `python -m ref_factcheck evidence` (`Snippet + gemini-3.8-flash` 1차 → `MISMATCH` 건만 `Full PDF` 2차 에스컬레이션)를 호출한다.
