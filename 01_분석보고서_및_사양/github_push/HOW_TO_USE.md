# GitHub Push 가이드

이 폴더의 7개 파일을 한 번에 GitHub repo (https://github.com/kyungsang-ryu/battery) 에 push 한다.

---

## 폴더 내용

| 파일 | 어디로 가는가 |
|---|---|
| `main_README.md` | main 브랜치 → `README.md` |
| `KCI1_strategy.md` | KCI1 브랜치 → `strategy.md` |
| `KCI2_strategy.md` | KCI2 브랜치 → `strategy.md` |
| `SCI1_strategy.md` | SCI1 브랜치 → `strategy.md` |
| `SCI2_strategy.md` | SCI2 브랜치 → `strategy.md` |
| `SCI3_strategy.md` | SCI3 브랜치 → `strategy.md` |
| `push_all.ps1` | 위 6개를 자동 push 하는 PowerShell 스크립트 |

---

## 사전 준비 (한 번만)

### 1. Git 설치 확인

```powershell
git --version
```

없으면 https://git-scm.com 에서 설치.

### 2. GitHub 인증 셋업

다음 중 **하나** 선택.

**옵션 A — Personal Access Token (PAT, 권장)**

1. https://github.com/settings/tokens 접속
2. "Generate new token (classic)" → 권한 `repo` 체크 → 발급
3. 토큰 문자열 복사 (이걸 비밀번호 대신 사용)
4. 첫 push 시 GitHub 가 사용자명·비밀번호 물어봄 — 비밀번호 칸에 PAT 붙여넣기. 한 번만 입력하면 Git 이 캐시에 저장.

**옵션 B — SSH 키**

1. `ssh-keygen -t ed25519 -C "ksryu3212@gmail.com"` 실행 후 공개키 (`~/.ssh/id_ed25519.pub`) 를 GitHub Settings → SSH Keys 에 등록
2. `push_all.ps1` 안의 `$REPO_URL` 을 `git@github.com:kyungsang-ryu/battery.git` 로 수정

---

## 실행 (한 줄)

PowerShell 을 열고:

```powershell
cd "D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data\01_분석보고서_및_사양\github_push"
.\push_all.ps1
```

스크립트가 알아서:
1. repo 를 임시 폴더 (`%TEMP%\battery_repo_push`) 에 clone
2. main 브랜치 README 갱신 → push
3. KCI1, KCI2, SCI1, SCI2, SCI3 브랜치 각각 만들어서 strategy.md push
4. 완료 메시지 출력

---

## 만약 PowerShell 실행 정책 오류 ("script is not digitally signed")

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\push_all.ps1
```

이건 현재 PowerShell 세션에만 적용되어 안전. 또는 한 줄씩 직접 실행도 가능 — `push_all.ps1` 코드 참고.

---

## 결과 확인

브라우저로 https://github.com/kyungsang-ryu/battery 열고:
- main 브랜치 → README.md 5편 매트릭스 확인
- 좌상단 브랜치 드롭다운에서 KCI1 / KCI2 / SCI1 / SCI2 / SCI3 각각 선택 → strategy.md 확인

---

## 다음 push (수정 후 재실행)

전략 MD 파일을 수정한 뒤 같은 명령:

```powershell
.\push_all.ps1
```

스크립트가 변경 사항만 감지해서 commit + push (변경 없는 브랜치는 skip).

---

## 트러블슈팅

| 에러 | 해결 |
|---|---|
| `git clone` 실패 (repo not found) | repo URL 확인. private 이면 PAT/SSH 인증 필요 |
| `Authentication failed` | PAT 만료. 새 토큰 발급 후 재시도 |
| `non-fast-forward` reject | 원격 브랜치를 누가 먼저 수정. `git pull --rebase origin <branch>` 후 재시도 |
| 한국어 폴더명 인코딩 깨짐 | `git config --global core.quotepath false` 한 번 실행 |
| `Permission denied` (스크립트) | PowerShell 관리자 모드 또는 `Set-ExecutionPolicy Bypass` |

---

## 보안 메모

- PAT 는 비밀번호 = 절대 GitHub repo 에 commit 하지 말 것 (`.gitignore` 권장)
- 본 스크립트는 hardcoded 토큰 사용 안 함 — Git credential helper 가 OS 키체인에 저장
