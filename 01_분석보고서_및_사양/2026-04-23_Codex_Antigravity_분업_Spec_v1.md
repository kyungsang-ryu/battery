# Codex(알고리즘) ↔ Antigravity(GUI) 분업 인터페이스 사양서 v1

**작성일**: 2026-04-23
**상위 문서**:
- `2026-04-20_SOC_SOH_통합추정_Spec_v1.md` (Spec v1.1, JH3 셀 확정)
- `2026-04-20_M스코프_backend_design.md` (백엔드 공개 API 4개 정의)
- `2026-04-23_SCI논문_전략_v2.md` (논문 novelty·로드맵)

**목적**: 두 개의 코딩 에이전트(**Codex** = 알고리즘/시뮬레이션, **Antigravity(Gemini)** = GUI/시각화)가 동일 저장소를 공유하면서 **충돌 없이, 독립적으로, 그러나 매끄럽게 연동**되도록 책임 경계와 통신 규약을 못 박는다.

이 문서가 **계약(Contract)** 이다. Codex와 Antigravity 양쪽 에이전트는 작업 시작 전에 본 문서를 반드시 읽고, 본 문서의 규칙을 위반하는 변경은 **반드시 사용자 승인 후** 본 문서를 먼저 갱신한다.

---

## 1. 책임 경계 (Responsibility Matrix)

| 영역 | 담당 | 비고 |
|---|---|---|
| 데이터 I/O 레이어 (`data_io.py`) | Codex | UI는 read-only로 import |
| OCV–SOC, dQ/dV (`ocv_soc.py`, `chemistry_check.py`) | Codex | UI는 결과만 표시 |
| ECM 식별 (`ecm_identify.py`) | Codex | UI는 파라미터만 표시 |
| 추정기(`estimators/`): EKF, AEKF, Dual, PINN, TCN | Codex | UI는 모듈 import + 파라미터 dict 전달 |
| 시뮬레이션 러너(`runners/`) | Codex | CLI 진입점 + Python API 둘 다 |
| 평가/메트릭(`evaluation/`) | Codex | RMSE, MAE, MAX, PICP, NLL 표준 산출 |
| 데이터셋 로더(`loaders/`) — KIER, NASA, CALCE, MIT | Codex | 표준 DataFrame 스키마로 통일 |
| 논문용 그림(`figures/`) | Codex | matplotlib 정적 이미지 |
| GUI 메인 (`ui/data_analysis_ui.py`) | Antigravity | Streamlit 또는 PySide 권고 |
| GUI 위젯·플롯·테마 | Antigravity | plotly/altair 자유 |
| 사용자 입력 검증 | Antigravity | 잘못된 입력은 UI에서 차단 |
| 산출물 다운로드 UI | Antigravity | `outputs/`에서 파일 노출 |
| 파이썬 환경(`requirements.txt`, `pyproject.toml`) | **공유** — 변경은 항상 사용자 승인 | 충돌 잦은 영역 |
| `tests/` 전체 | **공유** — 본인 코드 변경 시 본인이 테스트 추가 | CI 게이트 |
| 본 문서·Spec·논문 초고 | **사용자 단독** | 양 에이전트는 제안만, 직접 수정 금지 |

**원칙 1 (단방향 의존)**: UI → 알고리즘은 OK. 알고리즘 → UI는 **금지**. 알고리즘 모듈은 `streamlit`, `plotly`, `tkinter` 등 UI 라이브러리를 import 해서는 안 된다.

**원칙 2 (헤드리스 가능)**: 모든 알고리즘 코드는 GUI 없이 CLI/Python 스크립트만으로 100% 재현 가능해야 한다. 논문용 실험은 항상 헤드리스로 돌린다.

**원칙 3 (UI는 얇게)**: GUI는 알고리즘의 결과를 **렌더링·인터랙션**만 담당. 알고리즘 로직(필터 식, OCV 보정, ECM 회귀)은 UI 코드 안에 절대 두지 않는다.

---

## 2. 디렉터리 분할 (Source Tree)

저장소 루트 = `D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data` (현 워크스페이스)

