# M 스코프 Backend 구현 플랜 (2026-04-20)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 공통 파일 I/O · OCV–SOC 룩업 추출 · Chemistry 판정 · ECM 1-RC 초기 파라미터 식별을 오늘 안에 완료하여, Stage 1 Dual Adaptive EKF 구현의 선결 조건을 확보한다.

**Architecture:** 얇은 Python 모듈 4개(`data_io`, `ocv_soc`, `chemistry_check`, `ecm_identify`)를 프로젝트 루트에 배치. 각 모듈은 순수 함수 중심으로 설계하고 Gemini UI가 `import`로 소비한다. 실제 싸이클러 파일(PNE 포맷)은 Task 1에서 포맷을 확인한 뒤 Task 2의 `data_io`에 반영한다.

**Tech Stack:** Python 3.14, pandas 2.3, numpy, scipy (`optimize.least_squares`, `signal.find_peaks`, `signal.savgol_filter`), matplotlib, pytest.

**상위 Spec:** [2026-04-20_M스코프_backend_design.md](2026-04-20_M스코프_backend_design.md)

---

## 플랜 메타

- **작업 디렉터리**: `D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data`
- **git 정책**: 본 프로젝트는 현재 git 초기화되어 있지 않음. 각 Task 말미의 커밋 단계는 **생략**. 진척은 TodoWrite + Spec v1 Changelog + 오늘의 Action List 체크박스로 추적.
- **산출 경로**: `outputs/` (없으면 생성), `tests/` (없으면 생성).
- **공개 API 계약**: 상위 Spec §4 그대로. 시그니처 변경 금지.
- **UI 파일 제외**: `data_analysis_ui.py`는 본 플랜 어느 Task에서도 수정하지 않는다.

---

## Task 1: 싸이클러 파일 포맷 정찰 (research)

**Files:**
- Read: `02_실험_데이터/최근셀데이터/22_12_27_에기연 열화셀_25deg_1300cycle_RPT_ch2/M01Ch002[002]/22_12_27_에기연 열화셀_25deg_1300cycle_RPT_ch2.txt`
- Read: 동일 폴더의 `_StepEnd.csv`, `.sch` (schedule)
- Read: `02_실험_데이터/최근셀데이터/23_01_05_에기연 열화셀_25deg_1300cycle_DCIR_ch2/M01Ch002[002]/` 하위 `.txt` (DCIR 포맷 확인용)
- Append: `01_분석보고서_및_사양/2026-04-20_M스코프_backend_design.md` Changelog

- [ ] **Step 1: RPT `.txt` 파일의 첫 40줄과 마지막 5줄을 읽어 헤더·구분자·인코딩 확인**

`_tmp_recon.py` 임시 스크립트(세션 말 삭제):

```python
from pathlib import Path
p = Path(r"D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data\02_실험_데이터\최근셀데이터\22_12_27_에기연 열화셀_25deg_1300cycle_RPT_ch2\M01Ch002[002]\22_12_27_에기연 열화셀_25deg_1300cycle_RPT_ch2.txt")
for enc in ("utf-8", "cp949", "euc-kr", "utf-16"):
    try:
        with p.open("r", encoding=enc) as f:
            head = [next(f) for _ in range(40)]
        print(f"\n=== ENCODING: {enc} ===")
        for i, line in enumerate(head):
            print(f"{i:02d}: {line.rstrip()}")
        break
    except (UnicodeDecodeError, StopIteration):
        continue
```

Run: `python _tmp_recon.py`
Expected: 인코딩 중 하나로 40줄 출력. 헤더 라인(컬럼명), 구분자(tab/comma/space), 데이터 시작 위치 기록.

- [ ] **Step 2: pandas로 한 번 읽어서 컬럼명·shape 확인**

```python
import pandas as pd
for sep in ("\t", ",", r"\s+"):
    try:
        df = pd.read_csv(p, sep=sep, encoding="cp949", engine="python", nrows=50)
        if df.shape[1] > 1:
            print(f"\n=== SEP={sep!r} shape={df.shape} ===")
            print("cols:", list(df.columns))
            print(df.head(3))
            break
    except Exception as e:
        print(f"  [sep={sep!r} failed: {e}]")
```

Expected: 컬럼명 배열 확보. `Step`/`Voltage`/`Current`/`Time` 등 실제 이름 확인.

- [ ] **Step 3: `_StepEnd.csv` 열어 step 요약 구조 확인** (스텝 전류·지속시간 요약이 있으면 추후 저율 스텝 식별 간소화 가능)

```python
q = p.parent / (p.stem + "_StepEnd.csv")
for enc in ("cp949", "utf-8"):
    try:
        df2 = pd.read_csv(q, encoding=enc)
        print("StepEnd cols:", list(df2.columns))
        print(df2.head())
        break
    except UnicodeDecodeError:
        continue
```

Expected: StepEnd 컬럼 구조 기록.

- [ ] **Step 4: DCIR 폴더의 `.txt` 파일도 동일 확인**

DCIR 파일 경로:
```
02_실험_데이터/최근셀데이터/23_01_05_에기연 열화셀_25deg_1300cycle_DCIR_ch2/M01Ch002[002]/
```
안의 `.txt` 파일에 대해 Step 1~2 반복. 펄스 구조(예: 10s 방전 + 30s 휴지)가 드러나면 기록.

- [ ] **Step 5: 발견 내용을 design doc Changelog에 요약 기록**

`01_분석보고서_및_사양/2026-04-20_M스코프_backend_design.md`의 `## Changelog` 아래에 다음 형식 한 블록 추가:

```markdown
- **2026-04-20 v1.1 (Task 1 정찰 결과)**
  - RPT `.txt`: 인코딩=`<확인값>`, 구분자=`<확인값>`, 컬럼=`[…실제 컬럼명…]`, 헤더 라인=`<줄번호>`
  - StepEnd `.csv`: 컬럼=`[…]`
  - DCIR `.txt`: 펄스 구조=`<요약>` (예: 10s -1C + 30s 휴지)
  - 이 결과로 §5 `data_io.py` alias 테이블 키=`step|voltage|current|time_s` 매핑 확정
```

- [ ] **Step 6: `_tmp_recon.py` 삭제** (정찰 끝나면 보관 불필요)

---

## Task 2: `data_io.py` 작성 (TDD)

**Files:**
- Create: `data_io.py`
- Create: `tests/__init__.py` (빈 파일)
- Create: `tests/test_data_io.py`

- [ ] **Step 1: `tests/` 폴더 생성 + 빈 `__init__.py` 작성**

```bash
mkdir tests
echo "" > tests/__init__.py
```

- [ ] **Step 2: 실패할 테스트 작성 (`tests/test_data_io.py`)**

