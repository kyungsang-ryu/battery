# Codex (알고리즘) 작업 사양서 v1

**작성일**: 2026-04-23
**대상**: Codex (알고리즘·시뮬레이션·평가 담당 코딩 에이전트)
**상위 문서**:
- `2026-04-23_Codex_Antigravity_분업_Spec_v1.md` (책임 경계·인터페이스 계약)
- `2026-04-23_SCI논문_전략_v2.md` (논문 novelty·로드맵)
- `2026-04-20_SOC_SOH_통합추정_Spec_v1.md` (셀 사양·전체 사양 v1.1)

**노선 결정 (사용자 2026-04-23)**: **미드티어 SCI 허용**. 따라서 Stage A(Fractional ECM + Dual AEKF + Adaptive Q/R) 만으로 J. Energy Storage / IEEE TTE 노선 직진을 메인으로 한다. PINN-AEKF (Stage B/C)는 시간 여유 있을 때만 stretch.

**셀 chemistry (사용자 2026-04-23)**: **NCM 확정** (= NMC, 동일 물질의 한국식 표기). dQ/dV 판정은 검증 목적으로만 수행하고, 모델·OCV 룩업·코드 주석에 **NCM** 으로 표기 통일한다.

---

## 0. 시작 전 필독

본 문서를 작업 시작 시 매번 다시 읽는다. 분업 Spec(2026-04-23)을 위반하는 변경이 필요하면 **반드시 사용자 승인 후 분업 Spec을 먼저 갱신**한다.

**핵심 원칙 재고지**

- `algo/` 만 만진다. `ui/` 절대 금지.
- UI 라이브러리(streamlit, plotly, tkinter 등) import 금지.
- 모든 추정기는 `algo/estimators/base.py`의 `Estimator` 추상 클래스를 상속한다.
- 모든 시뮬레이션 결과는 `outputs/runs/<run_id>/` 1폴더 = 1실행 형태로 저장한다.
- 공개 API(분업 Spec §3) 시그니처 변경 시 사용자 승인 필요.

---

## 1. 데이터 카탈로그 (2026-04-23 정밀 조사 결과 + Pouch only 확정)

루트: `D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data`

**스코프 (사용자 확정 2026-04-23)**: 본 논문은 **Pouch 폼팩터·NCM chemistry 단일** 로 진행. 데이터는 두 축.

| 축 | dataset | 역할 |
|---|---|---|
| **셀 단위 (Pouch)** | §1.1 main_cell + §1.2 pouch_SOH | 메인 알고리즘 학습·검증 |
| **모듈 단위 (Pouch)** | §1.4 module (CH1) | Cross-scale (cell → module) 일반화 검증 |

§1.3은 18650 (원통형) 제외 처리, §1.5~§1.9는 보조·표준·중복 경고.

### 1.1 메인: JH3 셀 단위 (`셀 엑셀파일\셀 엑셀파일\`)

논문 메인 contribution이 사용할 데이터셋. **PNE 사이클러 CSV, cp949, 콤마 구분, 1 Hz 샘플링**. 컬럼 표준은 §1.7.

```
셀 엑셀파일\셀 엑셀파일\
├── CH2_25deg\          ← 채널 2, 온도 25 °C
│   ├── RPT\        (~30 파일)
│   ├── DCIR\       (DCIR + DCIR후 충전 별도)
│   ├── ACIR\
│   └── Pattern\
├── CH7_50deg\          ← 채널 7, 온도 50 °C
│   ├── RPT\        (~38 파일)
│   ├── DCIR\
│   ├── ACIR\
│   └── Pattern\
├── 전압하한 데이터파일\         ← 0 °C 데이터 (전압 하한 검증용)
│   ├── ch2 전압하한 데이터(최근)\
│   │   ├── RPT\         (cycle 0 만)
│   │   └── Pattern\     (cycle 100 만)
│   └── ch3 전압하한 데이터\
│       ├── RPT\         (cycle 0 만)
│       └── Pattern\     (cycle 100/101 만)
└── 열화셀 패턴주행\               (24 파일, 별도 패턴주행 시리즈)
```

**확정된 (channel, temperature) 매핑** (2026-04-23 v1.4 갱신 — 5/10/15 °C supplementary 추가)

| Channel | Temperature | 자료 종류 | 셀 정체성 | 비고 |
|---|---|---|---|---|
| ch2 | 25 °C | RPT, DCIR, ACIR, Pattern | JH3 #1 | **메인** |
| ch7 | 50 °C | RPT, DCIR, ACIR, Pattern | JH3 #2 | **메인** (가속 노화) |
| ch2/ch3 | 0 °C | RPT (cycle 0 만) | JH3 (전압하한 시리즈, 다른 개체) | Temperature 외삽 메인 |
| ch2/ch3 | 5 °C | Pattern (cycle 100 만) | 동상 | **Supplementary** (SOC 외삽만 — RPT 없음 → SOH 산출 X) |
| ch2/ch3 | 10 °C | Pattern (cycle 100, 200) | 동상 | Supplementary (SOC 외삽만) |
| ch2/ch3 | 15 °C | Pattern (cycle 100 만) | 동상 | Supplementary (SOC 외삽만) |

