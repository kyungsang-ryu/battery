# Stage 0 — Codex 인벤토리 보고서 정정 메시지 (짧음)

**복사해서 Codex 에 그대로 붙여넣어줘.** 아래 `=== 시작 ===` 부터 `=== 끝 ===` 까지.

---

```
=== 시작 ===

T1~T7 본 작업 잘 끝냈어. catalog (outputs/catalog_summary_v0.md, catalog_kier_v0.csv) 는 올바른 경로로 잘 잡혔음 — 큰 일 했음.

다만 인벤토리 보고서 (01_분석보고서_및_사양/2026-04-23_battery_dataset_inventory_report.md + .csv) 가 아직 첫 버전 그대로야. 다음 3가지만 정정해줘:

[정정 1] 잘못된 경로 → 정본 경로로 교체

§2 표 (그리고 §5 세부 해석, §7 최종 정리) 의 dataset 경로를 다음으로 정정:
- main_cell: "02_실험_데이터\최근셀데이터"  →  "셀 엑셀파일\셀 엑셀파일"
- module: "02_실험_데이터\Module 데이터★★★★★"  →  "모듈엑셀파일\모듈엑셀파일\모듈데이터 엑셀파일(2022.01~2023.07)\CH1"
- pouch_soh: "02_실험_데이터\pouch_SOH" (그대로 OK)

[정정 2] "최근셀데이터/" 의미 정정

"최근셀데이터/" 는 main_cell 의 정본이 아니라 PNE 사이클러 원본 raw (.txt + .sch + .cyc) 임. 분석에 쓰는 csv 변환본은 "셀 엑셀파일/셀 엑셀파일/" 에 있음 (사용자 확정 2026-04-23). 보고서 §2 의 무시 목록에 한 줄 추가:
- "최근셀데이터": PNE 원본 raw (전용 프로그램 필요). 분석은 셀 엑셀파일/ csv 변환본 사용

[정정 3] catalog 가 정본임을 명시

보고서 §6 또는 §7 끝에 한 단락 추가:
"본 보고서는 dataset 개요용. 실제 알고리즘·UI 가 사용하는 정본 카탈로그는 outputs/catalog_kier_v0.csv 와 outputs/catalog_summary_v0.md 임. 두 catalog 가 정확하면 본 보고서의 폴더 경로 표기 차이는 영향 없음."

[보너스 — 시간 남으면]
catalog 결과에서 발견된 두 가지 cleanup 메모를 보고서 §6 끝에 한 줄씩 추가:
- main_cell 에 5/10/15/20 °C Pattern 데이터도 잡혔음 (전압하한 시리즈). SCI1 SOC 외삽 supplementary 로 활용 예정.
- ch7 의 25°C cycle 2300 RPT 1건은 폴더명/파일명 typo 가능성 (실제 ch7 은 50°C 시리즈). 추후 사용자 확인 필요.

[종료 후]
- git push 는 하지 말 것. 워크스페이스 폴더 자체가 git repo 가 아니라서 push 가 실패함. 파일 변경만 하고 종료.
- outputs/handoff_stage0_codex.md 한 장 만들어줘 (4줄 핸드오프):
  1. [변경 요약]: T1~T7 + 보고서 정정 무엇을, 왜
  2. [공개 API 영향]: 분업 Spec §3 변경 여부
  3. [pytest 결과]: tests/algo 마지막 5줄
  4. [Antigravity에 알릴 것]: 새로 import 가능한 함수 + outputs/ 새 산출물

이게 끝나면 Stage 0 100% 마무리. GitHub 동기화는 사용자가 별도 push 스크립트로 일괄 진행할 예정.
Stage 1 (KCI1, 분수계 ECM 식별) 킥오프 프롬프트는 사용자가 별도 메시지로 보낼 예정.

=== 끝 ===
```

---

## 사용 안내

1. 위 `=== 시작 ===` ~ `=== 끝 ===` 사이만 복사
2. Codex 에 추가 메시지로 붙여넣기
3. 코덱스가 정정 + commit + push + handoff.md 생성
4. 끝나면 너 → 나에게 "보고서 정정 끝" 한 줄
5. 내가 짧게 검증 → **Stage 1 (KCI1) 킥오프 프롬프트 두 개 만들어줌**
