# Stage 0 — Codex GitHub Push 위임 메시지

**복사해서 Codex 에 그대로 붙여넣어줘.** 아래 `=== 시작 ===` 부터 `=== 끝 ===` 까지.

---

```
=== 시작 ===

Stage 0 마무리 — workspace 전체를 GitHub main 브랜치에 push 해줘.

[배경]
사용자가 PowerShell 스크립트로 push 시도했지만 PowerShell 5.1 의 한국어 폴더명 인코딩 버그로 .gitignore 가 깨졌고, raw 데이터(GB 단위)가 staging 시도되면서 멈춤. 너는 PC 에서 직접 git 명령을 실행할 수 있으니 깔끔하게 처리해줘.

[현재 상태 — 청소 필요할 수 있음]
- workspace 루트: D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data
- 그 안에 .git/ 과 .gitignore 가 이미 만들어져 있을 수 있음 — 깨진 상태
- 두 파일을 강제 삭제 후 처음부터 깔끔하게 시작할 것

[작업 순서]

1. PowerShell 또는 git bash 로 workspace 이동
   cd "D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data"

2. 기존 .git, .gitignore 삭제 (없으면 무시)
   PowerShell: Remove-Item -Recurse -Force .git, .gitignore -ErrorAction SilentlyContinue

3. git init + config + remote
   git init -b main
   git config user.name  "Kyungsang Ryu"
   git config user.email "ksryu3212@gmail.com"
   git config core.quotepath false
   git remote add origin https://github.com/kyungsang-ryu/battery.git

4. .gitignore 작성 (UTF-8, 한국어 안전)
   ⚠ PowerShell 5.1 의 Out-File 은 한국어를 cp949 로 잘못 인코딩하니 사용 금지.
   대신 Python 한 줄 또는 git bash 의 echo, 또는 [System.IO.File]::WriteAllBytes 사용.

   .gitignore 내용 (UTF-8, 한국어 폴더명 정확히 보존):

   ```
   # Python
   .venv/
   __pycache__/
   *.py[cod]
   *.egg-info/
   .pytest_cache/
   .mypy_cache/
   .ruff_cache/

   # OS
   Thumbs.db
   desktop.ini
   ~$*
   *.tmp

   # Raw data folders — local only (GB-scale)
   02_실험_데이터/
   03_매뉴얼_및_참고자료/
   99_상관없는_자료_및_기타/
   셀 엑셀파일/
   모듈엑셀파일/
   모듈,셀 엑셀파일_by_고병찬,이중선/

   # Bulk document folders inside 01_분석보고서_및_사양/
   01_분석보고서_및_사양/PPt 파일/
   01_분석보고서_및_사양/모듈 및 셀 열화분석 정리본★★★★★/
   01_분석보고서_및_사양/셀 실험 정리본/

   # Binary file types (anywhere)
   *.pptx
   *.ppt
   *.pdf
   *.xlsx
   *.xls
   *.xlsm
   *.mat
   *.zip
   *.rar
   *.7z
   *.iso
   *.parquet
   *.h5
   *.hdf5
   *.pt
   *.pth
   *.onnx
   *.bin
   *.dll
   *.exe

   # Run outputs
   outputs/runs/
   outputs/figures/

   # Old root-level files (already migrated to algo/ and ui/)
   data_io.py
   ocv_soc.py
   data_analysis_ui.py
   requirements.txt
   .claude/
   .codex_pydeps/

   # IDE
   .vscode/
   .idea/

   # Locks
   .locks/

   # Whitelist (force-include)
   !outputs/ocv_soc/
   !outputs/ocv_soc/*.csv
   !outputs/ocv_soc/*.png
   !outputs/ocv_soc/*.md
   !outputs/ecm/
   !outputs/ecm/*.json
   !outputs/catalog*.csv
   !outputs/catalog*.md
   !outputs/recon*.md
   !outputs/handoff*.md
   !outputs/figures/.gitkeep
   !outputs/runs/.gitkeep
   !.gitkeep
   ```

   ⚠ 작성 후 reading test 필수:
   ```
   python -c "print(open('.gitignore', encoding='utf-8').read())"
   ```
   한국어가 멀쩡하게 보여야 함. cp949/깨진 글자면 다시 작성.

5. pull origin main (이미 push 된 5편 strategy README 와 합치기)
   git pull origin main --allow-unrelated-histories --no-edit
   - README.md 충돌 시: workspace 의 README.md 가 우선 (만약 있으면)
   - workspace 에 README.md 가 없으면 origin 의 것 그대로 받기

6. staging 직전 sanity check
   git status | head -50
   - 차단해야 할 폴더 (02_실험_데이터/, 셀 엑셀파일/, 모듈엑셀파일/ 등) 가 untracked 목록에 보이지 않아야 함
   - 만약 보이면 .gitignore 가 매칭 못 한 것 — Step 4 다시
   - 보이지 않으면 OK

7. add + commit + push
   git add .
   git status   # 한 번 더 확인 — staging 된 게 algo/, ui/, outputs/, tests/, pyproject.toml, 01_분석보고서_및_사양/*.md 정도만 (~100~200개 파일)이면 정상
   git commit -m "stage0: workspace snapshot — algo/, ui/, outputs/, pyproject.toml, tests/, docs"
   git push -u origin main

8. push 후 결과 보고
   - GitHub 페이지 확인: https://github.com/kyungsang-ryu/battery
   - main 브랜치에 algo/, ui/, outputs/ 등이 잘 올라갔는지
   - raw 데이터 폴더는 안 올라갔는지

[규칙]
- raw 데이터는 절대 push 금지 (.gitignore 로 차단)
- 단일 파일 100MB 초과 시 GitHub reject — 미리 .gitignore 로 차단
- 한국어 폴더명 인코딩 깨짐 검증 필수 (Step 4의 reading test)

[종료 후]
- outputs/handoff_stage0_github_push.md 한 장 만들어서:
  1. push 한 파일 수
  2. 차단된 폴더 목록 확인
  3. GitHub URL
  4. 다음 stage 에 영향 있는 사항

지금 바로 시작해줘. 사용자는 다음 메시지에서 확인.

=== 끝 ===
```

---

## 사용 안내

1. 위 `=== 시작 ===` ~ `=== 끝 ===` 사이만 복사해서 Codex 에 보내기
2. Codex 가 git 작업 + push 끝내면 너 → 나에게 "GitHub push 끝났어" 한 줄
3. 내가 GitHub 결과 검증 → Stage 1 (KCI1) 작업 진행

---

## 너가 할 일 (사이드 정리)

지금 PowerShell 창에서 멈춘 상태가 있으면:
- 그냥 PowerShell 창 닫아도 OK
- 코덱스가 알아서 .git 과 .gitignore cleanup 후 새로 시작