5/10/15 °C 데이터 위치: `셀 엑셀파일\셀 엑셀파일\전압하한 데이터파일\ch{2,3} 전압하한 데이터*\Pattern\`. 이 데이터는 **SOC 추정의 wide thermal envelope 일반화 검증** 보조용으로만 사용. SOH는 RPT 부재로 산출 불가 — 본문에서는 25/50 °C만 SOH 보고, supplementary 에서 5/10/15 °C SOC RMSE 만 보고.

채널이 곧 셀 개체. **셀 단위 split(cell-level split)을 하려면 ch2 vs ch7 두 셀만 가용**. 동일 channel 내에서는 시계열 시점 분할(time-ordered split) 또는 cycle 그리드 분할(condition-level split)을 사용.

**확정된 cycle 그리드**

- `CH2_25deg/RPT`: 0(=신셀), 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1460, 1580, 1640, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000.
- `CH7_50deg/RPT`: 위와 동일 + 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800 (가속 노화로 더 많은 cycle).
- 0 °C: cycle 0, 100, 101 만 (제한적).

**Spec v1.1의 "−15~45 °C × 1300~3200" 표기 정정 (사용자 확정 2026-04-23)**: 실제로는 **0/25/50 °C × 0~3800 cycle**. 단, **0 °C는 cycle 0~101 만**. **−15 °C, 45 °C 데이터는 본 폴더에 존재하지 않음 → 본 논문 대상 외**. 외삽 실험은 가용 범위(0/25/50 °C)와 pouch_SOH(25/40 °C) 안에서만 정의한다.

### 1.2 보조: pouch_SOH (`02_실험_데이터\pouch_SOH\`)

JH3와 동일 또는 유사 폼팩터(Pouch). 주행 패턴 SOH 시계열. 25/40 °C, ch1~ch8 다채널 → **multi-cell cross-validation 1순위 후보**.

**중요**: pouch_SOH의 노화 단위는 **사이클이 아니라 weeks** (5/10/15/20/25/30 weeks 등 — 실험 기간). 따라서 카탈로그·split·플롯에서 **`cycle` 컬럼과 별개로 `weeks` 컬럼**을 둔다. 두 단위를 한 컬럼에 섞으면 외삽 split의 의미가 깨짐. main_cell·module은 `cycle` 만, pouch_SOH는 `weeks` 만 채워지고 그 반대 쪽은 NaN.

```
02_실험_데이터\pouch_SOH\
├── pattern_MG_data\
│   ├── 25도\               (ch1, MG_5/10/15/20/25/30 weeks)
│   ├── 25도step\           (위 raw의 step 분리 버전)
│   ├── 40도\               (ch6, MG_5/10/15/20/25)
│   └── 40도step\
├── pattern_PVsmoothing_data\
│   ├── 25도\, 25도step\    (ch2, 12/24/36/48/60/72)
│   └── 40도\, 40도step\    (ch7, 12/24/36/48/60)
├── pattern_PowerQuality_data\
│   ├── 25도\, 25도step\    (ch3, 60/120/180/240/300/360)
│   └── 40도\, 40도step\    (ch8, 60/120/180/240/300)
├── matlabMat\               (.mat 후처리본, 13개 — 중복 있음)
│   └── step\               (위 .mat의 step 버전 6개 — 중복)
└── PatternData.m, capacityPlot.m, Temp_Time*.m  (MATLAB 스크립트, 참고만)
```

**활용 전략**: P3 외삽 벤치마크의 **multi-cell, multi-pattern cross-validation 데이터**로 사용. 25 °C / 40 °C 온도 boundary는 메인 데이터(25/50 °C)와 살짝 다른데, 이건 **temperature interpolation/extrapolation 실험**에 오히려 유리.

**주의**: `step` suffix 폴더(`25도step/`, `40도step/`, `matlabMat/step/`)는 같은 raw의 후처리본 — **카탈로그 등록 시 중복 제거 필요**. 우선 raw(`25도/`, `40도/`)를 정본으로.

### 1.3 ~~보조: 18650_SOH~~ — **본 논문 제외 확정 (사용자 2026-04-23)**

`02_실험_데이터\18650_SOH\` 의 **18650 원통형 셀**은 본 논문이 다루는 Pouch 폼팩터와 다름. 사용자 결정으로 **본 논문 대상에서 제외**. §1.8 무시 경로로 이동.

→ 본 논문은 **Pouch 폼팩터 일관성**을 유지: Pouch 셀 (main_cell + pouch_SOH 다채널) + Pouch 모듈 (module CH1) 두 축으로 구성. NASA PCoE 같은 외부 18650 데이터셋도 같은 사유로 옵션 한정.

### 1.4 메인 (Cross-Scale 검증축): Pouch 모듈 (`모듈엑셀파일\모듈엑셀파일\모듈데이터 엑셀파일(2022.01~2023.07)\`)

본 논문의 **두 번째 메인 데이터축**. Pouch 셀과 동일 chemistry(NCM)·동일 폼팩터 가정의 14S 모듈. 셀에서 학습한 알고리즘이 모듈에도 동작하는지 — **cross-scale (cell → module) 일반화** 검증.

```
모듈엑셀파일\모듈엑셀파일\모듈데이터 엑셀파일(2022.01~2023.07)\
└── CH1\
    ├── RPT\
    ├── ACIR\
    ├── DCIR\           (DCIR + DCIR 후 용량충전)
    └── Pattern\
        ├── 2023_01_08_25deg_2000cycle\
        │   ├── 2023_01_08_..._CH01.csv          (정본, 분할의 첫 부분)
        │   ├── 2023_01_08_..._CH01(0).csv       (이어지는 청크 1)
        │   ├── 2023_01_08_..._CH01(1).csv
        │   └── 2023_01_08_..._CH01(2).csv
        ├── 2023_01_13_25deg_2100cycle\          (5 청크)
        └── ...                                   (cycle별 폴더, 100 간격)
