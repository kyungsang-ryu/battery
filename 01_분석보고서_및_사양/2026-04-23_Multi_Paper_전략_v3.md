# Multi-Paper 전략 v3 — SCI 3편 + KCI 2편 (총 5편)

**작성일**: 2026-04-23
**상위 문서**: `2026-04-23_SCI논문_전략_v2.md` (v2.2) — 단일 논문 전략을 본 v3 가 **대체 (supersede)**
**관련**: `2026-04-23_Codex_TODO_v1.md`, `2026-04-23_Antigravity_TODO_v1.md`

**노선 결정 (사용자 2026-04-23)**:
- 단일 논문 → **5편 multi-paper 분할**.
- SCI 3편 (미드티어 ~ 상위) + 국내 KCI 2편.
- 한 데이터·코드 베이스에서 5편 산출 — 글쓰기 비용만 추가.

---

## 1. 5편 전체 매트릭스

| # | 등급 | 제목 (가제) | 핵심 contribution | 사용 데이터 | 타깃 저널 | 자료 확보 | 투고 |
|---|---|---|---|---|---|---|---|
| **K1** | KCI | NCM Pouch 셀의 분수계 등가회로모델 식별 및 노화 추적 (한글) | 분수계 ECM (R + CPE) 식별 절차 + α의 노화 추적성 | DCIR cycle 100~3000 (CH2/CH7) | 한국산학기술학회 논문지 / 대한전기학회 논문지 | T+2~3개월 | T+3개월 |
| **K2** | KCI | NCM Pouch 14S 모듈 내 셀간 전압편차 분석 및 SOC 추정 영향 (한글) | 셀간 편차가 모듈 SOC 추정에 미치는 정량 영향 + cell-equiv 시나리오 한계 분석 | module CH1 + KTL 모듈 측정본 | 한국산학기술학회 논문지 / 대한전기학회 논문지 | T+5~6개월 | T+6개월 |
| **S1** | SCI | FOM-AEKF: Joint SOC/SOH Estimation for NCM Pouch Cells with Temperature-Aging Adaptive Q/R Scheduling | Stage A 본체 — 분수계 ECM + Dual AEKF + 2D Q/R lookup (4 split: Aging/Temp/Cell/Cross-pattern) | main_cell + pouch_SOH (셀 단위만) | **J. Energy Storage IF 8~9** 또는 IEEE TTE IF 7 | T+5개월 | T+5~6개월 |
| **S2** | SCI | Cross-Scale Generalization of a Cell-Trained Joint SOC/SOH Estimator to a 14-Series NCM Pouch Module | S1 알고리즘을 모듈에 추가 학습 없이 적용. cell-equiv vs module-direct + 셀간 편차 영향 | S1 + module CH1 | **IEEE TTE IF 7** 또는 J. Power Sources IF 8 | T+8개월 | T+8~9개월 |
| **S3** | SCI | Hybrid Physics-Data Joint Estimator with Calibrated Uncertainty for NCM Pouch Battery State Estimation | FOM-AEKF + 얕은 NN/GPR residual + UQ (PICP/NLL) | 셀+모듈 전체 + (선택) NASA PCoE | **Applied Energy IF 11** 또는 eTransportation IF 13 | T+13개월 | T+14개월 |

**T = 본 프로젝트 시작일 (2026-04-23 기준)**.

---

## 2. 의존 관계 (어느 논문이 다른 논문을 leverage)

```
                    ┌─── K1 (분수계 ECM 식별) ───┐
                    │                          │
   P0~P2 (코드)  ───┤                          ├─→ S1 (FOM-AEKF) ─┐
                    │                          │                  │
                    └─── K2 (모듈 셀간 편차) ──→ S2 (Cross-Scale) ─┤
                                                                  │
                                                S3 (Hybrid + UQ) ─┘
```

- **K1 → S1**: 분수계 ECM 식별 절차를 한글로 먼저 게재해두면 S1이 "ECM 식별 자세한 절차는 [K1] 참조" 로 압축 가능. 페이지 수 절약 + reviewer 신뢰도 ↑.
- **K2 → S2**: 모듈 셀간 편차 정량 분석을 한글로 먼저 빼면 S2가 cross-scale 결과 해석에 [K2] 인용. cell-equiv 시나리오의 한계가 사전 입증되어 있어서 S2 reviewer 가 "왜 module-direct만 의존?" 같은 코멘트를 미리 차단.
- **S1 → S2 → S3**: 영어 SCI 3편의 시계열 leverage. S2/S3 가 "Building on our prior work [S1]" 로 시작 — reviewer 컨셉 빨리 이해 + 자체 reputation 확보.

---

## 3. 각 논문 상세

### K1 — KCI. 분수계 ECM 식별 및 노화 추적 (한글)

