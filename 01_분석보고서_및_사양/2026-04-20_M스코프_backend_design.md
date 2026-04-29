# M 스코프 Backend Design (2026-04-20)

**상위 Spec**: [2026-04-20_SOC_SOH_통합추정_Spec_v1.md](2026-04-20_SOC_SOH_통합추정_Spec_v1.md) §12 Immediate Actions (P1·P2·ECM 초기 식별).
**스코프 구분**: M — 반나절 분량. P1 (Chemistry 판정) + P2 (OCV-SOC 25°C 룩업) + ECM 초기 파라미터 식별까지.
**배경 결정**: UI는 Gemini 담당, backend만 Claude Code 담당 ([feedback_ui_vs_backend_split](../../../../Users/User/.claude/projects/D------JGRC-----------------battery-data/memory/feedback_ui_vs_backend_split.md)). 본 문서는 **backend 공개 API와 산출물**만 정의함 — UI 설계는 포함하지 않는다.

---

## 1. 목적

Stage 1 Dual Adaptive EKF 구현의 **선결 조건 3가지**를 오늘 안에 확보한다.

1. 셀 chemistry 최종 판정(NMC vs NCA vs LFP) — novelty 주장의 전제가 되는 "셀 정체성" 확정
2. OCV–SOC 룩업(25 °C 초판) — Fast filter의 측정모델 제공
3. ECM 초기 파라미터(R₀·R₁·C₁ 한 조) — Slow filter의 초기화 값 제공

부수 목표: Gemini UI가 안정적으로 import할 수 있는 **얇은 공개 API 4개** 확보.

---

## 2. 비-목표 (명시적 제외)

- Dual AEKF 구현 자체 (다음 세션)
- Adaptive Q/R scheduler 설계·학습
- 공개 데이터셋 로더 (NASA/CALCE)
- UI 수정·신설 (`data_analysis_ui.py`는 건드리지 않음)
- 성능 최적화 (정확도·재현성 우선; 대용량 파일 처리 최적화는 나중)
- 다온도 확장 (25 °C만. −15·0·45 °C는 후속)

---

## 3. 산출물

| 파일 | 종류 | 역할 |
|---|---|---|
| `data_io.py` | 신규 | 공통 파일 I/O. 포맷 자동 감지(`.txt/.csv/.xlsx`), 컬럼 alias 정규화 |
| `ocv_soc.py` | 수정 | `data_io` 사용하도록 리팩터. `compute_dqdv()` 신규 함수 추가. CLI 진입점 추가 |
| `chemistry_check.py` | 신규 | RPT 저율 방전 파일로부터 dQ/dV 분석 → NMC/NCA/LFP 판정 |
| `ecm_identify.py` | 신규 | DCIR 펄스 데이터로부터 1-RC 파라미터 식별(`scipy.optimize.least_squares`) |
| `tests/test_ocv_soc.py` | 신규 | 합성 데이터로 sanity check (pytest) |
| `outputs/ocv_soc_25C_v0.csv` | 산출 | SOC 0.00~1.00, 0.01 간격의 OCV 룩업 |
| `outputs/dqdv_25C_rpt0_v0.png` | 산출 | dQ/dV 곡선 플롯 |
| `outputs/chemistry_판정_2026-04-20.md` | 산출 | Chemistry 판정 리포트 |
| `outputs/ecm_params_initial_v0.json` | 산출 | `{"R0": ..., "R1": ..., "C1": ..., "rmse": ..., "meta": {...}}` |

---

## 4. 공개 API (Gemini UI가 import할 대상 — 안정 약속)