```

**중요 발견**:
- **CH1만 가용 (CH2 폴더 부재 — 사용자 확정 2026-04-23)**. 모듈 supplementary는 CH1 단독으로 진행.
- **Pattern 데이터는 cycle별 서브폴더 + 분할 파일 구조**. `CH01.csv`가 정본, `CH01(0).csv`~`CH01(4).csv`가 시간순 이어지는 청크. → `data_io`에 분할 자동 통합 함수 필요 (Task P0.5에 추가).
- 모듈 컬럼은 ~90개 (14S 셀 전압 + Aux 온도 3채널 + Capacitance). 셀 스키마와 다름 → 모듈 전용 alias 테이블 필요.
- 본 논문 메인은 **셀 단위**. 모듈은 **supplementary 또는 향후 확장**으로만.

### 1.5 보조: KTL 모듈 측정본 (`02_실험_데이터\모듈내 셀간 전압편차 경향확인(EXCEL)\`)

KTL(한국산업기술시험원)이 측정한 모듈 RPT/ACIR. cycle 100~1300, 25 °C 만. CH01, CH02 두 채널. .xlsx + .csv 혼재. **모듈 셀간 편차 분석용** — 본 논문 SOC/SOH 알고리즘 검증과는 직결되지 않음. **무시 가능, 단 모듈 쪽 자료가 부족하면 보조 활용**.

### 1.6 NCM 셀 사양 (Spec v1.1 §1.4 재확인, JH3 cell 사양서.pdf 기준)

| 항목 | 값 | 비고 |
|---|---|---|
| Form factor | Pouch (Wing folded + PET tape 6-point sealing) | |
| 치수 (T×W×L) | 16 × 100.2 × 352.5 mm | |
| 무게 | 1,175 g | |
| **Capacity** | **63.0 Ah** | ECM `Cn₀` 초기값 |
| Nominal Voltage | 3.7 V | |
| Operating Voltage | 3.0 ~ 4.2 V | OCV 룩업 boundary |
| Energy | 233 Wh | |
| Cycle Life | 80% @ 4,000 cycle | SOH 80% = EOL |
| **DCIR** | 1.03 ± 0.25 mΩ (25 °C, SOC 30%) | ECM `R0` 초기값 |
| **ACIR** | 0.575 ± 0.175 mΩ (25 °C, SOC 30%) | EIS 보조 검증 |
| Chemistry | **NCM** (사용자 확정 2026-04-23) | dQ/dV 검증으로 sanity check |

PDF에 chemistry 명시 없음 → 사용자 확정 정보가 정본. dQ/dV 분석 결과가 NCM과 모순되면 즉시 사용자에게 보고.

### 1.7 RPT/Pattern 파일 컬럼 표준 (PNE 셀 데이터)

cp949, 콤마, 1 Hz. 38+1 컬럼. 주요:

```
State, Voltage(V), Current(mA), Capacity(mAh), Impedance(mΩ),
Code, StepTime(H:M:S), TotTime(H:M:S), Grade, StepNo,
Power(mW), wattHour(mWh), Temp(°C), Press, Type,
CurCycle, TotCycle, TestName, Schedule, Channel, Module, Serial,
DataSequence, Avg. Crt, Avg. Vtg, Capa. Sum(mAh), Char. Cap.(mAh),
Dischar. Cap.(mAh), Meter, Start Time, End Time, SharingInfo,
Goto Count, WattHour. Sum(mWh), Char. WattHour(mWh), DisChar. WattHour(mWh),
Integral Cap.(mAh), Integral WattHour(mWh), CV Time(H:M:S)
```

단위 주의: **셀은 mA·mAh**, **모듈은 A·Ah** (양쪽 모두 Ah/A로 정규화). 시간은 `D{days} HH:MM:SS.cs` → 초 변환.
`data_io.py`의 `_ALIAS`/`_MA_COLS`/`_HMS_COLS`는 이미 위에 맞춰져 있음. 모듈 컬럼은 별도 alias 추가 필요 (Task P0.5에서).

### 1.8 무시할 경로

| 경로 | 사유 |
|---|---|
| `02_실험_데이터/최근셀데이터/` 전체 | **PNE 사이클러 원본 raw** (.txt + .sch + .cyc + .ini + StepEnd.csv). PNE 전용 프로그램 필요 → 분석에는 `셀 엑셀파일/셀 엑셀파일/`의 csv 변환본 사용 (사용자 확정 2026-04-23). 본 폴더 파싱 코드 작성 금지 |
| `02_실험_데이터/Cell 데이터★★★★★/180504~180508_*` | 2018년 dithering/charging/discharging 실험 — **사용자 결정 2026-04-23: 본 논문에서 제외**. 다른 셀 시리즈로 추정 |
| `02_실험_데이터/18650_SOH/` | 18650 원통형 셀 — **사용자 결정 2026-04-23: Pouch 폼팩터 일관성 유지를 위해 본 논문에서 제외** |
| `99_상관없는_자료_및_기타/` | 옛 MATLAB 스크립트, 무시 |
| `03_매뉴얼_및_참고자료/` | 매뉴얼·PNNL 문서 등 참고용. 입력 아님 |
| `01_분석보고서_및_사양/PPt 파일/` | 발표자료. 참고만 (특히 `JH3_63000mAh_150~1150Cycle 충방전 특성 실험 데이터 분석.pptx`, `SoH SoC 추정기법.pptx`, `EECM 및 Parameter 추정.pptx`, `220805_발표자료(이후 용량감소율, Hysteresis 수정 추가본).pdf` 는 향후 논문 작성 시 인용·검증에 유용) |
| `01_분석보고서_및_사양/모듈 및 셀 열화분석 정리본★★★★★/` | 분석본 .xlsx. 실험 raw 아님. 결과 sanity check 용 |

### 1.9 ⚠️ 중복·정본 경고

같은 데이터가 여러 위치에 복제된 사례. **정본만 사용**.

| 데이터 | 정본 (사용) | 부분집합/복제본 (무시) |
|---|---|---|
| 셀 raw CSV | `data\셀 엑셀파일\셀 엑셀파일\CHx_NNdeg\...` | `data\01_분석보고서_및_사양\셀 실험 정리본\셀 엑셀파일\CHx_NNdeg\...` (RPT 누락, `desktop.ini` 시스템 파일 섞임, cycle 100~1300 부분집합만) |
| pouch_SOH MATLAB | `data\02_실험_데이터\pouch_SOH\matlabMat\PowerQualityStep25.mat` 등 | `data\02_실험_데이터\pouch_SOH\matlabMat\step\PowerQualityStep25.mat` 등 (6쌍 동일 파일명) |
| 분석 정리본 .xlsx | `data\01_분석보고서_및_사양\모듈 및 셀 열화분석 정리본★★★★★\` | `data\셀 엑셀파일\` 루트, `data\모듈엑셀파일\` 루트 (같은 파일명 .xlsx) |
| PNNL 시험 패턴 | `data\03_매뉴얼_및_참고자료\시험관련자료\` | `data\03_매뉴얼_및_참고자료\시험관련자료\시험 패턴\PNNL protocol\` |

`data\01_분석보고서_및_사양\셀 실험 정리본\셀 엑셀파일\CH2_25deg\` 안의 `desktop.ini` 같은 Windows 시스템 파일은 카탈로그 스캔 시 **확장자 화이트리스트(`.csv`만)** 로 자동 배제.

---

## 2. 디렉터리 분할 + 마이그레이션 (P0의 첫 작업)

분업 Spec §2에 정의된 트리로 일괄 이동한다. **반드시 단일 PR**.

### 2.1 이동 매핑

| 현재 위치 | 신규 위치 |
|---|---|
| `data_io.py` | `algo/data_io.py` |
| `ocv_soc.py` | `algo/ocv/ocv_soc.py` (리팩터 + `compute_dqdv` 추가) |
| `tests/test_data_io.py` | `tests/algo/test_data_io.py` |
| `tests/__init__.py` | `tests/__init__.py`, `tests/algo/__init__.py` 둘 다 생성 |

### 2.2 신규 생성 (빈 패키지)

```
algo/__init__.py
algo/loaders/__init__.py
algo/ocv/__init__.py
algo/ecm/__init__.py
algo/estimators/__init__.py
algo/runners/__init__.py
algo/evaluation/__init__.py
algo/schemas.py
outputs/{ocv_soc,ecm,runs,figures}/.gitkeep
```

### 2.3 import 경로 일괄 수정

이동 후 `from data_io import ...` → `from algo.data_io import ...` 전부 grep + replace. Antigravity 영역의 `ui/data_analysis_ui.py`도 확인은 하되 직접 고치지는 말고 분업 Spec §10 핸드오프 노트로 알린다.

### 2.4 검증

```bash
python -m pytest tests/algo -q
```

기존 3개 통과 유지가 마이그레이션 성공 기준.

---

## 3. P0 — 백엔드 기초 완성 (1주)

### Task P0.0 — 보조 데이터 포맷 정찰 (1일, 신규)

§1.2 pouch_SOH, §1.4 module의 형식이 메인 셀과 다르므로 본격 작업 전 한 번 정찰. 산출물은 `outputs/recon_2026-04-23.md` 한 장.

1. **모듈 CSV 컬럼** 정찰: 14S 셀 전압 컬럼명, Aux 온도 컬럼명, Capacitance 컬럼 → 모듈 전용 alias 후보 작성.
   - 입력: `모듈엑셀파일\모듈엑셀파일\모듈데이터 엑셀파일(2022.01~2023.07)\CH1\RPT\2023_01_12_에기연_열화모듈_CYCLE_25deg_2000cycle_RPT_CH01.csv`
2. **모듈 Pattern 분할**: cycle 폴더 안의 `CH01.csv` + `CH01(N).csv` 들의 `time_s` 연속성·`StepNo` 연속성 확인. merge 알고리즘 가설 검증.
   - 입력: `모듈엑셀파일\모듈엑셀파일\모듈데이터 엑셀파일(2022.01~2023.07)\CH1\Pattern\2023_01_08_25deg_2000cycle\` 폴더 전체.
3. **pouch_SOH `25도/` vs `25도step/`** 차이 정찰: step 버전이 raw에서 step별로 split만 한 건지, 아니면 후처리(필터·다운샘플)가 들어갔는지.
   - 입력: 같은 파일의 두 버전 1쌍.

산출 `outputs/recon_2026-04-23.md` 에는 위 3건의 결론을 한 줄씩 기록 (컬럼/연속성/특이사항). 이 결과로 Task P0.5의 `data_io` 보강 범위가 결정된다.

(18650 .txt 정찰은 18650_SOH 본 논문 제외 결정으로 삭제. 향후 NASA PCoE 등 외부 18650 도입 시 별도 Task로.)

### Task P0.1 — `algo/ocv/ocv_soc.py` 리팩터 (Plan v1.1 Task 3 미완료분 처리)

- `data_io.read_cycler_file` 사용으로 변경 (현재는 `pd.read_csv` 직접 호출, 컬럼명도 옛날 이름).
- `compute_dqdv(voltage, current, time_s, smoothing_window=51) -> pd.DataFrame[V, dQdV]` 신규 함수 추가.
- `extract_ocv_soc_from_rpt(file_path, nominal_capacity_ah=63.0) -> dict` 시그니처 유지.
- CLI: `python -m algo.ocv.ocv_soc <file> [<capacity_Ah>]` 추가.
- 테스트: `tests/algo/test_ocv_soc.py` 신규. 합성 RPT 파일 1개 + dQ/dV 합성 1개로 round-trip.

### Task P0.2 — OCV 룩업 3종 추출 (25/50/0 °C)

- **25 °C** 입력: `셀 엑셀파일\셀 엑셀파일\CH2_25deg\RPT\22_09_06_에기연 열화셀_25deg_RPT_ch2_M01Ch002(002).csv` (cycle 0, 가장 fresh).
- **50 °C** 입력: `셀 엑셀파일\셀 엑셀파일\CH7_50deg\RPT\22_09_06_에기연 열화셀_50deg_RPT_ch7_M01Ch007(007).csv` (cycle 0).
- **0 °C** 입력: `셀 엑셀파일\셀 엑셀파일\전압하한 데이터파일\ch2 전압하한 데이터(최근)\RPT\23_06_21_에기연 열화셀_0deg_0cycle_RPT_ch2_M01Ch002(002).csv` (cycle 0, ch2와는 다른 셀임에 주의).
- 처리: 저율 충·방전 스텝 식별 → SOC-OCV 평균.
- 산출: `outputs/ocv_soc/{25C,50C,0C}_cycle0_v0.csv` (SOC 0..100%, 1% 간격).
- 산출: `outputs/ocv_soc/{25C,50C,0C}_cycle0_v0.png` (방전·충전·평균 3선 플롯).
- 산출: `outputs/ocv_soc/temp_correction_v0.csv` — 온도 보정항 = 50 °C/0 °C OCV − 25 °C OCV (SOC bin별).
- 검증: 운용 범위 3.0~4.2 V 안에 들어가는지, NCM 곡선 형태가 단조 + 부드러운지.

**주의**: 0 °C 셀은 ch2 (전압하한 시리즈, **메인 ch2와 다른 개체**)다. 따라서 0 °C OCV는 셀 개체차 + 온도차가 섞임 — 본 결과는 P2 단계의 fast filter가 사용할 boundary 추정용으로만, 정밀 비교는 cell-level split에서 따로.

### Task P0.3 — Chemistry 검증 (NMC 확정 가정)

- 사용자 결정으로 **NMC 확정**. 본 작업은 **검증** 용.
- `algo/ocv/chemistry_check.py` 작성, `classify_chemistry(dqdv_df) -> dict` 시그니처(분업 Spec §3.2).
- 25 °C cycle 0 RPT의 저율 방전으로 dQ/dV 계산 → 피크 검출.
- 기대: 3.6~3.8 V, 3.9~4.0 V 부근에 완만한 피크 2~3개 관찰.
- 산출:
  - `outputs/ocv_soc/dqdv_25C_cycle0.png`
  - `outputs/ocv_soc/chemistry_검증_2026-04-23.md` ("NMC 가정과 dQ/dV 피크 일치/불일치 + confidence" 기재)
- 만약 NMC와 모순되는 결과가 나오면 **즉시 사용자에게 보고**, 코드는 NMC로 일단 진행.

### Task P0.4 — DCIR 1-RC 초기 파라미터 식별

- 입력 1차: `셀 엑셀파일\셀 엑셀파일\CH2_25deg\DCIR\23_01_05_에기연 열화셀_25deg_1300cycle_DCIR_ch2_M01Ch002(002).csv`. 더 fresh가 필요하면 `22_09_27_..._100cycle_DCIR_ch2`(부분집합 경로 `01_분석보고서/.../셀 실험 정리본/`에 있는데 정본이 루트 `셀 엑셀파일/`에 없으면 해당 100cycle 부분만 부분집합 사용 — 단, **메인 카탈로그에는 등록하지 않고 일회성 사용**).
- `algo/ecm/ecm_identify.py` 작성, `identify_1rc(...) -> dict` (분업 Spec §3.2 시그니처).
- 산출: `outputs/ecm/1rc_25C_cycle1300_v0.json`.
- 검증: `R0` 추정값이 JH3 스펙(1.03 ± 0.25 mΩ @ 25 °C, SOC 30%)과 같은 자릿수면 PASS. cycle 1300이라 노화로 R0가 약간 더 높게 나올 수 있음 (정상).
- 추가 (보너스): 같은 방식으로 50 °C DCIR 1-RC 식별 → `outputs/ecm/1rc_50C_cycle1300_v0.json`. R0 비교로 온도 의존성 확인.

### Task P0.5 — `algo/loaders/kier.py` 작성 (데이터셋 카탈로그)

§1.1, §1.2, §1.4의 3종 데이터(Pouch 셀 메인 + Pouch 셀 다채널 + Pouch 모듈)를 통합 카탈로그로 색인. **정본 경로만** 스캔 (§1.9 중복 무시).

```python
# algo/loaders/kier.py