```
data/                                    ← 저장소 루트
├── algo/                                ← Codex 전용 ⭐
│   ├── __init__.py
│   ├── data_io.py                       (기존, 유지)
│   ├── loaders/
│   │   ├── kier.py                      (에기연 RPT/DCIR/Pattern 로더)
│   │   ├── nasa.py                      (NASA PCoE)
│   │   ├── calce.py
│   │   └── mit.py
│   ├── ocv/
│   │   ├── ocv_soc.py                   (compute_dqdv 포함, 리팩터)
│   │   └── chemistry_check.py
│   ├── ecm/
│   │   ├── ecm_identify.py              (1-RC, 2-RC)
│   │   └── fractional_ecm.py            (분수계 ECM, novelty)
│   ├── estimators/
│   │   ├── base.py                      (Estimator 추상 클래스)
│   │   ├── ah_counting.py
│   │   ├── ekf.py
│   │   ├── ukf.py
│   │   ├── dual_aekf.py                 (Stage 1)
│   │   ├── tcn_multitask.py             (Stage 2)
│   │   ├── pinn_joint.py                (Stage 3)
│   │   └── neural_aekf.py               (Stage 3 stretch)
│   ├── runners/
│   │   ├── run_ocv_extract.py
│   │   ├── run_chemistry_check.py
│   │   ├── run_ecm_identify.py
│   │   ├── run_simulation.py            (메인 시뮬레이션 진입점)
│   │   └── run_benchmark.py             (전 baseline 비교)
│   ├── evaluation/
│   │   ├── metrics.py                   (RMSE/MAE/MAX/PICP/NLL)
│   │   └── plots.py                     (논문용 정적 그림)
│   └── schemas.py                       (DataFrame/dict 스키마 정의)
│
├── ui/                                  ← Antigravity 전용 ⭐
│   ├── data_analysis_ui.py              (메인 진입점, 기존 위치에서 이동)
│   ├── pages/
│   │   ├── 01_data_explorer.py
│   │   ├── 02_ocv_dqdv.py
│   │   ├── 03_ecm_fitting.py
│   │   ├── 04_estimator_run.py
│   │   └── 05_benchmark_view.py
│   ├── widgets/                         (재사용 위젯)
│   └── theme/
│
├── outputs/                             ← 공유 (산출물) ⭐
│   ├── ocv_soc/
│   ├── ecm/
│   ├── runs/                            (각 시뮬레이션 결과: run_id 단위)
│   │   └── <run_id>/
│   │       ├── config.json              (입력 설정)
│   │       ├── results.parquet          (시계열 결과)
│   │       ├── metrics.json             (스칼라 평가지표)
│   │       └── log.txt
│   └── figures/                         (논문용 그림)
│
├── tests/                               ← 공유, 단 테스트 파일별 ownership
│   ├── algo/                            (Codex 책임)
│   └── ui/                              (Antigravity 책임)
│
├── 01_분석보고서_및_사양/               ← 사용자 + 양 에이전트 공동 (편집은 사용자만)
├── 02_실험_데이터/                      ← read-only
├── 03_매뉴얼_및_참고자료/               ← read-only
├── 99_상관없는_자료_및_기타/            ← 무시
│
├── pyproject.toml                       ← 공유 (변경 시 사용자 승인)
├── requirements.txt                     ← 공유 (변경 시 사용자 승인)
├── pytest.ini                           ← 공유
├── .gitignore                           ← 공유
└── README.md                            ← 사용자 단독
```

**마이그레이션 노트**: 현재 루트에 평탄하게 놓인 `data_io.py`, `ocv_soc.py`, `data_analysis_ui.py`, `tests/` 는 위 구조로 이동해야 한다. 이동은 **첫 작업 단일 PR로 일괄 처리**하고, 그 PR에서 import 경로 전체를 한 번에 수정한다 (이후 매번 부분 이동하면 충돌 폭발).

---

## 3. 공개 API 계약 (Algo → UI 단방향)

UI가 Codex 모듈을 import할 때 의존하는 표면. 이 계약은 **메이저 변경 시 반드시 본 문서 § 12 Changelog 갱신 + 사용자 승인**.

### 3.1 데이터 로딩

```python
from algo.data_io import read_cycler_file, read_excel_sheet, detect_format
from algo.loaders.kier import list_kier_files, load_kier_run
# load_kier_run(file_path) -> dict { "df": DataFrame, "meta": {"temp_C": float, "cycle": int, "type": str} }
```

### 3.2 분석 (이미 정의된 4개 + 신규 2개)

```python
# 기존 정의 유지 (Spec v1 §4 그대로)
from algo.ocv.ocv_soc        import extract_ocv_soc_from_rpt, compute_dqdv
from algo.ocv.chemistry_check import classify_chemistry
from algo.ecm.ecm_identify    import identify_1rc

# 신규 (v1)
from algo.ecm.ecm_identify    import identify_2rc          # 2-RC 옵션
from algo.ecm.fractional_ecm  import identify_fractional   # FOM 식별
```

### 3.3 추정기 — `Estimator` 추상 클래스 (핵심)

