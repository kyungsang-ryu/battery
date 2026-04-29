# 2026-04-20 오늘의 Action List

**컨텍스트**: 프로젝트 착수일. Spec v1.1 발행(JH3 Cell 확정) 직후.
**관련 문서**: [Spec v1](2026-04-20_SOC_SOH_통합추정_Spec_v1.md)

---

## 완료 (오늘)
- [x] **Spec v1.1 발행** — JH3 Cell(보성파워텍) 사양 §1.4 반영. Open 이슈 ① "Cell spec 미확정" 종결.
- [x] **`requirements.txt` 초안** 프로젝트 루트에 작성. Python 3.11 타깃.

## 이어서 할 일 (우선순위順)

### [P0] Python 환경 실제 구성
- [ ] `python --version` 확인. 3.11이 아니면 설치 또는 pyenv/conda로 선택.
- [ ] 가상환경 생성: `python -m venv .venv` (또는 `conda create -n battery python=3.11`)
- [ ] `pip install -r requirements.txt` 실행 → 에러 로그는 이 파일 하단 "이슈 메모"에 기록.
- [ ] 동작 확인: `python -c "import numpy, scipy, pandas, filterpy, torch; print('ok')"`

### [P1] Chemistry 최종 확정 (Open 이슈 ② 해결)
- [ ] `02_실험_데이터/pouch_SOH/` 에서 **저율(0.1C 이하) 완전방전 RPT** 파일 탐색.
- [ ] Python에서 V(t), I(t) 읽어 Q(누적) 계산 → `dQ/dV vs V` 플롯.
- [ ] 판정 기준:
  - **NMC**: 3.6~3.8 V, 3.9~4.0 V 근처에 2~3개 완만한 피크.
  - **NCA**: NMC와 유사하나 피크가 더 평평.
  - **LFP**: 3.3 V 근처에 매우 날카로운 단일 plateau (다른 구간 거의 평탄).
- [ ] 판정 결과를 `01_분석보고서_및_사양/2026-04-20_chemistry_판정.md` 로 요약.

### [P2] OCV–SOC 룩업 초판
- [ ] 같은 저율 RPT의 **충·방전 평균(pseudo-OCV)**를 SOC 0~100%에 대해 산출.
- [ ] `02_실험_데이터/pouch_SOH/` 중 25 °C 기준 데이터 1개부터 시작 → 온도 확장은 후속.
- [ ] 산출물: `ocv_soc_25C_v0.csv` (SOC 0.0~1.0, 0.01 간격).

### [P3] 공개 데이터셋 계획
- [ ] NASA PCoE 다운로드 URL·용량 확인만 (실제 다운로드는 내일 이후).
- [ ] `dataloader_public.py`는 내일 이후 착수.

---

## Open 이슈 현황 (Spec §1.3 / §12 연동)

| 번호 | 내용 | 상태 | 비고 |
|---|---|---|---|
| ① | Cell spec 미확정 | **Closed (2026-04-20)** | JH3 확정, Spec §1.4 |
| ② | Chemistry 미확정 | Open (오늘 P1) | dQ/dV 판정 예정 |
| ③ | Python 환경 미구성 | Open (오늘 P0) | requirements 초안 작성됨 |
| ④ | 공개 데이터셋 로더 없음 | Open | NASA → CALCE → MIT |
| ⑤ | OCV–SOC 룩업 없음 | Open (오늘 P2) | 25 °C 부터 |

---

## 이슈 메모 (작업 중 발견 시 추가)
<!-- 예: pip install 에러, 데이터 포맷 특이사항, 결정 변경 등 -->

---

## 다음 날 이월 후보
- NASA PCoE 실제 다운로드 + `dataloader_public.py` 초판
- 25 °C 외 온도(−15, 0, 45 °C)의 OCV 온도 보정항 추출
- Spec v1.2 반영 (chemistry 확정 + OCV 초판 기반)