```python
"""data_io 모듈 단위 테스트. 합성 파일을 생성해 round-trip 검증."""
import io
import tempfile
from pathlib import Path
import pandas as pd
import pytest

from data_io import detect_format, read_cycler_file, normalize_columns


def test_detect_format_by_extension():
    assert detect_format("foo/bar.txt") == "txt"
    assert detect_format("x/y.csv") == "csv"
    assert detect_format("a.XLSX") == "xlsx"
    assert detect_format("no_ext") == "unknown"


def test_normalize_columns_standardizes_aliases():
    df = pd.DataFrame(
        {"StepNo": [1, 2], "Voltage(V)": [3.6, 3.7], "Current(A)": [-0.1, -0.1], "TotalTime": [0, 1]}
    )
    out = normalize_columns(df)
    assert set(["step", "voltage", "current", "time_s"]).issubset(out.columns)
    assert out["voltage"].iloc[0] == 3.6


def test_read_cycler_file_tab_separated(tmp_path: Path):
    # 실제 PNE 스타일: tab 구분, cp949. Task 1 정찰 결과에 맞춰 sep/encoding 기본값 조정될 수 있음.
    content = "StepNo\tVoltage\tCurrent\tTotalTime\n1\t3.60\t-0.10\t0.0\n1\t3.59\t-0.10\t1.0\n"
    f = tmp_path / "sample.txt"
    f.write_text(content, encoding="utf-8")
    df = read_cycler_file(str(f))
    assert list(df.columns)[:4] == ["step", "voltage", "current", "time_s"]
    assert len(df) == 2
    assert df["voltage"].iloc[1] == pytest.approx(3.59)
```

- [ ] **Step 3: 테스트 실행하여 실패 확인**

Run: `python -m pytest tests/test_data_io.py -v`
Expected: `ModuleNotFoundError: No module named 'data_io'` 또는 `ImportError`. **반드시 실패해야 함**.

- [ ] **Step 4: `data_io.py` 최소 구현** (Task 1 정찰 결과로 `_DEFAULT_SEP`, `_DEFAULT_ENCODINGS`를 실제 값에 맞춰 조정)

```python
"""공통 파일 I/O: 싸이클러 원시 파일(.txt/.csv) 및 엑셀 읽기.

Task 1 정찰 결과로 _DEFAULT_SEP, _DEFAULT_ENCODINGS가 실제 파일에 맞게 고정됨.
"""
from __future__ import annotations
from pathlib import Path
from typing import List
import pandas as pd

# Task 1 결과로 채워짐. 잠정:
_DEFAULT_ENCODINGS = ("cp949", "utf-8", "euc-kr", "utf-16")
_DEFAULT_SEPS = ("\t", ",", r"\s+")

# 컬럼 alias 테이블. key=표준명, value=허용되는 원본명 리스트.
_ALIAS = {
    "step":    ["StepNo", "Step", "StepIndex", "Step_Index", "Step No"],
    "voltage": ["Voltage", "V", "Vt", "Voltage(V)", "Cell Voltage", "Cell Voltage(V)"],
    "current": ["Current", "I", "Current(A)", "Cell Current(A)"],
    "time_s":  ["TotalTime", "Time", "ElapsedTime", "Time(s)", "Total Time"],
    # 선택 컬럼:
    "temperature": ["Temperature", "Temp", "T", "Temperature(degC)", "Chamber Temp"],
    "cycle":       ["Cycle", "CycleNo", "Cycle Index"],
    "ah":          ["Ah", "Capacity", "Capacity(Ah)", "Q"],
    "wh":          ["Wh", "Energy", "Energy(Wh)"],
}


def detect_format(path: str) -> str:
    ext = Path(path).suffix.lower().lstrip(".")
    if ext in ("txt", "tsv"):
        return "txt"
    if ext == "csv":
        return "csv"
    if ext in ("xlsx", "xlsm", "xls"):
        return "xlsx"
    return "unknown"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for canon, aliases in _ALIAS.items():
        for a in aliases:
            if a in df.columns and canon not in rename.values():
                rename[a] = canon
                break
    return df.rename(columns=rename)


def _try_read(path: str, sep: str, encoding: str) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(path, sep=sep, encoding=encoding, engine="python")
        if df.shape[1] >= 2:
            return df
    except Exception:
        return None
    return None


def read_cycler_file(path: str) -> pd.DataFrame:
    """싸이클러 원시 파일(.txt/.csv)을 정규화된 DataFrame으로 반환.

    반환 컬럼(필수): step, voltage, current, time_s
    """
    fmt = detect_format(path)
    if fmt not in ("txt", "csv"):
        raise ValueError(f"Unsupported format for cycler file: {path}")

    last_err = None
    for enc in _DEFAULT_ENCODINGS:
        for sep in _DEFAULT_SEPS:
            df = _try_read(path, sep, enc)
            if df is not None:
                df = normalize_columns(df)
                required = ["step", "voltage", "current", "time_s"]
                missing = [c for c in required if c not in df.columns]
                if missing:
                    last_err = f"Missing required columns {missing}. Got {list(df.columns)[:20]}"
                    continue
                # dtype 보정
                for col in ("voltage", "current", "time_s"):
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                df = df.dropna(subset=["voltage", "current", "time_s"]).reset_index(drop=True)
                return df
    raise RuntimeError(f"Failed to read {path}. Last error: {last_err}")


def read_excel_sheet(path: str, sheet: str | int = 0) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet)
```

- [ ] **Step 5: 테스트 재실행하여 통과 확인**

Run: `python -m pytest tests/test_data_io.py -v`
Expected: 3 passed.

- [ ] **Step 6: 실제 RPT 파일로 smoke test** (정찰 결과 반영된 alias가 진짜 매칭되는지 확인)

`_tmp_smoke_dataio.py`:
```python
from data_io import read_cycler_file
p = r"D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data\02_실험_데이터\최근셀데이터\22_12_27_에기연 열화셀_25deg_1300cycle_RPT_ch2\M01Ch002[002]\22_12_27_에기연 열화셀_25deg_1300cycle_RPT_ch2.txt"
df = read_cycler_file(p)
print("shape:", df.shape)
print("cols:", list(df.columns))
print(df.head())
print(df.describe())
```

Run: `python _tmp_smoke_dataio.py`
Expected: 컬럼에 `step, voltage, current, time_s` 포함. 전압 범위 대략 2.5~4.3 V. **실패 시 alias 테이블 보강 → 테스트 다시 통과 확인 → 여기로 복귀**.

- [ ] **Step 7: `_tmp_smoke_dataio.py` 삭제.**

---

## Task 3: `ocv_soc.py` 리팩터 + `compute_dqdv` 추가 (TDD)

**Files:**
- Modify: `ocv_soc.py`
- Create: `tests/test_ocv_soc.py`

