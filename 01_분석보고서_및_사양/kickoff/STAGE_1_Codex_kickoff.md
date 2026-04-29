# Stage 1 — KCI1 — Codex 킥오프 프롬프트 (분수계 ECM 식별)

**복사해서 Codex 에 첫 메시지로 붙여넣어줘.** 아래 `=== 시작 ===` 부터 `=== 끝 ===` 까지.

---

```
=== 시작 ===

Stage 1 시작. KCI1 페이퍼 (한글 KCI 논문) 의 알고리즘·실험 자료를 만든다.

[페이퍼 정보]
- 제목 (가제): NCM Pouch 셀의 분수계 등가회로모델 식별 및 노화 추적
- 등급: KCI (한국산학기술학회 / 대한전기학회)
- 가설: 분수계 R+CPE 모델이 정수 1-RC 대비 voltage RMSE 가 유의하게 낮고, CPE 차수 α 가 cycle 진행에 따라 단조 변화한다 (SOH 새 지표).

[너의 역할]
- KCI1 브랜치에서 작업 (git checkout KCI1).
- algo/ 폴더 안의 .py 작성·수정만. ui/ 는 Antigravity 담당.
- main 의 코드 (Stage 0 산출물) 는 그대로 사용.

[Stage 1 시작 전 정독 (반드시)]
1. 01_분석보고서_및_사양/2026-04-23_Codex_TODO_v1.md (특히 §1.1 데이터, §3 P0~P2 task)
2. 01_분석보고서_및_사양/2026-04-23_Multi_Paper_전략_v3.md (S1 와의 leverage 흐름)
3. 워크스페이스의 strategy.md (KCI1 브랜치 루트)
4. outputs/handoff_stage0_codex.md (Stage 0 무엇이 있는지)

[Stage 1 작업 순서 — 순서 엄수]

K1.1 브랜치 전환
   - git checkout KCI1
   - 워크스페이스가 git repo 가 아니면 push 는 하지 말 것 (Stage 0 와 동일).
     사용자가 별도 push_workspace.ps1 로 일괄 push 예정.

K1.2 algo/ecm/fractional_ecm.py 구현
   - 모델: V(t) = OCV(SOC) − I·R0 − V_CPE(t),  V_CPE 는 R+CPE 시간응답
   - 구현 방식: Oustaloup 정수계 근사 (4~5차) 또는 Grünwald-Letnikov 이산 근사.
     둘 다 prototype 후 빠른 쪽 채택.
   - 공개 API:
     def identify_fractional(file_path: str, nominal_capacity_ah: float = 63.0) -> dict
     반환: {"model": "FOM", "R0", "R1", "C1_eq", "alpha", "rmse_V", "meta"}
   - scipy.optimize.least_squares (TRF, max_nfev=2000)
   - bound: R0 ∈ [1e-5, 1e-2], R1 ∈ [1e-5, 1e-2], Q ∈ [1, 1e5], α ∈ [0.5, 1.0]

K1.3 algo/ecm/ecm_2rc.py 신규 (비교 baseline)
   - 정수 2-RC 식별 (R0 + R1//C1 + R2//C2)
   - identify_2rc() 동일 패턴

K1.4 algo/runners/run_ecm_identify.py 확장
   - --model {1RC, 2RC, FOM} 옵션
   - --files 패턴 (glob) 으로 cycle별 일괄 식별
   - 산출: outputs/runs/K1-fom-25C/, K1-fom-50C/ 안에 params_per_cycle.csv

K1.5 cycle 별 식별 실행 (자료 산출 메인)
   - 입력 1: 셀 엑셀파일/셀 엑셀파일/CH2_25deg/DCIR/*.csv
     cycle 100, 500, 1000, 1500, 2000, 2500, 3000 일괄 (있는 것만)
   - 입력 2: 셀 엑셀파일/셀 엑셀파일/CH7_50deg/DCIR/*.csv
     cycle 100, 500, 1000, 1500, 2000, 2500, 3000, 3500 일괄
   - 모델 3종: 1RC, 2RC, FOM 모두 식별
   - 산출: outputs/runs/K1-{1rc,2rc,fom}-{25C,50C}/params_per_cycle.csv (총 6개)

K1.6 figure 생성 (algo/evaluation/plots.py 활용)
   outputs/figures/K1_fractional_ecm/ 안에 6장:
   - fig1_pulse_fit_1rc_vs_fom.pdf — 한 펄스 (예: 25°C cycle 1300) 에서 두 모델 fit 비교
   - fig2_rmse_vs_cycle_25C.pdf — cycle별 voltage RMSE (1RC vs 2RC vs FOM)
   - fig3_rmse_vs_cycle_50C.pdf — 동일 50°C
   - fig4_r0_alpha_trajectory_25C.pdf — R0(cycle), α(cycle)
   - fig5_r0_alpha_trajectory_50C.pdf — 동일 50°C
   - fig6_temperature_comparison.pdf — 25 vs 50°C R0·α 비교
   각 PDF 와 PNG 동시 저장.

K1.7 평가 자동 보고
   outputs/runs/K1-summary/REPORT.md 자동 생성:
   - 평균 voltage RMSE 표 (1RC / 2RC / FOM)
   - 분수계가 1-RC 대비 X% 감소 비율
   - α(cycle) Spearman ρ (단조성)
   - 권고: KCI1 페이퍼의 Methods·Results 에 직접 활용

K1.8 unit tests
   - tests/algo/test_fractional_ecm.py
     - 합성 펄스 데이터 (R0/R1/Q/α 알려진 값) → 식별 결과가 ground truth 와 일치
     - 정수 2-RC 도 동일 패턴

[규칙 — 엄수]
- ui/ 안 만지기
- pickle 인터페이스 금지
- 공개 API 시그니처 변경 시 사용자 승인
- outputs/runs/<run_id>/ 덮어쓰기 금지 (KCI1 작업은 K1- prefix 로 충돌 회피)
- 한국어 폴더 path 인코딩 안전 처리 (PYTHONUTF8=1 권장)

[acceptance 기준]
- 분수계 모델 평균 voltage RMSE 가 정수 1-RC 대비 20% 이상 감소 — 가설 입증
- α(cycle) Spearman ρ 절댓값 0.7 이상 — SOH 지표 후보 입증
- 25 vs 50°C 변화 방향 전기화학적 직관과 일치 (R0 ↓ at higher T 등)

[Stage 1 종료 시]
- 위 모든 산출물 완성
- outputs/handoff_stage1_codex.md 한 장 (4줄):
  1. [변경 요약]: KCI1 브랜치 무엇을, 왜
  2. [공개 API 영향]: identify_fractional, identify_2rc 신규 + 시그니처 명시
  3. [pytest 결과]: tests/algo 마지막 5줄
  4. [Antigravity에 알릴 것]: K1 결과를 시각화하려면 어느 파일/함수 사용
- KCI1 브랜치를 origin/KCI1 로 push: git push -u origin KCI1
- main 브랜치는 손대지 말 것 (Antigravity 영역). KCI1 결과가 main 에 필요하면 PR 또는 사용자 merge 결정 후.

지금 K1.1 부터 시작하라.

=== 끝 ===
```

---

## 사용 안내

1. **GitHub 동기화 먼저**: 너가 `push_workspace.ps1` 한 번 실행해서 Stage 0 산출물 + KCI1 브랜치 strategy.md 가 GitHub 에 올라가 있어야 코덱스가 KCI1 브랜치를 받을 수 있어
2. 그 후 Codex 에 위 `=== 시작 ===` ~ `=== 끝 ===` 사이만 복사해서 첫 메시지로 붙여넣기
3. Codex 가 K1.1 ~ K1.8 작업 (대략 2~3시간 예상, fractional ECM 식별이 수치적으로 까다로움)
4. 끝나면 너 → 나에게 "Stage 1 Codex 끝났어" 한 줄
5. 내가 검증 + Antigravity 진행 동의 받은 후 → Antigravity 킥오프
