# 프로젝트 브리핑 — 새 Claude 채팅에서 논문 작성을 이어가기 위한 핸드오버 문서

> **사용 방법**: 새 Claude 채팅창(claude.ai 등)을 열고, 이 문서 전체를 첫 메시지로 붙여넣으세요. 그 뒤 "이 브리핑 읽고, KCI1 논문 본문 4.3 절을 다듬어줘" 같이 구체적인 요청을 이어가시면 됩니다.

---

## 0. 한 문장 요약

NCM 파우치 셀의 조인트 SOC/SOH 추정 알고리즘 개발 과제를 14개월에 걸쳐 진행 중이며, **5편 논문 (SCI 3 + KCI 2)** 출판이 목표입니다. 현재 첫 논문(KCI1) 의 알고리즘·시각화·초고 빌드 스크립트까지 완성된 상태이고, **본문 다듬기와 그림·참고문헌 보완 단계** 에 진입했습니다.

---

## 1. 사용자 프로필

| 항목 | 값 |
|---|---|
| 이름 | 유경상 (RYU) |
| 이메일 | ksryu3212@gmail.com |
| 분야 | 배터리 SOC/SOH 추정 (Lithium-ion BMS) |
| 작업 PC 경로 | `D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data` |
| GitHub | https://github.com/kyungsang-ryu/battery |
| 이전 논문 (참고용 글·형식) | 2021_rev02 — OLTC-ESS 주제 KCI 논문 (한국산학기술학회 논문지) |
| 목표 일정 | 14개월 내 5편 출판 (KCI1 → KCI2 → SCI1 → SCI2 → SCI3 순) |

---

## 2. 연구 컨셉

### 2.1 핵심 주제
**조인트 SOC–SOH 추정 (Joint State-Parameter Estimation)** — 운용 중 (online) 셀의 SOC 와 ECM 파라미터(R0, R1, Cn) 를 동시에 추정하고, 파라미터 trajectory 로부터 SOH 를 도출.

### 2.2 알고리즘 골자

| 구성요소 | 역할 | 주요 novelty |
|---|---|---|
| **Fractional ECM (R + CPE)** | 등가회로 모델 | Constant Phase Element (CPE) 차수 α 가 SOH 보조 지표 후보 |
| **Dual EKF** | 빠른 필터(SOC) + 느린 필터(ECM 파라미터) | 시간 스케일 분리로 안정성 확보 |
| **Adaptive Q/R Scheduling** | (T, SOH) 2D 룩업 기반 노이즈 공분산 자동 조정 | **본 연구의 main novelty** |
| **FOM-AEKF** | Fractional ECM + Adaptive EKF 통합 | 기존 IEKF/UKF 대비 RMSE 감소 |
| **Cross-Scale Generalization** | 셀에서 학습한 알고리즘을 14S 모듈에 재학습 없이 적용 | SCI2 의 핵심 |

### 2.3 데이터셋

| 항목 | 값 |
|---|---|
| 셀 모델 | JH3 NCM Pouch (보성파워텍 제작) |
| 정격 | 63.0 Ah, 3.7V nominal, 3.0~4.2V |
| DCIR @ 25°C SOC30% | 1.03 ± 0.25 mΩ |
| 데이터 출처 | 한국에너지기술연구원 (KIER) 열화 시험 데이터 |
| 시험 채널 | 25°C 2채널 + 50°C 2채널, cycle 100 ~ 3000 |
| 모듈 데이터 | 14S 모듈 시계열 (2022.01 ~ 2023.07) |

---

## 3. 5편 논문 전략