- [ ] **Step 1: 실패할 테스트 작성 (`tests/test_ocv_soc.py`)**

```python
"""ocv_soc 단위 테스트."""
import numpy as np
import pandas as pd
import pytest
from pathlib import Path

from ocv_soc import compute_dqdv, extract_ocv_soc_from_rpt


def test_compute_dqdv_monotonic_discharge():
    # 합성: 1시간 동안 1A 일정 방전, 전압이 4.2 → 3.0 선형 강하
    t = np.arange(0, 3600, 1.0)  # 1 Hz
    current = -np.ones_like(t)   # -1A
    voltage = 4.2 - (4.2 - 3.0) * (t / t[-1])  # 선형
    df = compute_dqdv(voltage, current, t)
    assert "V" in df.columns and "dQdV" in df.columns
    assert len(df) > 10
    # 선형 V 강하 + 일정 전류 → dQ/dV는 대체로 양수·유한
    assert df["dQdV"].dropna().abs().max() < 1e6
    assert df["dQdV"].dropna().size > 10


def test_extract_ocv_soc_from_rpt_synthetic(tmp_path: Path):
    # 합성 PNE 스타일 파일: 한 스텝 = 저율 방전 1시간
    n = 3600
    step = np.ones(n, dtype=int)
    v = np.linspace(4.15, 3.05, n)
    i = np.full(n, -0.06)  # ~ 0.1C for 63Ah? 사실 매우 저율 — 필터에 걸리도록 > 1800s 지속
    tt = np.arange(n, dtype=float)
    df = pd.DataFrame({"StepNo": step, "Voltage": v, "Current": i, "TotalTime": tt})
    f = tmp_path / "synthetic.txt"
    df.to_csv(f, sep="\t", index=False, encoding="utf-8")
    res = extract_ocv_soc_from_rpt(str(f), nominal_capacity_ah=63.0)
    assert "error" not in res
    assert "discharge" in res
    dis = res["discharge"]
    assert {"SOC", "OCV"}.issubset(dis.columns)
    assert dis["SOC"].min() >= 0 and dis["SOC"].max() <= 100
```

- [ ] **Step 2: 테스트 실행하여 실패 확인**

Run: `python -m pytest tests/test_ocv_soc.py -v`
Expected: `compute_dqdv` import 실패 또는 `extract_ocv_soc_from_rpt` 기존 구현이 `read_csv` 단일 호출이라 새 테스트 실패.

- [ ] **Step 3: `ocv_soc.py` 전체 교체**

```python
"""OCV–SOC 룩업 추출 + dQ/dV 계산.

공개 API:
- extract_ocv_soc_from_rpt(file_path, nominal_capacity_ah) -> dict
- compute_dqdv(voltage, current, time_s, smoothing_window=51) -> DataFrame[V, dQdV]
"""
from __future__ import annotations
from typing import Dict
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

from data_io import read_cycler_file


def compute_dqdv(
    voltage: np.ndarray,
    current: np.ndarray,
    time_s: np.ndarray,
    smoothing_window: int = 51,
) -> pd.DataFrame:
    """시계열 (V, I, t) → dQ/dV 곡선.

    방법: Q(t) = 적분 I(t)dt → dQ/dV를 V 기준으로 수치 미분 후 Savitzky-Golay 평활.
    음수 전류(방전) 기준으로 |dQ/dV| 양수화. NaN은 드롭.
    """
    v = np.asarray(voltage, dtype=float)
    i = np.asarray(current, dtype=float)
    t = np.asarray(time_s, dtype=float)
    if not (len(v) == len(i) == len(t)):
        raise ValueError("voltage/current/time_s 길이 불일치")

    # Q(t), Ah 적산 (절댓값 기준, 방전·충전 무관하게 dQ 방향 양수)
    dt_h = np.diff(t, prepend=t[0]) / 3600.0
    q = np.cumsum(np.abs(i) * dt_h)

    # V 기준 정렬 (V 단조성 확보 위해 중복 제거)
    order = np.argsort(v)
    v_sorted = v[order]
    q_sorted = q[order]
    # V 중복 제거(같은 V 여러 개면 평균 Q)
    v_unique, idx_inv = np.unique(v_sorted, return_inverse=True)
    q_unique = np.bincount(idx_inv, weights=q_sorted) / np.bincount(idx_inv)

    if len(v_unique) < 5:
        return pd.DataFrame({"V": v_unique, "dQdV": np.full_like(v_unique, np.nan)})

    # 수치 미분
    dqdv = np.gradient(q_unique, v_unique)

    # 평활 (홀수 window, 배열 길이 초과 시 축소)
    w = min(smoothing_window, len(v_unique) - (1 - len(v_unique) % 2))
    if w >= 5 and w % 2 == 1:
        dqdv = savgol_filter(dqdv, window_length=w, polyorder=3, mode="interp")

    return pd.DataFrame({"V": v_unique, "dQdV": dqdv})


def extract_ocv_soc_from_rpt(
    file_path: str,
    nominal_capacity_ah: float = 63.0,
) -> Dict:
    """RPT 파일에서 저율 충·방전 스텝을 식별해 SOC–OCV 테이블을 반환.

    Returns: {"discharge": DataFrame[SOC, OCV], "charge": DataFrame[SOC, OCV]}
             실패 시: {"error": str}
    """
    try:
        df = read_cycler_file(file_path)
    except Exception as e:
        return {"error": f"read failed: {e}"}

    # 스텝 요약: 평균 전류, 지속시간
    summary = (
        df.groupby("step", as_index=False)
        .agg(avg_current=("current", "mean"), duration=("time_s", lambda x: float(x.max() - x.min())))
    )

    LOW_C = 0.2 * nominal_capacity_ah  # 0.2C를 저율 상한으로 가정 (A 단위)
    MIN_DURATION = 1800.0               # 30분 이상

    dis = summary[(summary["avg_current"] < -0.1) & (summary["avg_current"] > -LOW_C) & (summary["duration"] > MIN_DURATION)]
    chg = summary[(summary["avg_current"] > 0.1) & (summary["avg_current"] < LOW_C) & (summary["duration"] > MIN_DURATION)]

    result: Dict = {}

    def _to_ocv_soc(sub_df: pd.DataFrame, start_soc: float, direction: str) -> pd.DataFrame:
        sub = sub_df.sort_values("time_s").reset_index(drop=True)
        dt_h = sub["time_s"].diff().fillna(0) / 3600.0
        ah = (sub["current"].abs() * dt_h).cumsum()
        if direction == "discharge":
            soc = (start_soc - ah / nominal_capacity_ah * 100.0).clip(0, 100)
        else:
            soc = (start_soc + ah / nominal_capacity_ah * 100.0).clip(0, 100)
        out = pd.DataFrame({"SOC": soc.values, "OCV": sub["voltage"].values})
        # 200개로 다운샘플
        if len(out) > 200:
            idx = np.linspace(0, len(out) - 1, 200).astype(int)
            out = out.iloc[idx].reset_index(drop=True)
        return out

    if not dis.empty:
        best = dis.sort_values("duration", ascending=False).iloc[0]["step"]
        sub = df[df["step"] == best]
        result["discharge"] = _to_ocv_soc(sub, start_soc=100.0, direction="discharge")

    if not chg.empty:
        best = chg.sort_values("duration", ascending=False).iloc[0]["step"]
        sub = df[df["step"] == best]
        result["charge"] = _to_ocv_soc(sub, start_soc=0.0, direction="charge")

    if not result:
        return {"error": "저율 충·방전 스텝(>30분, |I|<0.2C) 미발견"}
    return result


if __name__ == "__main__":
    # CLI: python ocv_soc.py <file> [<capacity_Ah>]
    import sys, json
    if len(sys.argv) < 2:
        print("usage: python ocv_soc.py <file> [<nominal_capacity_Ah>]")
        raise SystemExit(1)
    f = sys.argv[1]
    cap = float(sys.argv[2]) if len(sys.argv) >= 3 else 63.0
    res = extract_ocv_soc_from_rpt(f, cap)
    if "error" in res:
        print(json.dumps(res, ensure_ascii=False))
        raise SystemExit(2)
    for k, df in res.items():
        print(f"=== {k} ({len(df)} rows) ===")
        print(df.head())
        print(df.tail())
```