KIER_ROOT = Path(r"D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data")

# 정본 스캔 경로 — 다른 경로의 동명 파일은 무시
# 18650_SOH는 사용자 결정으로 본 논문 제외 (Pouch 폼팩터 일관성 유지)
SCAN_ROOTS = {
    "main_cell":    KIER_ROOT / "셀 엑셀파일" / "셀 엑셀파일",
    "pouch_soh":    KIER_ROOT / "02_실험_데이터" / "pouch_SOH",
    "module":       KIER_ROOT / "모듈엑셀파일" / "모듈엑셀파일" / "모듈데이터 엑셀파일(2022.01~2023.07)",
}

def list_kier_files(roots: dict | None = None) -> pd.DataFrame:
    """전체 데이터를 표준 카탈로그 DataFrame으로.

    컬럼:
      dataset  : 'main_cell' | 'pouch_soh' | 'module'
      channel  : 'ch1'~'ch8' | 'CH01' (없으면 NaN)
      temp_C   : 0 | 25 | 40 | 50 (없으면 NaN)
      cycle    : int — main_cell, module 의 노화 단위 (없으면 NaN)
      weeks    : int — pouch_SOH 전용 노화 단위 (없으면 NaN)
      type     : 'RPT' | 'DCIR' | 'DCIR후충전' | 'ACIR' | 'Pattern'
                 | 'Pattern_MG' | 'Pattern_PVSmoothing' | 'Pattern_PowerQuality'
                 | 'capacity_check'
      date     : YYYY-MM-DD (파일명 또는 폴더명에서)
      file_path: 절대경로
      pattern_chunks: List[Path] | None  (모듈 Pattern 분할 파일들의 ordered list. 정본 파일은 chunks[0])

    원칙: cycle 과 weeks 는 **상호 배타** (한 행에서 한쪽만 채워짐).
    별도 컬럼으로 두는 이유: 두 단위는 의미가 달라서 외삽 split·플롯·통계에서
    혼용하면 결과가 왜곡됨 (사용자 결정 2026-04-23).
    """

