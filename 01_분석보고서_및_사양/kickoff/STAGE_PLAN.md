# 단계별 작업 계획 (Stage Plan)

**원칙**: 한 번에 한 stage. 한 stage 안에서 Codex 와 Antigravity 가 병렬로 일할 수는 있지만, **stage 종료 시 사용자가 검토하고 다음 stage 진행 결정**.

---

## 5 Stages

| Stage | 기간 | 작업 | 산출 |
|---|---|---|---|
| **0** | ~1주 | **공통 기반** — 디렉터리, 환경, 데이터 카탈로그, OCV/ECM 룩업 | algo/ ui/ 골격, outputs/ocv_soc/, outputs/ecm/, catalog_kier_v0.csv |
| **1** | ~3주 | **KCI1 (분수계 ECM 식별)** | KCI1 브랜치 코드 + outputs/figures/K1_*/ + 한글 논문 초고 |
| **2** | ~6주 | **SCI1 (FOM-AEKF 본체)** + KCI2 분석 (병행) | SCI1 브랜치 코드 + KCI2 분석 + 두 결과 figure |
| **3** | ~3주 | **SCI2 (Cross-Scale)** | SCI2 브랜치 코드 + 모듈 cross-scale 결과 |
| **4** | ~5주 (stretch) | **SCI3 (Hybrid + UQ)** | SCI3 브랜치 코드 + NN/GPR 비교 + UQ 결과 |

---

## Stage 0 — 공통 기반 (지금 시작)

**목적**: 모든 후속 stage 의 전제 조건. main 브랜치에서 진행.

**Codex 작업** (algo/):
- 디렉터리 마이그레이션 (`data_io.py` → `algo/data_io.py` 등)
- Task P0.0 보조 데이터 포맷 정찰
- Task P0.1 `ocv_soc.py` 리팩터 + `compute_dqdv` 추가
- Task P0.2 OCV 룩업 3종 (25/50/0 °C) 추출
- Task P0.3 NCM chemistry 검증 (dQ/dV)
- Task P0.4 DCIR 1-RC 초기 파라미터 식별
- Task P0.5 `loaders/kier.py` 통합 카탈로그 (3 dataset)

**Antigravity 작업** (ui/):
- `pyproject.toml` 작성 + venv + smoke test
- `ui/` 골격 + 5개 페이지 빈 파일
- `Data Explorer` 페이지 (placeholder 카탈로그로 시작)
- (Codex P0.5 결과 도착 시) 실데이터 카탈로그 연결
- (Codex P0.2/P0.3/P0.4 결과 도착 시) `OCV/dQ-dV`, `ECM Fitting` 페이지 1차 시각화

**사용자 결정 포인트**: Stage 0 종료 시
- `outputs/ocv_soc/25C_cycle0_v0.csv` 가 진짜 운용범위 (3.0~4.2 V) 안에 들어가는가?
- dQ/dV 결과가 NCM 가정과 일치하는가?
- DCIR 1-RC R0 가 JH3 스펙 (1.03 ± 0.25 mΩ) 자릿수에 들어가는가?

위 셋이 통과되면 Stage 1 (KCI1) 진입.

---

## Stage 1 — KCI1 (T+2~3월 자료 확보 → T+3월 투고)

**Codex 작업** (KCI1 브랜치):
- `algo/ecm/fractional_ecm.py` (R + CPE 식별)
- `algo/runners/run_ecm_identify.py` 확장 — `--model FOM` 옵션
- 25/50 °C 각 cycle (100, 500, …, 3000) DCIR 에서 R0/R1/Q/α 식별
- 1-RC vs 2-RC vs 분수계 voltage 잔차 RMSE 비교
- α(cycle) trajectory 산출
- `outputs/figures/K1_fractional_ecm/` 6장 figure

**Antigravity 작업** (main 브랜치):
- `ECM Fitting` 페이지 분수계 옵션 추가
- KCI1 결과 시각화 (cycle별 α trend, voltage RMSE 비교)

**사용자**: KCI1 한글 논문 초고 작성 (Codex 가 만든 figure + table 활용).

---

## Stage 2 — SCI1 + KCI2 병행 (T+5~6월 투고)

**Codex 작업**:
- **SCI1 브랜치**: `algo/estimators/dual_aekf.py` (FOM-AEKF), `lstm_joint.py` baseline, 2D Q/R 스케줄러 학습, Split 1/2/3/5 벤치
- **KCI2 브랜치** (병행): `algo/analysis/cell_dispersion.py` 모듈 14 셀 unpack + σ 추적 + cell-equiv RMSE 영향

**Antigravity 작업**:
- `Estimator Run` 페이지에 FOM-AEKF 추가
- `Benchmark View` 페이지 SCI1 결과 박스플롯·trajectory 시각화
- KCI2 결과 (σ vs cycle, RMSE 영향) 별도 sheet

**사용자**: SCI1 영어 논문 + KCI2 한글 논문 초고 동시 작성.

---

## Stage 3 — SCI2 (T+8~9월 투고)

**Codex 작업** (SCI2 브랜치):
- `algo/runners/run_cross_scale.py` 신규
- SCI1 학습된 FOM-AEKF 를 `module CH1` 에 두 시나리오 (cell-equiv / module-direct) 로 적용
- KCI2 σ 결과와 회귀

**Antigravity 작업**:
- `Benchmark View` 에 cross-scale 결과 패널 추가

**사용자**: SCI2 영어 논문 초고.

---

## Stage 4 — SCI3 (stretch, T+12~14월)

**Codex 작업** (SCI3 브랜치):
- `algo/estimators/hybrid_nn_aekf.py` + `hybrid_gpr_aekf.py` 둘 다 prototype
- P4.1 (1주) 비교 후 우위 쪽 확장 + UQ
- ensemble or variational dropout, PICP/NLL 산출

**Antigravity 작업**:
- `Benchmark View` 에 UQ panel 추가 (calibration curve 등)

**사용자**: SCI3 영어 논문. 최악 시 P4 포기 → SCI 2 + KCI 2 = 4편 마무리.

---

## 단계 진행 규칙

1. 한 stage 완료 = 양 에이전트가 4줄 핸드오프 (분업 Spec §10) 보고
2. 사용자 검토 통과 시 다음 stage 킥오프 프롬프트 요청
3. 문제 발생 시 stage 안에서 fix-loop, **다음 stage 진입 금지**
4. 모든 코드는 본인 브랜치에 commit + push (Codex), main 의 UI 는 Antigravity 가 통합
