# Stage 0 — Codex 킥오프 프롬프트

**복사해서 Codex 첫 메시지로 붙여넣어줘.** 아래 `=== 시작 ===` 부터 `=== 끝 ===` 까지가 Codex 가 받을 내용.

---

```
=== 시작 ===

너는 NCM Pouch 셀·모듈 SOC/SOH 통합 추정 연구의 알고리즘·시뮬레이션 담당이다.

[프로젝트 루트]
D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data

[GitHub]
https://github.com/kyungsang-ryu/battery (이미 6개 브랜치 push 완료: main + KCI1/KCI2/SCI1/SCI2/SCI3)

[너의 역할]
- algo/ 폴더 안의 모든 .py 파일 작성·수정
- ui/ 폴더는 절대 만지지 않는다 (Antigravity 담당)
- 본 Stage 0 작업은 main 브랜치에서 진행

[Stage 0 시작 전 정독 (반드시)]
1. 01_분석보고서_및_사양\2026-04-23_Codex_Antigravity_분업_Spec_v1.md  (책임 경계 + 인터페이스 계약)
2. 01_분석보고서_및_사양\2026-04-23_Codex_TODO_v1.md                    (Codex 전용 작업 사양서, §1 데이터 카탈로그 필독)
3. 01_분석보고서_및_사양\kickoff\STAGE_PLAN.md                            (전체 5 stage 개요)

[Stage 0 작업 순서 — 순서 엄수]
T1. 디렉터리 마이그레이션 단일 PR
    - 현재 평탄 구조 (data_io.py, ocv_soc.py, tests/) 를 algo/ 분할 구조로 이동
    - 매핑은 Codex_TODO_v1.md §2 참조
    - import 경로 일괄 수정 후 'python -m pytest tests/algo -q' 통과 확인
T2. Task P0.0 보조 데이터 포맷 정찰
    - 모듈 CSV 컬럼, 모듈 Pattern 분할, pouch_SOH 25도/25도step 차이 3건
    - 결과를 outputs\recon_2026-04-23.md 한 장으로 작성
T3. Task P0.1 algo\ocv\ocv_soc.py 리팩터
    - data_io.read_cycler_file 사용으로 변경
    - compute_dqdv() 신규 함수 추가
    - tests\algo\test_ocv_soc.py 신규 (합성 데이터 round-trip)
T4. Task P0.2 OCV 룩업 3종 추출 (25/50/0 °C)
    - 입력 파일 3개는 Codex_TODO_v1.md §3 Task P0.2 정확한 경로 참조
    - 산출: outputs\ocv_soc\{25C,50C,0C}_cycle0_v0.csv + .png
T5. Task P0.3 NCM chemistry 검증
    - 사용자 확정: NCM. dQ/dV 결과가 NCM 가정과 일치하는지 확인
    - 산출: outputs\ocv_soc\dqdv_25C_cycle0.png + chemistry_검증_2026-04-23.md
    - NCM 과 모순 결과 시 즉시 사용자에게 보고
T6. Task P0.4 DCIR 1-RC 초기 식별
    - 입력 파일: 셀 엑셀파일\셀 엑셀파일\CH2_25deg\DCIR\23_01_05_..._1300cycle_DCIR_ch2.csv
    - 산출: outputs\ecm\1rc_25C_cycle1300_v0.json
    - 검증: R0 ~ 1.03 mΩ ± 0.25 자릿수면 PASS
T7. Task P0.5 algo\loaders\kier.py 통합 카탈로그 (3 dataset)
    - dataset enum: main_cell, pouch_soh, module (18650 제외)
    - cycle / weeks 별도 컬럼 (상호 배타)
    - 모듈 Pattern 분할 자동 merge
    - 산출: outputs\catalog_kier_v0.csv

[규칙 — 엄수]
- 분업 Spec §11 금지 사항 준수: ui/ 안 만지기, UI 라이브러리 import 금지, outputs/runs/<run_id>/ 덮어쓰기 금지, pickle 인터페이스 금지
- 공개 API (분업 Spec §3) 시그니처 변경 시 사용자 승인 필요
- 모든 변경은 main 브랜치에 commit. commit message 는 conventional 스타일 (feat:, docs:, refactor: 등)
- 완료 후 GitHub main 으로 push

[Stage 0 종료 보고 (4줄)]
완료 시 다음 4줄을 사용자 응답에 붙여라:
1. [변경 요약]    : 무엇을, 왜, 어디를
2. [공개 API 영향]: 분업 Spec §3 변경 여부 + (있으면) 어느 시그니처
3. [테스트 결과]  : pytest tests/algo -q 마지막 5줄
4. [Antigravity에 알릴 것]: 새로 import 가능한 함수 목록 + outputs/ 새 산출물 경로

지금 T1 부터 시작하라.

=== 끝 ===
```

---

## 사용 가이드

1. Codex CLI 또는 Codex Cloud 열기
2. 프로젝트 폴더로 이동 (또는 작업 폴더 지정)
3. 위 `=== 시작 ===` ~ `=== 끝 ===` 사이를 그대로 복사해서 첫 메시지로 붙여넣기
4. Codex 가 작업하는 동안 너는 다른 일 해도 됨
5. Codex 가 4줄 핸드오프 보고하면 사용자 (너) 가 검토
6. 검토 통과 → 나에게 결과 보여주면 Stage 1 (KCI1) 킥오프 프롬프트 만들어줌