def load_kier_run(file_path: str, merge_chunks: bool = True) -> dict:
    """단일 파일 로드 (또는 모듈 Pattern 분할 파일들 merge).

    Returns:
        {"df": pd.DataFrame (분업 Spec §4.1 TimeSeriesSchema),
         "meta": {"dataset", "channel", "temp_C", "cycle", "type", "date",
                   "n_chunks", "schema_variant"}}
    """

def merge_pattern_chunks(chunk_paths: list[Path]) -> pd.DataFrame:
    """모듈 Pattern 분할 파일들을 시간순 정합하여 하나의 DataFrame으로.
    각 청크의 마지막 time_s + 다음 청크의 첫 time_s 사이 점프 보정.
    StepNo 연속성 보장."""
```

**파일명 정규식** (메인 셀 / pouch / 모듈 3종):

| dataset | 정규식 패턴 (예시) |
|---|---|
| main_cell | `(\d{2}_\d{2}_\d{2})_에기연 열화셀_(?P<temp>\d+)deg_(?P<cycle>\d+)cycle_(?P<type>RPT\|DCIR\|DCIR후 충전\|ACIR\|Pattern)_(?P<channel>ch\d+)_M01Ch\d+\(\d+\)\.csv` |
| pouch_soh | `(?P<pattern>MG\|PVSmoothing\|PowerQuality)(?:_(?P<temp>\d+)도)?_(\d{2}_\d{2}_\d{2})_\w+_(?P<weeks>\d+)_(?P<channel>ch\d+)_M01Ch\d+\(\d+\)\.csv` (캡처된 weeks → catalog의 `weeks` 컬럼으로, `cycle`은 NaN) |
| module | `(\d{4}_\d{2}_\d{2})_에기연_열화모듈_CYCLE_(?P<temp>\d+)deg_(?P<cycle>\d+)cycle(_RPT\|_ACIR\|_DCIR\|_DCIR 후 용량충전\|)_(?P<channel>CH\d+)(?:\((?P<chunk>\d+)\))?\.csv` |

**모듈 Pattern 분할 처리** (§1.4 발견):
- `<...>_CH01.csv` (정본, chunk 없음 = chunk 0)
- `<...>_CH01(0).csv`, `<...>_CH01(1).csv`, ... (이어지는 청크들)
- `list_kier_files()`는 정본만 row로 등록하고 `pattern_chunks` 필드에 ordered list로 매핑.
- `load_kier_run(merge_chunks=True)` 호출 시 자동으로 `merge_pattern_chunks()` 실행.

**카탈로그 덤프**:
- `outputs/catalog_kier_v0.csv` — 전체 카탈로그 (Antigravity의 Data Explorer가 사용).
- `outputs/catalog_summary_v0.md` — dataset × (channel, temp_C, type) × cycle 그리드 요약 표.

**테스트** (`tests/algo/test_kier_loader.py`):
- 합성 파일 3종(메인 셀, pouch, 모듈) 각 1개 + 모듈 분할 청크 3개로 정규식·merge 동작 검증.
- 정본 vs 부분집합 경로 충돌이 없는지 (§1.9 중복 무시 확인).

### Task P0.6 — 환경 정합 검증

- `pip install -e ".[dev]"` 후 `python -m pytest tests/algo -q` 통과.
- 만약 Antigravity가 아직 `pyproject.toml`을 안 만들었다면, **본인은 만들지 말고** 사용자에게 알리고 임시로 `requirements.txt` 갱신만.

---

## 4. P1 — Baseline Zoo (2주)

분업 Spec §3.3의 `Estimator` 추상 클래스를 먼저 확정한 후, baseline 6종을 차례로 구현. (전략 v2의 11종에서 미드티어 노선에 맞춰 6종으로 축소.)

### Task P1.1 — `algo/estimators/base.py`

```python
from abc import ABC, abstractmethod
from typing import Any, ClassVar
import pandas as pd

class Estimator(ABC):
    name: ClassVar[str]
    def __init__(self, config: dict): self.config = config
    @abstractmethod
    def fit(self, train_runs: list[dict]) -> None: ...   # Kalman 계열은 noop
    @abstractmethod
    def step(self, v: float, i: float, t: float, T: float | None = None) -> dict: ...
    @abstractmethod
    def run(self, df: pd.DataFrame) -> pd.DataFrame: ...
    def to_config(self) -> dict: return self.config
    @classmethod
    def from_config(cls, cfg: dict) -> "Estimator": return cls(cfg)
```

`algo/estimators/__init__.py`에 `REGISTRY: dict[str, type[Estimator]]` 정의 + 자동 등록 데코레이터.

### Task P1.2 — Baseline 6종 구현

| 우선 | 모듈 | 구현 | 비고 |
|---|---|---|---|
| 1 | `algo/estimators/ah_counting.py` | Coulomb counting (no feedback) | 가장 단순, sanity 기준 |
| 2 | `algo/estimators/ocv_lookup.py` | 휴지 시간 ≥ X분일 때만 OCV→SOC 보정 | OCV 룩업(Task P0.2) 사용 |
| 3 | `algo/estimators/ekf.py` | 1-RC ECM EKF (SOC만) | filterpy 사용 |
| 4 | `algo/estimators/ukf.py` | 1-RC UKF | filterpy `UnscentedKalmanFilter` |
| 5 | `algo/estimators/dual_ekf.py` | Dual EKF (SOC + R0/Cn 분리 추정) | non-adaptive |
| 6 | `algo/estimators/dual_ukf.py` | Dual UKF | 비교 baseline |

각 추정기는:
- `tests/algo/test_<name>_contract.py` — `Estimator` 계약 충족 확인 (합성 데이터로 step·run 동작).
- 학습/캘리브레이션 필요 없으면 `fit`은 no-op.

### Task P1.3 — `algo/runners/run_simulation.py`

```bash
python -m algo.runners.run_simulation \
    --estimator dual_ekf \
    --dataset kier --temp 25 --cycle 1300 --channel ch2 \
    --tag bench-v0
