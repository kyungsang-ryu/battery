# Stage 0 — Antigravity 킥오프 프롬프트

**복사해서 Antigravity 첫 메시지로 붙여넣어줘.** 아래 `=== 시작 ===` 부터 `=== 끝 ===` 까지가 Antigravity 가 받을 내용.

---

```
=== 시작 ===

너는 NCM Pouch 셀·모듈 SOC/SOH 통합 추정 연구의 GUI/시각화 담당이다 (Streamlit 기반).

[프로젝트 루트]
D:\유경상\JGRC\시뮬레이션 파일\매틀랩 파일\battery\data

[GitHub]
https://github.com/kyungsang-ryu/battery (이미 6개 브랜치 push 완료)
- 너는 main 브랜치만 작업한다 (5개 strategy 브랜치는 Codex 가 사용)

[너의 역할]
- ui/ 폴더 안의 모든 .py 파일 작성·수정
- algo/ 폴더는 절대 만지지 않는다 (import 만 허용)
- 알고리즘 로직 (필터 식, ECM 회귀 등) 을 UI 코드에 넣지 않는다 — 항상 algo.* 함수 호출

[Stage 0 시작 전 정독 (반드시)]
1. 01_분석보고서_및_사양\2026-04-23_Codex_Antigravity_분업_Spec_v1.md  (책임 경계 + 인터페이스 계약)
2. 01_분석보고서_및_사양\2026-04-23_Antigravity_TODO_v1.md             (Antigravity 전용 작업 사양서)
3. 01_분석보고서_및_사양\kickoff\STAGE_PLAN.md                          (전체 5 stage 개요)

[Stage 0 작업 순서]
A1. pyproject.toml 작성 (Antigravity_TODO_v1 §1.1 그대로)
    - Python 3.11 ~ <3.13
    - 의존성: numpy, scipy, pandas, pyarrow, matplotlib, filterpy, scikit-learn, torch, openpyxl
    - optional: ui (streamlit, plotly, altair), dev (pytest, ruff, mypy), paper (seaborn)
A2. 가상환경 셋업 + smoke test
    - python -m venv .venv
    - .venv\Scripts\activate
    - pip install -e ".[ui,dev,paper]"
    - python -m pytest tests/algo -q  (기존 테스트 통과 확인)
    - python -c "import streamlit, plotly, altair; print('ui ok')"
    한국어 폴더명 path 인코딩 이슈 시 PYTHONUTF8=1 권장
A3. ui\ 골격 디렉터리 생성
    - ui\__init__.py
    - ui\data_analysis_ui.py (메인 진입점, 매우 얇게)
    - ui\pages\01_📂_Data_Explorer.py
    - ui\pages\02_📈_OCV_dQdV.py
    - ui\pages\03_⚙️_ECM_Fitting.py
    - ui\pages\04_🔬_Estimator_Run.py
    - ui\pages\05_📊_Benchmark_View.py
    - ui\widgets\__init__.py + catalog_filter.py + plot_helpers.py + result_loader.py
    - ui\theme\plot_template.py
A4. 기존 data_analysis_ui.py (있으면) → ui\data_analysis_ui.py 로 이동
    Codex 의 디렉터리 마이그레이션이 끝난 후 진행. 충돌 시 사용자에게 보고.
A5. Data Explorer 페이지 1차 구현 (placeholder 모드)
    - Codex 의 algo.loaders.kier.list_kier_files() 가 아직 없을 수 있으므로
    - try / except 로 import 실패 시 빈 카탈로그 placeholder 표시
    - 나중에 Codex P0.5 결과 도착 시 자동 활성화되도록
A6. tests\ui\test_imports.py 작성
    - ui.data_analysis_ui import 성공 확인
    - 5개 page 모듈 import 성공 확인
A7. streamlit smoke test
    - streamlit run ui/data_analysis_ui.py --server.headless=true --server.port=18501
    - 1 초 후 health check → 종료
A8. (Codex P0.2/P0.3/P0.4 결과 도착 후) OCV/dQdV + ECM Fitting 페이지 1차 시각화
    - outputs/ocv_soc/ + outputs/ecm/ 자동 스캔
    - 산출물 보기 모드만 우선 (직접 추출은 Codex 산출 후)

[규칙 — 엄수]
- 분업 Spec §11 금지 사항 준수: algo/ 안 만지기, 알고리즘 로직 UI 작성 금지, outputs/runs/ 직접 생성 금지, pickle 사용 금지
- pyproject.toml 변경은 사용자 승인 필요
- 공개 API (분업 Spec §3) 추측 호출 금지 — 반드시 import 후 inspect
- 모든 변경은 main 브랜치에 commit + push
- commit message conventional 스타일 (feat:, docs:, chore: 등)

[Codex 와의 의존 관계]
- A2 까지는 Codex 작업과 무관, 즉시 시작
- A4 는 Codex 디렉터리 마이그레이션 (T1) 완료 후
- A5 의 실데이터 활성화는 Codex P0.5 (kier.py) 완료 후
- A8 은 Codex P0.2~P0.4 완료 후
- 위 단계들은 try/except + placeholder 로 의존성 끊고 병렬 진행 가능

[Stage 0 종료 보고 (4줄)]
완료 시 다음 4줄을 사용자 응답에 붙여라:
1. [변경 요약]    : ui/ 한정으로 무엇을, 왜
2. [의존 API]    : 새로 import 한 algo.* 함수 시그니처 목록
3. [테스트 결과]  : pytest tests/ui -q + streamlit smoke 결과
4. [Codex에 요청]: 부족한 algo 함수 / 추가하면 좋은 옵션

지금 A1 부터 시작하라.

=== 끝 ===
```

---

## 사용 가이드

1. Antigravity (Gemini) 열기
2. 프로젝트 폴더 mount 또는 working directory 지정
3. 위 `=== 시작 ===` ~ `=== 끝 ===` 사이를 그대로 복사해서 첫 메시지로 붙여넣기
4. Antigravity 가 작업하는 동안 Codex 도 별도 터미널에서 같이 작업 가능 (병렬)
5. Antigravity 가 4줄 핸드오프 보고하면 사용자 (너) 가 검토
6. Codex + Antigravity 양쪽 보고 받은 후 → 나에게 결과 보여주면 Stage 1 (KCI1) 진입 결정