UI는 어떤 알고리즘이든 동일한 메서드만 호출한다. Codex는 새 추정기를 추가할 때 이 클래스를 상속한다.

```python
from algo.estimators.base import Estimator
# 시그니처:
#   class Estimator(ABC):
#       name: str
#       def __init__(self, config: dict): ...
#       def fit(self, train_runs: list[dict]) -> None: ...        # 학습/캘리브레이션 (Kalman은 noop)
#       def step(self, v: float, i: float, t: float, T: float)    # 단일 스텝
#           -> dict { "soc": float, "soh": float, "v_hat": float, "uncertainty": dict }
#       def run(self, df: pd.DataFrame) -> pd.DataFrame: ...      # 배치 실행
#           # 컬럼: soc_hat, soh_hat, v_hat, soc_std, soh_std (UQ 가능 시)
#       def to_config(self) -> dict: ...
#       @classmethod
#       def from_config(cls, cfg: dict) -> "Estimator": ...
```

UI는 다음 한 줄로 임의 알고리즘을 돌릴 수 있다:

```python
from algo.estimators import REGISTRY    # name → class 매핑
est = REGISTRY[user_choice].from_config(user_config)
result_df = est.run(input_df)
```

### 3.4 평가

```python
from algo.evaluation.metrics import (
    rmse, mae, max_abs_error, picp, nll,
    summarize_run,        # 한 run의 모든 메트릭을 dict로 반환
)
from algo.evaluation.plots import (
    plot_soc_trajectory, plot_soh_trend, plot_residual,
    save_paper_figure,
)
```

### 3.5 시뮬레이션 러너 (CLI + Python)

```bash
# CLI
python -m algo.runners.run_simulation --estimator dual_aekf --dataset kier_25C_1300cyc --out outputs/runs/exp001
python -m algo.runners.run_benchmark --estimators ekf,ukf,dual_aekf,tcn,pinn --dataset all --out outputs/runs/bench_v1
```

```python
# Python API (UI에서 직접 호출)
from algo.runners.run_simulation import run_simulation
run_id = run_simulation(estimator_name="dual_aekf", dataset_id="kier_25C_1300cyc", config=cfg)
# 반환: 산출물이 outputs/runs/<run_id>/ 에 저장된 경로
```

---

## 4. 데이터 교환 포맷 (양방향 무손실)

UI ↔ 알고리즘 사이를 오가는 **모든 객체**는 아래 5개 형태 중 하나여야 한다. 새로운 ad-hoc 자료구조 도입 금지.

### 4.1 시계열 DataFrame — `algo.schemas.TimeSeriesSchema`

**필수 컬럼** (소문자 snake_case 고정):

| 컬럼 | 단위 | 비고 |
|---|---|---|
| `time_s` | s | 0부터 시작 권장, 단조 증가 |
| `voltage` | V | 단자전압 |
| `current` | A | 방전 음수, 충전 양수 |
| `step` | int | 싸이클러 스텝 번호 |

**선택 컬럼**

| 컬럼 | 단위 |
|---|---|
| `temperature` | °C |
| `cycle` | int |
| `ah_cum` | Ah |

**추정 결과 추가 컬럼**

| 컬럼 | 단위 |
|---|---|
| `soc_hat`, `soc_std` | % |
| `soh_hat`, `soh_std` | % |
| `v_hat`, `v_residual` | V |

### 4.2 메타 dict — `RunMeta`

```python
{
    "run_id": "exp001-dual_aekf-kier_25C_1300cyc-2026-04-23T15:30",
    "estimator": "dual_aekf",
    "dataset_id": "kier_25C_1300cyc",
    "config": {...},               # 추정기 config 통째
    "data_files": [...],           # 입력 파일 절대경로 리스트
    "git_commit": "abc1234",       # 가능 시
    "started_at": "2026-04-23T...",
    "duration_s": 12.4,
    "env": {"python": "3.11.x", "torch": "2.x", ...},
}
```

### 4.3 메트릭 JSON — `MetricsReport`

```json
{
  "soc": {"rmse": 1.2, "mae": 0.9, "max_abs": 3.4, "picp_95": 0.94, "nll": ...},
  "soh": {"rmse": 0.5, "mae": 0.4, "max_abs": 1.2},
  "robustness": {"init_err_recovery_s": 12.3, ...},
  "compute": {"infer_per_step_us": 45, "memory_mb": 18}
}
```

### 4.4 OCV 룩업 CSV

`outputs/ocv_soc/<temp>C_<source>.csv`:

| 컬럼 | 비고 |
|---|---|
| `SOC_pct` | 0..100, 1% (또는 0.5%) 그리드 |
| `OCV_discharge_V`, `OCV_charge_V`, `OCV_avg_V` | NaN 허용 |