```

- 산출 디렉터리: `outputs/runs/<run_id>/` (분업 Spec §9). `run_id` 자동 생성.
- 산출 파일: `config.json`, `results.parquet`, `metrics.json`, `log.txt`.

### Task P1.4 — `algo/evaluation/metrics.py`

함수 5개: `rmse(y_true, y_pred)`, `mae`, `max_abs_error`, `picp(y_true, y_lower, y_upper)`, `nll(y_true, y_pred, y_std)`.
+ `summarize_run(results_df, ground_truth_df) -> dict` (분업 Spec §4.3 MetricsReport 형태).

**Ground truth 산출 규칙**:
- `soc_truth`: Coulomb counting 기준 (RPT 처음을 SOC=100%로 normalize, 또는 OCV 룩업 기준 휴지 시점 보정).
- `soh_truth`: 사이클 RPT의 dis-/charge capacity / 63 Ah × 100.

### Task P1.5 — `algo/runners/run_benchmark.py`

```bash
python -m algo.runners.run_benchmark --estimators ah_counting,ocv_lookup,ekf,ukf,dual_ekf,dual_ukf \
    --dataset kier --temps 25,50 --cycles 100,500,1000,1500,2000,2500,3000 --tag bench-v1
```

- 한 번 실행으로 모든 (추정기 × 조건) 매트릭스 → `outputs/runs/bench-v1/summary.csv`.

---

## 5. P2 — Stage A 메인 contribution (3주)

미드티어 노선의 메인. 다음 3개 핵심 컴포넌트.

### Task P2.1 — `algo/ecm/fractional_ecm.py`

- Fractional-Order Model (FOM): R0 + R1 || CPE(α) (CPE = Constant Phase Element).
- `identify_fractional(file_path, nominal_capacity_ah=63.0) -> dict`. 반환 키 분업 Spec §4.5: `{"model": "FOM", "R0", "R1", "C1", "alpha", "rmse_V", "meta"}`.
- 정수 1-RC, 2-RC도 옵션으로 둠 (`identify_2rc()`).
- 테스트: 합성 펄스로 α 회수 검증.

### Task P2.2 — `algo/estimators/dual_aekf.py` (Stage A 본체)

```
[V, I, T] ─┬─► Fast Filter (AEKF, dt = 1s)        ──► SOC, V1, V2
           │       ↑ θ = [R0, R1, Cn]
           │       │
           └─► Slow Filter (cycle-scale)          ──► SOH (= Cn / Cn0)
                   ↑
                   Adaptive Q/R scheduler  f_Q, f_R(T, SOH_hat)
