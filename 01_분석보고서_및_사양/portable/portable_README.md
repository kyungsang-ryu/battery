# 집에서 작업 이어가기 — Portable Workspace 가이드

본 폴더(`battery_portable\`) 는 회사 PC 의 워크스페이스에서 **코드·문서·작은 outputs·환경 설정만** 복사한 portable 버전. **raw 데이터(GB 단위)는 포함되지 않음**. 집에서도 이걸로 검토·전략·문서 작업·일부 코드 수정 가능. 본격 알고리즘 실행은 raw 데이터 처리 전략에 따라 다름 (아래 §3 참조).

---

## 1. 회사 PC 에서 portable 폴더 만들기 (한 번만)

PowerShell 에서:

```powershell
cd "D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data\01_분석보고서_및_사양\portable"
.\portable_setup.ps1
```

→ 기본 위치 `D:\battery_portable\` 에 생성. USB 드라이브로 직접 만들고 싶으면:

```powershell
.\portable_setup.ps1 -Destination "E:\battery_portable"
```

(`E:\` 는 USB 드라이브 letter)

스크립트가 robocopy 로 raw 데이터·.venv·.git·큰 바이너리 다 제외하고 작업 파일만 복사. 1~2분 안에 끝나고, 마지막에 폴더별 파일 수 + 총 사이즈 (보통 50MB 이내) 보고.

---

## 2. 집 PC 에서 셋업 (첫 번째)

### 2.1 폴더 가져오기

USB / 클라우드(드라이브, OneDrive, Dropbox) / GitHub 중 편한 방법으로 `battery_portable\` 폴더를 집 PC 어디에든 둠. 권장 위치: `D:\battery_portable\` 또는 `C:\Users\<너>\battery_portable\`.

### 2.2 Python 3.12 설치

회사에서 했던 것과 동일. 이미 깔려 있으면 skip.

```powershell
py -3.12 --version
```

`Python 3.12.x` 가 안 나오면 https://www.python.org/downloads/release/python-3128/ 에서 Windows installer 받아 설치 (Add to PATH 체크).

### 2.3 가상환경 + 의존성

```powershell
cd "C:\Users\<너>\battery_portable"   # 또는 너가 둔 위치
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install -e ".[ui,dev,paper]"
```

설치 후 sanity check:

```powershell
python -m pytest tests\algo -q
streamlit run ui\data_analysis_ui.py
```

pytest 통과 + Streamlit 메인 페이지 보이면 OK.

---

## 3. raw 데이터 처리 — 스크립트 옵션 + 수동 옵션

집에서 진짜로 알고리즘을 돌리려면 raw 데이터 (`02_실험_데이터\`, `셀 엑셀파일\`, `모듈엑셀파일\`) 도 함께 옮겨야 해. `portable_setup.ps1` 의 `-IncludeData` 옵션으로 자동 처리 가능.

### 옵션 1 — 코드·문서만 (default, ~50MB)

```powershell
.\portable_setup.ps1
```

집에서 검토·문서 작업·메시지 작성 등 두뇌 작업 위주 시. Streamlit 은 placeholder 만 표시.

### 옵션 2 — 본 논문 핵심 raw 데이터까지 (권장, ~1~3 GB)

```powershell
.\portable_setup.ps1 -IncludeData core
```

복사되는 raw 데이터:
- `셀 엑셀파일\셀 엑셀파일\` — 메인 셀 데이터 (CH2/25°C, CH7/50°C, 전압하한)
- `02_실험_데이터\pouch_SOH\` — multi-cell 패턴 데이터 (ch1~ch8)
- `모듈엑셀파일\모듈엑셀파일\모듈데이터 엑셀파일(2022.01~2023.07)\CH1\` — 14S 모듈

이 셋이 5편 논문 (KCI1, K2, S1, S2, S3) 작업에 필요한 모든 raw. **집에서 알고리즘 돌릴 거면 이 옵션 권장**.

### 옵션 3 — 옛날 데이터 포함 모두 (~5~10 GB+)

```powershell
.\portable_setup.ps1 -IncludeData all
```

옵션 2 + 옛날 데이터 (`18650_SOH/`, `Cell 데이터★★★★★/`, `최근셀데이터/`, `모듈내 셀간 전압편차 경향확인/`, `모듈 CH2`, `모듈,셀 엑셀파일_*/`, `03_매뉴얼/`, `99_상관없는/`).

본 논문에서는 안 쓰지만 백업이 필요하거나, 미래에 다른 방향으로 확장할 가능성 있으면 선택.

### USB 직접 만들기

```powershell
.\portable_setup.ps1 -Destination "E:\battery_portable" -IncludeData core
```

(USB 드라이브 letter 가 E: 라고 가정)

### 클라우드 sync 대안

옵션 1 (코드만) 으로 portable 만든 뒤, raw 데이터는 OneDrive / Google Drive / Dropbox 로 별도 sync. 집 PC 에서 같은 클라우드 클라이언트 설치해두면 portable 폴더와 같은 상대 경로에 데이터가 자동 동기화. 장기·다인용에 유리.

---

## 4. GitHub 동기화 (병행)

코드 변경은 `git` 로 push/pull 하면 됨. 단 그러려면 portable 폴더가 git repo 여야 함. 첫 sync:

```powershell
cd "C:\Users\<너>\battery_portable"
git init -b main
git config user.name  "Kyungsang Ryu"
git config user.email "ksryu3212@gmail.com"
git remote add origin https://github.com/kyungsang-ryu/battery.git
git pull origin main --allow-unrelated-histories --no-edit
```

이후엔 평소 git workflow:
```powershell
git pull origin main          # 회사에서 push 한 변경 받기
# ... 작업 ...
git add .
git commit -m "..."
git push origin main          # 집에서 push 한 변경 보내기
```

⚠ portable 의 .gitignore 가 회사 워크스페이스의 .gitignore 와 일치하는지 확인. 다르면 raw 데이터 path 가 충돌.

---

## 5. Codex / Antigravity 집에서 사용

두 도구 다 PC 별로 설정 필요:
- **Codex CLI/Cloud**: 집 PC 에서 로그인 다시. 토큰 한도는 계정별이라 회사·집 합쳐 카운트.
- **Antigravity (Gemini)**: 집 PC IDE 에서 다시 열기. Google 계정 로그인.

작업 폴더는 집 PC 의 `battery_portable\` 로 지정. 사양서·strategy·kickoff .md 다 portable 에 있으니 그대로 사용 가능.

---

## 6. 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `pip install` 시 numpy/torch 빌드 실패 | Python 3.13/3.14 사용 중 | Python 3.12 로 다시 |
| streamlit 한국어 깨짐 | OS locale 문제 | PowerShell 에 `$env:PYTHONUTF8 = "1"` |
| algo.loaders.kier 가 raw 데이터 못 찾음 | 데이터 경로 다름 | 옵션 B 또는 C 로 raw 데이터 같은 상대 경로에 두기 |
| git pull conflict | 회사·집에서 같은 파일 수정 | 평범한 git merge resolution |

---

## 7. 추천 워크플로

1. **회사**: raw 데이터 + 알고리즘 실행 (Codex/Antigravity 메인) + 결과 push
2. **집**: 검토 + 사양·전략 보강 + 논문 글쓰기 + Codex/Antigravity 에 다음 단계 메시지 (가벼운 작업)

집에서는 "코드 돌려야 할 일 큰 거" 보다는 **두뇌 작업** 위주가 효율적이야. 그러면 raw 데이터 옮기는 부담 없음.