- [ ] **Step 4: 테스트 재실행하여 통과 확인**

Run: `python -m pytest tests/test_ocv_soc.py -v`
Expected: 2 passed.

- [ ] **Step 5: 전체 테스트 슈트 통과 재확인**

Run: `python -m pytest tests/ -v`
Expected: 5 passed (data_io 3 + ocv_soc 2).

---

## Task 4: 실제 25 °C RPT 파일로 OCV 추출 → `outputs/ocv_soc_25C_v0.csv`

**Files:**
- Create: `outputs/` (디렉터리 생성)
- Create: `outputs/ocv_soc_25C_v0.csv`
- Create: `outputs/ocv_soc_25C_v0.png` (플롯)

- [ ] **Step 1: `outputs/` 디렉터리 생성**

```bash
mkdir -p outputs
```

- [ ] **Step 2: 추출 실행 스크립트 작성 (`run_ocv_25C.py`, 영구 보관)**

```python
"""25 °C RPT 파일에서 OCV–SOC 룩업 추출하여 outputs/에 저장."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ocv_soc import extract_ocv_soc_from_rpt

RPT_FILE = Path(
    r"D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data"
    r"\02_실험_데이터\최근셀데이터\22_12_27_에기연 열화셀_25deg_1300cycle_RPT_ch2"
    r"\M01Ch002[002]\22_12_27_에기연 열화셀_25deg_1300cycle_RPT_ch2.txt"
)
OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

NOMINAL_AH = 63.0

res = extract_ocv_soc_from_rpt(str(RPT_FILE), NOMINAL_AH)
if "error" in res:
    raise SystemExit(f"추출 실패: {res['error']}")

# 0.01 간격 SOC 그리드로 평균(방·충전 둘 다 있으면 평균, 하나만 있으면 그것 사용)
soc_grid = np.arange(0.0, 100.01, 1.0)  # 1% 간격 초판 (0.01 간격은 다음 세션)
def _interp(df_so, grid):
    df_so = df_so.sort_values("SOC")
    return np.interp(grid, df_so["SOC"].values, df_so["OCV"].values)

ocv_d = _interp(res["discharge"], soc_grid) if "discharge" in res else None
ocv_c = _interp(res["charge"], soc_grid) if "charge" in res else None

if ocv_d is not None and ocv_c is not None:
    ocv_avg = 0.5 * (ocv_d + ocv_c)
elif ocv_d is not None:
    ocv_avg = ocv_d
else:
    ocv_avg = ocv_c

out = pd.DataFrame({
    "SOC_pct": soc_grid,
    "OCV_discharge_V": ocv_d if ocv_d is not None else np.nan,
    "OCV_charge_V":    ocv_c if ocv_c is not None else np.nan,
    "OCV_avg_V":       ocv_avg,
})
out_csv = OUT_DIR / "ocv_soc_25C_v0.csv"
out.to_csv(out_csv, index=False, encoding="utf-8-sig")
print(f"saved: {out_csv}")

# 플롯
fig, ax = plt.subplots(figsize=(7, 4))
if ocv_d is not None: ax.plot(soc_grid, ocv_d, label="Discharge OCV")
if ocv_c is not None: ax.plot(soc_grid, ocv_c, label="Charge OCV")
ax.plot(soc_grid, ocv_avg, label="Average", linestyle="--")
ax.set_xlabel("SOC (%)"); ax.set_ylabel("OCV (V)"); ax.grid(True); ax.legend()
ax.set_title("OCV–SOC @ 25 °C (JH3 Cell, 1300 cycle, v0)")
fig.tight_layout()
out_png = OUT_DIR / "ocv_soc_25C_v0.png"
fig.savefig(out_png, dpi=150)
print(f"saved: {out_png}")
```

- [ ] **Step 3: 실행**

Run: `python run_ocv_25C.py`
Expected:
- stdout에 `saved: outputs\ocv_soc_25C_v0.csv` 및 `...ocv_soc_25C_v0.png` 출력
- CSV 파일이 101행(SOC 0~100, 1% 간격) 생성됨

- [ ] **Step 4: CSV 내용 sanity check**

```bash
python -c "import pandas as pd; d=pd.read_csv(r'outputs/ocv_soc_25C_v0.csv'); print(d.describe()); print('V range:', d['OCV_avg_V'].min(), d['OCV_avg_V'].max())"
```
Expected: `OCV_avg_V` 최소 ~3.0 V, 최대 ~4.2 V (JH3 운용범위). 벗어나면 Task 3 `extract_ocv_soc_from_rpt` 로직 재점검.

---

## Task 5: `chemistry_check.py` 작성 + 실행 (TDD)

**Files:**
- Create: `chemistry_check.py`
- Create: `tests/test_chemistry_check.py`
- Create: `outputs/dqdv_25C_rpt0_v0.png`
- Create: `outputs/chemistry_판정_2026-04-20.md`

- [ ] **Step 1: 실패할 테스트 작성 (`tests/test_chemistry_check.py`)**

