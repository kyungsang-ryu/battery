# KCI1 한글 논문 초고 빌드 가이드

본 폴더는 **KCI1 (한국산학기술학회 논문지) 한글 논문 초고**를 자동 생성하기 위한 빌드 스크립트와 결과물을 보관합니다.

- 양식 기준: 심사용논문서식-국문(2019).pdf — 한국산학기술학회 논문지 양식
- 글·형식 참고: 심사용논문서식-국문(2021)_rev02.pdf — 사용자의 기존 OLTC-ESS 논문
- 출력: `K1_paper_draft.docx` (Word 문서)
- 한글(.hwp) 변환: 빌드된 .docx 를 한글 워드프로세서에서 열어 "다른 이름으로 저장 → .hwp" 수행

---

## 1. 사전 준비

### Node.js 및 docx 패키지 설치

```powershell
# Node.js 18+ 가 설치되어 있어야 함 (https://nodejs.org)
node --version

# 본 폴더로 이동
cd "D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data\01_분석보고서_및_사양\K1_paper_draft"

# docx 패키지를 본 폴더에만 설치 (전역 설치도 가능)
npm install docx
```

전역 설치를 선호하면:

```powershell
npm install -g docx
```

---

## 2. 빌드

```powershell
cd "D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data\01_분석보고서_및_사양\K1_paper_draft"
node build_paper.js
```

성공 시 같은 폴더에 `K1_paper_draft.docx` 가 생성됩니다.

---

## 3. .hwp 로 변환

1. 생성된 `K1_paper_draft.docx` 를 **한글 워드프로세서** 에서 엽니다.
2. `파일 → 다른 이름으로 저장 → 한글 문서(*.hwp)` 선택 후 저장.
3. 본문 폰트가 자동으로 맑은 고딕 9pt 로 매핑되는지 확인. 누락 시 `편집 → 글자 모양` 으로 일괄 변경.

> 참고: docx-js 는 `.hwpx` 직접 출력을 지원하지 않습니다. 따라서 .docx 빌드 후 한글에서 .hwp/.hwpx 로 저장하는 워크플로우가 표준입니다.

---

## 4. 빌드 결과물 점검 체크리스트

빌드된 .docx 를 한글 또는 Word 에서 열어 다음을 점검합니다.

| 항목 | 확인 내용 |
|---|---|
| 페이지 크기 | 188 × 258 mm (한국산학기술학회 논문지 표준) |
| 본문 단 구성 | 제목/초록/Keywords 는 1단, 본문(서론~결론)은 2단 |
| 본문 폰트 | 한글 = 맑은 고딕 9pt, 영문/수식 = Times New Roman 9pt |
| 제목 폰트 | 14pt Bold (한글), 영문 부제는 12pt |
| Abstract | 8.5pt italic, 영문 |
| Keywords | 영문 5개 |
| Section Heading | "1. 서론", "2.1 모델 정의" 등 번호 매김 일관성 |
| 표 | Table 1~4 모두 캡션 위치 (위쪽), 가운데 정렬 |
| 그림 | Fig. 1~3 placeholder 텍스트 → 실제 PNG 삽입 필요 |
| 결론 | (1)(2)(3)(4) 번호 형식 |
| 참고문헌 | [1]~[7] 번호 + DOI 포함 |

---

## 5. 사용자 수동 보완 필수 항목

자동 생성된 초고는 **다음 항목을 사용자가 직접 수정해야** 최종 제출 가능합니다.

1. **저자 정보** — 현재 placeholder ("유경상", "○○대학교 ○○공학과") 로 입력. 실제 소속·이메일·ORCID 로 교체.
2. **그림 삽입** — `D:\…\battery\data\outputs\figures\K1_fractional_ecm\fig{1~6}.png` 중 본문 흐름에 맞는 3장을 선택해 placeholder 위치에 삽입.
   - Fig. 1: fig1 또는 fig3 (RMSE 비교 또는 전압 트랙 예시)
   - Fig. 2: fig4 (R0/α Trajectory)
   - Fig. 3: fig5 또는 fig6 (PDF Grid 또는 온도 비교)