### 4.5 ECM 파라미터 JSON

`outputs/ecm/<source>_<temp>C.json`:

```json
{
  "model": "1RC" | "2RC" | "FOM",
  "R0": ..., "R1": ..., "C1": ..., "R2": ..., "C2": ...,
  "alpha": ...,                  // FOM 한정
  "rmse_V": ..., "meta": {...}
}
```

**금지 사항**: pickle, joblib 등 Python-specific 직렬화 포맷은 UI ↔ algo 인터페이스에서 사용 금지. 모델 가중치(`.pt`) 같은 algo-내부 자산은 OK.

---

## 5. 동시 편집 충돌 방지 (File Ownership)

같은 파일을 두 에이전트가 같은 세션에 만지면 머지 지옥이다. 다음 규칙을 강제한다.

### 5.1 Ownership 매트릭스

| 경로 패턴 | 소유자 | 다른 쪽이 만져도 되는가 |
|---|---|---|
| `algo/**/*.py` | Codex | NO (UI는 import만) |
| `ui/**/*.py` | Antigravity | NO (Codex는 호출 시그니처만 본다) |
| `tests/algo/*` | Codex | NO |
| `tests/ui/*` | Antigravity | NO |
| `outputs/**` | 둘 다 쓰기 가능 | YES — 단 `run_id`로 디렉터리 분리 필수 |
| `01_분석보고서_및_사양/*` | 사용자 | NO (양 에이전트는 새 .md 추가만 OK) |
| `pyproject.toml`, `requirements.txt` | 공유 | YES — 단 변경 전 사용자 승인 필수 |

### 5.2 Lock 파일 (선택)

장기 작업 시 같은 파일을 동시에 만질 우려가 있으면, 작업 시작 전에 `.locks/<path>.lock` 빈 파일을 만들고 끝나면 지운다. (간이 mutex.) 양 에이전트가 시작 전에 lock 존재 여부를 확인.

### 5.3 일일 체크인

매일 작업 시작 시:
1. 반대 에이전트가 어제 무엇을 바꿨는지 `git log --since=yesterday` 확인.
2. 본인이 의존하는 공개 API에 변경이 있었는지 확인.
3. 본 문서 §3 계약과 실제 시그니처가 일치하는지 grep.

---

## 6. 통신 방식 (Process Boundary)

### 6.1 기본: **In-process import** (Streamlit/PySide 모두 동일 파이썬 프로세스)

UI가 `from algo... import ...` 로 직접 호출. 장점: 단순, 빠름. 단점: UI가 알고리즘 dependency를 모두 끌어안아야 함.

### 6.2 백업: **Subprocess + 파일 교환** (대형 시뮬레이션 시)

오래 걸리는 시뮬레이션은 UI에서 `subprocess.Popen("python -m algo.runners.run_simulation ...")`로 띄우고, UI는 `outputs/runs/<run_id>/` 폴더를 watch. 장점: UI 멈춤 없음. 단점: 진행률 통신 별도 필요.

진행률 파일 규약: `outputs/runs/<run_id>/progress.json` — `{"pct": 0.42, "stage": "filtering", "msg": "..."}` 를 1초마다 갱신, UI는 파일 mtime 폴링.

### 6.3 (선택) FastAPI 서버

논문 단계에선 불필요. 향후 웹 데모 만들 때만 도입.

---

## 7. 환경 부트스트랩 (Antigravity가 자동 셋업)

본 사양에 따라 Antigravity가 다음 순서로 환경을 만든다 (사용자가 명시 요청).

### 7.1 `pyproject.toml` (권장)