```python
"""chemistry_check 단위 테스트: 합성 dQ/dV 곡선에 대한 라벨링."""
import numpy as np
import pandas as pd

from chemistry_check import classify_chemistry


def _synthetic_nmc():
    V = np.linspace(3.0, 4.2, 400)
    dqdv = (
        8.0 * np.exp(-((V - 3.70) / 0.04) ** 2)   # NMC peak 1
        + 5.0 * np.exp(-((V - 3.95) / 0.05) ** 2) # NMC peak 2
        + 0.2
    )
    return pd.DataFrame({"V": V, "dQdV": dqdv})


def _synthetic_lfp():
    V = np.linspace(2.8, 3.6, 400)
    dqdv = 30.0 * np.exp(-((V - 3.32) / 0.015) ** 2) + 0.05  # 매우 높고 좁은 단일 피크
    return pd.DataFrame({"V": V, "dQdV": dqdv})


def test_nmc_detected():
    res = classify_chemistry(_synthetic_nmc())
    assert res["label"] in ("NMC", "NCA")  # 유사 스펙이라 NCA로 튈 가능성도 수용
    assert res["confidence"] > 0.3
    assert len(res["peaks"]) >= 2


def test_lfp_detected():
    res = classify_chemistry(_synthetic_lfp())
    assert res["label"] == "LFP"
    assert res["confidence"] > 0.6
```

- [ ] **Step 2: 테스트 실행하여 실패 확인**

Run: `python -m pytest tests/test_chemistry_check.py -v`
Expected: `ModuleNotFoundError: No module named 'chemistry_check'`.

- [ ] **Step 3: `chemistry_check.py` 구현**

```python
"""dQ/dV 곡선에서 셀 chemistry를 추정한다.

판정 휴리스틱:
- LFP: 3.2–3.4 V 범위에 매우 뾰족한 단일 피크 (FWHM 좁음, 높이 >> 나머지).
- NMC: 3.6–3.8, 3.9–4.0 V 부근에 2~3개 완만한 피크.
- NCA: NMC와 유사하나 피크가 더 낮고 넓음. 구분 어려움 — confidence 낮춤.
"""
from __future__ import annotations
from typing import Dict, List
import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def classify_chemistry(dqdv_df: pd.DataFrame) -> Dict:
    V = dqdv_df["V"].values.astype(float)
    Y = dqdv_df["dQdV"].values.astype(float)

    # 피크 검출 (prominence를 Y 분포로 자동 설정)
    prom_thresh = max(1e-6, 0.15 * (np.nanmax(Y) - np.nanmin(Y)))
    peaks_idx, props = find_peaks(Y, prominence=prom_thresh)
    peaks: List[Dict] = [{"V": float(V[i]), "height": float(Y[i])} for i in peaks_idx]

    def _in_range(v, lo, hi):
        return lo <= v <= hi

    lfp_peaks  = [p for p in peaks if _in_range(p["V"], 3.20, 3.40)]
    nmc1_peaks = [p for p in peaks if _in_range(p["V"], 3.60, 3.82)]
    nmc2_peaks = [p for p in peaks if _in_range(p["V"], 3.88, 4.05)]

    label = "unknown"
    confidence = 0.0
    reason_bits: List[str] = []

    total_height = sum(p["height"] for p in peaks) + 1e-9

    if lfp_peaks:
        lfp_h = max(p["height"] for p in lfp_peaks)
        if lfp_h / total_height > 0.6 and len(peaks) <= 3:
            label = "LFP"
            confidence = min(0.95, lfp_h / total_height)
            reason_bits.append(f"3.2~3.4 V 피크 높이 비중 {lfp_h/total_height:.2f} > 0.6 → LFP")

    if label == "unknown" and nmc1_peaks and nmc2_peaks:
        label = "NMC"  # NCA와 잠정 동일 취급
        confidence = 0.6
        reason_bits.append(f"3.6~3.8 V 피크 {len(nmc1_peaks)}개 + 3.9~4.0 V 피크 {len(nmc2_peaks)}개 관찰 → NMC 계열")
        # NCA 힌트: 피크가 현저히 낮고 넓으면 confidence 감쇠 + 라벨 변경 여지
        avg_nmc_h = np.mean([p["height"] for p in nmc1_peaks + nmc2_peaks])
        if avg_nmc_h < 0.25 * total_height:
            label = "NCA"
            reason_bits.append("피크가 완만·저진폭 → NCA 가능성")
            confidence = 0.4

    if label == "unknown":
        if nmc1_peaks or nmc2_peaks:
            label = "NMC"
            confidence = 0.3
            reason_bits.append("NMC 구간 피크 일부만 존재 — 확신도 낮음")
        else:
            reason_bits.append("표준 구간 피크 미검출")

    return {
        "label": label,
        "confidence": float(confidence),
        "peaks": peaks,
        "reason": " / ".join(reason_bits) if reason_bits else "판정 근거 없음",
    }
```

- [ ] **Step 4: 테스트 재실행하여 통과 확인**

Run: `python -m pytest tests/test_chemistry_check.py -v`
Expected: 2 passed.

- [ ] **Step 5: 실제 RPT 파일로 chemistry 판정 실행 스크립트 (`run_chemistry_check.py`)**