| # | 분류 | 가제 | 핵심 novelty | 사용 데이터 | 상태 |
|---|---|---|---|---|---|
| 1 | **KCI1** | NCM 파우치 셀의 분수계 등가회로모델 식별을 통한 단자전압 정확도 향상 | FOM 기반 R0/α 식별, 1RC 대비 RMSE 70% 감소 | 25°C/50°C cycle 100~3000 | **본문 다듬기 단계** ← 현재 |
| 2 | **KCI2** | 14S 모듈 셀간 편차 분석 및 약셀 추정 | 셀간 OCV·R0 편차의 통계적 모델링 | 14S 모듈 |  대기 (Stage 2 병렬) |
| 3 | **SCI1** | FOM-AEKF for joint SOC-SOH estimation with adaptive Q/R scheduling | (T, SOH) 룩업 기반 적응형 EKF | 셀 (다온도 다 cycle) | 대기 (Stage 2 병렬) |
| 4 | **SCI2** | Cross-scale generalization from cell to 14S module | 셀에서 학습한 ECM/EKF 를 모듈에 적용, 재학습 없음 | 셀 + 모듈 | 대기 (Stage 3) |
| 5 | **SCI3** | Hybrid physics-informed estimator with uncertainty quantification | 데이터+물리 하이브리드, UQ | 전체 | Stretch 목표 (Stage 4) |

**현실적 출판 전망 (자체 평가)**:
- 3편 (KCI1 + KCI2 + SCI1): 85% 이상 가능
- 5편 전체: 30~40%
- SCI 등급: 미드티어 (J. Energy Storage IF 8~9, IEEE TTE IF 7) 현실적

---

## 4. 작업 분담 아키텍처

세 명의 AI 협업자가 역할을 분담합니다.

| 협업자 | 역할 | 주요 작업 |
|---|---|---|
| **Codex** | 알고리즘 엔지니어 | `algo/` 하위 모든 모듈, fitting/identification, EKF 구현, GitHub 푸시 실행 |
| **Antigravity** | UI/시각화 엔지니어 | `ui/` 하위 Streamlit 페이지, plot 헬퍼, pytest |
| **Claude (Cowork)** | 컨트롤 타워 | 전략 수립, kickoff 메시지 작성, 결과 검증, 논문 초고 작성 |
| **Claude (채팅창)** | 논문 라이팅 어시스턴트 | (이 문서 사용처) — 본문 다듬기, 영어 번역, 참고문헌 정리 |

코덱스와 안티그래비티는 사용자가 직접 실행하며, Cowork 가 만든 `kickoff/STAGE_*.md` 문서를 입력으로 받아 작업합니다. 결과는 `outputs/` 또는 `handoff_*.md` 로 회수됩니다.

---

## 5. 폴더 레이아웃 (현재 상태)

