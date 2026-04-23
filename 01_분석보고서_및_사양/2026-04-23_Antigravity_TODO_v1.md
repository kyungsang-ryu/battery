# Antigravity (GUI) 작업 사양서 v1

**작성일**: 2026-04-23
**대상**: Antigravity (Gemini 기반 GUI/시각화 담당 코딩 에이전트)
**상위 문서**:
- `2026-04-23_Codex_Antigravity_분업_Spec_v1.md` (책임 경계·인터페이스 계약)
- `2026-04-23_SCI논문_전략_v2.md` (논문 novelty·로드맵)
- `2026-04-23_Codex_TODO_v1.md` (반대편 에이전트 작업 목록 — 의존성 파악용)
- `2026-04-20_SOC_SOH_통합추정_Spec_v1.md` (셀 사양·전체 사양)

**노선 결정 (사용자 2026-04-23)**: 미드티어 SCI 허용. GUI는 **연구 보조 도구**로서 데이터 탐색·결과 시각화·산출물 다운로드를 담당. 화려할 필요 없고 안정·생산성 우선.

**셀 chemistry**: **NCM** (사용자 확정 2026-04-23, NMC와 동일 물질의 한국식 표기). UI 라벨·툴팁·뱃지 등에 표기 시 **NCM** 으로 통일.

**데이터 스코프 (사용자 확정 2026-04-23)**: **Pouch 폼팩터 일관성**. 두 축으로 구성.
- **셀 단위 (Pouch)**: main_cell (ch2/25 °C, ch7/50 °C, ch3/0 °C 부분) + pouch_SOH (25/40 °C, ch1~ch8, MG/PVSmoothing/PowerQuality 패턴, weeks 단위 노화).
- **모듈 단위 (Pouch)**: module CH1 (25 °C, cycle 단위, 14S 셀, Pattern 분할 파일 포함).

18650_SOH는 폼팩터 차이로 본 논문 제외. UI 필터·페이지·시각화는 이 두 축만 노출.

---

## 0. 시작 전 필독

본 문서를 작업 시작 시 매번 다시 읽는다. 분업 Spec(2026-04-23)을 위반하는 변경이 필요하면 **반드시 사용자 승인 후 분업 Spec을 먼저 갱신**한다.

**핵심 원칙 재고지**

- `ui/` 만 만진다. `algo/` 절대 금지 (import만 OK).
- 알고리즘 로직(필터 식, OCV 보정, ECM 회귀, 학습 루프 등)을 UI 코드 안에 두지 않는다 — 항상 `algo.*` 함수를 호출한다.
- 모든 사용자 입력은 UI에서 검증한 뒤 `algo`로 전달.
- 무거운 시뮬레이션은 subprocess로 띄우고 진행률은 파일 폴링으로 받는다 (분업 Spec §6.2).

---

## 1. P0.A — 환경·디렉터리 부트스트랩 (1~2일)

### Task A0.1 — `pyproject.toml` 작성