```python
"""25 °C RPT 파일의 저율 방전 스텝에서 dQ/dV 곡선 계산 → chemistry 판정.
결과: outputs/dqdv_25C_rpt0_v0.png, outputs/chemistry_판정_2026-04-20.md
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from data_io import read_cycler_file
from ocv_soc import compute_dqdv
from chemistry_check import classify_chemistry

RPT_FILE = Path(
    r"D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data"
    r"\02_실험_데이터\최근셀데이터\22_12_27_에기연 열화셀_25deg_1300cycle_RPT_ch2"
    r"\M01Ch002[002]\22_12_27_에기연 열화셀_25deg_1300cycle_RPT_ch2.txt"
)
OUT = Path("outputs")
OUT.mkdir(exist_ok=True)

df = read_cycler_file(str(RPT_FILE))

# 저율 방전 스텝 선택 (duration 긴 것, |I|<0.2C 방전)
NOMINAL = 63.0
summary = df.groupby("step").agg(
    avg_current=("current", "mean"),
    duration=("time_s", lambda x: float(x.max() - x.min())),
).reset_index()
cand = summary[(summary["avg_current"] < -0.1) & (summary["avg_current"] > -0.2 * NOMINAL) & (summary["duration"] > 1800)]
if cand.empty:
    raise SystemExit("저율 방전 스텝 없음")
best_step = int(cand.sort_values("duration", ascending=False).iloc[0]["step"])
sub = df[df["step"] == best_step].sort_values("time_s").reset_index(drop=True)
print(f"selected step={best_step}, n={len(sub)}, avg_I={sub['current'].mean():.3f} A, dt={sub['time_s'].max()-sub['time_s'].min():.0f}s")

dqdv = compute_dqdv(sub["voltage"].values, sub["current"].values, sub["time_s"].values)
res = classify_chemistry(dqdv)

# 플롯
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(dqdv["V"], dqdv["dQdV"])
for p in res["peaks"]:
    ax.axvline(p["V"], color="red", linestyle=":", alpha=0.6)
    ax.text(p["V"], p["height"], f"{p['V']:.2f} V", fontsize=8)
ax.set_xlabel("Voltage (V)"); ax.set_ylabel("dQ/dV (Ah/V)")
ax.set_title(f"dQ/dV @ 25 °C | label={res['label']} (conf={res['confidence']:.2f})")
ax.grid(True)
fig.tight_layout()
png = OUT / "dqdv_25C_rpt0_v0.png"
fig.savefig(png, dpi=150); print(f"saved: {png}")

md = OUT / "chemistry_판정_2026-04-20.md"
lines = [
    "# Chemistry 판정 리포트 (2026-04-20)",
    "",
    f"**대상 파일**: `{RPT_FILE.name}`",
    f"**스텝**: {best_step}",
    f"**평균 전류**: {sub['current'].mean():.3f} A (≈ {sub['current'].mean()/NOMINAL:.3f} C)",
    f"**지속**: {sub['time_s'].max()-sub['time_s'].min():.0f} s",
    "",
    f"## 판정: **{res['label']}** (confidence {res['confidence']:.2f})",
    "",
    f"**근거**: {res['reason']}",
    "",
    "## 검출 피크",
    "| V (V) | 높이 (dQ/dV) |",
    "|---|---|",
] + [f"| {p['V']:.3f} | {p['height']:.2f} |" for p in res["peaks"]] + [
    "",
    "## 다음 액션",
    "- NMC/NCA 로 판정되면 Spec v1 §1.3 Chemistry 추정을 확정으로 표기하고, Open 이슈 ② Close.",
    "- LFP 로 판정되면 OCV 룩업 전략 재검토 필요 (LFP는 넓은 plateau → EKF 관측가능성 취약). Spec v1 §4 ECM 설계 변경 여지.",
    "- confidence < 0.5 이면 보성파워텍 김태연 과장에 직접 문의(010-9504-4416) + 다른 온도 RPT로 교차검증.",
]
md.write_text("\n".join(lines), encoding="utf-8")
print(f"saved: {md}")
print(f"\n=== 결과 ===\nlabel={res['label']} conf={res['confidence']:.2f}\nreason={res['reason']}\npeaks={res['peaks']}")
```

- [ ] **Step 6: 실행**

Run: `python run_chemistry_check.py`
Expected:
- stdout에 `label=NMC`(또는 NCA/LFP) 및 `saved: outputs\dqdv_25C_rpt0_v0.png`, `saved: outputs\chemistry_판정_2026-04-20.md` 출력
- 세 산출물 생성 확인

- [ ] **Step 7: 전체 테스트 재실행**

Run: `python -m pytest tests/ -v`
Expected: 7 passed (data_io 3 + ocv_soc 2 + chemistry 2).

---

## Task 6: `ecm_identify.py` 작성 + 실행 (TDD)

**Files:**
- Create: `ecm_identify.py`
- Create: `tests/test_ecm_identify.py`
- Create: `outputs/ecm_params_initial_v0.json`

- [ ] **Step 1: 실패할 테스트 작성 (`tests/test_ecm_identify.py`)**

```python
"""ecm_identify 단위 테스트: 합성 펄스로 1-RC 파라미터 회수 검증."""
import numpy as np
import pandas as pd
from pathlib import Path
import json

from ecm_identify import identify_1rc, _fit_1rc_core


def test_fit_1rc_recovers_params():
    # 합성: R0=1.0 mΩ, R1=0.5 mΩ, C1=10000 F, I=63A 펄스 30초, 이후 휴지 120초
    R0, R1, C1 = 1.0e-3, 0.5e-3, 10000.0
    tau = R1 * C1
    OCV = 3.70
    I_pulse = 63.0
    t_pulse = np.arange(0, 30.0, 0.1)
    t_rest  = np.arange(30.0, 150.0, 0.1)

    V_pulse = OCV - I_pulse * R0 - I_pulse * R1 * (1 - np.exp(-t_pulse / tau))
    v1_end = I_pulse * R1 * (1 - np.exp(-30.0 / tau))
    V_rest = OCV - v1_end * np.exp(-(t_rest - 30.0) / tau)

    t = np.concatenate([t_pulse, t_rest])
    v = np.concatenate([V_pulse, V_rest])
    i = np.concatenate([np.full_like(t_pulse, -I_pulse), np.zeros_like(t_rest)])

    params = _fit_1rc_core(t, v, i, ocv=OCV)
    assert abs(params["R0"] - R0) / R0 < 0.1
    assert abs(params["R1"] - R1) / R1 < 0.2
    assert abs(params["tau"] - tau) / tau < 0.2
    assert params["rmse"] < 0.005  # 5 mV 이하


def test_identify_1rc_from_synthetic_file(tmp_path: Path):
    # 합성 파일 저장 → identify_1rc로 round-trip
    R0, R1, C1 = 1.0e-3, 0.5e-3, 10000.0
    tau = R1 * C1
    OCV = 3.70
    I_pulse = 63.0
    t_pulse = np.arange(0, 30.0, 0.1)
    t_rest  = np.arange(30.0, 150.0, 0.1)
    V_pulse = OCV - I_pulse * R0 - I_pulse * R1 * (1 - np.exp(-t_pulse / tau))
    v1_end = I_pulse * R1 * (1 - np.exp(-30.0 / tau))
    V_rest = OCV - v1_end * np.exp(-(t_rest - 30.0) / tau)
    t = np.concatenate([t_pulse, t_rest])
    v = np.concatenate([V_pulse, V_rest])
    i = np.concatenate([np.full_like(t_pulse, -I_pulse), np.zeros_like(t_rest)])

    df = pd.DataFrame({
        "StepNo": np.concatenate([np.ones_like(t_pulse, dtype=int), 2*np.ones_like(t_rest, dtype=int)]),
        "Voltage": v, "Current": i, "TotalTime": t,
    })
    f = tmp_path / "pulse.txt"
    df.to_csv(f, sep="\t", index=False, encoding="utf-8")

    res = identify_1rc(str(f), nominal_capacity_ah=63.0)
    assert "error" not in res
    assert abs(res["R0"] - R0) / R0 < 0.15
```

- [ ] **Step 2: 테스트 실행하여 실패 확인**

Run: `python -m pytest tests/test_ecm_identify.py -v`
Expected: `ModuleNotFoundError`.

- [ ] **Step 3: `ecm_identify.py` 구현**

