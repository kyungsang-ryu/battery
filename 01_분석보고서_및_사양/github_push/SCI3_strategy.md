# [SCI3] Hybrid Physics-Data Estimator with Calibrated UQ — 알고리즘 개발 전략

**Branch**: `SCI3`
**Paper**: Hybrid Physics-Data Joint Estimator with Calibrated Uncertainty for NCM Pouch Battery State Estimation
**Target Journal**: Applied Energy IF 11 (1차) / eTransportation IF 13 (스트레치)
**Submission**: T+14개월
**Status**: Plan (도전 SCI 페이퍼, **stretch — P4 학습 안정 시 진행**)

---

## 1. 연구 가설 (한 줄)

SCI1 의 FOM-AEKF 잔차에 **얕은 NN residual 또는 GPR 보정 헤드** 를 추가하면 SOC/SOH RMSE 가 추가로 X% 감소하며, **calibrated uncertainty (PICP_95, NLL)** 을 동반해 BMS 안전 마진 설계에 직접 활용 가능하다.

**중요 (사용자 결정 2026-04-23)**: NN vs GPR 둘 중 어느 쪽이 우위인지 모름 → P4.1 prototype 단계에서 **둘 다 시도 후 우위 쪽 채택**, 또는 **두 변종을 모두 ablation 으로 논문에 포함**.

---

## 2. 사용 데이터

SCI1 + SCI2 와 동일 (셀 + 모듈 전체). 추가 데이터 없음 — 같은 데이터에서 hybrid 효과 분리 검증.

(선택) NASA PCoE 18650 — reviewer 추가 어필 필요 시 cross-form-factor 비교.

---

## 3. 알고리즘 / 메소드

### 3.1 Hybrid 구조 (두 변종)

**구조 공통 (Hybrid block)**:

```
[V, I, T]_t
    ↓
FOM-AEKF (SCI1)  ─→  SOC_kf, SOH_kf, e_v (단자전압 잔차)
    ↓                      ↓
            ┌──── [e_v window, T, SOH_kf] ────┐
            │                                  │
       (a) NN residual                  (b) GPR 보정
            │                                  │
            ↓                                  ↓
        Δ_NN                              Δ_GPR
            └────→ SOC_final = SOC_kf + Δ ────┘
                         SOH_final = SOH_kf + Δ_SOH
```

**변종 (a) NN residual**:
- 작은 MLP (3 layer, hidden 32~64, params < 5k).
- 입력: e_v 의 N 스텝 window + (T, SOH_kf) + 정규화.
- 출력: ΔSOC, ΔSOH.
- 학습: multi-task MSE.

**변종 (b) GPR 보정**:
- Sparse GPR (SGPR / SVGP) — O(N³) 회피.
- 입력 동일.
- 출력: 평균 + 분산 (자연스러운 UQ).

### 3.2 학습 Loss

```
L = L_data           (SOC, SOH 정답 vs 추정 MSE)
  + λ1 · L_phys      (ECM 단자전압 잔차)
  + λ2 · L_OCV       (SOC↔OCV 일관성)
  + λ3 · L_smooth    (SOH의 시간미분 평탄성)
  + λ4 · L_calib     (UQ calibration)
```

λ는 Kendall et al. (2018) **uncertainty-weighted** 자동 균형.

### 3.3 UQ (calibrated)

**옵션 1 — Ensemble**: 5 models (다른 seed) 학습 → 출력 분포의 평균·표준편차.
**옵션 2 — Variational dropout**: 추론 시 dropout on, K samples.
**옵션 3 — GPR 자체 분산**: 변종 (b) 의 자연 산출.

**Calibration**: Temperature scaling 또는 isotonic regression 으로 PICP_95 ≈ 0.95 보정.

### 3.4 P4 분기 전략 (어느 쪽 모를 때)

1. **P4.1 (1주)**: 두 변종 모두 작은 prototype + Split 1 (Aging) RMSE 1차 비교.
2. **P4.2 (1~2주)**: 우위 쪽으로 확장 학습 + UQ 통합.
3. **차이가 미미하면 둘 다 ablation 으로 유지** — S3 페이퍼의 부가 contribution.

**참고**:
- **NN**: 데이터 많을수록 강함, 외삽 약함, 학습 시간 ↑, 임베디드 추론 빠름.
- **GPR**: 데이터 적어도 강건, **불확실성이 자연 산출** (UQ 유리), 데이터 ↑ 시 sparse GPR 권장.
- UQ 가 본 페이퍼 핵심 → **GPR 약간 더 자연스러움**, 단 학습 데이터 충분하면 NN+ensemble 도 경쟁력.