**Why KCI**: 방법론 단독 논문. 글쓰기·데이터 부담 적음. SCI S1 의 Methods §3.1 을 한글로 확장해서 단독 게재.

**Core**:
- DCIR 펄스 데이터에서 분수계 R + CPE 모델 파라미터 (R0, R1, C1, α) 식별 절차
- cycle 100, 500, 1000, 1500, 2000, 2500, 3000 의 α 변화 추적 → 노화 지표로서 α 의 단조성·민감도 평가
- 25 °C / 50 °C 온도별 R0·α trajectory

**메서드**:
- `algo/ecm/fractional_ecm.py` (Codex Task P2.1)
- `scipy.optimize.least_squares` 잔차 최소화

**산출**:
- 노화에 따른 α 변화 표 + 그림 (CH2/CH7)
- 25 vs 50 °C R0·α 비교 그림
- 정수 1-RC 와의 voltage 잔차 RMSE 비교 (분수계 우위 입증)

**타깃 저널 후보**: 한국전기학회 논문지 (전력전자기 부문) / 한국전력전자학회 학술대회 + 논문지 / 대한전기학회

**예상 분량**: 본문 6~8쪽 (한글 게재 표준)

---

### K2 — KCI. 모듈 셀간 전압편차 분석 (한글)

**Why KCI**: 셀간 편차 분석은 데이터 분석 중심 — 알고리즘 contribution 작음. SCI S2 의 사전 분석으로 한글 게재가 자연스러움.

**Core**:
- module CH1 + `02_실험_데이터/모듈내 셀간 전압편차 경향확인(EXCEL)/` 데이터로 14개 셀 전압의 cycle 별 편차 추적
- 평균 셀 전압 (Vmod/14) 가정의 정량 오차 — SOC 추정에 미치는 영향
- 셀간 ±편차가 클 때 cell-equivalent 시나리오의 한계 (S2 의 핵심 기여)

**메서드**:
- module CH1 RPT × cycle 100~3000 의 14개 셀 전압 unpack
- σ(Vcell) / V̄cell 비율 계산
- 단순 EKF 1-RC 를 적용해 σ가 SOC 오차에 미치는 영향 simulation

**산출**:
- σ(Vcell) vs cycle 곡선
- 셀간 편차의 SOC 추정 RMSE 영향 (정량)
- cell-equivalent 시나리오 적용 가능 cycle 범위 권고

**타깃 저널 후보**: 한국산학기술학회 논문지 / 대한전기학회 논문지 / 한국 BMS 관련 학회

**예상 분량**: 본문 6~8쪽

---

### S1 — SCI. FOM-AEKF (셀 단위, 메인)

**Core (현 SCI 전략 v2.2 §2.1 그대로)**:
- 분수계 ECM × Dual Adaptive EKF × 온도×SOH 2D Q/R lookup
- Split 1, 2, 3, 5 (Aging / Temperature / Cell / Cross-pattern) 4종
- Baseline 7종 + 추가 LSTM 1종 (reviewer 코멘트 예방)

**의존**: P0~P3 (Cross-scale 부분 제외)

**Cross-scale 결과는 S1에 포함시키지 않고 S2로 미룬다** — S1을 깔끔하게 셀 단위만 다루어 scope 좁히고 reviewer 부담 감소.

**산출**:
- Methods 4 절 (3.1 분수계 ECM / 3.2 Dual AEKF / 3.3 2D Q/R 학습 / 3.4 구현)
- Results: 4 split × 8 baseline = 32 셀 비교 표 + 박스플롯·trajectory
- Discussion: 2D Q/R surface 학습된 형태 해석 + α 의 노화 의미

**타깃 저널**: J. Energy Storage IF 8~9 (1차) / IEEE TTE IF 7 (대안)

---

### S2 — SCI. Cross-Scale (Cell → Module)

**Core**:
- S1 에서 학습한 FOM-AEKF 를 module CH1 에 추가 학습 없이 적용
- 두 시나리오: (a) cell-equivalent (Vmod/14, Imod), (b) module-direct (Vmod, Imod + R0/Cn 재캘리브레이션)
- 셀간 편차의 영향 정량 (K2 인용)

**의존**: P3 Task P3.3 (Cross-Scale split 6) + K2

**Why 단독 논문 가치**: 동일 chemistry 셀→모듈 cross-scale 일반화는 SOC/SOH joint 분야에서 사례 희소. SCI S1 안에 묻으면 "supplementary 결과" 처럼 약화되지만, 단독 논문이면 메인 contribution으로 강력.

**산출**:
- 두 시나리오 RMSE 비교 표
- 셀간 편차 σ(t) vs cross-scale RMSE 손실 상관관계
- 권고 적용 범위 (몇 cycle 까지 cell-equivalent 가능한가)

**타깃 저널**: IEEE TTE IF 7 (1차, EV BMS angle 강조) / J. Power Sources IF 8 (대안, 전기화학 + 모듈 angle)

