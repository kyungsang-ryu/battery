# [KCI2] 14S 모듈 내 셀간 전압편차 분석 및 SOC 추정 영향 — 알고리즘 개발 전략

**Branch**: `KCI2`
**Paper**: NCM Pouch 14S 모듈 내 셀간 전압편차 분석 및 SOC 추정 영향 (한글)
**Target Journal**: 한국산학기술학회 논문지 (1차) / 대한전기학회 논문지 (1차 대안)
**Submission**: T+6개월
**Status**: Plan

---

## 1. 연구 가설 (한 줄)

14S NCM Pouch 모듈 내 14개 셀의 **전압편차 σ가 사이클 진행에 따라 증가**하며, 그 σ가 **모듈 SOC 추정 정확도에 정량적·예측 가능한 영향**을 미친다 → cell-equivalent 가정의 적용 한계 cycle 을 정량 도출.

---

## 2. 사용 데이터

**경로 1 — 모듈 raw**: `D:\…\battery\data\모듈엑셀파일\모듈엑셀파일\모듈데이터 엑셀파일(2022.01~2023.07)\CH1\`

| 자료 종류 | cycle 그리드 | 비고 |
|---|---|---|
| RPT | ~1900, 2000, 2100, …, 3200 | 14개 셀 전압 (`[004]~[017]AuxV(V)`) 동시 기록 |
| Pattern | cycle별 폴더 + 분할 청크 | `CH01.csv` + `CH01(0~4).csv` 자동 merge 필요 |

**경로 2 — KTL 측정본**: `D:\…\battery\data\02_실험_데이터\모듈내 셀간 전압편차 경향확인(EXCEL)\` (cycle 100~1300, RPT/ACIR)

**파일 포맷**: PNE CSV (~90 컬럼, 모듈 전용 alias 필요).

**사전 조건**: `algo/loaders/kier.py` 의 `dataset='module'` 로딩 + Pattern 분할 자동 merge 동작.

---

## 3. 알고리즘 / 메소드

### 3.1 셀간 편차 추적

각 RPT 시점 t 에서:

$$\bar{V}_{cell}(t) = \frac{1}{14} \sum_{i=1}^{14} V_{cell,i}(t)$$
$$\sigma_V(t) = \sqrt{\frac{1}{14} \sum_{i=1}^{14} (V_{cell,i}(t) - \bar{V}_{cell}(t))^2}$$

**전 cycle 에 걸쳐 σ 추적**: $\sigma(\text{cycle})$ trajectory 산출.

**SOC 의존성**: 동일 cycle 내에서 SOC 0/30/50/80/100% 별 σ 차이 비교 (충방전 곡선 분리).

### 3.2 SOC 추정 영향 simulation

가설: "셀간 편차가 클수록 cell-equivalent 가정 (모듈 V/14 = 평균 셀 V) 의 SOC 추정 RMSE 증가".

**실험 절차**:
1. cycle k 의 모듈 데이터 로드.
2. (a) 평균 셀 가정: $V_{cell}^{avg} = V_{module}/14$ → 단순 EKF 1-RC 로 SOC 추정.
3. (b) 14개 개별 셀 SOC 평균: 14개 셀 각각 EKF → 평균 → ground truth proxy.
4. RMSE($\text{SOC}^{(a)}, \text{SOC}^{(b)}$) 산출.
5. 모든 cycle 에 대해 반복 → RMSE vs σ 의존성 회귀.

### 3.3 적용 한계 도출

회귀 결과로 "**σ ≤ X mV 인 cycle 까지는 cell-equivalent 가정의 SOC 오차 < 1%**" 같은 정량 권고.

---

## 4. 구현 모듈 (Codex 가 짤 .py)

```
algo/loaders/
└── kier.py                 # 기존 — module 데이터 로딩 (dataset='module')

