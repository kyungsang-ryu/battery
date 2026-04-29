# NCM Pouch 셀·모듈 SOC/SOH 통합 추정 — Multi-Paper 연구

**Repo**: https://github.com/kyungsang-ryu/battery
**Author**: Kyungsang Ryu (RYU)
**Status**: 연구·개발 진행 중 (T+0, 2026-04-23 시작)
**상위 전략 문서**: `2026-04-23_Multi_Paper_전략_v3.md` (로컬 워크스페이스)

---

## 한 줄 요약

NCM Pouch 셀과 14S 모듈에서 **SOC와 SOH를 동시에 추정하는 알고리즘 (FOM-AEKF)** 을 개발하고, 그 결과를 **국내 KCI 2편 + 국제 SCI 3편 = 총 5편 논문**으로 산출한다.

---

## 5편 매트릭스

| # | 등급 | 브랜치 | 제목 (가제) | 핵심 contribution | 타깃 저널 | 투고 시점 |
|---|---|---|---|---|---|---|
| K1 | KCI | `KCI1` | NCM Pouch 셀의 분수계 등가회로모델 식별 및 노화 추적 (한글) | 분수계 R+CPE 식별 + α 노화 추적성 | 한국산학기술학회 / 대한전기학회 | T+3 |
| K2 | KCI | `KCI2` | 14S 모듈 내 셀간 전압편차 분석 및 SOC 추정 영향 (한글) | 셀간 σ가 SOC 정확도에 미치는 정량 영향 | 한국산학기술학회 / 대한전기학회 | T+6 |
| S1 | SCI | `SCI1` | FOM-AEKF: Joint SOC/SOH for NCM Pouch Cells | 분수계 ECM × Dual AEKF × 2D Q/R lookup | J. Energy Storage IF 8~9 / IEEE TTE | T+5~6 |
| S2 | SCI | `SCI2` | Cross-Scale Generalization: Cell → 14S Module | 셀 학습 알고리즘의 모듈 적용 + 셀간 편차 영향 | IEEE TTE IF 7 / J. Power Sources IF 8 | T+8~9 |
| S3 | SCI | `SCI3` | Hybrid Physics-Data Estimator with Calibrated UQ | FOM-AEKF + NN/GPR + PICP/NLL | Applied Energy IF 11 / eTransportation IF 13 | T+14 |

자료 확보 ~14개월 / 게재 ~24개월. 자세한 leverage 흐름·fallback 전략은 로컬 v3 문서 참조.

---

## 브랜치 구조

```
main         ← 통합 진척 + Antigravity GUI + 5편 시뮬레이션 결과 종합
├── KCI1     ← K1 분수계 ECM 식별 (한글)
├── KCI2     ← K2 모듈 셀간 전압편차 분석 (한글)
├── SCI1     ← S1 FOM-AEKF 본체 (영어)
├── SCI2     ← S2 Cross-Scale 일반화 (영어)
└── SCI3     ← S3 Hybrid + UQ (영어, 도전)
```

각 브랜치 루트에 `strategy.md` — 해당 paper 의 알고리즘 개발 전략·구현 모듈·평가 protocol·산출물 명세.

---

## 데이터 (로컬, push 안 됨)

용량·저작권 이유로 raw 데이터는 repo 에 포함하지 않음. 로컬 경로:

```
D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data\
├── 셀 엑셀파일\셀 엑셀파일\           ← Pouch 셀 (CH2/25°C, CH7/50°C, ch3/0°C)
├── 02_실험_데이터\pouch_SOH\          ← 다채널 ch1~ch8, MG/PVS/PQ 패턴
└── 모듈엑셀파일\모듈엑셀파일\…\CH1\   ← 14S 모듈
```

전부 NCM Pouch (사용자 확정). 18650/Cell 데이터★★★★★ 폴더는 본 논문 제외.

---

## 코드 디렉터리 (예정)

```
algo/                ← Codex 작업 영역
├── data_io.py
├── loaders/         ← KIER 카탈로그
├── ocv/             ← OCV 룩업, dQ/dV
├── ecm/             ← 1-RC, 2-RC, fractional ECM
├── estimators/      ← Estimator 추상 + baseline + FOM-AEKF + Hybrid
├── runners/         ← run_simulation, run_benchmark
├── evaluation/      ← metrics, plots, tables
└── schemas.py

ui/                  ← Antigravity 작업 영역
├── data_analysis_ui.py
├── pages/
└── widgets/

outputs/             ← 산출물 (figures, runs, ocv_soc, ecm)
tests/
```