---

### S3 — SCI. Hybrid + UQ (상위 도전)

**Core**:
- FOM-AEKF 의 fast filter 잔차에 **얕은 NN residual + GPR 보정 헤드 둘 다 시도 후 좋은 쪽 채택** (사용자 결정 2026-04-23). 또는 두 변종을 모두 보고하는 ablation 형태로 논문화.
- Multi-task loss (SOC + SOH + ECM 잔차 + UQ calibration)
- Calibrated UQ: ensemble (5 models) 또는 variational dropout → PICP_95, NLL 보고
- 외삽 영역에서 UQ 가 자동으로 confidence ↓ 하는지 검증

**P4 분기 전략 (어느 쪽 모를 때)**:
1. **P4.1 (1주)**: 두 변종 모두 작은 prototype 구현 — `algo/estimators/hybrid_nn_aekf.py` + `algo/estimators/hybrid_gpr_aekf.py`. 각 학습/추론 안정성 + Split 1 (Aging) RMSE 1차 비교.
2. **P4.2 (1~2주)**: 우위 쪽으로 확장 학습 + UQ 통합. 차이가 미미하면 두 변종 모두 ablation으로 유지 (S3 페이퍼의 부가 contribution).
3. **NN vs GPR 비교 관점 참고**:
   - **NN residual**: 데이터 많을수록 강함, 외삽 약함, 학습 시간 ↑, 임베디드 추론 빠름.
   - **GPR**: 데이터 적어도 강건, **불확실성이 자연 산출** (UQ에 유리), 데이터 ↑ 시 O(N³) 부담 — sparse GPR (SGPR/SVGP) 사용 권장.
   - UQ 동반이 본 S3의 핵심 contribution이므로 **GPR이 약간 더 자연스러운 선택**, 단 학습 데이터 많으면 NN+ensemble 도 경쟁력 ↑.

**의존**: P4 (stretch) + S1, S2 게재 후 leverage

**Why 상위 저널 가능**: 
- Hybrid (filter + NN/GPR) 가 4축 differential
- Calibrated UQ 동반은 SOC/SOH joint 분야 희소
- BMS 안전 마진 application angle 강함

**타깃 저널**: Applied Energy IF 11 (1차) / eTransportation IF 13 (스트레치)

---

## 4. 타임라인 (마일스톤 v3)

| 시점 (T+개월) | 작업 | 산출 |
|---|---|---|
| 0~1 | P0 데이터·환경 정비 | 카탈로그, OCV 룩업 3종, 1-RC ECM |
| 1~2 | P1 Baseline 7종 (LSTM 추가) | bench-baseline 결과 |
| 2~3 | P2.1 분수계 ECM 식별 | **K1 자료 확보** |
| 3 | **K1 한글 글쓰기 시작** | T+3.5: 투고 |
| 3~5 | P2.2 Dual AEKF + 2D Q/R 학습 | **S1 자료 확보** |
| 5 | **S1 영어 글쓰기 시작** | T+5.5~6: 투고 |
| 5~6 | P3.2 외삽 4 split + 모듈 셀간 편차 분석 | **K2 자료 확보** |
| 6 | **K2 한글 글쓰기 시작** | T+6.5: 투고 |
| 6~7 | P3.3 Cross-Scale (Split 6) | **S2 자료 확보** |
| 7~8 | **S2 영어 글쓰기** | T+8~9: 투고 |
| 8~12 | P4 Hybrid NN/GPR + UQ | **S3 자료 확보** |
| 12~14 | **S3 영어 글쓰기** | T+14: 투고 |

**자료 확보 합계**: ~14개월. 게재까지는 + 6~12개월 더 (저널별).

---

## 5. 글쓰기 우선순위 원칙

1. **K1 → S1 → K2 → S2 → S3 순서 엄수**. 각 페이퍼가 다음 페이퍼의 leverage가 되도록.
2. **K1·K2 (한글)** 는 글쓰기 부담 작음 + 게재 빠름. 박사 졸업 요건 / 국내 평가 / SCI 게재 전 자기 인용 풀 확보.
3. **S1 가장 중요**. Scope 좁히고 contribution 분명. **욕심 금지**. 잘 reject 안 되도록 만든 후 → S2/S3 가 stand on shoulders.
4. **S3 는 조건부**. P4 학습 안정되면 진행, 안 되면 S2 까지 4편 (SCI 2 + KCI 2) 으로 마무리.

---

## 6. Self-plagiarism 방지

5편이 같은 데이터·코드 베이스를 공유하므로 self-plagiarism 위험. 다음 원칙 엄수.