```

- Fast 필터: AEKF (innovation-based + 본 연구의 T·SOH 룩업 가중).
- Slow 필터: parameter EKF, 사이클 단위 갱신.
- Adaptive Q/R: 오프라인 학습 룩업표 또는 얕은 MLP. 학습은 `fit(train_runs)` 안에서.
- 시간 척도 분리: fast = 1 Hz, slow = 사이클 종료 시점에만.
- 테스트: 합성 noise·온도 시나리오에서 SOC RMSE < 2%.

### Task P2.3 — Adaptive Q/R 스케줄러

`algo/estimators/dual_aekf.py` 내부 또는 `algo/estimators/_adaptive_scheduler.py`로 분리.

- 입력: `T_k`, `SOH_hat_k`. 출력: `Q_k`, `R_k` 매트릭스 (또는 스칼라 게인).
- 오프라인 학습: KIER 데이터의 (T, cycle) 그리드에서 정답 RMSE를 최소화하도록 Q, R 스케일 학습.
- 함수: `learn_qr_lookup(train_runs, base_Q, base_R) -> {(T_bin, SOH_bin): (Q_scale, R_scale)}`.
- 시각화: 25 °C × cycle, 50 °C × cycle 평면의 Q/R 히트맵 → `outputs/figures/qr_schedule_heatmap.png`.

### Task P2.4 — Stage A 벤치마크 실행

P1.5의 `run_benchmark` 확장. `dual_aekf`까지 포함한 7종 비교.
- 산출: `outputs/runs/bench-stageA/summary.csv`, `outputs/figures/fig_stageA_rmse_box.pdf` 등.
- 결과 요약을 `outputs/runs/bench-stageA/REPORT.md`로 자동 생성 (Antigravity가 페이지에 그대로 렌더).

---

## 6. P3 — 외삽 벤치마크 + 일반화 (3주)

### Task P3.1 — Split 프로토콜 구현

`algo/evaluation/splits.py`:
- `cell_level_split(catalog, test_channels) -> (train, test)` (CH2 학습 / CH7 테스트 등)
- `condition_level_split(catalog, test_temps, test_cycle_ranges)` — KIER 단일셀 다조건 분리
- `time_ordered_split(df, train_ratio=0.7)` — 단일 파일 내 시점 분리
- `extrapolation_split(catalog, train_corner, test_corner)` — unseen (T, cycle) 코너

### Task P3.2 — 외삽 실험 (실데이터 그리드 기반)

§1.1의 실제 cycle 그리드에 맞춰 정의.

**Split 1 — Aging extrapolation (메인)**
- 학습: 25 °C(ch2) × cycle ∈ {100, 200, ..., 1500} ∪ 50 °C(ch7) × cycle ∈ {100, 200, ..., 1500}.
- 테스트: 25 °C × cycle ∈ {2000, 2500, 3000} (unseen aging) ∪ 50 °C × cycle ∈ {2500, 3000, 3500, 3800} (unseen aging extreme).
- 메트릭: 학습 cycle 범위에서의 RMSE vs 테스트 cycle 범위에서의 RMSE 증가율.

**Split 2 — Temperature extrapolation**
- 학습: 25 °C 전체 + 50 °C 전체 (cycle 무관).
- 테스트: 0 °C 전체 (cycle 0/100/101 만, ch2/ch3 두 셀).
- 주의: 0 °C 데이터는 다른 셀 개체 → cell + temp 외삽 동시. **이중 외삽 결과는 별도 표기**.

**Split 3 — Cell extrapolation (제한)**
- 학습: ch2(25 °C) 전체.
- 테스트: ch7(50 °C) 전체. (또는 반대)
- 한계: 두 셀이 서로 다른 온도에서 노화되었기 때문에 순수한 cell 외삽이 아님 (cell + temp 혼합). 제한 표기 후 보고.

**Split 4 — Cross-dataset (multi-cell, multi-pattern)**
- 학습: 메인 셀(ch2/ch7) 전체 (cycle 단위).
- 테스트: pouch_SOH (ch1~ch8, MG/PVSmoothing/PowerQuality 패턴, 25/40 °C, **weeks 단위 노화**).
- 노화 단위가 다르므로 SOH 비교 시 두 단위를 한 그래프에 섞지 말고 **별도 panel**로. SOC 비교는 노화 단위 무관하게 가능.

**Split 5 — Cross-pattern (pouch_SOH 내부)**
- 학습: pouch_SOH MG + PVSmoothing.
- 테스트: pouch_SOH PowerQuality (unseen 주행패턴).
- 동일 셀종·온도에서 unseen 주행 패턴 일반화 확인.

**비교 대상**: P2의 7종.

**산출**:
- `outputs/runs/bench-extrap-aging/`, `bench-extrap-temp/`, `bench-extrap-cell/`, `bench-extrap-cross/`.
- `outputs/figures/fig_extrap_heatmap.pdf` (4개 split RMSE 증가율 히트맵).

### Task P3.3 — Cross-Scale 일반화 (cell → module, **신규 메인**)

18650 외삽 대신 **Pouch 셀 → Pouch 모듈** cross-scale 일반화로 대체. 같은 chemistry·동일 폼팩터의 다른 스케일에서 알고리즘이 어디까지 작동하는지 측정.

**메커니즘**:
- 14S 모듈은 셀 14개 직렬. 모듈 단자전압 V_module ≈ Σ V_cell (이상적). 실제로는 셀간 편차·접촉저항으로 살짝 다름.
- 본 알고리즘은 셀 단위에서 학습됐는데, 모듈 데이터에 적용 시 **(a) 모듈 평균 셀 V·I 로 스케일링** 또는 **(b) 모듈 전체 V·I 로 그대로 적용 후 파라미터 재캘리브레이션** 두 시나리오 비교.

**Split 6 — Cross-Scale (cell → module)**
- 학습: main_cell ch2/ch7 전체 (cycle, 25/50 °C).
- 테스트: module CH1 전체 (cycle, 25 °C, ~3000 cycle).
- 두 시나리오 (a) cell-equivalent (Vmod/14, Imod), (b) module-direct (Vmod, Imod with re-scaled R0/Cn) 모두 비교.
- 산출: `outputs/runs/bench-cross-scale/`, `outputs/figures/fig_cross_scale_cell_to_module.pdf`.
- contribution: "Pouch NCM 셀 학습 알고리즘이 동일 chemistry 14S 모듈에서 [N]% 이내 SOC RMSE 유지" 같은 결론 서술.

**(선택) NASA PCoE 도입**: 본 논문 미드티어 노선에서는 필수 아님. P3 1~2 단계가 끝나고 reviewer 어필 더 필요하면 NASA 18650 도입 — 단, "form factor 다른 셀로 일반화" 라는 별도 contribution으로만, 메인 표는 Pouch 일관성 유지.

---

## 7. P4 — Stretch: PINN-AEKF (4주, 선택)

전략 v2 §4의 PINN-AEKF. **P3까지 무사 완료 + 시간 남을 때만 착수**. 미드티어 노선에서는 생략 가능.

### Task P4.1 — `algo/estimators/pinn_aekf.py`

분업 Spec §3.3 인터페이스 준수. fit에서 multi-task loss로 NN 학습, step/run에서 AEKF + NN residual.

### Task P4.2 — UQ 동반 (PICP, NLL)

- ensemble (5~10 models) 또는 variational dropout으로 점추정 + 표준편차 출력.
- `picp_95`, `nll` 평가지표 추가.

### Task P4.3 — Final benchmark + 외삽 결과 갱신

- `outputs/runs/bench-pinn/` + `outputs/figures/fig_paper_main.pdf`.

---

## 8. P5 — 논문 그림·표 자동 생성 (1주)

### Task P5.1 — `algo/evaluation/plots.py` 확장

함수:
- `plot_soc_trajectory(true, pred, std=None) -> Figure`
- `plot_soh_trend_over_cycles(catalog, results) -> Figure`
- `plot_residual_histogram(residuals) -> Figure`
- `plot_extrapolation_heatmap(extrap_df) -> Figure`
- `save_paper_figure(fig, name, dpi=300, format='pdf')` — `outputs/figures/`에 저장

### Task P5.2 — 논문용 Figure 자동 생성 스크립트

`algo/runners/make_paper_figures.py`:
- benchmark 결과 폴더(들)을 읽어 논문 Figure 1~6 자동 생성.
- 모든 Figure는 PDF + PNG 양쪽으로 저장.
- 캡션 후보 텍스트도 `outputs/figures/captions.md`에 자동 기록.

### Task P5.3 — LaTeX 표 자동화

`algo/evaluation/tables.py`:
- `summary_to_latex(summary_csv, output_path)` — pandas → booktabs 스타일 latex 표.
- 본 논문 Table 1 (전체 baseline RMSE), Table 2 (외삽 결과), Table 3 (추론 시간)을 자동 산출.

---

## 9. 마일스톤 요약

| Phase | 기간 | 산출 |
|---|---|---|
| P0 | 1주 | 디렉터리 마이그레이션, `ocv_soc` 리팩터, OCV 25/50/0 °C 룩업, NMC 검증, 1-RC ECM, KIER 카탈로그 |
| P1 | 2주 | Baseline 6종, runner, metrics, summary 표 |
| P2 (메인) | 3주 | Fractional ECM, Dual AEKF + Adaptive Q/R, Stage A 벤치 |
| P3 | 3주 | 외삽 split, 외삽 벤치, (선택) NASA |
| P4 (Stretch) | 4주 | PINN-AEKF, UQ |
| P5 | 1주 | 논문 그림·표 자동 |

미드티어 노선이면 **P0~P3로 논문 가능**. 합 ~9주 + 사용자의 논문 작성. P4·P5는 보너스.

---

## 10. 핸드오프 의무 (작업 단위 종료 시)

분업 Spec §10. 매번 다음 4줄 보고.

```
[변경 요약]    : 무엇을, 왜, 어디를
[공개 API 영향]: 분업 Spec §3 변경 여부 + (있으면) 갱신 PR 링크
[테스트 결과]  : pytest 마지막 5줄
[다음 액션 후보]: Antigravity가 새로 import 가능한 함수 / 노출하면 좋을 파라미터
```

---

## 11. 금지 사항 (Codex 자체 점검용)

- ❌ `ui/` 어떤 파일도 만들거나 수정하지 않는다.
- ❌ `streamlit`, `plotly`, `tkinter`, `dash`, `gradio` 등 UI 라이브러리 import 하지 않는다.
- ❌ `outputs/runs/<run_id>/`를 덮어쓰지 않는다 (항상 새 ID).
- ❌ pickle/joblib을 UI 인터페이스에 사용하지 않는다 (모델 가중치 `.pt` 내부 사용은 OK).
- ❌ 본 문서 또는 `01_분석보고서_및_사양/*` 의 기존 .md 를 직접 수정하지 않는다 (사용자만). 새 .md 추가만 가능.
- ❌ `pyproject.toml`, `requirements.txt` 변경 시 사용자 승인 없이 머지하지 않는다.
- ❌ 분업 Spec §3 공개 API 시그니처를 사용자 승인 없이 변경하지 않는다.

---

## 12. 즉시 시작 액션 (Day 1)

1. 본 문서 + 분업 Spec + 전략 v2 + Spec v1.1 정독. **§1 데이터 카탈로그(2026-04-23 정밀 조사)는 통째로 숙지**.
2. **Task P0 디렉터리 마이그레이션 단일 PR** — `data_io.py`, `ocv_soc.py`, `tests/test_data_io.py` 이동 + import 경로 수정. 기존 pytest 통과 확인.
3. **Task P0.0 보조 데이터 포맷 정찰** — 모듈 컬럼, 모듈 Pattern 분할, pouch step 3건 정찰. `outputs/recon_2026-04-23.md` 한 장 작성.
4. Task P0.1 `ocv_soc.py` 리팩터 + `compute_dqdv` 추가 + 신규 테스트.
5. Task P0.2 OCV 룩업 3종(25 °C, 50 °C, 0 °C) cycle 0 산출.
6. 사용자에게 1차 핸드오프 — 위 결과 + 다음 단계(P0.3~P0.6) 진행 동의 요청.

---

## Changelog

- **2026-04-23 v1** (초판)
  - 미드티어 SCI 노선 + NMC 확정 반영 (사용자 결정)
  - P0~P5 마일스톤 구체화 (P4 PINN은 stretch)
  - 데이터 카탈로그 §1 명시 (`셀 엑셀파일/셀 엑셀파일/CHx_NNdeg/...`)
  - Estimator 추상 클래스 + REGISTRY 패턴 확정
  - Stage A (FOM + Dual AEKF + Adaptive Q/R)을 메인 contribution로 명시

- **2026-04-23 v1.1** (정밀 조사 반영)
  - Chemistry 표기를 **NMC → NCM** 으로 통일 (사용자 확정, 동일 물질의 한국식 표기).
  - §1 데이터 카탈로그 전면 개편:
    - §1.1 메인: (channel, temp) = (ch2, 25 °C), (ch7, 50 °C), (ch3, 0 °C 부분) 매핑 확정. cycle 그리드 명시.
    - §1.2 신규: pouch_SOH (Pattern 3종 × 25/40 °C × ch1~ch8 다채널) — multi-cell cross-validation 1순위.
    - §1.3 신규: 18650_SOH (NCM 18650, .txt 포맷) — cross-cell-format 일반화 보강.
    - §1.4 신규: 모듈 데이터 (CH1만, **Pattern 파일 분할 구조** + DCIR 후 용량충전 별도 발견).
    - §1.5 KTL 모듈 측정본, §1.6 NCM 셀 사양 표, §1.7 PNE 컬럼 표준, §1.8 무시 경로, §1.9 ⚠️ 중복 경고.
  - −15 °C, 45 °C 데이터 부재 확인 → Spec v1.1 §1.3 "−15~45 °C × 1300~3200" 표기 정정 필요 (사용자 갱신 권고).
  - Task P0.0 (보조 데이터 포맷 정찰) 신설 — 18650 `.txt`, 모듈 컬럼, Pattern 분할, pouch step 4건.
  - Task P0.2 (OCV 룩업) 25 °C 단일 → **25/50/0 °C 3종 추출 + 온도 보정항 산출**로 확장.
  - Task P0.4 (DCIR 식별) 입력 파일 명시 + 50 °C 보너스 추가.
  - Task P0.5 (KIER loader) 4 dataset 통합 카탈로그 + **모듈 Pattern 분할 자동 merge** 기능 명시.
  - Task P3.2 외삽 split을 실제 가용 그리드(0/25/50 °C, ch2/ch3/ch7)에 맞춰 **4종 split (Aging / Temperature / Cell / Cross-dataset)** 으로 재정의.
  - Task P3.3 NASA PCoE → **자체 18650_SOH 데이터로 대체**, NASA는 옵션화.

- **2026-04-23 v1.2** (사용자 확정 정정)
  - **−15 °C, 45 °C 데이터 부재 확정** (사용자) → §1.1 표기 정정 + 외삽 split에서 해당 코너 제거. 본 논문은 가용 범위(0/25/40/50 °C)만 다룸.
  - **모듈 데이터는 CH1 단독 가용 확정** (사용자) → §1.4 갱신, 본 논문은 CH1만 supplementary.
  - **Cell 데이터★★★★★ (2018년) 본 논문 제외 확정** (사용자) → §1.8 사유 강화.
  - **pouch_SOH 노화 단위는 weeks** → 카탈로그에 **`weeks` 컬럼을 `cycle`과 별도로 추가** (사용자 결정: "더 좋은 걸로"). cycle/weeks 상호 배타. Task P0.5 schema·정규식 매핑·Split 4 비교 패널 분리 등 일관 반영.
  - Split 5 (pouch_SOH 내부 cross-pattern, MG+PVSmoothing → PowerQuality) 신설.

- **2026-04-23 v1.4** (실데이터 추가 발견 + 정정)
  - **5/10/15 °C 데이터 발견** — `셀 엑셀파일\셀 엑셀파일\전압하한 데이터파일\ch{2,3} 전압하한 데이터*\Pattern\` 위치. RPT/DCIR 부재로 SOH 산출 불가, **SOC 외삽만 supplementary 활용**. §1.1 매핑 표 갱신.
  - **`최근셀데이터/` 의미 정정**: PNE 사이클러 원본 raw (전용 프로그램 필요). 분석은 `셀 엑셀파일/`의 csv 변환본만 사용 (사용자 확정). §1.8 사유 정정 — Codex 가 .txt 파싱 코드 작성하지 않도록.
  - **`02_실험_데이터/Module 데이터★★★★★/` 폴더는 존재하지 않음** — Codex 1차 인벤토리 보고서의 fake 경로 차단. 진짜 모듈 raw 는 `모듈엑셀파일\모듈엑셀파일\모듈데이터 엑셀파일(2022.01~2023.07)\CH1\` (§1.4 그대로).

- **2026-04-23 v1.3** (Pouch 폼팩터 일관성 + 모듈 격상)
  - **18650_SOH 본 논문 제외 확정** (사용자: "Pouch 타입의 셀 데이터로만 했으면 좋겠어. 파우치 타입은 셀과 모듈 데이터 둘 다 있어"). §1.3 무효화 → §1.8 무시 경로로 이동. SCAN_ROOTS·정규식·Task P0.0 정찰 항목 일괄 제거.
  - **모듈 데이터(CH1)를 supplementary에서 메인 두 번째 축으로 격상**. §1.4 헤더를 "메인 (Cross-Scale 검증축)"으로 변경. 본 논문은 두 축: Pouch 셀 (§1.1+§1.2) + Pouch 모듈 (§1.4).
  - §1 도입부 새 표 — "셀 단위 / 모듈 단위" 두 축 매트릭스.
  - **Task P3.3 18650 외삽 → Cross-Scale (cell → module) 외삽으로 대체**. Split 6 신설 — 셀 학습 알고리즘을 14S 모듈에 적용. 두 시나리오(cell-equivalent / module-direct) 비교.
  - NASA PCoE는 옵션화 (Pouch 일관성 유지 + form factor 다른 별도 contribution으로만 도입 가능).