algo/analysis/              # 신규 폴더
├── __init__.py
├── module_unpack.py        # 14 셀 전압·온도 unpack
└── cell_dispersion.py      # σ 계산, RMSE 영향 simulation
```

**공개 API**:
```python
def unpack_module_cells(df: pd.DataFrame) -> pd.DataFrame:
    """모듈 raw → 컬럼 V_cell_01 ~ V_cell_14, T_aux_1~3, V_module"""

def compute_cell_dispersion(df_unpacked: pd.DataFrame, soc_bins: list = None) -> dict:
    """sigma(t), sigma at SOC bins"""

def simulate_celleq_vs_individual(df, ekf_config) -> dict:
    """Returns: {sigma, rmse_celleq_vs_indiv, ...}"""
```

---

## 5. 실험 Protocol

| 항목 | 값 |
|---|---|
| 데이터 | module CH1 RPT 전 cycle (모듈엑셀파일) + KTL 모듈 측정본 |
| 셀 단일 알고리즘 | EKF 1-RC (단순화, 본 페이퍼 메인 기여 아님) |
| 비교 | cell-equivalent (V_module/14) vs 14개 셀 개별 EKF 평균 |
| 메트릭 | $\sigma_V(t)$, $\Delta$SOC RMSE, 회귀 R² |
| 횟수 | 모든 RPT cycle (~30 점) |

---

## 6. 산출물

```
outputs/figures/K2_module_voltage_dev/
├── fig1_module_schematic.pdf            # 14S 구조 + 측정 채널
├── fig2_cell_voltage_traces.pdf         # 한 cycle 의 14개 셀 전압
├── fig3_sigma_vs_cycle.pdf              # σ trajectory
├── fig4_sigma_vs_soc.pdf                # SOC bin별 σ
├── fig5_celleq_rmse_vs_sigma.pdf        # 핵심 결과 회귀
├── fig6_application_window.pdf          # 한계 cycle 권고
└── captions.md

outputs/runs/K2-cell-dispersion/
├── sigma_per_cycle.csv
├── rmse_celleq_per_cycle.csv
└── REPORT.md
```

---

## 7. 평가 기준 (acceptance)

- $\sigma(\text{cycle})$ 가 단조 증가 trend (Spearman ρ > 0.6) 면 가설 1 입증.
- $\Delta$SOC RMSE vs σ 회귀의 R² > 0.7 이면 cell-equivalent 한계 정량화 가능.
- 한계 cycle 권고가 **명확한 임계값 (예: 2,000 cycle)** 형태로 도출되면 KCI 게재 가치 충분.

---

## 8. 글쓰기 일정 (한글)

| 시점 | 작업 |
|---|---|
| T+5~6 | 자료 확보 + figure 산출 |
| T+6.0 | 본문 6~8쪽 한글 글쓰기 |
| T+6.5 | 한국산학기술학회 논문지 투고 |
| T+8~9 | revision |
| T+10~11 | 게재 (예상) |

---

## 9. 위험 & 대응

| 위험 | 대응 |
|---|---|
| 14개 셀 전압 분리 컬럼 인덱스 불일치 | Codex Task P0.0 정찰에서 `[004]~[017]AuxV(V)` 매핑 확정 |
| Pattern 분할 청크 merge 시 시점 불연속 | `algo.loaders.kier.merge_pattern_chunks` 단위 테스트 |
| σ trend 가 평탄 (가설 실패) | "cycle 3000 까지는 셀 밸런싱 안정" 결론으로 재포지셔닝 |

---

## 10. 다음 페이퍼 leverage

K2 게재 후 **SCI2 (Cross-Scale)** 의 cell-equivalent 시나리오 분석에서 "[K2] 결과에 따라 σ ≤ X mV 인 cycle 영역에서만 cell-equivalent 가정 적용" 으로 정당화 가능. Reviewer 가 "왜 평균 셀 가정?" 물으면 [K2] 인용 한 줄로 차단.