---

## 4. 구현 모듈 (Codex 가 짤 .py)

```
algo/estimators/
├── dual_aekf.py            # SCI1 본체 (재사용)
├── hybrid_nn_aekf.py       # 신규 — 변종 (a)
├── hybrid_gpr_aekf.py      # 신규 — 변종 (b)
└── ensemble_wrapper.py     # 신규 — 5-model ensemble 추론

algo/evaluation/
└── metrics.py              # picp(), nll() 추가
```

**공개 API**: `Estimator` 추상 클래스 준수. `run()` 반환에 `soc_std`, `soh_std` 컬럼 추가.

**Runner**:
```bash
python -m algo.runners.run_benchmark \
    --estimators dual_aekf,hybrid_nn_aekf,hybrid_gpr_aekf \
    --dataset main_cell --temps 25,50 --cycles all \
    --uq ensemble --tag bench-hybrid-v1
```

---

## 5. 실험 Protocol

| 항목 | 값 |
|---|---|
| 비교 대상 | FOM-AEKF (SCI1, baseline) + Hybrid-NN + Hybrid-GPR + (선택) PINN |
| Split | SCI1 Split 1~5 + SCI2 Split 6 (cross-scale) |
| UQ 메트릭 | PICP_95, NLL, Sharpness |
| Calibration | Temperature scaling on validation |
| Ablation | (1) FOM-AEKF only, (2) +NN no UQ, (3) +NN + ensemble UQ, (4) +GPR (자체 UQ) |

---

## 6. 산출물

```
outputs/figures/S3_hybrid_uq/
├── fig1_hybrid_architecture.pdf
├── fig2_nn_vs_gpr_rmse.pdf
├── fig3_uq_calibration.pdf            # PICP curve, reliability diagram
├── fig4_uncertainty_extrapolation.pdf # 외삽 영역에서 σ 자동 증가 검증
├── fig5_safe_soc_envelope.pdf         # BMS 안전 마진 시나리오
├── tab1_full_ablation.tex
└── captions.md

outputs/runs/bench-hybrid-v1/
├── summary.csv
├── calibration_metrics.csv
└── REPORT.md
```

---

## 7. 평가 기준 (acceptance)

- Hybrid (NN 또는 GPR) 가 FOM-AEKF (SCI1) 대비 **추가 SOC RMSE 15% 이상 감소**.
- PICP_95 calibration 후 0.93~0.97 범위 유지.
- 외삽 영역에서 **불확실성이 자동 증가** (Sharpness 검증).
- BMS 안전 SOC envelope 시나리오에서 의미 있는 활용 사례.

---

## 8. 글쓰기 일정 (영어)

| 시점 | 작업 |
|---|---|
| T+8~12 | 자료 확보 (P4) |
| T+12~14 | 영어 글쓰기 |
| T+14 | Applied Energy 또는 eTransportation 투고 |
| T+18~20 | revision |
| T+22~24 | 게재 (예상) |

---

## 9. 위험 & 대응

| 위험 | 대응 |
|---|---|
| NN 학습 발산 | 변종 (b) GPR 만으로 진행, 페이퍼 scope 축소 |
| GPR 둘 다 학습 곤란 | hybrid 부분 제거, FOM-AEKF + UQ ensemble 만으로 IEEE TIE/TPEL 도전 |
| UQ calibration 실패 | reliability diagram 보고 + temperature scaling 권고 한계 명시 |
| Applied Energy reject | eTransportation → IEEE TTE → J. Energy Storage 단계 다운 |
| **전체 P4 stretch 실패** | 본 페이퍼 포기, K1+K2+SCI1+SCI2 = 4편 (KCI 2 + SCI 2) 으로 마무리 |

---

## 10. 다른 페이퍼와의 관계

- **SCI1 leverage**: FOM-AEKF 본체를 baseline 으로 직접 사용. "Building on our prior works [SCI1, SCI2]…"
- **SCI2 leverage**: cross-scale 부분도 hybrid 적용 가능 (모듈 데이터에서 hybrid 가 더 좋은가?).
- **K1/K2 인용**: 분수계 ECM 식별 절차 + 셀간 편차 영향에 대한 자기 인용 풀.
- **본 페이퍼는 5편 시리즈의 capstone** — 모든 prior works 종합 인용으로 reviewer 신뢰도 ↑.