```python
# ---- ocv_soc.py ----
def extract_ocv_soc_from_rpt(
    file_path: str,
    nominal_capacity_ah: float = 63.0,
) -> dict:
    """
    RPT 파일에서 저율 충·방전 스텝을 식별해 SOC–OCV 테이블을 반환.
    Returns: {"discharge": DataFrame[SOC, OCV], "charge": DataFrame[SOC, OCV]}
             실패 시: {"error": str}
    """

def compute_dqdv(
    voltage: np.ndarray,
    current: np.ndarray,
    time_s: np.ndarray,
    smoothing_window: int = 51,
) -> pd.DataFrame:
    """
    시계열 (V, I, t) → dQ/dV 곡선.
    Returns: DataFrame[V, dQdV]
    """

# ---- chemistry_check.py ----
def classify_chemistry(dqdv_df: pd.DataFrame) -> dict:
    """
    dQ/dV 곡선에서 피크 수·위치·plateau를 분석해 chemistry 추정.
    Returns: {
        "label": "NMC" | "NCA" | "LFP" | "unknown",
        "confidence": float,          # 0~1
        "peaks": [{"V": float, "height": float}, ...],
        "reason": str,                # 한국어 설명
    }
    """

# ---- ecm_identify.py ----
def identify_1rc(
    pulse_file: str,
    nominal_capacity_ah: float = 63.0,
    rest_before_s: float = 600.0,
) -> dict:
    """
    DCIR 펄스 파일에서 1-RC Thevenin 모델 파라미터 초기 식별.
    Returns: {
        "R0": float,       # Ohm
        "R1": float,       # Ohm
        "C1": float,       # F
        "tau": float,      # s = R1*C1
        "rmse": float,     # 단자전압 예측 오차
        "meta": {"file": str, "pulse_current_A": float, "soc_est": float},
    }
    """
```

**호환성 원칙**:
- 위 4개 함수 시그니처는 **후속 세션에서도 유지**. 변경이 필요하면 사용자에게 명시 고지 후 deprecate 경로 제공.
- 반환 스키마의 키 추가는 자유. 키 삭제·이름 변경은 major change.

---

## 5. `data_io.py` 설계

```python
def read_cycler_file(path: str) -> pd.DataFrame:
    """
    싸이클러 원시 파일(.txt/.csv) 읽어 정규화된 DataFrame 반환.
    반환 컬럼(필수): 'step', 'voltage', 'current', 'time_s'
    반환 컬럼(선택): 'temperature', 'cycle', 'ah', 'wh'
    컬럼 alias 처리:
      - step:        StepNo, Step, StepIndex, Step_Index
      - voltage:     Voltage, V, Vt, Voltage(V)
      - current:     Current, I, Current(A)
      - time_s:      TotalTime, Time, ElapsedTime, Time(s)
    인코딩: utf-8 → cp949 → euc-kr 순차 시도.
    """

def read_excel_sheet(path: str, sheet: str | int = 0) -> pd.DataFrame:
    """엑셀 시트 읽어 반환. 헤더 자동 감지는 호출자 책임."""

def detect_format(path: str) -> str:
    """'txt' | 'csv' | 'xlsx' | 'unknown' — 확장자 + 내용 시그니처로 판정."""
```

- 첫 작업: `02_실험_데이터/최근셀데이터/` 또는 `Module 데이터★★★★★/` 내 파일 **1개** 실제로 열어 컬럼 이름·인코딩·구분자 확인 → 위 alias 테이블 확정.
- 실제 포맷이 예상과 다르면 이 단계에서 alias 테이블을 보강하고, 그 결정을 본 문서 Changelog에 기록.

---

## 6. `chemistry_check.py` 판정 휴리스틱

1. **입력**: RPT 저율(0.05~0.2 C) 방전 파일 경로 + `nominal_capacity_ah`.
2. **처리**: `read_cycler_file` → 최장 저율 방전 스텝 추출 → `compute_dqdv` → 피크 검출(`scipy.signal.find_peaks`, prominence=임계).
3. **판정 규칙**:
   - **LFP**: 3.2~3.4 V 구간에 매우 높은 단일 피크, 나머지 구간 평탄.
   - **NMC**: 3.6~3.8 V와 3.9~4.0 V 사이 2~3개 완만한 피크.
   - **NCA**: NMC와 유사하나 피크가 더 낮고 넓음 (분리가 어려움 — 낮은 confidence).
   - 그 외: `unknown` + 이유 기술.
4. **출력**: 판정 결과 dict + `outputs/dqdv_25C_rpt0_v0.png` + `outputs/chemistry_판정_2026-04-20.md`.

> 휴리스틱 임계값은 **작업 중 실제 곡선 보고 튜닝**. 본 문서 Changelog에 최종 값 기록.

---

## 7. `ecm_identify.py` 식별 절차

