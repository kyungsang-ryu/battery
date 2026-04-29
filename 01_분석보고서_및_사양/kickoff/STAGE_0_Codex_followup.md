# Stage 0 — Codex 두 번째 메시지 (인벤토리 정정 + 진짜 작업 시작)

**복사해서 Codex 에 그대로 붙여넣어줘.** 아래 `=== 시작 ===` 부터 `=== 끝 ===` 까지.

---

```
=== 시작 ===

인벤토리 보고서 잘 봤어. 좋은 발견 하나, 정정 필요 두 개, 그리고 진짜 본 작업 안내 — 다음 순서대로 진행해줘.

[좋은 발견 — 그대로 두기]
- "최근셀데이터/" 안에 5/10/15 °C 데이터 발견. 정확함.
  단, 이 데이터는 PNE 사이클러 원본 raw (.txt + .sch + .cyc + .ini) 라서 PNE 전용 프로그램이 필요해.
  분석은 같은 실험을 csv 변환한 "셀 엑셀파일/" 폴더에서 진행. 사용자가 확정함.
  "셀 엑셀파일/셀 엑셀파일/전압하한 데이터파일/ch{2,3} 전압하한 데이터*/Pattern/" 에 5/10/15 °C csv 가 있음.
  이건 SOC 외삽 supplementary 로 쓸 예정 (SOH 는 RPT 부재로 25/50 °C 만).

[정정 1 — fake 경로 제거]
보고서의 module dataset 경로가 잘못됐어:
  잘못: "02_실험_데이터/Module 데이터★★★★★/"
  정답: "모듈엑셀파일/모듈엑셀파일/모듈데이터 엑셀파일(2022.01~2023.07)/CH1/"
인벤토리 보고서 (.md + .csv) 둘 다 정정해줘. CH02 폴더는 raw 에는 있을 수도 있지만 본 논문 스코프는 CH01만.

[정정 2 — "최근셀데이터/" 의 의미]
보고서가 main_cell 의 정본을 "최근셀데이터/"로 잡았는데, 이건 PNE 원본이라 분석에 직접 쓰지 않아.
정정: main_cell 의 정본 = "셀 엑셀파일/셀 엑셀파일/" (csv).
"최근셀데이터/" 는 같은 실험의 PNE 원본 (배경 정보로만 보고서에 한 줄 언급).
인벤토리 보고서 .md + .csv 둘 다 그대로 정정.

[진짜 본 작업 — Stage 0 의 T1~T7]
첨부했던 STAGE_0_Codex_kickoff.md 의 [Stage 0 작업 순서] 섹션이 아직 0건이야.
지금부터 다음 7개 task 를 순서대로 진행해줘. 각 task 의 자세한 내용은 STAGE_0_Codex_kickoff.md + Codex_TODO_v1.md (특히 §3) 정독.

T1. 디렉터리 마이그레이션 단일 PR
    - 현재 평탄 구조 (data_io.py, ocv_soc.py, tests/) → algo/ 분할 구조로 이동
    - import 경로 일괄 수정 후 'python -m pytest tests/algo -q' 통과

T2. Task P0.0 보조 데이터 포맷 정찰
    - 모듈 CSV 컬럼 (14S 셀 전압 [004]~[017]AuxV(V), Aux 온도, Capacitance)
    - 모듈 Pattern 분할 청크 (CH01.csv + CH01(N).csv) 시간·StepNo 연속성
    - pouch_SOH 25도/ vs 25도step/ 차이
    - 산출: outputs/recon_2026-04-23.md

T3. Task P0.1 algo/ocv/ocv_soc.py 리팩터
    - data_io.read_cycler_file 사용으로 변경
    - compute_dqdv() 신규 함수 추가
    - tests/algo/test_ocv_soc.py 신규 (합성 데이터 round-trip)

T4. Task P0.2 OCV 룩업 3종 추출 (25/50/0 °C)
    - 25 °C: 셀 엑셀파일/셀 엑셀파일/CH2_25deg/RPT/22_09_06_..._25deg_RPT_ch2_M01Ch002(002).csv (cycle 0)
    - 50 °C: 셀 엑셀파일/셀 엑셀파일/CH7_50deg/RPT/22_09_06_..._50deg_RPT_ch7_M01Ch007(007).csv (cycle 0)
    - 0 °C: 셀 엑셀파일/셀 엑셀파일/전압하한 데이터파일/ch2 전압하한 데이터(최근)/RPT/23_06_21_..._0deg_0cycle_RPT_ch2_M01Ch002(002).csv
    - 산출: outputs/ocv_soc/{25C,50C,0C}_cycle0_v0.csv + .png + temp_correction_v0.csv

T5. Task P0.3 NCM chemistry 검증 (사용자 확정값과 일치 검증)
    - 25 °C cycle 0 RPT 의 저율 방전 dQ/dV
    - NCM 가정 일치 시 통과, 모순 시 즉시 보고
    - 산출: outputs/ocv_soc/dqdv_25C_cycle0.png + chemistry_검증_2026-04-23.md

T6. Task P0.4 DCIR 1-RC 초기 식별
    - 입력: 셀 엑셀파일/셀 엑셀파일/CH2_25deg/DCIR/23_01_05_..._1300cycle_DCIR_ch2_M01Ch002(002).csv
    - 산출: outputs/ecm/1rc_25C_cycle1300_v0.json
    - 검증: R0 ~ 1.03 mΩ ± 0.25 자릿수면 PASS (JH3 스펙)

T7. Task P0.5 algo/loaders/kier.py 통합 카탈로그 (3 dataset)
    - dataset enum: main_cell, pouch_soh, module (18650 제외)
    - 5/10/15 °C 도 카탈로그에 인식 (temp_C 컬럼 = 0/5/10/15/25/40/50)
    - cycle / weeks 별도 컬럼 (상호 배타)
    - 모듈 Pattern 분할 자동 merge
    - 산출: outputs/catalog_kier_v0.csv

[Stage 0 종료 시]
outputs/handoff_stage0_codex.md 파일 만들어서 4줄 핸드오프 적어줘:
1. [변경 요약]
2. [공개 API 영향]
3. [pytest 결과]
4. [Antigravity에 알릴 것]

main 브랜치에 commit + push.

지금 [정정 1] [정정 2] 인벤토리 보고서 갱신부터 시작해줘. 끝나면 바로 T1.

=== 끝 ===
```

---

## 사용 안내

1. 위 `=== 시작 ===` ~ `=== 끝 ===` 사이만 복사해서 Codex 에 두 번째 메시지로 붙여넣기
2. Codex 가 인벤토리 정정 + T1 ~ T7 순서대로 진행
3. 끝나면 `outputs/handoff_stage0_codex.md` 만들고 너에게 보고
4. 너 → 나에게 "Stage 0 끝났어 검토해줘" 한 줄
5. 내가 워크스페이스 자동 스캔 → 결과 검토 → Stage 1 진입 결정