```
D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data\
│
├─ algo/                                # Codex 영역 (소스 코드)
│  ├─ ecm/
│  │   ├─ fractional_ecm.py             # FOM (R + CPE) — KCI1 메인 모델
│  │   ├─ ecm_2rc.py                    # 2-RC 베이스라인
│  │   └─ ecm_identify.py               # 1-RC 베이스라인
│  ├─ loaders/kier.py                   # KIER 카탈로그 로더
│  ├─ ocv/
│  │   ├─ ocv_soc.py                    # OCV-SOC 룩업
│  │   └─ chemistry_check.py            # NCM 케미스트리 검증
│  └─ data_io.py                        # 공통 데이터 I/O
│
├─ ui/                                  # Antigravity 영역 (Streamlit)
│  ├─ data_analysis_ui.py
│  ├─ pages/
│  │   ├─ 03_⚙️_ECM_Fitting.py          # ECM 식별 + K1 결과 보기
│  │   └─ 05_📊_Benchmark_View.py       # KCI1 시트 (Section 1~5)
│  └─ widgets/plot_helpers.py
│
├─ tests/ui/                            # pytest (3건 모두 통과)
│
├─ outputs/                             # 산출물 (git 제외)
│  ├─ runs/
│  │   ├─ K1-1rc-{25C,50C}/params_per_cycle.csv
│  │   ├─ K1-2rc-{25C,50C}/params_per_cycle.csv
│  │   ├─ K1-fom-{25C,50C}/params_per_cycle.csv
│  │   └─ K1-summary/
│  │       ├─ REPORT.md                 # KCI1 핵심 수치
│  │       └─ diagnosis_low_cycle.md    # cycle 100/500 데이터부족 진단
│  ├─ figures/K1_fractional_ecm/
│  │   └─ fig{1~6}.{pdf,png}            # 본문 그림 후보
│  ├─ handoff_stage1_codex.md
│  └─ handoff_stage1_antigravity.md
│
├─ 01_분석보고서_및_사양/
│  ├─ BRIEFING_for_new_chat.md          # ← 이 문서
│  ├─ 2026-04-23_Codex_Antigravity_분업_Spec_v1.md
│  ├─ 2026-04-23_Codex_TODO_v1.md       (v1.4)
│  ├─ 2026-04-23_Antigravity_TODO_v1.md (v1.4)
│  ├─ 2026-04-23_SCI논문_전략_v2.md     (v2.3)
│  ├─ 2026-04-23_Multi_Paper_전략_v3.md (v3.2)
│  ├─ 2026-04-23_battery_dataset_inventory_report.md
│  ├─ kickoff/                          # Cowork 가 작성한 단계별 kickoff
│  │   ├─ STAGE_PLAN.md
│  │   ├─ STAGE_0_*.md
│  │   ├─ STAGE_1_Codex_kickoff.md
│  │   ├─ STAGE_1_Antigravity_kickoff.md
│  │   └─ STAGE_1_Codex_github_push.md
│  ├─ K1_paper_draft/                   # KCI1 한글 논문 초고
│  │   ├─ build_paper.js                # docx-js 빌드 스크립트
│  │   ├─ README.md                     # 빌드 가이드
│  │   └─ K1_paper_draft.docx           # (빌드 시 생성, git 제외)
│  ├─ ppt_build/                        # SCI 전략 18-슬라이드 PPT
│  ├─ portable/                         # 집 PC용 셋업 스크립트
│  └─ github_push/                      # PowerShell 푸시 스크립트
│
├─ 02_실험_데이터/                      # Raw 데이터 (git 제외)
├─ 셀 엑셀파일/                         # KIER 셀 DCIR (git 제외)
└─ 모듈엑셀파일/                        # 14S 모듈 데이터 (git 제외)
```

---

## 6. 현재까지 완료된 단계

### Stage 0 (공통 기반) — 완료
- 데이터 카탈로그 생성, OCV-SOC 룩업, NCM 케미스트리 검증
- 1-RC ECM 베이스라인 식별
- KIER 로더 구현
- pytest 통과
- GitHub 5개 브랜치(main + KCI1 + KCI2 + SCI1 + SCI2 + SCI3) 초기 푸시

### Stage 1 (KCI1) — 90% 완료
- **알고리즘 (Codex)**: Fractional ECM 구현, 25°C/50°C × cycle 100~3000 식별 완료
  - 결과: cycle 1000/1100/1200/1300/3000 (cycle 100/500 은 데이터 부족으로 제외)
  - α 범위 [0.32, 0.41] (lower bound 0.3 으로 완화 후)
- **시각화 (Antigravity)**: ECM Fitting K1 결과 보기, Benchmark View 5섹션 구현
- **논문 초고 (Cowork)**: docx-js 빌드 스크립트 작성, 본문/표/참고문헌 placeholder 포함
- **남은 작업** (이 새 채팅에서 진행할 것):
  1. 본문 다듬기 (특히 4.3, 4.4, 4.5 절)
  2. 그림 3장 실제 PNG 삽입
  3. 참고문헌 7편의 권/호/페이지 검증
  4. 저자 정보 placeholder → 실제 정보
  5. 수식 (Eq.1, Eq.2) 한글 워드프로세서 수식편집기로 재입력
  6. KIER 데이터 사용에 대한 사사 (Acknowledgement) 추가
  7. Abstract 영문 정제

---

## 7. KCI1 핵심 결과 (논문에 들어갈 숫자)

이 숫자들은 `outputs/runs/K1-summary/REPORT.md` 에서 확정된 값입니다. 논문 수치 인용 시 이 표를 정전(正典)으로 사용하세요.