1. **입력**: DCIR 펄스 파일 (CC 방전 펄스 + 휴지 구조).
2. **전제**: 펄스 직전 충분한 휴지로 OCV 안정 → 펄스 시작 직후 순간 전압 강하 = R₀. 펄스 중/후 지수 감쇠로 R₁·C₁ 추출.
3. **모델**: `V(t) = OCV - I·R₀ - I·R₁·(1 - exp(-t/τ))`, τ = R₁·C₁.
4. **식별**: `scipy.optimize.least_squares`로 파라미터 (R₀, R₁, C₁) 잔차 최소화.
5. **검증**: 재구성 잔차 RMSE < 5 mV (1 mΩ 수준 오차 가정). 실패 시 `rmse` 필드에 값만 싣고 사용자 경고.

---

## 8. 테스트 (최소 범위)

`tests/test_ocv_soc.py` — 합성 데이터 1케이스:
- `compute_dqdv`: 선형 V 감소 + 일정 전류 → 단조 dQ/dV 생성 여부 검증
- `extract_ocv_soc_from_rpt`: mock CSV 생성 후 round-trip → SOC 0~100% 범위 유지 검증

pytest 단일 실행(`pytest tests/`) 통과가 완료 기준.

---

## 9. 실행 순서 (TODO 매핑용)

1. `data_io.py` 작성 + 실제 파일 1개로 포맷 검증 **← 전제 리스크 해소 단계**
2. `ocv_soc.py` 리팩터 + `compute_dqdv` 추가 + smoke test
3. 25 °C RPT 1개로 OCV 추출 → `outputs/ocv_soc_25C_v0.csv` 저장
4. `chemistry_check.py` 작성 + 실행 → 판정 리포트 md 저장
5. `ecm_identify.py` 작성 + DCIR 1개로 실행 → json 저장
6. `tests/test_ocv_soc.py` 작성 + `pytest` 통과 확인
7. Spec v1 v1.2 Changelog 추가 (chemistry 확정·OCV·ECM 초기값 반영), Open 이슈 ②③⑤ 상태 갱신
8. `_tmp_inspect_excel.py` 삭제 (temp 정리)

---

## 10. 리스크와 대응

| 리스크 | 영향 | 대응 |
|---|---|---|
| 실제 파일 컬럼이 예상과 완전히 다름 | data_io 전부 재작업 | 1단계에서 우선 탐색. alias 테이블을 작업 결과로 확정. |
| 저율 방전 스텝이 RPT에 없음 | chemistry 판정 지연 | 대안: DCIR 전후 30분+ 휴지 구간의 OCV로 boundary만 추정, 판정은 보류. |
| DCIR 펄스가 너무 짧아 C1 식별 불안정 | ECM τ 오차 큼 | `rmse` 경고만 내고 값 저장. 후속에서 긴 펄스 데이터 확보. |
| 25 °C RPT 파일이 어느 것인지 불분명 | OCV 추출 위치 혼선 | 1단계 탐색에서 파일별 온도·cycle 메타 정리. |

---

## 11. 제약 (소스 정책)

- `data_analysis_ui.py` **수정 금지** (Gemini 담당).
- 공개 API(§4) 시그니처 변경 시 사용자에게 명시 고지.
- `outputs/` 폴더의 산출물은 덮어쓰기 가능. 소스 코드 파일(`.py`)은 덮어쓸 때 diff 보여줄 것.
- 승인 자동화 정책(`~/.claude/settings.json`) 하에서 진행 — 네트워크·git push·파괴적 명령은 여전히 수동.

---

## Changelog

- **2026-04-20 v1** (초판)
  - M 스코프 선언, 공개 API 4개 명시, 산출물 9개 정의
  - UI 제외 원칙, Gemini-Claude 분업 반영

