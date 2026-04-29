# SCI 전략 PPT 생성 가이드

`build_ppt.js` 를 실행하면 `FOM_AEKF_SCI_strategy.pptx` 16장 슬라이드가 생성된다.

## 한 번만 — 의존성 설치

이 폴더(`ppt_build/`)에서 PowerShell 또는 cmd 를 열고:

```powershell
npm install pptxgenjs
```

(Node.js 가 설치되어 있어야 한다. `node --version` 확인. 없으면 https://nodejs.org 에서 LTS 설치.)

## 실행

```powershell
node build_ppt.js
```

성공하면 `ppt_build\FOM_AEKF_SCI_strategy.pptx` 가 생성된다. 실행 시간 약 3~5초.

## 슬라이드 구성 (18장, v3 multi-paper 반영)

| # | 제목 |
|---|---|
| 1 | Title — FOM-AEKF SCI 전략 (dark) |
| 2 | Agenda — 발표 개요 9항목 |
| 3 | 배경 — 왜 SOC·SOH를 동시에 추정해야 하는가 (3-column) |
| 4 | 2025–2026 SOTA 동향과 빈 공간 (포화 영역 + white space) |
| 5 | 본 연구 한 줄 답 — FOM-AEKF + Cross-Scale (3 pillar) |
| 6 | 4대 Contribution Statement (2x2 grid) |
| 7 | 데이터셋 — Pouch 셀과 모듈 두 축 |
| 8 | FOM-AEKF 알고리즘 구조도 (블록 다이어그램) |
| 9 | 온도 × SOH 2D Q/R 스케줄러 (heatmap 컨셉) |
| 10 | 비교 baseline 7종 (테이블) |
| 11 | Split 프로토콜 6종 (그리드 카드) |
| 12 | 평가 메트릭 4축 |
| 13 | 예상 결과 — 정량 시나리오 (SOC RMSE / SOH MAE 차트 + 4 stat) |
| 14 | 논문 섹션 구성 IMRaD 매핑 (Abstract ~ Conclusion 8행) |
| **15** | **Multi-Paper 5편 매트릭스 (SCI 3 + KCI 2)** |
| **16** | **Multi-Paper 타임라인 (Gantt 14개월)** |
| 17 | 코드 마일스톤 14개월 + 타깃 저널 표 |
| 18 | Conclusion + 리스크 + 다음 단계 (dark) |

## 색상 팔레트

- 배경 어두운 슬라이드: `#0A2540` (ocean deep)
- 본문 슬라이드: 흰색
- 강조: `#F96E46` (coral), `#FFD166` (gold)
- 본문 텍스트: `#1A2B3A`

## 수정·재생성

`build_ppt.js` 를 편집한 뒤 `node build_ppt.js` 를 다시 실행하면 같은 파일명으로 덮어쓴다.

## 한국어 폰트

기본은 Calibri. 한국어는 시스템 fallback (Windows 에선 보통 Malgun Gothic 자동 적용). PPT 열었을 때 한국어가 깨지면 PowerPoint 에서 슬라이드 마스터의 폰트를 'Malgun Gothic' 으로 바꾸거나, `build_ppt.js` 상단의 `FONT.head` / `FONT.body` 를 `"Malgun Gothic"` 으로 수정 후 재실행.

## 차트·결과 수치

Slide 13 의 SOC RMSE / SOH MAE / stat 카드 수치는 **SOTA 문헌 통상 범위 + 본 연구 목표치로 구성한 가상 시나리오**다. P2~P3 실측 후 실제 값으로 교체할 것 — `build_ppt.js` 의 `socData.values`, `sohData.values`, `stats[].v` 를 수정.