- **각 논문은 stand-alone**: 다른 논문 안 봐도 이해 가능해야 함 (단, Methods 일부 압축은 허용).
- **데이터 description 중복 최소**: K1·K2·S1·S2·S3 모두 "Same dataset as [K1] / [S1]" cross-cite + 핵심 spec 만 1단락 재진술.
- **Method 중복**: 분수계 ECM 식별 자세한 절차는 K1 에서, 다른 논문에선 "[K1] 참조" + 한 단락 요약.
- **Figure 재사용 금지**: 같은 그림을 두 논문에 그대로 쓰지 않음. 다른 cycle/조건 그림으로 교체.
- **Reviewer 가 의심하면 cover letter 에 명시**: "This work uses the same KIER NCM-pouch dataset as our prior works [K1, K2, S1], with non-overlapping contributions detailed in §1."

---

## 7. 실패 시 fallback

| 시나리오 | 대응 |
|---|---|
| K1 reject | 다른 KCI 학회 재시도 (한국전력전자학회 ↔ 한국전기학회). 한국 학회는 보통 reject 적음 |
| S1 reject | J. Energy Storage → IEEE TTE → J. Power Sources 단계 다운. fallback 가능 |
| S2 cross-scale 결과 부진 (RMSE 증가율 큼) | Title 을 "limitations and lessons learned" 로 재포지셔닝 → MDPI Batteries IF 4~5 빠른 게재 |
| S3 NN 학습 발산 | hybrid 부분 제거, FOM-AEKF + UQ ensemble 만으로 IEEE TIE/TPEL 도전 |

전 단계가 완전 실패해도 **K1 + K2 + S1 = 3편 (KCI 2 + SCI 1)** 은 거의 확실히 확보.

---

## 8. Codex / Antigravity 영향 (실행 측면)

- **코드 작업은 거의 변경 없음** — 5편 모두 같은 `algo/`, `outputs/` 사용.
- Codex_TODO_v1.md 의 P5 (논문 그림 자동 생성) 만 갱신 — 5편별 Figure 디렉터리 분리:
  - `outputs/figures/K1_fractional_ecm/`
  - `outputs/figures/K2_module_voltage_dev/`
  - `outputs/figures/S1_fom_aekf/`
  - `outputs/figures/S2_cross_scale/`
  - `outputs/figures/S3_hybrid_uq/`
- Antigravity_TODO_v1.md 는 변경 없음 — UI는 5편 데이터 모두 대상.

---

## 9. 사용자 결정 포인트

본 v3 채택 시 다음 갱신 필요. 동의하면 일괄 진행:

1. PPT (`ppt_build/build_ppt.js`) 슬라이드 추가 — Multi-Paper Roadmap 1~2장 + 마일스톤 슬라이드 v3로 교체.
2. Codex_TODO_v1.md Task P5 의 그림 산출 디렉터리를 5편별 분리로 갱신.
3. SCI 전략 v2.2 → v3 supersede 명시 (v2.2 문서 끝에 "본 문서는 v3 (Multi-Paper)로 대체됨" 한 줄 추가) — 단, 양 에이전트 금지 정책에 따라 사용자가 직접 추가.

---

## Changelog

- **2026-04-23 v3.2** (5/10/15 °C supplementary 추가)
  - SCI 전략 v2.3 § 5.2 Split 2 갱신을 그대로 반영 — main_cell 의 0/25/50 °C + 추가 5/10/15 °C (Pattern only, SOC 만) 가 S1 의 wide thermal envelope contribution 강화.
  - K1·K2 는 영향 없음 (DCIR/RPT 만 쓰므로 25/50 °C 그대로).
  - S2/S3 는 영향 없음 (모듈 cross-scale + Hybrid).

- **2026-04-23 v3.1** (사용자 추가 결정)
  - **K1·K2 KCI 학회 후보 확정** (사용자): **한국산학기술학회 논문지** 또는 **대한전기학회 논문지**.
  - **S3 hybrid 컴포넌트 결정 보류** (사용자: "둘 다 잘 모르겠어") → P4.1 prototype 단계에서 **NN residual + GPR 둘 다 시도 후 우위 쪽 채택** 또는 ablation 형태로 둘 다 논문에 포함. P4 분기 전략 §3 (S3) 에 절차 명시.

- **2026-04-23 v3** (초판)
  - 단일 논문 → **5편 multi-paper 분할** (사용자 결정).
  - SCI 3편 (S1 FOM-AEKF / S2 Cross-Scale / S3 Hybrid+UQ) + KCI 2편 (K1 분수계 ECM / K2 모듈 셀간 편차).
  - K1·K2 를 SCI 의 사전·보조 작업으로 위치시켜 글쓰기 leverage 확보.
  - 자료 확보 ~14개월 / 게재 ~24개월 / fallback 시 3편 (KCI 2 + SCI 1) 확실 확보.
  - 코드·데이터 작업은 기존 plan 거의 그대로 — 글쓰기 단계만 5분할.
