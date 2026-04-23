# [SCI2] Cross-Scale Generalization: Cell → 14S Module — 알고리즘 개발 전략

**Branch**: `SCI2`
**Paper**: Cross-Scale Generalization of a Cell-Trained Joint SOC/SOH Estimator to a 14-Series NCM Pouch Module
**Target Journal**: IEEE Trans. on Transportation Electrification IF 7 (1차) / J. Power Sources IF 8 (대안)
**Submission**: T+8~9개월
**Status**: Plan (두 번째 SCI 페이퍼)

---

## 1. 연구 가설 (한 줄)

SCI1 의 셀 단위에서 학습한 FOM-AEKF 알고리즘이 **추가 학습 없이 동일 chemistry 14S NCM Pouch 모듈에 적용** 되어, **SOC/SOH RMSE 손실을 X% 이내**로 유지하면서 강건하게 동작한다 — 단, K2 결과에 따른 **σ ≤ 임계값 cycle 영역**에서.

---

## 2. 사용 데이터

**셀 (학습)**: SCI1 와 동일 — main_cell ch2/ch7 전체.

**모듈 (테스트)**: `D:\…\battery\data\모듈엑셀파일\모듈엑셀파일\모듈데이터 엑셀파일(2022.01~2023.07)\CH1\` (~3000 cycle 까지).

**보조**: K2 의 σ(cycle) 분석 결과 (`outputs/runs/K2-cell-dispersion/`).

전부 NCM Pouch 동일 chemistry.

---

## 3. 알고리즘 / 메소드

### 3.1 두 시나리오 비교

**시나리오 (a) cell-equivalent**:
- 모듈 측정값을 셀 1개 등가로 변환: $V_{cell}^{eq} = V_{module}/14$, $I_{cell}^{eq} = I_{module}$ (직렬 가정).
- SCI1 의 학습된 FOM-AEKF 를 그대로 적용.
- K2 결과로 σ ≤ X mV cycle 영역에 한정 — "cell-equivalent 적용 가능 윈도우" 사전 입증된 영역.

**시나리오 (b) module-direct**:
- 모듈 단자전압·전류를 그대로 입력.
- ECM 파라미터를 14배 스케일 (R0 ×14, Cn 그대로) 또는 **모듈 1회 캘리브레이션** (모듈 첫 cycle DCIR 1회) 후 적용.
- 본 시나리오는 셀→모듈 일반화의 정량적 한계 분석.

### 3.2 분리 분석

각 시나리오에서:
- SOC RMSE / SOH MAE 산출.
- (a) 의 RMSE 가 (b) 의 몇 % 인가 — cell-equivalent 가정의 효율성.
- σ(cycle) vs cross-scale RMSE 손실 회귀 (K2 결과와 결합).

### 3.3 셀간 편차의 영향 정량화

- 14개 셀 개별 V_cell 을 14개 EKF 로 독립 추정 → SOC 평균 = ground truth proxy.
- 본 알고리즘 SOC vs proxy SOC RMSE = "module-level joint estimation 손실".

---

## 4. 구현 모듈 (Codex 가 짤 .py)

```
algo/estimators/
└── dual_aekf.py            # SCI1 의 FOM-AEKF 그대로 사용 (no retrain)

algo/runners/
├── run_cross_scale.py      # 신규 — cell→module 적용 runner
└── run_simulation.py       # 기존 (재사용)

algo/analysis/
└── cell_dispersion.py      # K2 모듈 unpack 함수 재사용
```

**Runner**:
```bash
python -m algo.runners.run_cross_scale \
    --estimator dual_aekf \
    --train-tag bench-stageA-v1 \
    --module-files "모듈엑셀파일/.../CH1/RPT/*.csv" \
    --scenarios cell-equivalent,module-direct \
    --tag bench-cross-scale-v1
```

**핵심**: 학습된 알고리즘 weights/lookup 은 SCI1 산출물 (`outputs/runs/bench-stageA-v1/model_artifacts/`) 에서 그대로 로드. **재학습 없음** = 본 페이퍼의 contribution.

---

## 5. 실험 Protocol

| 항목 | 값 |
|---|---|
| Split | Split 6 (Cross-Scale) — 학습 = main_cell ch2/ch7, 테스트 = module CH1 |
| 비교 시나리오 | (a) cell-equivalent, (b) module-direct |
| 비교 baseline | SCI1 의 8 종 추정기 모두 동일 cross-scale 적용 |
| 메트릭 | SOC RMSE / MAE, SOH MAE, σ vs RMSE 회귀 |
| Cycle 영역 | 전체 + K2 권고 한계 cycle 영역 분리 보고 |

---

## 6. 산출물

```
outputs/figures/S2_cross_scale/
├── fig1_cross_scale_concept.pdf         # cell→module 다이어그램
├── fig2_celleq_vs_moduledirect.pdf      # 두 시나리오 SOC trajectory 비교
├── fig3_rmse_per_scenario.pdf           # 박스플롯
├── fig4_sigma_vs_rmse_loss.pdf          # K2 σ 결과와 회귀
├── fig5_application_window_module.pdf   # 권고 적용 cycle 영역
├── tab1_baseline_cross_scale.tex
└── captions.md

outputs/runs/bench-cross-scale-v1/
├── summary.csv
├── per_cycle_rmse.csv
└── REPORT.md
```

---

## 7. 평가 기준 (acceptance)

- (a) cell-equivalent 시나리오에서 σ ≤ K2 임계값 cycle 영역에서 SOC RMSE **셀 학습 영역의 1.5× 이내**.
- (b) module-direct 시나리오에서 SOC RMSE **셀 영역의 2× 이내** (모듈 캘리브레이션 1회만으로).
- σ vs cross-scale RMSE 회귀 R² > 0.6 → 정량 모델링 가능.
- 적용 cycle 권고 윈도우가 명확하면 BMS 응용 가치 부각.

---

## 8. 글쓰기 일정 (영어)

| 시점 | 작업 |
|---|---|
| T+6~7 | 자료 확보 (P3.3) + figure 산출 |
| T+7~8 | 영어 글쓰기 시작 |
| T+8~9 | IEEE TTE 또는 J. Power Sources 투고 |
| T+11~13 | revision |
| T+15~17 | 게재 (예상) |

---

## 9. 위험 & 대응

| 위험 | 대응 |
|---|---|
| Cross-scale RMSE 손실 너무 큼 | "limitations and lessons learned" 로 재포지셔닝 → MDPI Batteries IF 4~5 빠른 게재 |
| 모듈 측정 노이즈 (셀간 unpack 어려움) | K2 의 unpack 함수 재사용 + Aux 온도 채널 활용 |
| Reviewer "왜 NASA 18650 안 비교?" | 본 연구는 동일 chemistry·동일 폼팩터 cross-scale 의도. NASA 18650 은 cross-form-factor 별도 contribution 으로 향후 |

---

## 10. 다른 페이퍼와의 관계

- **K2 leverage**: cell-equivalent 가정의 σ 의존성을 [K2] 결과로 정당화 — 본 페이퍼 §3.1 한 단락만으로 압축.
- **SCI1 leverage**: "Building on our prior work [SCI1], we apply the FOM-AEKF without retraining …" — 알고리즘 설명 압축, scope 좁힘.
- **SCI3 의 baseline**: cross-scale + hybrid 결합 시 SCI3 의 비교군.