### 7.1 평균 전압 RMSE (V)

| Temp | 1RC | 2RC | FOM | FOM 개선율 (vs 1RC) |
|---|---:|---:|---:|---:|
| 25°C | 0.00137591 | 0.00121213 | 0.000412691 | **70.01%** |
| 50°C | 0.000904236 | 0.00102436 | 0.000334991 | **62.95%** |

### 7.2 단조성 (Spearman ρ vs cycle)

| Temp | α ρ | α p-value | R0 ρ | R0 p-value |
|---|---:|---:|---:|---:|
| 25°C | -0.1026 | nan | 0.1 | nan |
| 50°C | 0.5643 | nan | 1.0 | nan |

→ **α 단조성은 약함**. 결론에서는 α 를 "추가 데이터 확보 후 검토할 후보 지표" 로 신중하게 기술.

### 7.3 온도 비교

| cycle | R0_50/R0_25 | Δα (50-25) |
|---:|---:|---:|
| 1000 | 0.6252 | 0 |
| 1100 | 0.6072 | 0 |
| 1200 | 0.6027 | -0.05 |
| 1300 | 0.6848 | 0.04 |
| 3000 | 0.7248 | 0.03 |

- **평균 R0_50/R0_25 = 0.649** — 50°C 에서 R0 가 일관되게 낮음 (전기화학적 직관에 부합)

### 7.4 Cycle 100/500 이상 현상
DCIR 펄스 윈도우 내 비-제로 전류 샘플 1개, 회복 샘플 1개로 dynamic fitting 불가능. 데이터 해상도 한계로 분류 (`fit_quality_flag = insufficient_dynamic_samples`). 본문 4.6 절에서 별도 다룸.

---

## 8. KCI1 논문 메인 클레임 (수정됨)

원래는 "α 가 cycle 에 따라 단조감소하는 SOH 지표" 였으나, 실데이터에서 단조성이 약하게 나와 **다음 두 축으로 재포지셔닝**:

1. **FOM 적용 시 1RC 대비 평균 전압 RMSE 가 25°C 70%, 50°C 63% 감소**
2. **R0 가 50°C 에서 25°C 대비 평균 0.649 배** — 전기화학적 직관에 부합

α 는 "추가 데이터 확보 후 SOH 보조 지표로 검토할 후보 변수" 정도의 톤으로 기술.

---

## 9. KCI1 논문 양식

| 항목 | 값 |
|---|---|
| 학회 | 한국산학기술학회 논문지 |
| 양식 기준 | 심사용논문서식-국문(2019).pdf |
| 글·형식 참고 | 사용자의 2021_rev02 OLTC-ESS 논문 |
| 페이지 크기 | 188 × 258 mm |
| 단 구성 | 제목/Abstract/Keywords 1단, 본문 2단 |
| 본문 폰트 | 맑은 고딕 9pt (한글), Times New Roman 9pt (영문) |
| 제목 폰트 | 14pt Bold (한글) |
| 분량 | 6페이지 이내 |
| 결론 형식 | (1)(2)(3)(4) 번호 매김 |
| 참고문헌 | [번호] 형식, DOI 포함 |

논문 본문은 한국어로 작성, Abstract/Keywords 만 영어.

---

## 10. 기술 스택

- **Python 3.12** + numpy, scipy, pandas, filterpy, scikit-learn, torch
- **Streamlit** + plotly (UI)
- **pytest** (테스트)
- **Node.js** + docx-js (.docx 빌드)
- **Git** (5-브랜치)
- **PowerShell** (자동화 스크립트, UTF-8 인코딩 주의)

---

## 11. 새 채팅창에서 이어가기 좋은 작업들

이 브리핑을 붙여넣은 뒤, 다음과 같은 후속 요청을 권장합니다.

### 본문 다듬기
- "KCI1 본문 4.3 절(분수계 ECM 식별 결과) 을 다음 RMSE 표를 자연스럽게 인용해서 다시 써줘: [표 붙여넣기]"
- "결론 (1)(2)(3)(4) 항목을 사용자의 2021_rev02 톤에 맞게 다듬어줘"
- "서론을 아래 인용 흐름으로 7~8문장으로 압축해줘: Plett 2004 → Doyle 1993 → ..."