분업 Spec §7.1을 그대로 반영. 한 번에 작성:

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
paper = ["seaborn>=0.13"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["algo*", "ui*"]
```

기존 `requirements.txt` 가 있으면 보존(레거시), 본 `pyproject.toml`을 정본으로.

### Task A0.2 — 가상환경 셋업 + smoke test

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install -e ".[ui,dev,paper]"
python -m pytest tests/algo -q              # 기존 알고 테스트 통과 확인
python -c "import streamlit, plotly, altair; print('ui ok')"
```

문제가 있으면:
- 한국어 폴더명(`유경상`)으로 인한 path encoding 이슈 → venv 활성화 후 `python -X utf8` 모드 또는 `PYTHONUTF8=1` 환경변수 권장.
- torch가 무겁다면 `torch>=2.3` 대신 CPU-only wheel을 명시적으로 설치 후 진행.

### Task A0.3 — 디렉터리 마이그레이션 협조

Codex가 Task P0 첫 작업으로 디렉터리 분할을 진행한다(`Codex_TODO_v1.md` §2). Antigravity는:

- 같은 시간대에 `ui/` 영역에 빈 패키지 골격만 만들고, `algo/` 쪽은 **건드리지 않는다**.
- Codex가 마이그레이션 PR을 머지한 직후, 기존 `data_analysis_ui.py`가 새 import 경로(`from algo... import ...`)로 잘 동작하는지 확인 후 `ui/data_analysis_ui.py`로 이동.

### Task A0.4 — `ui/` 골격 생성

```
ui/
├── __init__.py
├── data_analysis_ui.py            (메인 진입점, 페이지 router 또는 Streamlit Multipage)
├── pages/
│   ├── 01_📂_Data_Explorer.py
│   ├── 02_📈_OCV_dQdV.py
│   ├── 03_⚙️_ECM_Fitting.py
│   ├── 04_🔬_Estimator_Run.py
│   └── 05_📊_Benchmark_View.py
├── widgets/
│   ├── __init__.py
│   ├── catalog_filter.py          (channel/temp/cycle 필터 위젯)
│   ├── plot_helpers.py            (plotly figure factory)
│   └── result_loader.py           (outputs/runs/<run_id>/ 로드 헬퍼)
└── theme/
    └── plot_template.py           (plotly template + 색상 팔레트)
```

빈 파일이라도 만들어 두고, 이후 페이지별로 채워나간다.

### Task A0.5 — Smoke test 작성

`tests/ui/test_imports.py`:
- `from ui.data_analysis_ui import main` 임포트 성공 확인.
- 각 page 모듈 import만 (Streamlit 런타임 없이) 성공 확인.

`tests/ui/test_e2e_run.py` (P1.A 이후 작성):
- subprocess로 `streamlit run ... --server.headless=true --browser.serverAddress=localhost --server.port=18501` 띄우고 1초 후 health 체크 → 종료.

---

## 2. P1.A — Data Explorer 페이지 (3일)

### Task A1.1 — `01_📂_Data_Explorer.py`

**의존**: Codex의 `algo.loaders.kier.list_kier_files()` (Task P0.5 결과). 이 함수가 만들어지기 전에는 placeholder 카탈로그(빈 DataFrame)로 작업.

**기능**:

1. 페이지 상단: 카탈로그 갱신 버튼 (`outputs/catalog_kier_v0.csv` 다시 읽기).
2. 사이드바 필터 (실측 그리드 기준, Pouch 일관성):
   - **dataset**: `main_cell` / `pouch_soh` / `module` (multi-select). 18650_SOH는 본 논문 제외 — 노출하지 않음.
   - **channel**: 카탈로그에 등장하는 채널을 동적으로 (메인은 ch2/ch3/ch7, pouch는 ch1~ch8, 모듈은 CH1)
   - **temp_C**: `0` / `5` / `10` / `15` / `25` / `40` / `50` (multi-select. 5/10/15는 전압하한 Pattern 전용, 40은 pouch_SOH 전용)
   - **type**: `RPT` / `DCIR` / `DCIR후충전` / `ACIR` / `Pattern` / `Pattern_MG` / `Pattern_PVSmoothing` / `Pattern_PowerQuality` / `capacity_check`
   - **cycle range**: slider — main_cell, cell_18650, module 전용. dataset 따라 max 다름 (main_cell ch7는 3800까지). pouch_SOH 선택 시 비활성.
   - **weeks range**: slider — pouch_SOH 전용 (5~30 weeks). 다른 dataset 선택 시 비활성.
   - **date range**: optional

   ⚠️ cycle 과 weeks 는 **상호 배타 컬럼** (사용자 결정 2026-04-23). 한 슬라이더로 묶지 말고 dataset 선택에 따라 자동 토글.
3. 본문 좌측: 필터링된 파일 테이블 (`st.dataframe`). 컬럼에 `n_chunks`(모듈 Pattern 분할 청크 수) 표시.
4. 본문 우측: 사용자가 한 행을 선택하면 `algo.loaders.kier.load_kier_run(file_path, merge_chunks=True)` 호출 → `voltage`, `current`, `temperature` 시계열 plotly 플롯. 분할 파일은 자동 merge되어 한 시계열로 보여짐.
5. 다운로드: 선택한 파일의 정규화된 (또는 merge된) DataFrame을 CSV로.
6. 우상단 카드: 현재 카탈로그 통계 — dataset별 파일 수, (temp × type) 매트릭스 미니히트맵.

**금지**: 카탈로그 정규식 파싱·시계열 정규화·분할 파일 merge는 직접 하지 말고 반드시 `algo` 함수 호출.

### Task A1.2 — `widgets/catalog_filter.py`

```python
import streamlit as st
import pandas as pd

def render_catalog_filter(catalog: pd.DataFrame) -> pd.DataFrame:
    """사이드바에 필터 위젯을 렌더하고, 필터링된 catalog를 반환."""
    ...
```

다른 페이지에서도 재사용.

### Task A1.3 — `widgets/plot_helpers.py`

`make_voltage_current_figure(df)`, `make_temperature_figure(df)`, `make_step_overlay(df, step_filter=None)` 등의 plotly Figure 팩토리.

### Task A1.4 — 페이지 단위 테스트

`tests/ui/test_data_explorer.py`:
- 카탈로그 mock으로 필터 함수가 의도된 행 개수를 반환하는지.
- plotly Figure 생성이 에러 없이 완료되는지 (브라우저 렌더 테스트는 skip).

---

## 3. P1.B — OCV / dQ/dV 페이지 (2일)

### Task A1.5 — `02_📈_OCV_dQdV.py`

**의존**: Codex Task P0.1 (`algo.ocv.ocv_soc.extract_ocv_soc_from_rpt`, `compute_dqdv`), P0.3 (`algo.ocv.chemistry_check.classify_chemistry`), P0.2 산출물(`outputs/ocv_soc/25C_cycle0_v0.csv` 등).

**기능**:

1. 두 가지 모드 선택: ① "기존 산출물 보기" (`outputs/ocv_soc/*.csv`, `*.png`), ② "새 RPT 파일에서 추출".
2. 모드 ② 선택 시:
   - 사용자가 카탈로그에서 RPT 1개 선택.
   - "OCV 추출" 버튼 → `extract_ocv_soc_from_rpt()` 호출 → 방전·충전·평균 SOC-OCV plotly 플롯.
   - "dQ/dV 보기" 버튼 → `compute_dqdv()` 호출 → V vs dQ/dV plotly + 피크 마커.
   - "Chemistry 검증" 버튼 → `classify_chemistry()` 결과를 카드 UI(label, confidence, reason)로 표시. **사용자 확정값 = NCM**. Codex 분류 결과가 NMC/NCM 계열이 아니면 ⚠️ 경고 배지("사용자 확정 NCM과 불일치, 데이터 또는 휴리스틱 점검 필요").
3. "이 결과를 outputs/ocv_soc/에 저장" 버튼 (옵션) — Codex의 산출 디렉터리 규칙 준수, 사용자 정의 suffix 입력받음.

---

## 4. P1.C — ECM Fitting 페이지 (2일)

### Task A1.6 — `03_⚙️_ECM_Fitting.py`

**의존**: Codex Task P0.4 (`algo.ecm.ecm_identify.identify_1rc`), P2.1 (`identify_2rc`, `identify_fractional`).

**기능**:

1. 모델 선택: Radio (`1-RC`, `2-RC`, `Fractional`).
2. DCIR 파일 선택 (카탈로그 위젯 재사용, type=`DCIR` 강제 필터).
3. "Fit" 버튼 → 해당 `identify_*` 함수 호출 → 파라미터 카드(R0, R1, C1, [α], RMSE) + 단자전압 측정/예측 비교 플롯.
4. "JH3 스펙과 비교" 토글 → R0가 1.03 ± 0.25 mΩ 범위에 들어가면 ✅, 벗어나면 ⚠️ 표기.
5. 결과 JSON 다운로드 버튼.

---

## 5. P1.D — Estimator Run 페이지 (4일)

분업 Spec §3.3 `Estimator` 인터페이스 활용의 **핵심 페이지**.

### Task A1.7 — `04_🔬_Estimator_Run.py`

**의존**: Codex Task P1.1 (`algo.estimators.REGISTRY`), P1.3 (`algo.runners.run_simulation`), P0.5 (catalog).

**기능**:

1. **추정기 선택**: `REGISTRY.keys()`를 `st.selectbox`로 노출. 옵션 예: `ah_counting`, `ocv_lookup`, `ekf`, `ukf`, `dual_ekf`, `dual_ukf`, `dual_aekf`(P2 후), `pinn_aekf`(P4 후).
2. **데이터 선택**: 카탈로그 필터로 RPT 또는 Pattern 1개 선택.
3. **Config 슬라이더 자동 생성**: 선택한 추정기의 `config` schema를 introspection (`Estimator.from_config({}).to_config()` + 타입 힌트). 프리셋 3종(`default`, `aggressive`, `conservative`)도 제공.
4. **Run 버튼** → 두 가지 모드:
   - **In-process** (작은 파일, < 50 MB): `est = REGISTRY[name].from_config(cfg); result = est.run(df)`. UI 진행 표시는 spinner로.
   - **Subprocess** (큰 파일 또는 사용자가 토글): `subprocess.Popen("python -m algo.runners.run_simulation ...")`. 진행률은 `outputs/runs/<run_id>/progress.json` 파일 폴링.
5. **결과 시각화 패널**:
   - SOC trajectory (true vs hat ± std band).
   - SOH trend.
   - 단자전압 잔차 히스토그램.
   - 메트릭 카드 (RMSE, MAE, MAX, PICP_95).
6. **결과 영구 저장**: 자동으로 `outputs/runs/<run_id>/`에 저장됨. 사용자에게 `run_id` 표시 + 다음 페이지(Benchmark View)로의 링크.

### Task A1.8 — Subprocess 진행률 폴링 헬퍼

`widgets/result_loader.py`에:

```python
def poll_progress(run_id: str, timeout_s: int = 600) -> Iterator[dict]:
    """outputs/runs/<run_id>/progress.json 파일을 mtime 변화 시 yield."""
    ...

def load_run(run_id: str) -> dict:
    """results.parquet, metrics.json, config.json 한 번에 로드."""
    ...
```

UI는 `st.empty()` + 폴링으로 진행률·로그를 흘려보낸다.

---

## 6. P1.E — Benchmark View 페이지 (3일)

### Task A1.9 — `05_📊_Benchmark_View.py`

**의존**: Codex Task P1.5 (`run_benchmark`), P2.4 (Stage A 벤치), P3.2 (외삽).

**기능**:

1. 좌측 사이드바: 벤치마크 폴더 선택 (`outputs/runs/bench-*/` 글롭).
2. 메인:
   - 추정기별 RMSE 박스플롯 (SOC / SOH 각각).
   - 조건별(=temperature × cycle) 히트맵.
   - 외삽 결과 폴더(`bench-extrap*`)면 "학습 영역 vs 외삽 영역" 비교 그래프.
   - 메트릭 표 (`summary.csv` raw view + 정렬).
3. **자동 리포트**: Codex가 만들어둔 `outputs/runs/<bench>/REPORT.md`가 있으면 그대로 렌더 + 다운로드.
4. **논문 그림 미리보기**: `outputs/figures/*.pdf|png`를 그리드로 표시 + 다운로드.

---

## 7. P2.A — 결과 검증·발표 보조 도구 (선택, P2 이후)

### Task A2.1 — Adaptive Q/R 스케줄 시각화

Codex의 P2.3 산출물(`outputs/figures/qr_schedule_heatmap.png` + 학습 룩업 데이터)을 받아서:
- 인터랙티브 plotly heatmap (T × cycle 평면, hover 시 Q/R 값).
- 사용자가 (T, SOH)를 슬라이더로 움직이며 Q/R이 어떻게 변하는지 미리보기.

### Task A2.2 — 논문 그림 큐레이션 페이지

`06_🎨_Paper_Figures.py`:
- `outputs/figures/`의 모든 그림을 카드 그리드로.
- 캡션 후보 텍스트(`outputs/figures/captions.md`) 표시.
- 한꺼번에 zip으로 다운로드.

---

## 8. UI 디자인 가이드라인

- **테마**: 기본 light 테마. 한국어 폰트 가용성 확인(예: 'Malgun Gothic'). plotly 한글 깨짐 시 `font=dict(family="Malgun Gothic, Arial")`.
- **레이아웃**: `st.set_page_config(layout="wide")` 권장. 한 페이지 안에 너무 많은 위젯 X. 2~3 컬럼 그리드.
- **에러 처리**: `algo` 함수가 `{"error": "..."}`를 반환하면 `st.error`로 노출하고 traceback은 expander에 숨김.
- **상태 보존**: `st.session_state`에 마지막 선택 파일·run_id를 저장해서 페이지 이동 시 유지.
- **속도**: 카탈로그·OCV 룩업은 `@st.cache_data`로 캐시. 추정기 인스턴스는 `@st.cache_resource`.
- **보안**: 사용자가 임의 path를 입력하지 못하게 한다. 카탈로그 또는 file picker로만 선택.

---

## 9. 의존 관계 (Codex 산출물 ↔ Antigravity 페이지)

| Antigravity Task | 의존 Codex Task | 차단되면 |
|---|---|---|
| A0.4 (골격) | 없음 | 즉시 시작 |
| A0.5 (smoke test) | Codex P0 마이그레이션 | 마이그레이션 후 |
| A1.1~A1.4 (Data Explorer) | Codex P0.5 (`list_kier_files`) | placeholder로 시작 → 실데이터로 갱신 |
| A1.5 (OCV/dQdV) | Codex P0.1, P0.2, P0.3 | 함수 시그니처만 있어도 mock으로 시작 가능 |
| A1.6 (ECM) | Codex P0.4, (P2.1 fractional) | 1-RC 부터 시작 → 2-RC/FOM 추가 |
| A1.7~A1.8 (Estimator Run) | Codex P1.1 (Estimator base), P1.2 (baseline 6종) | base 클래스만 있으면 mock estimator로 시작 |
| A1.9 (Benchmark View) | Codex P1.5 (`run_benchmark`) | summary.csv mock으로 시작 |

**병행 작업 권장**: A0 (1~2일) → A0.4 골격 + Codex P0와 동시 → A1.1~A1.6는 Codex P0 결과 도착 즉시 → A1.7~A1.9는 Codex P1·P2와 병행.

---

## 10. 핸드오프 의무 (작업 단위 종료 시)

분업 Spec §10. 매번 다음 4줄 보고.

```
[변경 요약]    : 무엇을, 왜, 어디를 (ui/ 한정)
[의존 API]     : 어떤 algo 함수에 새로 의존하게 되었나 (시그니처 목록)
[테스트 결과]  : pytest tests/ui -q 마지막 5줄 + streamlit smoke test 결과
[Codex에 요청]: 부족한 algo 함수 / 추가하면 좋은 옵션 / 수정 제안
```

---

## 11. 금지 사항 (Antigravity 자체 점검용)

- ❌ `algo/` 어떤 파일도 만들거나 수정하지 않는다.
- ❌ 알고리즘 로직(필터 식, OCV 보정, 회귀, 학습 등)을 UI 코드에 작성하지 않는다.
- ❌ `outputs/runs/<run_id>/`를 직접 생성하지 않는다 (반드시 algo runner를 통해).
- ❌ pickle을 사용자 파일·세션 저장에 쓰지 않는다 (분업 Spec §4 금지 사항).
- ❌ 본 문서 또는 `01_분석보고서_및_사양/*` 의 기존 .md 를 직접 수정하지 않는다 (사용자만). 새 .md 추가만 가능.
- ❌ 분업 Spec §3 공개 API 시그니처를 추측해서 호출하지 않는다 (반드시 import 후 inspect).

---

## 12. 즉시 시작 액션 (Day 1)

1. 본 문서 + 분업 Spec + Codex_TODO_v1 + Spec v1.1 정독.
2. Task A0.1 — `pyproject.toml` 작성 (사용자 승인 후 commit).
3. Task A0.2 — venv 셋업 + `pytest tests/algo` 통과 확인.
4. Task A0.4 — `ui/` 골격 디렉터리·빈 페이지 5개 생성.
5. (Codex가 마이그레이션 완료할 때까지 대기) → `data_analysis_ui.py`를 `ui/data_analysis_ui.py`로 이동.
6. 사용자에게 1차 핸드오프 — 환경 셋업 결과 + 골격 + smoke test 결과 보고.

---

## 13. 부록: Streamlit Multipage 구조 권장

`ui/data_analysis_ui.py`는 thin entrypoint:

```python
import streamlit as st

st.set_page_config(
    page_title="JH3 Cell SOC/SOH Analyzer",
    page_icon="🔋",
    layout="wide",
)

st.title("JH3 Cell — SOC/SOH 통합 추정 연구 대시보드")
st.markdown("""
좌측 사이드바에서 페이지를 선택하세요.

- **Data Explorer**: KIER 셀 데이터 카탈로그·시계열 보기
- **OCV / dQ/dV**: OCV 룩업·chemistry 검증
- **ECM Fitting**: 등가회로모델 파라미터 식별
- **Estimator Run**: SOC/SOH 추정기 실행
- **Benchmark View**: 벤치마크 결과·논문 그림
""")
```

각 페이지는 `pages/`에 두면 Streamlit이 자동으로 사이드바에 등록. 페이지 파일명에 이모지·한글 가능 (`01_📂_Data_Explorer.py`).

---

## Changelog

- **2026-04-23 v1** (초판)
  - 미드티어 SCI 노선 + NMC 확정 반영
  - 5개 Streamlit 페이지 명세
  - Codex 산출물과의 의존 관계 표 명시
  - 환경 부트스트랩 + 디렉터리 마이그레이션 협조 절차

- **2026-04-23 v1.1** (정밀 조사 반영)
  - Chemistry 표기 NMC → **NCM** 통일 (사용자 확정).
  - 페이지 0(데이터 그리드 안내) 신규 안내 — 메인 (ch2/25 °C, ch7/50 °C, ch3/0 °C 부분), 보조 (pouch_SOH 25/40 °C × ch1~ch8, 18650, 모듈 CH1).
  - Task A1.1 Data Explorer 필터에 `dataset` (4종) / `temp_C` (0/25/40/50) / `type` (RPT/DCIR/DCIR후충전/ACIR/Pattern/Pattern_MG/Pattern_PVSmoothing/Pattern_PowerQuality/capacity_check) 옵션 명세.
  - Task A1.5 Chemistry "판정 → 검증" 으로 의미 변경 (사용자 확정 NCM과 일치 확인).
  - 모듈 Pattern 분할 청크 자동 merge 시각화 흐름 명시 (Codex의 `load_kier_run(merge_chunks=True)` 의존).

- **2026-04-23 v1.2** (사용자 확정 정정)
  - **−15 °C, 45 °C 필터 옵션 제거** (데이터 부재 확정) — temp_C는 0/25/40/50 만.
  - **모듈 채널 필터는 CH1 단독** (CH2 부재 확정).
  - **cycle / weeks 슬라이더 분리** (사용자 결정: "더 좋은 걸로" → 별도 컬럼 채택). dataset 선택에 따라 자동 토글: main_cell·module → cycle, pouch_SOH → weeks. 한 슬라이더로 묶지 않음.
  - Cell 데이터★★★★★ (2018년) 본 논문 제외 확정 → 카탈로그·필터에서 노출 안 함.

- **2026-04-23 v1.4** (5/10/15 °C supplementary)
  - Data Explorer 의 temp_C 필터 옵션에 **5 / 10 / 15** 추가. 전압하한 Pattern 전용 표기.
  - Codex 의 `algo.loaders.kier.list_kier_files()` 가 v1.4 에서 5/10/15 °C 를 자동 인식하도록 정정될 예정 (Codex_TODO_v1.md v1.4 §1.1 참조). UI 측은 카탈로그 컬럼만 그대로 노출.

- **2026-04-23 v1.3** (Pouch 폼팩터 일관성 + 모듈 격상)
  - **18650_SOH 본 논문 제외 확정** (사용자: "Pouch 타입의 셀 데이터로만"). dataset 필터에서 `cell_18650` 옵션 제거 — 3종(main_cell/pouch_soh/module)만.
  - **모듈 데이터를 supplementary가 아닌 메인 두 번째 축으로 격상**. Benchmark View 페이지에 **cross-scale (cell→module) 외삽 결과 패널** 추가 — Codex Task P3.3 산출물 `outputs/runs/bench-cross-scale/` 시각화.
  - 데이터 그리드 안내(상단 §0)를 두 축 (Pouch 셀 / Pouch 모듈) 매트릭스로 갱신.
