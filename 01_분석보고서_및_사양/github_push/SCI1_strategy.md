# [SCI1] FOM-AEKF: Joint SOC/SOH Estimation for NCM Pouch Cells — 알고리즘 개발 전략

**Branch**: `SCI1`
**Paper**: FOM-AEKF: Joint SOC/SOH Estimation for NCM Pouch Cells with Temperature-Aging Adaptive Q/R Scheduling
**Target Journal**: J. Energy Storage IF 8~9 (1차) / IEEE Trans. on Transportation Electrification IF 7 (대안)
**Submission**: T+5~6개월
**Status**: Plan (메인 SCI 페이퍼)

---

## 1. 연구 가설 (한 줄)

분수계 ECM + Dual Adaptive EKF + **온도×SOH 2D Q/R 스케줄링** 의 결합이 **SOC/SOH 동시 추정에서 7종 SOTA baseline 대비 정량 우위** 를 보이며, 외삽 영역 (unseen aging / temperature / pattern) 에서 강건성을 유지한다.

---

## 2. 사용 데이터 (셀 단위만, 모듈 제외)

**경로**: `D:\…\battery\data\셀 엑셀파일\셀 엑셀파일\` + `02_실험_데이터\pouch_SOH\`

| Dataset | 채널·온도 | 노화 단위 | 활용 |
|---|---|---|---|
| main_cell | ch2/25°C, ch7/50°C | cycle 0~3,800 | 학습·테스트 |
| main_cell | ch3/0°C | cycle 0~101 | Temperature 외삽 테스트 |
| pouch_SOH | ch1~ch8/25·40°C | weeks 5~30 | Cross-pattern·multi-cell |

전부 NCM Pouch. 모듈은 SCI2 에서.

---

## 3. 알고리즘 / 메소드

### 3.1 분수계 ECM (K1 결과 leverage)

K1 페이퍼의 분수계 R+CPE 모델 채택. R0, R1, CPE(Q, α), Cn 을 상태 또는 파라미터로 둠.

### 3.2 Dual Adaptive EKF 구조

```
[V, I, T]_t
    ↓
┌────────────────────────┐    ┌─────────────────────────┐
│ Fast Filter (1 Hz)      │    │ Slow Filter (per-cycle) │
│ State: x = [SOC, V1, V2]│ ↔ │ Param: θ = [R0, R1, Cn] │
└────────────────────────┘    └─────────────────────────┘
              ↓                          ↓
            SOC                        SOH = Cn / Cn0
```

- **Fast filter**: 1 Hz, EKF, 측정모델 OCV(SOC, T) 사용 (Task P0.2 산출 룩업).
- **Slow filter**: cycle 종료마다 EKF/RLS, $R_0, R_1, C_n$ 갱신.
- **Time-scale separation**: 안정성 분석 (Lyapunov 가능성).

### 3.3 2D Q/R 스케줄러 (핵심 차별점)

기존 AEKF: $Q_k, R_k = f(\text{innovation residual}_k)$ — 1D 적응.

본 연구: $Q_k = Q_0 \cdot f_Q(T_k, \widehat{\text{SOH}}_k)$, $R_k = R_0 \cdot f_R(T_k, \widehat{\text{SOH}}_k)$

여기서 $f_Q, f_R$ 는 **2D 룩업 표** 또는 **얕은 MLP** 로 KIER 데이터의 (T, cycle) 그리드 위에서 오프라인 학습.

**학습 절차**:
1. (T, cycle) 그리드 위 각 셀에서 cell-equivalent SOC/SOH ground truth 산출.
2. 각 셀에서 fast filter 를 돌리며 Q, R 스케일을 grid search 또는 gradient.
3. 최적 Q-scale, R-scale 매트릭스 → 룩업 표 또는 MLP fit.
4. 추론 단계: 매 스텝 (T_k, $\widehat{\text{SOH}}_k$) 입력 → Q_k, R_k 출력.

### 3.4 추론 alg

```
init: x_0, θ_0 (K1 결과 또는 nominal)
for k = 1, 2, ...:
    Q_k, R_k = scheduler(T_k, SOH_hat_{k-1})
    x_k = fast_filter.predict_update(x_{k-1}, V_k, I_k, θ, Q_k, R_k)
    if cycle_end:
        θ = slow_filter.update(θ, residuals)
        SOH_hat = θ.Cn / Cn_0
    output (SOC_k, SOH_hat)
```

---

## 4. 구현 모듈 (Codex 가 짤 .py)

```
algo/estimators/
├── base.py                     # 추상 Estimator + REGISTRY
├── ah_counting.py              # baseline 1
├── ocv_lookup.py               # baseline 2
├── ekf.py                      # baseline 3 (1-RC)
├── ukf.py                      # baseline 4
├── dual_ekf.py                 # baseline 5
├── dual_ukf.py                 # baseline 6
├── aekf.py                     # baseline 7 (innovation-only)
├── lstm_joint.py               # baseline 8 (DL, reviewer 코멘트 예방)
├── _adaptive_scheduler.py      # 2D Q/R 룩업 학습 + 추론
└── dual_aekf.py                # ⭐ 본 연구 FOM-AEKF
```

**공개 API**: 분업 Spec §3.3 `Estimator` 추상 클래스 준수. UI 는 `REGISTRY['dual_aekf'].from_config(cfg).run(df)` 로 호출.

**Runner**:
```bash
python -m algo.runners.run_benchmark \
    --estimators ah_counting,ocv_lookup,ekf,ukf,dual_ekf,dual_ukf,aekf,lstm_joint,dual_aekf \
    --dataset main_cell --temps 25,50 --cycles all \
    --tag bench-stageA-v1
