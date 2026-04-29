# [KCI1] 분수계 등가회로모델 식별 및 노화 추적 — 알고리즘 개발 전략

**Branch**: `KCI1`
**Paper**: NCM Pouch 셀의 분수계 등가회로모델 식별 및 노화 추적 (한글)
**Target Journal**: 한국산학기술학회 논문지 (1차) / 대한전기학회 논문지 (1차 대안)
**Submission**: T+3개월
**Status**: Plan

---

## 1. 연구 가설 (한 줄)

분수계 R+CPE 등가회로모델이 **정수 1-RC 모델 대비 단자전압 잔차 RMSE 가 유의하게 낮고**, CPE 차수 α 가 **사이클 진행에 따라 단조 변화하여 SOH 추정의 새 지표**가 될 수 있다.

---

## 2. 사용 데이터

**경로**: `D:\…\battery\data\셀 엑셀파일\셀 엑셀파일\`

| 채널 | 온도 | 자료 종류 | cycle 그리드 |
|---|---|---|---|
| ch2 | 25 °C | DCIR + DCIR 후 충전 | 100, 500, 1000, 1500, 2000, 2500, 3000 |
| ch7 | 50 °C | DCIR + DCIR 후 충전 | 100, 500, 1000, 1500, 2000, 2500, 3000, 3500 |

**파일 포맷**: PNE CSV (cp949, 콤마, 1 Hz). 단위 변환 mA→A, mAh→Ah, HMS→초.

**사전 조건**: `algo/data_io.py` 의 `read_cycler_file()` + `algo/loaders/kier.py` 의 `list_kier_files(dataset='main_cell', type=['DCIR','DCIR후충전'])` 가 동작해야 함.

---

## 3. 알고리즘 / 메소드

### 3.1 모델 정의

**정수 1-RC (baseline)**:
$$V(t) = OCV(SOC) - I \cdot R_0 - I R_1 (1 - e^{-t/\tau}), \quad \tau = R_1 C_1$$

**분수계 R + CPE (제안)**:
$$V(t) = OCV(SOC) - I \cdot R_0 - V_{CPE}(t)$$

여기서 CPE 임피던스: $Z_{CPE} = 1 / [(j\omega)^\alpha \cdot Q]$, $0 < \alpha \le 1$.

시간영역 응답: Mittag-Leffler 함수 $E_\alpha(\cdot)$ 로 표현되며, 본 연구는 **Grünwald-Letnikov 이산 근사** 또는 **Oustaloup 정수계 근사 (4~5차)** 로 구현.

### 3.2 식별 절차

1. DCIR 파일에서 **펄스 직전 휴지** (≥ 30 s) 의 마지막 전압 → OCV 추정.
2. 펄스 시작 직후 **순간 전압 강하** $\Delta V$ 와 펄스 전류 $I$ → $R_0 = \Delta V / I$ 초기 추정.
3. 펄스 + 후속 휴지 구간 데이터로 `scipy.optimize.least_squares` 잔차 최소화 → $(R_0, R_1, Q, \alpha)$ 동시 식별.
4. Bound: $R_0 \in [10^{-5}, 10^{-2}]$, $R_1 \in [10^{-5}, 10^{-2}]$, $Q \in [1, 10^5]$, $\alpha \in [0.5, 1.0]$.

### 3.3 노화 추적

- 위 식별을 cycle 100, 500, …, 3000 (또는 3500) 각각 반복.
- $R_0(\text{cycle})$, $\alpha(\text{cycle})$ trajectory 산출.
- 25 °C vs 50 °C 비교로 온도 의존성 분석.

---

## 4. 구현 모듈 (Codex 가 짤 .py)

```
algo/ecm/
├── ecm_identify.py         # 기존 (1-RC). identify_1rc 재사용
├── ecm_2rc.py              # 2-RC 식별 (확장)
└── fractional_ecm.py       # 신규 — identify_fractional()
```

**공개 API** (분업 Spec §3.2):
```python
def identify_fractional(file_path: str, nominal_capacity_ah: float = 63.0) -> dict:
    """
    Returns: {
        "model": "FOM",
        "R0": float, "R1": float, "C1_eq": float,  # CPE → equivalent C
        "alpha": float,                              # CPE 차수
        "rmse_V": float,
        "meta": {"file": str, "step": int, ...}
    }
    """
```

**Runner**:
```bash
python -m algo.runners.run_ecm_identify --model FOM \
    --files "셀 엑셀파일/.../CH2_25deg/DCIR/*.csv" \
    --out outputs/runs/K1-fractional-25C/
```

---

## 5. 실험 Protocol

| 항목 | 값 |
|---|---|
| 모델 비교 | 1-RC vs 2-RC vs 분수계 R+CPE 3종 |
| 식별 방법 | `scipy.optimize.least_squares`, TRF, max_nfev=2000 |
| 적합도 메트릭 | 단자전압 잔차 RMSE, 잔차 자기상관 |
| 노화 추적 메트릭 | $R_0(\text{cycle})$, $\alpha(\text{cycle})$ 단조성 (Spearman ρ), 정규화 민감도 |
| 온도 비교 | 25 °C vs 50 °C 동일 cycle 에서 파라미터 비교 |

---

## 6. 산출물

```
outputs/figures/K1_fractional_ecm/
├── fig1_pulse_fit_1rc_vs_fom.pdf       # 한 펄스에서 두 모델 fit 비교
├── fig2_rmse_vs_cycle_25C.pdf          # cycle별 voltage RMSE (1-RC vs FOM)
├── fig3_rmse_vs_cycle_50C.pdf
├── fig4_r0_alpha_trajectory_25C.pdf    # R0, α의 cycle 변화
├── fig5_r0_alpha_trajectory_50C.pdf
├── fig6_temperature_comparison.pdf     # 25 vs 50°C
└── captions.md

outputs/runs/K1-fractional-25C/
├── params_per_cycle.csv                # cycle, R0, R1, alpha, rmse_V
└── REPORT.md
```

---

## 7. 평가 기준 (acceptance)

- 분수계 모델의 평균 voltage RMSE 가 정수 1-RC 대비 **20% 이상 감소** 시 가설 입증.
- $\alpha(\text{cycle})$ 의 Spearman ρ 절댓값이 **0.7 이상** 이면 노화 지표로 유효.
- 온도 변화 (25→50 °C) 시 파라미터 변화 방향이 전기화학적 직관과 일치 (R0 ↓ 등).

---

## 8. 글쓰기 일정 (한글)

| 시점 | 작업 |
|---|---|
| T+2~3 | 자료 확보 + 모든 figure 산출 |
| T+3.0 | 본문 6~8쪽 한글 글쓰기 (서론·이론·실험·결과·결론) |
| T+3.5 | 한국산학기술학회 논문지 투고 |
| T+5~6 | reviewer 코멘트 대응, revision |
| T+7~8 | 게재 (예상) |

---

## 9. 위험 & 대응

| 위험 | 대응 |
|---|---|
| 분수계 식별 발산 | 정수 2-RC 결과를 fallback 으로 함께 보고 |
| α 노화 trend 약함 | $R_0$ trend 만으로 SOH 지표 보고하고 α는 부가 분석 |
| KCI 한국산학기술학회 reject | 대한전기학회 논문지 재시도. 한국 학회는 보통 reject 적음 |

---

## 10. 다음 페이퍼 leverage

K1 게재 후 **SCI1 의 Methods §3.1** 에서 "분수계 ECM 식별 자세한 절차는 [K1] 참조" 로 압축 가능. 자기 인용 풀 형성.