```python
"""DCIR 펄스 파일에서 1-RC Thevenin 모델 파라미터 초기 식별.

모델: V(t) = OCV - I·R0 - I·R1·(1 - exp(-t/τ)),   τ = R1·C1
펄스 직전 휴지로 OCV 안정 → 펄스 시작 순간 전압 강하로 R0 추정.
펄스 전 구간 최소자승으로 (R0, R1, τ) 공동 식별.
"""
from __future__ import annotations
from typing import Dict
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from data_io import read_cycler_file


def _model(t: np.ndarray, i: np.ndarray, ocv: float, R0: float, R1: float, tau: float) -> np.ndarray:
    # 일정 전류 펄스 가정: V = ocv - i*R0 - i*R1*(1 - exp(-t/tau))
    # 휴지 구간에서 i=0, V1은 감쇠
    v = np.zeros_like(t)
    v1 = 0.0
    dt = np.diff(t, prepend=t[0])
    for k in range(len(t)):
        if k == 0:
            v1 = 0.0
        else:
            v1 = v1 * np.exp(-dt[k] / tau) + i[k] * R1 * (1 - np.exp(-dt[k] / tau))
        v[k] = ocv - i[k] * R0 - v1
    return v


def _fit_1rc_core(t: np.ndarray, v_meas: np.ndarray, i: np.ndarray, ocv: float) -> Dict:
    """펄스+휴지 구간에 대해 (R0, R1, tau)를 최소자승으로 식별."""
    # 초기 추정: 펄스 시작 지점 ΔV / |I| → R0
    pulse_start = np.argmax(np.abs(i) > 1.0)
    I_mag = float(np.abs(i[pulse_start]))
    R0_0 = max(1e-5, abs(ocv - v_meas[pulse_start]) / max(I_mag, 1e-6))
    R1_0 = R0_0 * 0.5
    tau_0 = 5.0

    def resid(params):
        R0, R1, tau = params
        v_pred = _model(t, i, ocv, R0, R1, tau)
        return v_pred - v_meas

    lb = [1e-6, 1e-6, 0.1]
    ub = [1.0, 1.0, 1e4]
    x0 = [R0_0, R1_0, tau_0]
    sol = least_squares(resid, x0=x0, bounds=(lb, ub), method="trf", max_nfev=2000)
    R0, R1, tau = sol.x
    C1 = tau / R1
    rmse = float(np.sqrt(np.mean(sol.fun ** 2)))
    return {"R0": float(R0), "R1": float(R1), "C1": float(C1), "tau": float(tau), "rmse": rmse}


def identify_1rc(
    pulse_file: str,
    nominal_capacity_ah: float = 63.0,
    rest_before_s: float = 30.0,
) -> Dict:
    try:
        df = read_cycler_file(pulse_file)
    except Exception as e:
        return {"error": f"read failed: {e}"}

    # 가장 큰 방전 펄스 스텝 찾기
    summary = df.groupby("step").agg(
        avg_I=("current", "mean"),
        max_abs_I=("current", lambda x: float(np.max(np.abs(x)))),
        dur=("time_s", lambda x: float(x.max() - x.min())),
    ).reset_index()
    # 펄스: |I| 큼 (>0.3C) 그리고 지속 5~120s
    LOW = 0.3 * nominal_capacity_ah
    cand = summary[(summary["max_abs_I"] > LOW) & (summary["dur"] > 5) & (summary["dur"] < 120)]
    if cand.empty:
        return {"error": "펄스 후보 스텝 없음 (|I|>0.3C, 5<dur<120s)"}
    best = cand.sort_values("max_abs_I", ascending=False).iloc[0]["step"]

    # 펄스 시작 인덱스와 직전 휴지의 OCV
    pulse_start_t = df[df["step"] == best]["time_s"].iloc[0]
    rest = df[(df["time_s"] < pulse_start_t) & (df["time_s"] >= pulse_start_t - rest_before_s)]
    if rest.empty:
        ocv = float(df[df["step"] == best]["voltage"].iloc[0])
    else:
        ocv = float(rest["voltage"].iloc[-1])

    # 펄스 + 이어지는 다음 스텝 (휴지) 30초까지 포함
    next_step = int(best) + 1
    pulse_part = df[df["step"] == best].copy()
    rest_part  = df[(df["step"] == next_step) & (df["time_s"] < df[df["step"] == next_step]["time_s"].iloc[0] + 30 if not df[df["step"] == next_step].empty else pulse_start_t)]
    # 간단히: step == best 구간만 써도 R0/R1/τ 식별 가능
    sub = pulse_part.reset_index(drop=True)
    t  = sub["time_s"].values - sub["time_s"].iloc[0]
    v  = sub["voltage"].values
    i  = sub["current"].values

    params = _fit_1rc_core(t, v, i, ocv=ocv)
    params["meta"] = {
        "file": str(pulse_file),
        "step": int(best),
        "pulse_current_A": float(np.mean(i[np.abs(i) > 1.0])) if np.any(np.abs(i) > 1.0) else 0.0,
        "ocv_used_V": ocv,
    }
    return params


if __name__ == "__main__":
    import sys, json
    if len(sys.argv) < 2:
        print("usage: python ecm_identify.py <dcir_file> [<capacity_Ah>]")
        raise SystemExit(1)
    f = sys.argv[1]
    cap = float(sys.argv[2]) if len(sys.argv) >= 3 else 63.0
    res = identify_1rc(f, cap)
    print(json.dumps(res, ensure_ascii=False, indent=2, default=float))
```

- [ ] **Step 4: 테스트 재실행하여 통과 확인**

Run: `python -m pytest tests/test_ecm_identify.py -v`
Expected: 2 passed.

- [ ] **Step 5: 실제 DCIR 파일로 식별 실행 (`run_ecm_identify.py`)**

```python
"""실제 25 °C DCIR 파일에서 1-RC 파라미터 식별 → outputs/ecm_params_initial_v0.json"""
from __future__ import annotations
import json
from pathlib import Path

from ecm_identify import identify_1rc

DCIR_DIR = Path(
    r"D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data"
    r"\02_실험_데이터\최근셀데이터\23_01_05_에기연 열화셀_25deg_1300cycle_DCIR_ch2\M01Ch002[002]"
)
# DCIR 폴더 안의 .txt 파일 중 첫 번째
txt_files = sorted(DCIR_DIR.glob("*.txt"))
if not txt_files:
    raise SystemExit(f"no .txt in {DCIR_DIR}")
DCIR_FILE = txt_files[0]
print(f"target: {DCIR_FILE.name}")

OUT = Path("outputs"); OUT.mkdir(exist_ok=True)
res = identify_1rc(str(DCIR_FILE), nominal_capacity_ah=63.0)
out_json = OUT / "ecm_params_initial_v0.json"
out_json.write_text(json.dumps(res, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
print(f"saved: {out_json}")
print(json.dumps(res, ensure_ascii=False, indent=2, default=float))

if "error" not in res and res.get("rmse", 1.0) > 0.005:
    print(f"\n⚠ RMSE={res['rmse']*1000:.2f} mV > 5 mV. 펄스가 짧거나 샘플링 문제 가능. 값은 저장하되 주의 요망.")
```