3. **참고문헌 검증** — 7편의 placeholder 참고문헌 (Plett 2004, Doyle 1993 등) 의 실제 권/호/페이지 정보를 본인 확인 후 보정. 추가 인용이 필요하면 [8] 이상 번호로 확장.
4. **수식 번호 (Eq.1, Eq.2)** — 현재 본문 내 "(1)", "(2)" 표기. 한글 워드프로세서의 수식 편집기로 LaTeX 수식을 다시 입력하면 가독성이 향상됨.
5. **Acknowledgement** — 한국에너지기술연구원 (KIER) 데이터 활용 사사문구 추가 권장.
6. **Cycle 100/500 이상 현상 보고** — 본문 4.6 절의 진단 결과는 `outputs/runs/K1-summary/diagnosis_low_cycle.md` 의 표를 그대로 인용. 필요 시 표 형태로 추가.

---

## 6. 본 초고에 반영된 KCI1 핵심 결과

| 결과 항목 | 값 | 출처 |
|---|---|---|
| FOM 평균 전압 RMSE 감소율 (vs 1RC, 25°C) | **70.01%** | `outputs/runs/K1-summary/REPORT.md` |
| FOM 평균 전압 RMSE 감소율 (vs 1RC, 50°C) | **62.95%** | 동일 |
| 평균 R0_50/R0_25 비율 | **0.649** | 동일 |
| α (CPE 차수) 범위 | **0.32 ~ 0.41** | `outputs/runs/K1-fom-*/params_per_cycle.csv` |
| α Spearman ρ (cycle, α) — 25°C | **-0.10** (단조성 약함) | `REPORT.md` |
| α Spearman ρ (cycle, α) — 50°C | **+0.56** | 동일 |
| 데이터 부족 cycle | **100, 500** (`insufficient_dynamic_samples`) | `diagnosis_low_cycle.md` |
| 사용 cycle | 100, 500, 1000, 1100, 1200, 1300, 3000 | 6개 CSV |

본 초고의 주장(main claim)은 다음 두 가지에 근거합니다.

1. **FOM 적용 시 1RC 대비 평균 전압 RMSE 가 25°C 70%, 50°C 63% 감소.**
2. **R0 가 50°C 에서 25°C 대비 평균 0.649배로 감소** — 전기화학적 직관에 부합.

α 의 단조성은 약하므로, 결론에서는 α 를 "추가 데이터 확보 후 SOH 보조 지표로 검토할 후보" 수준으로 신중하게 기술합니다.

---

## 7. 빌드 트러블슈팅

### `Cannot find module 'docx'`
→ 본 폴더에서 `npm install docx` 가 실행되지 않았거나, 전역 설치 경로가 PATH 에 없습니다.

### 한글 깨짐
→ `build_paper.js` 가 UTF-8 로 저장되어야 합니다. 수정 시 PowerShell 의 `Out-File -Encoding UTF8` 사용 금지 (BOM 없는 UTF-8 권장). VS Code 또는 Notepad++ 사용을 권장합니다.

### .docx 가 한글에서 깨짐
→ 한글 워드프로세서 버전에 따라 일부 docx-js 요소(컬럼 분할 등)가 호환되지 않을 수 있습니다. 우선 Word 에서 열어 정상 여부를 확인 후 한글로 변환하세요.

---

## 8. 다음 단계 (논문화 일정)

본 초고가 완성되면 다음 절차로 진행합니다.

1. 그림·참고문헌·저자 정보 보완 (사용자 직접)
2. 한글 변환 후 1차 자체 검토
3. 한국산학기술학회 논문지 양식 최종 확인 (목차, Keywords 5개, References 형식)
4. 지도교수 또는 공저자 검토
5. 학회 온라인 투고 시스템 업로드

예상 투고 시점: KCI1 — 2026년 6월 말 ~ 7월 초.
