# 집에서 작업 이어가기 — Portable Workspace 가이드

본 폴더(`battery_portable\`) 는 회사 PC 의 워크스페이스에서 **코드·문서·작은 outputs·환경 설정만** 복사한 portable 버전. **raw 데이터(GB 단위)는 포함되지 않음** (단 `--include-data core` 옵션 사용 시 본 논문 핵심 raw 까지 함께). 집에서도 이걸로 검토·전략·문서 작업·일부 코드 수정 가능.

⚠ **PowerShell 5.1 한국어 인코딩 버그 회피 — Python 스크립트 사용 권장**: PowerShell `.ps1` 버전 (`portable_setup.ps1`) 은 한국어 폴더명 파싱 문제로 실패. **`portable_setup.py` (Python)** 사용 권장.

---

## 1. 회사 PC 에서 portable 폴더 만들기 (Python 권장)

PowerShell 또는 cmd 에서 먼저 Python 명령 확인:

```powershell
python --version
```

`python` 이 안 잡히면 Python 3.12 설치 후 다시 진행. 설치되어 있는데 `python` 대신 Windows launcher 만 잡히는 PC 에서는 아래 명령의 `python` 을 `py -3.12` 로 바꿔서 실행.

그다음 portable 생성:

```powershell
cd "D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data\01_분석보고서_및_사양\portable"
python portable_setup.py --include-data core
```

→ 기본 위치 `D:\battery_portable\` 에 생성. **본 논문 핵심 raw 데이터까지 포함 (1~3 GB)**.

USB 직접:
```powershell
python portable_setup.py --destination "E:\battery_portable" --include-data core
```

다른 옵션:
- `--include-data none` → 코드·문서만 (~50 MB)
- `--include-data core` → + 본 논문 핵심 raw (1~3 GB) ← **권장**
- `--include-data all`  → + 옛날 데이터 모두 (5~10 GB+)

Python 이 robocopy 를 호출하면서 한국어 폴더명·인코딩을 안전하게 처리. 5~15분 (raw 데이터 양에 따라). 끝나면 폴더별 파일 수 + 사이즈 요약 출력. 생성된 폴더 루트에도 `portable_README.md` 가 복사되어 바로 열어볼 수 있음.

(PowerShell `.ps1` 버전도 같은 폴더에 있으나 PS 5.1 인코딩 버그로 실패할 수 있어서 비권장. Python 사용.)

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

## 3. raw 데이터 처리 — Python 옵션 + 수동 옵션

집에서 진짜로 알고리즘을 돌리려면 raw 데이터 (`02_실험_데이터\`, `셀 엑셀파일\`, `모듈엑셀파일\`) 도 함께 옮겨야 해. `portable_setup.py` 의 `--include-data` 옵션으로 자동 처리 가능.

### 옵션 1 — 코드·문서만 (default, ~50MB)

```powershell
python portable_setup.py --include-data none
```

집에서 검토·문서 작업·메시지 작성 등 두뇌 작업 위주 시. Streamlit 은 placeholder 만 표시.

### 옵션 2 — 본 논문 핵심 raw 데이터까지 (권장, ~1~3 GB)

```powershell
python portable_setup.py --include-data core
```

복사되는 raw 데이터:
- `셀 엑셀파일\셀 엑셀파일\` — 메인 셀 데이터 (CH2/25°C, CH7/50°C, 전압하한)
- `02_실험_데이터\pouch_SOH\` — multi-cell 패턴 데이터 (ch1~ch8)
- `모듈엑셀파일\모듈엑셀파일\모듈데이터 엑셀파일(2022.01~2023.07)\CH1\` — 14S 모듈

이 셋이 5편 논문 (KCI1, K2, S1, S2, S3) 작업에 필요한 모든 raw. **집에서 알고리즘 돌릴 거면 이 옵션 권장**.

### 옵션 3 — 옛날 데이터 포함 모두 (~5~10 GB+)

```powershell
python portable_setup.py --include-data all
```

옵션 2 + 옛날 데이터 (`18650_SOH/`, `Cell 데이터★★★★★/`, `최근셀데이터/`, `모듈내 셀간 전압편차 경향확인/`, `모듈 CH2`, `모듈,셀 엑셀파일_*/`, `03_매뉴얼/`, `99_상관없는/`).

본 논문에서는 안 쓰지만 백업이 필요하거나, 미래에 다른 방향으로 확장할 가능성 있으면 선택.

### USB 직접 만들기

```powershell
python portable_setup.py --destination "E:\battery_portable" --include-data core
```

(USB 드라이브 letter 가 E: 라고 가정)

### 클라우드 sync 대안

`--include-data none` 으로 portable 만든 뒤, raw 데이터는 OneDrive / Google Drive / Dropbox 로 별도 sync. 집 PC 에서 같은 클라우드 클라이언트 설치해두면 portable 폴더와 같은 상대 경로에 데이터가 자동 동기화. 장기·다인용에 유리.

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
| `python` 명령이 안 잡힘 | Python 이 PATH 에 없거나 미설치 | Python 3.12 설치 후 `python --version` 확인. 또는 `py -3.12 portable_setup.py ...` 사용 |
| `pip install` 시 numpy/torch 빌드 실패 | Python 3.13/3.14 사용 중 | Python 3.12 로 다시 |
| streamlit 한국어 깨짐 | OS locale 문제 | PowerShell 에 `$env:PYTHONUTF8 = "1"` |
| algo.loaders.kier 가 raw 데이터 못 찾음 | 데이터 경로 다름 | `--include-data core` 또는 `all` 로 raw 데이터 같은 상대 경로에 두기 |
| git pull conflict | 회사·집에서 같은 파일 수정 | 평범한 git merge resolution |

---

## 7. 추천 워크플로

1. **회사**: raw 데이터 + 알고리즘 실행 (Codex/Antigravity 메인) + 결과 push
2. **집**: 검토 + 사양·전략 보강 + 논문 글쓰기 + Codex/Antigravity 에 다음 단계 메시지 (가벼운 작업)

집에서는 "코드 돌려야 할 일 큰 거" 보다는 **두뇌 작업** 위주가 효율적이야. 그러면 raw 데이터 옮기는 부담 없음.