- [ ] **Step 6: 실행**

Run: `python run_ecm_identify.py`
Expected: `outputs/ecm_params_initial_v0.json` 생성. R0가 JH3 스펙(1.03 mΩ ±0.25)과 같은 자릿수(0.5~1.5 mΩ)에 있으면 건강한 값.

- [ ] **Step 7: 전체 테스트 최종 통과 확인**

Run: `python -m pytest tests/ -v`
Expected: **9 passed** (data_io 3 + ocv_soc 2 + chemistry 2 + ecm_identify 2).

---

## Task 7: 문서 갱신 + 정리

**Files:**
- Modify: `01_분석보고서_및_사양/2026-04-20_SOC_SOH_통합추정_Spec_v1.md` (Changelog에 v1.2 항목)
- Modify: `01_분석보고서_및_사양/2026-04-20_오늘의_Action_List.md` (체크박스 갱신)
- Modify: `C:\Users\User\.claude\projects\D------JGRC-----------------battery-data\memory\project_soc_soh_paper.md` (Open 이슈 ②③⑤ 상태 갱신)
- Delete: `_tmp_inspect_excel.py`

- [ ] **Step 1: Spec v1 Changelog 에 v1.2 블록 추가**

`01_분석보고서_및_사양/2026-04-20_SOC_SOH_통합추정_Spec_v1.md` 맨 아래 `## Changelog` 섹션 하단에:

```markdown
- **2026-04-20 v1.2**
  - Backend M 스코프 완료: `data_io.py`, `ocv_soc.py`(리팩터+compute_dqdv), `chemistry_check.py`, `ecm_identify.py` + 최소 pytest.
  - Chemistry 판정 결과: **<Task 5 결과 라벨>** (conf <값>) — §1.3 Chemistry 상태 `추정 → 확정`(또는 `유보`).
  - 25 °C OCV 룩업 v0 추출: `outputs/ocv_soc_25C_v0.csv` (SOC 1% 간격).
  - ECM 1-RC 초기 파라미터 v0: `outputs/ecm_params_initial_v0.json`.
  - Open 이슈 ②(chemistry) 상태 갱신, ③(OCV)·⑤(ECM 초기값) Close.
```

- [ ] **Step 2: 오늘의 Action List 체크박스 갱신**

`01_분석보고서_및_사양/2026-04-20_오늘의_Action_List.md`의 해당 항목 앞 `[ ]` → `[x]`.
- [x] P1 Chemistry 판정 (결과: <라벨> / conf <값>)
- [x] P2 OCV–SOC 25 °C v0
- 추가: ECM 초기 파라미터 v0 식별 완료 (Spec 외 보너스)

"Open 이슈 현황" 표도 동일 원칙으로 갱신.

- [ ] **Step 3: 메모리 파일 갱신**

`C:\Users\User\.claude\projects\D------JGRC-----------------battery-data\memory\project_soc_soh_paper.md`의 "해결 필요 이슈 (Open)" 섹션에서:
- 이슈 ② 상태에 `(2026-04-20 판정: <라벨>, conf <값>)` 덧붙임. conf > 0.6 이면 `Closed`, 아니면 `Open-저신뢰`.
- 이슈 ③ `Closed (2026-04-20, outputs/ocv_soc_25C_v0.csv)`.
- 이슈 ⑤ → 새 번호 추가: "ECM 1-RC 초기값: `Closed (outputs/ecm_params_initial_v0.json)`".

- [ ] **Step 4: 임시 스크립트 정리**

```bash
rm _tmp_inspect_excel.py 2>/dev/null
```
(세션 중 생성한 다른 `_tmp_*.py`도 있다면 같이 삭제.)

- [ ] **Step 5: 최종 점검**

```bash
ls outputs/
python -m pytest tests/ -v
```
Expected:
- `outputs/` 안에 4개 산출물 (`ocv_soc_25C_v0.csv`, `ocv_soc_25C_v0.png`, `dqdv_25C_rpt0_v0.png`, `chemistry_판정_2026-04-20.md`, `ecm_params_initial_v0.json` — 즉 5개)
- pytest 9 passed

---

## Self-Review (플랜 작성자 점검)

**Spec 커버리지**
- Spec §3 산출물 9종 → Task 2·3·5·6에서 전부 생성. ✓
- Spec §4 공개 API 4개 → Task 3·5·6에서 구현. ✓
- Spec §5 `data_io.py` → Task 2. ✓
- Spec §6 chemistry 휴리스틱 → Task 5 Step 3. ✓
- Spec §7 ECM 식별 절차 → Task 6 Step 3. ✓
- Spec §8 테스트 → Task 2·3·5·6에 TDD 내장. ✓
- Spec §9 실행 순서 → Task 1~7 매핑. ✓
- Spec §10 리스크 → Task 1 정찰이 가장 큰 리스크(파일 포맷)를 선두에서 해소. DCIR 펄스 짧음 리스크는 Task 6 Step 6에서 RMSE 경고로 처리. ✓
- Spec §11 제약 → 플랜 메타에서 UI 미수정·API 안정 명시. ✓

**Placeholder 점검**: "implement later", "TBD", "fill in", "add error handling" 없음. ✓

**타입/시그니처 일관성**:
- `extract_ocv_soc_from_rpt` 반환: Spec §4 = `{"discharge": DataFrame, "charge": DataFrame}` → Task 3 Step 3 구현 일치. ✓
- `compute_dqdv` 반환: Spec §4 = `DataFrame[V, dQdV]` → Task 3 Step 3 구현 일치. ✓
- `classify_chemistry` 반환: Spec §4 키 `label/confidence/peaks/reason` → Task 5 Step 3 구현 일치. ✓
- `identify_1rc` 반환: Spec §4 키 `R0/R1/C1/tau/rmse/meta` → Task 6 Step 3 구현 일치. ✓
- `read_cycler_file` 반환 컬럼: Spec §5 = `step, voltage, current, time_s` → Task 2 Step 4 구현 일치. ✓

**알려진 한계 (해결책 포함)**:
- Task 1 정찰 결과에 따라 Task 2 `_DEFAULT_ENCODINGS`·`_ALIAS`가 보강될 수 있음 → Task 2 Step 6에서 실파일 smoke test로 확인.
- Task 6에서 `_model` 구현이 O(N) 루프 — 대용량 펄스 파일에는 느릴 수 있으나 DCIR 파일은 보통 수백~수천 샘플이라 OK.
- `identify_1rc`의 `OCV` 추정을 펄스 직전 마지막 전압으로 단순화 — 정밀 필요 시 후속 세션에서 RPT OCV 룩업 참조로 업그레이드.