---

## main 브랜치 — Antigravity 종합 GUI + 시뮬레이션 결과 통합

**main 의 역할**: 5개 브랜치에서 만들어진 알고리즘들을 **Antigravity (Gemini) 가 통합 GUI 로 시각화**하고, **5편 시뮬레이션 결과를 한 화면에서 비교** 가능하게 한다.

**Antigravity 가 main 에서 만들 5개 페이지** (분업 Spec 2026-04-23 §10.2 + Antigravity_TODO_v1):

1. **Data Explorer** — Pouch 셀·모듈 카탈로그 브라우징, 시계열 플롯
2. **OCV / dQ/dV** — OCV 룩업·dQ/dV·NCM chemistry 검증
3. **ECM Fitting** — 1-RC / 2-RC / 분수계 ECM 회귀 결과 비교 (K1 결과 시각화 포함)
4. **Estimator Run** — 추정기 선택 + 파라미터 슬라이더 + 실행 + 결과 플롯
5. **Benchmark View** — 5편 결과 통합 비교
   - SCI1 (FOM-AEKF vs 7 baseline)
   - SCI2 (cell → module cross-scale)
   - SCI3 (Hybrid + UQ)
   - K1 / K2 분석 결과
   - 페이퍼별 Figure 그리드 + 다운로드

**시뮬레이션 결과 종합 디렉터리** (`outputs/runs/`):

```
outputs/runs/
├── bench-baseline-v1/      ← Baseline 7+1종 (SCI1)
├── bench-stageA-v1/        ← FOM-AEKF (SCI1)
├── bench-extrap-aging/     ← Split 1 (SCI1)
├── bench-extrap-temp/      ← Split 2 (SCI1)
├── bench-cross-pattern/    ← Split 5 (SCI1)
├── bench-cross-scale/      ← Split 6 (SCI2)
├── bench-hybrid-nn/        ← S3 NN variant
├── bench-hybrid-gpr/       ← S3 GPR variant
└── bench-final-v1/         ← 전 paper 종합
```

각 폴더에 `config.json`, `results.parquet`, `metrics.json`, `REPORT.md`. Antigravity Benchmark View 는 이 폴더들을 자동 스캔해 **5편별 sheet 로 분리 표시**.

**논문별 figure 디렉터리**:

```
outputs/figures/
├── K1_fractional_ecm/
├── K2_module_voltage_dev/
├── S1_fom_aekf/
├── S2_cross_scale/
└── S3_hybrid_uq/
```

각 페이퍼 글쓰기 단계에서 해당 폴더만 가져가면 된다.

---

## 빠른 시작 (개발자용)

```powershell
git clone https://github.com/kyungsang-ryu/battery.git
cd battery
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[ui,dev]"
python -m pytest tests/ -q
streamlit run ui/data_analysis_ui.py
```

(`pyproject.toml` 은 Antigravity 가 첫 작업으로 작성 — Antigravity_TODO_v1 §1 참조.)

---

## 진행 상황 (2026-04-23 기준)

- [x] 데이터 카탈로그 정밀 조사 완료 (Pouch 셀·모듈 일관 확정)
- [x] Spec v1.1 → v3 까지 5편 multi-paper 전략 확정
- [x] Codex / Antigravity 분업 사양서 v1.3 완료
- [ ] Codex Day 1 액션 — `algo/` 디렉터리 마이그레이션 + OCV 추출
- [ ] Antigravity Day 1 액션 — `pyproject.toml` + venv + `ui/` 골격
- [ ] K1 자료 확보 (P2.1 분수계 ECM 식별 후) — T+2~3
- [ ] S1 자료 확보 (P2.2 Dual AEKF + 2D Q/R 후) — T+5
- [ ] K2 자료 확보 (P3 모듈 분석 후) — T+5~6
- [ ] S2 자료 확보 (P3.3 Cross-Scale 후) — T+6~7
- [ ] S3 자료 확보 (P4 Hybrid + UQ 후, stretch) — T+12~13

---

## 라이선스 / 인용

연구용. 인용·이슈는 https://github.com/kyungsang-ryu/battery/issues 로.