```

---

## 5. 실험 Protocol — Split 4종

(Cross-Scale Split 6은 SCI2 에서 별도 페이퍼)

| Split | 학습 | 테스트 | 의도 |
|---|---|---|---|
| **1 Aging** | (25/50 °C) × cycle 100~1500 | (25/50 °C) × cycle 2000~3800 | 노화 외삽 |
| **2 Temperature** | 25/50 °C 전체 | 0 °C 전체 (cycle 0~101, ch3) | 온도 외삽 (셀 개체 다름 — 표기) |
| **3 Cell** | ch2 (25 °C) | ch7 (50 °C) | 셀+온도 혼합 외삽 |
| **5 Cross-Pattern** | pouch_SOH MG + PVSmoothing | pouch_SOH PowerQuality | 주행 패턴 외삽 |

---

## 6. 평가 메트릭

| 축 | 메트릭 | 목표 |
|---|---|---|
| 정확도 | SOC RMSE / MAE / MAX (%) | RMSE < 2% |
| 정확도 | SOH MAE (%) | < 1.5% |
| 강건성 | 초기 SOC 섭동 ±10/20/30% 회복 시간 (s) | < 60 s |
| 외삽 | 학습 영역 RMSE 대비 외삽 영역 RMSE 비율 | < 1.5× |
| 임베디드성 | 1 스텝 추론 시간 (μs) | < 100 μs |

---

## 7. 산출물

```
outputs/figures/S1_fom_aekf/
├── fig1_architecture.pdf           # FOM-AEKF 구조도
├── fig2_qr_surface_2d.pdf          # 학습된 2D Q/R 룩업 시각화
├── fig3_soc_trajectory.pdf         # 한 cycle SOC 추적 결과 (모든 baseline)
├── fig4_soh_trend.pdf              # cycle별 SOH 추적
├── fig5_split1_aging_rmse.pdf      # 박스플롯
├── fig6_split2_temp_rmse.pdf
├── fig7_split5_pattern_rmse.pdf
├── fig8_inference_time.pdf
├── tab1_full_benchmark.tex         # LaTeX 표 (8 method × 4 split)
└── captions.md

outputs/runs/bench-stageA-v1/
├── summary.csv                      # 전체 메트릭 매트릭스
└── REPORT.md                        # 자동 요약
```

---

## 8. 평가 기준 (acceptance)

- 분수계 ECM 기반 FOM-AEKF 가 baseline 7 + LSTM 1 = 8종 중 **모든 split 에서 SOC/SOH RMSE 1위**.
- vs AEKF (innovation-only) **SOC RMSE 30% 이상 감소** + **SOH MAE 30% 이상 감소** 면 contribution 강력.
- 외삽 영역 RMSE 비율 ≤ 1.5× 면 강건성 입증.
- 추론 시간 100 μs 이하 면 임베디드 친화 강조 가능.

---

## 9. 글쓰기 일정 (영어)

| 시점 | 작업 |
|---|---|
| T+5 | 자료 확보 + 모든 figure/table 산출 |
| T+5 | 영어 글쓰기 시작 (~10~12쪽 표준) |
| T+5.5~6 | J. Energy Storage 또는 IEEE TTE 투고 |
| T+8~10 | reviewer revision 1차 |
| T+12~14 | 게재 (예상) |

---

## 10. 위험 & 대응

| 위험 | 대응 |
|---|---|
| 2D Q/R 학습이 1D innovation-only 대비 우위 X | innovation + 2D 결합 형태로 수정 (Q_k = Q0 · f(T,SOH) + g(innov)) |
| LSTM baseline 가 FOM-AEKF 보다 강함 | LSTM 의 임베디드성·외삽 약점 강조, FOM-AEKF 의 이점 부각 |
| Reviewer "왜 IET PE 2025 와 달라?" | 본 연구 = 2D scheduling + 광범위 외삽 4 split + LSTM 비교. IET 는 1D + 단일 split |
| J. Energy Storage reject | IEEE TTE → J. Power Sources 단계 다운 |

---

## 11. 다른 페이퍼와의 관계

- **K1 leverage**: Methods §3.1 분수계 ECM 식별 부분 압축 + [K1] 자기 인용.
- **SCI2 의 입력**: SCI1 에서 학습된 FOM-AEKF model + 2D Q/R 룩업을 SCI2 에서 그대로 모듈에 적용.
- **SCI3 의 baseline**: SCI3 (Hybrid + UQ) 가 SCI1 결과를 baseline 으로 사용.