### Abstract / Keywords
- "한국어 초록을 영문 Abstract 로 옮겨줘. Times New Roman 9pt italic, 1단락, 200 words 이내, IEEE 스타일"
- "Keywords 5개 추천: NCM, fractional, ..."

### 참고문헌
- "Plett 2004 의 정확한 권/호/페이지/DOI 알려줘"
- "Doyle 1993 J. Electrochem. Soc. 인용형식 IEEE / ACS / KIIE 식으로 각각"

### 그림 캡션
- "Fig. 1 ~ Fig. 3 의 한국어 캡션을 한국산학기술학회 논문지 양식으로 작성"
- "Fig. 캡션은 그림 아래, Table 캡션은 표 위에 위치"

### 영어 번역 (SCI1 대비)
- "이 절의 한국어 본문을 SCI 영어 논문 톤으로 번역. 능동태 줄이고, present tense, IEEE Trans 톤"

---

## 12. 절대 잊지 말아야 할 사항

1. **이전 결과는 `outputs/` 폴더에 그대로 보존**되어 있다. 새 채팅에서는 직접 파일을 못 읽으므로, 위 표(7절) 의 숫자를 정전(正典)으로 사용.
2. **GitHub 에는 코드만 푸시**, outputs/ 는 .gitignore. 따라서 GitHub 만 보고 결과 추정 금지 — 항상 이 브리핑의 7절 표 참조.
3. **Cycle 100/500 은 데이터 부족**이므로 fitting 결과가 좋아 보여도 본문에서는 dynamic-fit 대상에서 제외하고 4.6 절 별도 처리.
4. **α 단조성 클레임 금지**. 약하게 나왔으므로 "추가 데이터 필요한 후보 지표" 로만 기술.
5. **저자명·소속은 placeholder** ("유경상", "○○대학교 ○○공학과"). 실제 정보로 교체 필요.
6. **수식은 docx 빌드 후 한글 워드의 수식 편집기로 재입력** 권장 (자동 빌드된 텍스트 수식은 가독성 낮음).
7. **사사문구**: KIER 데이터 활용 사사 추가 권장.

---

## 13. 단계별 다음 일정 (이 채팅 이후)

| 단계 | 작업 | 예상 시점 | 사용처 |
|---|---|---|---|
| KCI1 본문 다듬기 | 새 Claude 채팅 | 2026-05 초 | **현재** |
| KCI1 그림 보완 | 본인 작업 | 2026-05 초 | 본인 |
| KCI1 한글 변환·검토 | 본인 + 지도교수 | 2026-05 중 | 본인 |
| KCI1 학회 투고 | 본인 | **2026-06 말 ~ 7월 초** | 본인 |
| Stage 2 병렬 착수 | Cowork → Codex/Antigravity | 2026-05 중 | KCI2 + SCI1 |
| KCI2 + SCI1 초고 | 새 Claude 채팅 (이 문서 v2 로 갱신) | 2026-08 ~ 09 | 본인 |
| SCI2 (Cross-scale) | Stage 3 | 2026-11 ~ 2027-01 | 본인 |
| SCI3 (Hybrid+UQ) | Stage 4 (Stretch) | 2027-02 ~ 04 | 본인 |

---

## 14. 이 문서 사용 시 주의

- 이 문서는 **2026-04-29 시점 스냅샷**입니다. Stage 2 진입 시 갱신해야 합니다 (`v2` 추가 권장).
- 새 채팅에서 작업 후 새로 결정된 사항은 본 문서의 해당 절에 반영해 주세요.
- GitHub 최신 상태는 https://github.com/kyungsang-ryu/battery 에서 직접 확인.

---

*이 문서는 Claude Cowork (battery 프로젝트) 에서 자동 생성되었습니다. 작성: 2026-04-29.*