```toml
[project]
name = "battery-soc-soh"
version = "0.1.0"
requires-python = ">=3.11,<3.13"

dependencies = [
  "numpy>=1.26", "scipy>=1.12", "pandas>=2.2", "pyarrow>=15",
  "matplotlib>=3.8", "filterpy>=1.4.5",
  "scikit-learn>=1.4", "torch>=2.3",
  "openpyxl>=3.1",
]

[project.optional-dependencies]
ui  = ["streamlit>=1.32", "plotly>=5.20", "altair>=5"]
dev = ["pytest>=8", "ruff>=0.4", "mypy>=1.10"]
paper = ["seaborn>=0.13", "scienceplots>=2.1"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 7.2 가상환경 절차 (Antigravity 자동 실행 권장)

```bash
python -m venv .venv
.venv\Scripts\activate                       # Windows
pip install -U pip
pip install -e ".[ui,dev,paper]"
python -m pytest tests/algo -q               # 알고리즘 테스트 부트 확인
streamlit run ui/data_analysis_ui.py         # GUI 부트 확인
```

### 7.3 `.gitignore` 권장

```
.venv/
__pycache__/
*.pyc
outputs/runs/        # 시뮬 결과는 git에 안 올림 (대용량)
outputs/figures/     # 논문 그림은 별도 release 폴더
.locks/
~$*
```

---

## 8. 테스트·CI 게이트

### 8.1 테스트 책임

| 영역 | 누가 작성 | 어디에 |
|---|---|---|
| 단위 테스트 (algo) | Codex | `tests/algo/` |
| 단위 테스트 (UI 위젯·헬퍼) | Antigravity | `tests/ui/` |
| 통합 테스트 (Estimator 인터페이스) | Codex | `tests/algo/test_estimator_contract.py` |
| End-to-end (UI에서 algo 호출) | Antigravity | `tests/ui/test_e2e_run.py` |

### 8.2 게이트

- 모든 PR은 `pytest tests/ -q` 통과해야 머지.
- Codex가 `Estimator` 추상 클래스를 변경하면 `test_estimator_contract.py` 가 자동으로 모든 등록된 추정기를 검증한다 (subclass enforcement).
- UI 변경은 `streamlit run --headless` smoke test 권장.

---

## 9. 산출물(`outputs/`) 라이프사이클

- **runs/<run_id>/**: 한 시뮬레이션 = 한 폴더. **절대 덮어쓰지 않음**. 기본 ID 포맷: `<exp_tag>-<estimator>-<dataset>-<ISO8601>` (예: `bench-dual_aekf-kier_25C_1300cyc-2026-04-23T15-30`).
- **ocv_soc/**, **ecm/**: 버전 suffix `_v0`, `_v1` 사용. 정본은 항상 `_latest.csv` 심볼릭 링크 또는 README에 명시.
- **figures/**: 논문 그림. 파일명에 fig 번호 + section 표시 (`fig3_benchmark_rmse.pdf`).
- **자동 청소 금지**: 양 에이전트는 outputs를 자동 삭제하지 않는다. 사용자 승인 후 수동 정리.

---

## 10. 핸드오프 프로토콜 (한 작업 단위 종료 시)

본인 작업이 끝나면 다음 4개를 반드시 채운다.

1. **변경 요약** (3줄 이내) — 무엇을, 왜, 어디를.
2. **공개 API 영향** — § 3 계약에 변경이 있는가? 있으면 본 문서 갱신 + 사용자 승인 받기.
3. **테스트 결과** — `pytest` 출력 마지막 5줄.
4. **다음 에이전트 액션 후보** — "UI는 이제 새 함수 X를 사용 가능", "이 파라미터는 UI에서 슬라이더 노출 권장" 등.

이 4줄을 PR description 또는 사용자 응답 끝에 적는다.

---

## 11. 충돌·실패 시나리오 가이드

| 상황 | 대응 |
|---|---|
| UI가 import하는 함수가 사라짐 | Codex 책임. 즉시 deprecation shim 추가, 본 문서 §3 갱신, 사용자 알림 |
| `pyproject.toml` 의존성 충돌 | 변경자가 commit 전 `pip install -e ".[ui,dev]"` 클린 가상환경에서 검증 |
| `outputs/runs/` 폴더 사이즈 폭발 | 사용자에게 청소 제안. 자동 삭제는 절대 금지 |
| 같은 파일에 동시 편집 발생 | 늦게 시작한 쪽이 양보. 변경 사항을 패치로 떨궈두고 머지 후 재적용 |
| 에이전트가 다른 영역의 파일을 만지려는 충동이 듦 | **하지 말 것**. 사용자에게 위임 또는 본 문서를 먼저 갱신 |
| 알고리즘이 UI에서만 의미있는 옵션을 추가하려 함 | 알고리즘에는 일반 옵션으로 노출, UI가 사용자 친화 라벨로 wrapping |

---

## 12. Changelog

- **2026-04-23 v1** (초판)
  - Codex/Antigravity 분업 구도 명시 (사용자 결정)
  - 디렉터리 구조 `algo/` ↔ `ui/` 로 분할 제안
  - `Estimator` 추상 클래스 도입 — 모든 추정기의 통일 인터페이스
  - 데이터 교환 포맷 5종 표준화 (TimeSeries, RunMeta, MetricsReport, OCV CSV, ECM JSON)
  - 산출물 디렉터리 정책 (`outputs/runs/<run_id>/`) 확정
  - 환경 부트스트랩 권고안 명시 (`pyproject.toml`, venv, smoke test)
