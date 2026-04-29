# Stage 1 — KCI1 — Antigravity 킥오프 프롬프트 (ECM Fitting 페이지 + K1 시각화)

**복사해서 Antigravity 에 첫 메시지로 붙여넣어줘.** 아래 `=== 시작 ===` 부터 `=== 끝 ===` 까지.

**중요**: 이 메시지는 **Codex 의 Stage 1 작업이 끝난 후**에 보내야 효과적. (Codex 가 만든 algo.ecm.fractional_ecm 함수와 outputs/runs/K1-* 폴더를 사용)

---

```
=== 시작 ===

Stage 1 시작. KCI1 페이퍼 (분수계 ECM 식별) 의 결과를 ECM Fitting 페이지에 통합하고, 새 K1 결과 시각화 패널을 만든다.

[페이퍼 정보]
- KCI1: 분수계 R+CPE 모델이 정수 1-RC 대비 voltage RMSE 가 낮고, α 가 노화 추적성을 가진다는 가설.
- 너의 역할: Codex 가 만든 알고리즘·산출물을 시각화. UI 만 담당.

[전제 조건]
- Codex 가 Stage 1 (K1.1~K1.8) 을 끝낸 상태여야 한다.
- 다음 algo 함수가 import 가능해야 한다:
  from algo.ecm.ecm_identify import identify_1rc
  from algo.ecm.ecm_2rc import identify_2rc
  from algo.ecm.fractional_ecm import identify_fractional
- 다음 outputs/ 가 존재해야 한다:
  outputs/runs/K1-{1rc,2rc,fom}-{25C,50C}/params_per_cycle.csv  (총 6개)
  outputs/figures/K1_fractional_ecm/ (PDF 6장)
  outputs/runs/K1-summary/REPORT.md

위 조건이 안 맞으면 Codex 작업 끝나길 기다려.

[Stage 1 시작 전 정독]
1. 01_분석보고서_및_사양/2026-04-23_Antigravity_TODO_v1.md (§4 ECM Fitting 페이지)
2. 01_분석보고서_및_사양/2026-04-23_Codex_Antigravity_분업_Spec_v1.md (§3 공개 API)
3. 워크스페이스의 strategy.md (KCI1 브랜치 루트)
4. outputs/handoff_stage1_codex.md

[Stage 1 작업 순서]

A1. 너는 main 브랜치에서 작업 (Codex 의 KCI1 브랜치 코드는 main 으로 이미 merge 되어 있다고 가정).
    git pull origin main 먼저.

A2. ui/pages/03_⚙️_ECM_Fitting.py 확장
    - 기존 1-RC, 2-RC 옵션에 더해 "Fractional (FOM)" 옵션 추가
    - Radio 버튼: 1-RC / 2-RC / Fractional / Compare All 4가지
    - "Compare All" 선택 시 세 모델을 동시 식별하고 voltage 잔차 비교 플롯 표시
    - 식별 결과 (R0, R1, [C1, alpha], RMSE) 카드 UI

A3. ui/pages/03_⚙️_ECM_Fitting.py 에 K1 결과 보기 모드 추가
    - 사이드바 토글: "Identify new" vs "View K1 results"
    - "View K1 results" 선택 시:
      - outputs/runs/K1-{1rc,2rc,fom}-{25C,50C}/params_per_cycle.csv 자동 로드
      - cycle 별 R0(cycle), α(cycle) plotly trajectory
      - 1-RC vs 2-RC vs FOM voltage RMSE 비교 박스플롯
      - outputs/figures/K1_fractional_ecm/*.pdf 미리보기 그리드 (st.image 또는 download 링크)

A4. ui/pages/05_📊_Benchmark_View.py 에 KCI1 sheet 추가
    - 5편 결과 sheet 의 첫 번째로 KCI1
    - outputs/runs/K1-summary/REPORT.md 자동 렌더 (st.markdown)
    - K1 fig 6장 다운로드 zip 버튼

A5. ui/widgets/plot_helpers.py 에 함수 추가
    - make_ecm_param_trajectory(params_df, param='R0' or 'alpha') -> plotly Figure
    - make_ecm_rmse_box(summary_df) -> plotly Figure
    - make_pdf_grid(pdf_paths) -> streamlit components

A6. 단위 테스트
    - tests/ui/test_ecm_fitting_page.py
    - placeholder 데이터 (params CSV mock) 로 페이지 렌더 시 에러 없이 동작 확인

A7. streamlit smoke test
    streamlit run ui/data_analysis_ui.py --server.headless=true --server.port=18501
    1초 후 health check + 종료

[규칙 — 엄수]
- algo/ 안 만지기 (import만 OK)
- 알고리즘 로직 (분수계 식, 식별 회귀) 을 UI 에 작성 금지
- pickle 사용 금지
- pyproject.toml 변경 시 사용자 승인
- main 브랜치에 commit + push: git push origin main (UI 변경은 main 에서 직접 OK).

[Codex 와의 의존 관계]
- Codex 의 K1.5~K1.7 결과가 outputs/runs/K1-*/ 에 있어야 A3, A4 의 "View K1 results" 모드가 진짜 데이터를 보여줌
- 없으면 try/except 로 placeholder ("K1 결과 없음 — Codex Stage 1 완료 후 다시") 표시

[Stage 1 종료 시]
- outputs/handoff_stage1_antigravity.md 4줄 핸드오프
  1. [변경 요약]: ui/ 무엇을, 왜
  2. [의존 API]: 새로 import 한 algo.ecm.fractional_ecm 등 시그니처
  3. [pytest+streamlit 결과]
  4. [Codex에 요청]: 부족한 함수 / 추가 시각화 옵션

지금 A1 부터 시작하라.

=== 끝 ===
```

---

## 사용 안내

이건 **Codex Stage 1 끝난 후** 에 보내. 만약 너무 일찍 보내면 Antigravity 가 algo.ecm.fractional_ecm import 실패해서 placeholder 모드만 만들어둘 수 있어 (그것도 OK 지만 K1 결과 시각화는 Codex 끝난 후 다시 한 번 작업).

권장 순서:
1. push_workspace.ps1 한 번 실행 (Stage 0 산출물 GitHub 동기화)
2. STAGE_1_Codex_kickoff.md 의 메시지를 Codex 에 → 2~3시간 작업
3. Codex 끝났다고 너 → 나에게 알리면 → 나가 검증 → 결과 봐도 OK 하면
4. STAGE_1_Antigravity_kickoff.md 의 메시지를 Antigravity 에 → 1~2시간 작업
5. 둘 다 끝났다고 너 → 나에게 → 검증 → Stage 2 (SCI1+KCI2) 킥오프 진행
