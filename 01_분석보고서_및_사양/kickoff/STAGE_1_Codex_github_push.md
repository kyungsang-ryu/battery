# Codex Kickoff — Stage 1 (KCI1) GitHub Push (Code Only)

날짜: 2026-04-29
요청자: 유경상 (ksryu3212@gmail.com)
대상 저장소: https://github.com/kyungsang-ryu/battery
작업 위치: `D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data`

---

## 목표

오늘 (2026-04-29) Stage 1 KCI1 작업으로 추가/변경된 **소스 코드와 전략 문서만** GitHub 에 푸시한다.

**산출물(outputs/) 은 푸시 대상이 아님.** CSV, 그림, REPORT.md, handoff 메시지 등은 알고리즘을 다시 실행하면 재생성되므로 Stage 0 때와 동일하게 git 에서 제외한다.

브랜치 전략은 동일: **main + KCI1 + KCI2 + SCI1 + SCI2 + SCI3**. 각 브랜치는 main 의 최신 코드와 동기화만 수행.

---

## 푸시 대상 (코드 + 문서만)

```
01_분석보고서_및_사양/         # 전략 문서, kickoff 메시지, K1 paper scaffold
  ├─ kickoff/STAGE_1_*.md
  ├─ K1_paper_draft/build_paper.js
  ├─ K1_paper_draft/README.md
  └─ (그 외 수정된 .md 모두)

algo/                           # 알고리즘 소스
  ├─ ecm/fractional_ecm.py
  ├─ ecm/ecm_2rc.py
  ├─ ecm/ecm_identify.py
  ├─ loaders/kier.py
  ├─ ocv/ocv_soc.py
  ├─ ocv/chemistry_check.py
  └─ data_io.py

ui/                             # Streamlit UI 소스
  ├─ data_analysis_ui.py
  ├─ pages/03_⚙️_ECM_Fitting.py
  ├─ pages/05_📊_Benchmark_View.py
  └─ widgets/plot_helpers.py

tests/                          # 테스트 코드
  ├─ ui/test_ecm_fitting_page.py
  ├─ ui/test_benchmark_view_page.py
  └─ ui/test_imports.py
```

---

## 푸시 제외 (.gitignore 보강 필요)

다음을 .gitignore 에 반드시 포함시킬 것 (없으면 추가):

```
# 산출물 (재실행으로 생성)
outputs/

# 빌드 산출물
01_분석보고서_및_사양/K1_paper_draft/K1_paper_draft.docx
01_분석보고서_및_사양/K1_paper_draft/node_modules/
01_분석보고서_및_사양/K1_paper_draft/package.json
01_분석보고서_및_사양/K1_paper_draft/package-lock.json
node_modules/

# 원본 실험 데이터 (Stage 0 때 이미 등록됨, 재확인)
02_실험_데이터/
셀 엑셀파일/
모듈엑셀파일/
*.mat
*.MAT
```

`outputs/` 폴더 전체를 ignore 한다. CSV, PNG, PDF, MD 등 모든 산출물 파일이 자동 제외됨.

---

## 실행 절차 (PowerShell, Codex 환경)

```powershell
cd "D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data"

# 0. 현재 상태 확인
git status
git branch -a

# 1. .gitignore 보강 (이미 있으면 중복 추가 금지, 누락된 항목만 append)
#    위 "푸시 제외" 섹션 참고. UTF-8 (no BOM) 으로 작성.

# 2. 만약 outputs/ 가 이전에 트래킹되고 있다면 인덱스에서 제거 (파일은 디스크에 유지)
git rm -r --cached outputs/ 2>$null

# 3. main 브랜치에 코드+문서 커밋
git checkout main
git add 01_분석보고서_및_사양/ algo/ ui/ tests/ .gitignore
git status   # outputs/ 가 staged 목록에 없는지 재확인
git commit -m "Stage1: KCI1 fractional ECM code, UI K1 view, paper draft scaffold"
git push origin main

# 4. 나머지 5개 브랜치는 main 의 최신 코드와 fast-forward 머지만 수행
foreach ($br in @("KCI1", "KCI2", "SCI1", "SCI2", "SCI3")) {
    git checkout $br
    git merge main --no-edit
    git push origin $br
}

git checkout main
git status
git log --oneline -5
```

---

## 검증 체크리스트

다음을 GitHub 웹에서 확인 후 표로 보고:

| 항목 | 확인 방법 | 기대 결과 |
|---|---|---|
| main 최신 커밋 메시지 | https://github.com/kyungsang-ryu/battery/commits/main | "Stage1: KCI1 fractional ECM code..." |
| algo/ecm/fractional_ecm.py | main 브랜치 파일 트리 | 존재함 |
| ui/pages/05_📊_Benchmark_View.py | main 브랜치 파일 트리 | 존재함 |
| 01_분석보고서_및_사양/K1_paper_draft/build_paper.js | main 브랜치 | 존재함 |
| outputs/ 폴더 | main 및 모든 브랜치 | **존재하지 않음** (의도적 제외) |
| K1_paper_draft.docx | main 브랜치 | **존재하지 않음** (의도적 제외) |
| 02_실험_데이터/, 셀 엑셀파일/, 모듈엑셀파일/ | 모든 브랜치 | **존재하지 않음** |
| 5개 브랜치 (KCI1~SCI3) | 각 브랜치 최신 커밋 | main 의 최신 커밋 SHA 와 동일 |

---

## 보고 형식

다음 4개 항목으로 회신:

1. **[변경 요약]**: main 커밋 SHA + 푸시된 파일 수 + 5개 브랜치 동기화 여부
2. **[이슈/예외]**: 충돌, 인증, outputs/ 제거 시 이슈 등
3. **[검증 결과]**: 위 표
4. **[다음 작업]**: Stage 2 (SCI1 + KCI2 병렬 착수) 진입 가능 여부