- **2026-04-20 v1.1 (Task 1 정찰 결과 반영)**
  - **실데이터 CSV 발견**: 프로젝트 루트의 `셀 엑셀파일/` 과 `모듈엑셀파일/` 폴더가 두 겹 nested 구조라 초기에 놓쳤음. 실제 시계열 CSV 파일은 아래에 있음:
    - 셀: `셀 엑셀파일/셀 엑셀파일/CH{2,7}_{25,50}deg/{ACIR,DCIR,Pattern,RPT}/*.csv` — 총 258 파일
    - 셀 패턴주행: `셀 엑셀파일/셀 엑셀파일/열화셀 패턴주행/` — 24 파일
    - 모듈: `모듈엑셀파일/모듈엑셀파일/모듈데이터 엑셀파일(2022.01~2023.07)/CH{1,2}/{ACIR,DCIR,Pattern,RPT}/*.csv` — 601 파일
  - **cycle 커버리지 (CH2_25deg/RPT)**: 0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1460, 1580, 1640, 1800, 1900, ... (풍부)
  - **CSV 실제 컬럼 (셀)**: `State, Voltage(V), Current(mA), Capacity(mAh), Impedance(m\u03a9), Code, StepTime(H:M:S), TotTime(H:M:S), Grade, StepNo, Power(mW), wattHour(mWh), Temp(\u00b0C), Press, Type, CurCycle, TotCycle, TestName, Schedule, Channel, Module, Serial, DataSequence, Avg. Crt, Avg. Vtg, Capa. Sum(mAh), Char. Cap.(mAh), Dischar. Cap.(mAh), Meter, Start Time, End Time, SharingInfo, Goto Count, WattHour. Sum(mWh), Char. WattHour(mWh), DisChar. WattHour(mWh), Integral Cap.(mAh), Integral WattHour(mWh), CV Time(H:M:S)` (38+1 컬럼)
  - **CSV 실제 컬럼 (모듈)**: 셀과 유사하나 + `OvenTemperature(\u00b0C)`, `[001]~[003]AuxT(\u00b0C)` (3개 온도센서), `[004]~[017]AuxV(V)` (14S 모듈의 개별 셀 전압 14개), `Capacitance(F)` 등 추가. 총 90 컬럼.
  - **샘플링**: 1 Hz (StepTime 01.00초 간격).
  - **인코딩**: `cp949`. **구분자**: `,` (콤마).
  - **단위 주의**: 셀 CSV의 `Current(mA)`, `Capacity(mAh)`, `Power(mW)`, `wattHour(mWh)` — **mA·mAh** 단위. 모듈은 `Current(A)`, `Capacity(Ah)` — **A·Ah** 단위. `data_io.read_cycler_file`이 자동 단위 변환하여 표준(A, Ah)으로 반환해야 함.
  - **시간 형식**: `TotTime` = `"D0 00:00:00.10"` 같은 `D{days} HH:MM:SS.cs` 형식. 파서 필요.
  - **Type 컬럼**: `정전류`, `Pattern`, `정전압`, `휴지` 등 스텝 종류 구분.
  - **§5 `_ALIAS` 확정**:
    - `step`: `StepNo`
    - `voltage`: `Voltage(V)`
    - `current`: `Current(A)` (모듈) | `Current(mA)` (셀, 변환 필요)
    - `time_s`: `TotTime` 파싱 결과
    - `temperature`: `Temp(°C)` (셀) | `OvenTemperature(°C)` (모듈, 또는 `[001]AuxT` 평균)
    - `cycle`: `TotCycle`
    - `ah`: `Capacity(Ah)` | `Capacity(mAh)`/1000
  - **Task 3·4 실행용 RPT 샘플 파일**: `셀 엑셀파일/셀 엑셀파일/CH2_25deg/RPT/22_12_27_에기연 열화셀_25deg_1300cycle_RPT_ch2_M01Ch002(002).csv`
  - **Task 6 실행용 DCIR 샘플 파일**: `셀 엑셀파일/셀 엑셀파일/CH2_25deg/DCIR/22_12_27_에기연 열화셀_25deg_1300cycle_DCIR_ch2_M01Ch002(002).csv` (파일 존재 여부 확인 필요 — 없으면 `100cycle_DCIR` 파일로 대체)
  - **무시 대상 경로**: `02_실험_데이터/최근셀데이터/.../M01Ch002[002]/*.txt` 는 381 바이트 요약 파일만 있고 raw 시계열 없음. Plan의 원래 Task 1 명시된 이 경로들 대신 `셀 엑셀파일/셀 엑셀파일/CH2_25deg/` 하위 CSV 사용.
