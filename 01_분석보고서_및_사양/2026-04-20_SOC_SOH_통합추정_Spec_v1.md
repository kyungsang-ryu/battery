# SOC/SOH 통합 추정 알고리즘 개발 Spec (v1)

**작성일**: 2026-04-20
**목적**: SCI급 논문 발표를 위한 SOC/SOH 동시(Joint) 추정 알고리즘 개발 전략 및 구현 사양서
**관련 선행 문서**
- `SOC_SOH_통합추정_전략_및_인사이트.md` (Gemini 초안, 2026-04-20)
- `배터리_데이터_분석_보고서.md` (데이터 탐색 요약)

---

## 1. 연구 목표

### 1.1 일반 목표
하나의 알고리즘으로 **SOC와 SOH를 동시에(Joint) 추정**하며, 동일 조건에서 기존 단일/단순 Joint 기법 대비 **정량적으로 우수한 성능**을 보이는 알고리즘을 개발한다.

### 1.2 구체 목표
- 기존 SOC, SOH, Joint 기법들의 성능 한계를 정량 벤치마크로 입증
- 에기연 데이터의 고유 강점(온도 −15~45°C × 사이클 1300~3200)을 이용한 novelty 확보
- 공개 데이터셋(NASA PCoE / CALCE 등) 교차검증으로 일반화 성능 증명
- **SCI급 저널 게재 가능한 수준의 contribution 확보**

### 1.3 제약 및 가정
- 셀 chemistry는 1종(에기연 열화셀) — 셀 교차 일반화는 공개 데이터셋으로 보강
- Cell spec: **JH3 Cell(보성파워텍) 확정** — 상세는 §1.4
- Chemistry: **NMC/NCA 계열로 추정** (nominal 3.7 V, 3.0~4.2 V 운용 범위). RPT OCV 곡선 plateau 유무로 교차검증 예정
- OCV–SOC 곡선은 RPT로부터 추출 필요
- 구현 backend는 **Python 중심** (Simulink 필요 시 MATLAB 병행)

### 1.4 대상 셀 상세 (JH3, 보성파워텍)

| 분류 | 항목 | 값 |
|---|---|---|
| 일반 | Form factor | **Pouch** (Wing folded + PET tape 6-point sealing) |
| 일반 | 치수 (T×W×L) | 16 × 100.2 × 352.5 mm |
| 일반 | 무게 | 1,175 g |
| 일반 | Cell Lead | (+) 45×42 / 0.4t, (−) 45×42 / 0.2t |
| 정격 | **Capacity** | **63.0 Ah** |
| 정격 | Nominal Voltage | 3.7 V |
| 정격 | Operating Voltage | 3.0 ~ 4.2 V |
| 정격 | Energy | 233 Wh |
| 정격 | Cycle Life | 80% @ 4,000 cycles |
| 적용 | DCIR | 1.03 ± 0.25 mΩ (25 °C, SOC 30%) |
| 적용 | ACIR | 0.575 ± 0.175 mΩ (25 °C, SOC 30%) |

**활용 포인트**
- **Cₙ₀ = 63.0 Ah**: ECM의 초기 용량 파라미터.
- **R₀ 초기값**: DCIR 1.03 mΩ @ 25 °C, SOC 30% → Slow filter의 R₀ 초기 평균. 노화에 따른 증가분을 SOH 지표로 활용 가능.
- **운용범위 3.0~4.2 V**: OCV 룩업 경계. RPT에서 이 구간을 샘플링.
- **Chemistry 미서면기재 이슈**: 전압 프로파일·Nominal 3.7V → NMC/NCA 추정. 최종 확정을 위한 확인 경로:
  1. 보성파워텍 김태연 과장(010-9504-4416)에게 직접 문의(양극재 조성)
  2. RPT low-rate 방전의 dQ/dV 곡선 — NMC는 2~3개 피크, LFP는 매우 날카로운 단일 plateau
  3. 2번을 우선 시도(비용 0).

---

## 2. 기존 기법 비교 평가 (확장판)

선행 문서(Gemini) 테이블에 누락된 주요 SOTA 보강.

### 2.1 SOC 추정 기법
| 기법 | 원리 | 장점 | 단점 | 비고 |
|---|---|---|---|---|
| Ah Counting | 전류 적산 | 연산량 최소 | 초기오차·노이즈 누적 | 단독 사용 불가 |
| OCV Look-up | OCV-SOC 맵 | 높은 정확도 | 휴지시간 필요 | 보정용 |
| EKF / UKF / CKF | 비선형 베이즈 필터 | 실시간·노이즈 강건 | ECM 파라미터 SOH 변화에 취약 | 가장 흔함 |
| Particle Filter | 몬테카를로 베이즈 | 강비선형 대응 | 연산량 큼 | 고정밀용 |
| H∞ Filter | 최악케이스 보장 | 모델 불확실성 강건 | 튜닝 난이도 | 강건성 연구용 |
| Sliding Mode Observer | 슬라이딩 모드 이론 | 강건성·빠른 수렴 | chattering | 제어공학 트렌드 |
| Luenberger Observer | 선형관측기 | 구현 간단 | 비선형 대응 약함 | 기초 baseline |
| LSTM / CNN / GRU | 시계열 DL | 비선형 학습 | 데이터 의존·블랙박스 | 대규모 데이터 필요 |
| Transformer / TCN / Mamba | Attention / Dilated / SSM | 긴 시퀀스 강점 | 연산량 | 최신 트렌드 |

### 2.2 SOH 추정 기법
| 기법 | 원리 | 장점 | 단점 | 비고 |
|---|---|---|---|---|
| Direct Measurement | 완충·완방 용량 측정 | 정확도 최고 | 실사용 중 불가 | RPT/오프라인 |
| ECM Resistance Tracking | R₀ 증가 추적 | 물리 직관 | 파라미터 분리 어려움 | 필터와 결합 |
| **ICA** (Incremental Capacity) | dQ/dV 피크 분석 | 물리해석성 | 특정 충전 프로파일 필요 | 2020~ 핫함 |
| **DVA** (Differential Voltage) | dV/dQ 분석 | 노화모드 분리 가능 | 정전류 조건 필요 | ICA와 쌍 |
| Coulombic Efficiency | 충방전 비 추적 | 측정 단순 | 온도 민감 | 보조지표 |
| GPR (Gaussian Process) | 베이지안 회귀 | **불확실성 자연 포함** | 연산량 O(N³) | UQ 트렌드 |
| SVR | 서포트 벡터 회귀 | 소량 데이터 강점 | 커널 선택 | 보조 baseline |
| LSTM/CNN SOH | DL 기반 | end-to-end | 데이터 의존 | 흔한 baseline |

### 2.3 Joint (SOC+SOH 동시) 기법
| 기법 | 구조 | 장점 | 단점 |
|---|---|---|---|
| **Dual EKF/UKF** | 2 필터(상태+파라미터) 상호 피드백 | 안정·입증 다수 | Q/R 고정 한계 |
| **Joint (Augmented) EKF** | 단일 필터, 상태 확장 [SOC, R₀, Cₙ] | 수식 단순 | 수치 안정성·관측가능성 문제 |
| **AEKF / ASR-AEKF** | 잔차 기반 적응 공분산 | 시변 노이즈 대응 | 과적응 위험 |
| **Particle Filter Joint** | PF로 상태+파라미터 | 강비선형 | 연산량 큼 |
| **Multi-task NN** | 공유 인코더 + 2 head | 상관관계 학습 | 데이터 의존 |
| **PINN Joint** | 물리 잔차 loss + NN | 혁신성, 강건 | 훈련 불안정 |

---

## 3. 선정 방향성

### 3.1 최종 결정
- **구현 언어**: Python (PyTorch / NumPy / SciPy / filterpy 등)
- **접근법**: 단계형(Staged) 로드맵. Stage 1부터 논문 가능 수준 확보, Stage 2까지 상위 저널 겨냥, Stage 3는 스트레치 목표.

### 3.2 왜 Python인가
1. 배터리 ML 생태계(PyBaMM, impedance.py, battDB)가 Python 네이티브
2. 최근 배터리 논문 공개 코드 95%+가 Python → SOTA baseline 재현이 거의 무료
3. NASA PCoE / CALCE / MIT-Stanford Severson 등 공개 데이터셋 로더 기성 존재
4. Claude와의 작업 효율(코딩·디버깅·시각화) 압도적

### 3.3 왜 단계형인가
- "Easiest path to SCI" vs "최대 혁신"의 균형.
- Stage 1만으로도 SCI mid-tier 등재 가능 → fallback 확보.
- Stage 2는 기존 기법들과의 엄밀 비교를 논문 내부에 완성 → 상위 저널 가능.
- Stage 3는 성공 시 top-tier, 실패해도 앞 단계가 이미 논문.

### 3.4 로드맵 요약
| Stage | 내용 | 난이도 | 예상 저널 레벨 | 상태 |
|---|---|---|---|---|
| **Stage 1** | Dual Adaptive EKF (온도-노화 coupled Q/R) | ★★☆☆☆ | Mid-tier SCI (IF 3~5) | 1순위 |
| **Stage 2** | Multi-task TCN baseline + 비교 실험 | ★★★☆☆ | Upper-mid SCI (IF 5~8) | 2순위 |
| **Stage 3** | Neural-Augmented Filter (Stage 1+2 융합) | ★★★★★ | Top-tier (stretch) | 조건부 |

---

## 4. Stage 1 설계 — Dual Adaptive EKF (Temperature-Aging Coupled)

### 4.1 아키텍처 개요
2-filter 이중 구조 + 적응 튜닝 모듈.

```
[V, I, T] ──┬──► Fast Filter (SOC estimation)  ──► SOC
           │         ↑ (R₀, R₁, Cₙ update)
           │         │
           └──► Slow Filter (Parameter estimation: R₀, R₁, Cₙ → SOH) ──► SOH
                     ↑
        Adaptive Q/R scheduler  f(T, SOH) — 핵심 novelty
```

- Fast filter: 수 Hz ~ 분 단위. SOC 상태 실시간 추적.
- Slow filter: 사이클/시간 단위. 내부 저항·용량 추적 → SOH 환산.
- **Adaptive scheduler**: 현재 온도 T와 추정 SOH를 입력으로 Q, R 매트릭스를 스케줄링.

### 4.2 등가회로모델 (ECM)
- 1차 또는 2차 RC 병렬 Thevenin 모델
- 상태: x = [SOC, V₁, V₂]ᵀ  (2RC 기준)
- 파라미터: θ = [R₀, R₁, C₁, R₂, C₂, Cₙ]ᵀ
- OCV-SOC 관계: RPT 추출 룩업 + 온도 보정

### 4.3 Adaptive Q/R Scheduling (Novelty 핵심)
기존 AEKF는 Q, R을 이노베이션(innovation) 잔차만으로 조정. 본 연구에서는:

    Q_k = Q₀ · f_Q(T_k, SOH_k_hat)
    R_k = R₀ · f_R(T_k, SOH_k_hat)

함수 f_Q, f_R는 에기연 데이터의 **온도 × 사이클 그리드** 상에서 오프라인 학습(룩업 또는 얕은 MLP).

→ **"Temperature–aging coupled adaptive"** 키워드로 1순위 contribution claim.

### 4.4 Coupling 메커니즘
- Slow filter의 SOH 추정이 fast filter의 Cₙ(용량)·R₀(저항)에 즉시 반영 → SOC 계산 오차 저감.
- Fast filter의 SOC 추정이 slow filter의 OCV-SOC 매핑 정확도 유지.
- 두 필터는 time-scale separation으로 안정성 확보 (Lyapunov 분석 가능성).

### 4.5 구현 모듈 (Python)
| 파일 | 역할 |
|---|---|
| `ecm_model.py` | ECM 순방향 시뮬레이터 |
| `ocv_soc.py` | RPT 기반 OCV-SOC-T 룩업 |
| `dual_aekf.py` | 메인 Dual AEKF 알고리즘 |
| `adaptive_scheduler.py` | Q/R 스케줄러 (MLP or lookup) |
| `evaluate.py` | 메트릭 계산 및 플로팅 |
| `dataloader_kier.py` | 에기연 데이터 로더 |
| `dataloader_public.py` | NASA/CALCE 로더 |

---

## 5. Stage 2 설계 — Multi-task TCN Baseline

### 5.1 목적
1. 논문 내부에서 "딥러닝 대비 본 기법의 우위" 입증용 baseline.
2. Stage 3 설계의 예비 실험(공유 representation 학습 방식 탐색).

### 5.2 아키텍처
```
[V, I, T] 시계열 (window=N) ──► TCN 인코더 ──┬──► SOC head
                                            └──► SOH head
```

- Loss: L = λ₁·‖SOC − SOC_hat‖² + λ₂·‖SOH − SOH_hat‖²
- 가중치 λ는 uncertainty-weighted (Kendall et al., 2018) 방식 자동 튜닝.

---

## 6. Stage 3 설계 (Stretch) — Neural-Augmented Filter

### 6.1 컨셉
Stage 1의 Dual AEKF를 뼈대로, 다음 두 지점에 NN 삽입:
1. **ECM residual 보정 NN**: ECM이 담지 못하는 비선형 잔차를 NN이 학습 (physics-guided).
2. **Bayesian variant**: 변분 근사로 posterior 분포 추정 → uncertainty quantification 확보.

이 구조는:
- PINN의 정신(물리 + NN)을 계승하되
- Pure PINN의 훈련 불안정성 회피
- 수학적 안정성 분석 여지(Lyapunov) 남김

### 6.2 조건부 실행
Stage 1+2 완료 + 남은 시간·자원이 있을 때 착수. 실패해도 Stage 1/2 논문 영향 없음.

---

## 7. 벤치마크 방법론

### 7.1 데이터셋
**필수**
- 에기연 열화셀 (자체): RPT, DCIR, ACIR, Pattern — −15~45°C × cycle 1300~3200
- NASA PCoE Battery (공개): 18650 NMC, 실온~40°C

**선택**
- CALCE (U. Maryland): CS2 / CX2 셀
- MIT-Stanford Severson (2019): LFP 124개 셀 — cycle-life prediction 에 탁월

### 7.2 Train/Test Split 프로토콜 (리젝 방지 핵심)
- **Cell-level split** 기본: 학습 셀과 테스트 셀 비중복
- 에기연은 셀 수 제한 → **condition-level split** 병용 (일부 온도/사이클 구간은 테스트 전용)
- 시계열 누수 방지: 학습 구간 뒤 시점만 테스트

### 7.3 평가 메트릭
- **정확도**: RMSE, MAE, MAPE, MAX absolute error
- **강건성**: 초기 SOC 오차(10%/20%/30% 섭동) 복구 시간·수렴 오차
- **외삽**: 학습에 없는 온도 구간 테스트
- **불확실성 품질**: PICP (Prediction Interval Coverage Prob), NLL
- **연산량**: 추론 시간, 메모리 — BMS 탑재성 논의용

### 7.4 Baseline 비교 대상
- SOC: Ah Counting, OCV Look-up, EKF, UKF, LSTM
- SOH: ICA-RF, GPR, LSTM-SOH
- Joint: Dual EKF (non-adaptive), Joint EKF, Multi-task LSTM

---

## 8. Novelty Positioning (Contribution Statement 초안)

> This study proposes a **temperature–aging coupled dual adaptive Kalman filter** for joint SOC/SOH estimation of lithium-ion cells. Unlike conventional AEKF approaches that adapt process/measurement covariances solely based on the innovation residual, we introduce **a two-dimensional scheduling surface over temperature and estimated SOH**, learned offline from a thermally-rich aging dataset (KIER-cell, −15~45 °C × 1300–3200 cycles). The proposed method shows [X]% lower RMSE in SOC under aged conditions and [Y]% lower MAE in SOH compared to state-of-the-art dual EKF and multi-task LSTM baselines, verified on KIER-cell, NASA PCoE, and CALCE datasets.

**3 Contributions**
1. 온도-노화 coupled Q/R scheduling (오프라인 학습)
2. Dual filter 구조의 time-scale separation 안정성 분석
3. 넓은 열화·온도 커버리지 데이터셋에서 외삽 성능 입증

---

## 9. Target 저널

| 저널 | IF (대략) | 핏 |
|---|---|---|
| IEEE Transactions on Transportation Electrification | 7 | 매우 적합 (BMS, joint estimation 강점) |
| Journal of Energy Storage (Elsevier) | 8~9 | 범용, 채택 폭 넓음 |
| Applied Energy | 11 | 상위, 성능+임팩트 필요 |
| eTransportation | 13 | Top-tier, Stage 3까지 완성 시 |
| Journal of Power Sources | 8 | 전기화학 강조 시 |
| IEEE Transactions on Vehicular Technology | 6 | 차량 BMS 앵글 시 |

**1차 Target**: IEEE TTE 또는 J. Energy Storage (Stage 1 기반)

---

## 10. 리스크 & 완화책

| 리스크 | 영향 | 완화책 |
|---|---|---|
| Cell spec(용량, OCV) 미확정 | 전체 지연 | RPT에서 직접 추출, `18650_SOH`/`pouch_SOH` 폴더 재검토 |
| 공개 데이터셋 chemistry 상이 | 일반화 주장 약화 | chemistry별 파라미터 재추정 논문화 |
| Stage 2 TCN 과적합 | 비교 부당 | 엄격 cross-validation, early stopping, data augmentation |
| Stage 3 훈련 불안정 | 스트레치 미달 | 조건부 실행, Stage 1/2로 논문 완결 |
| Train/Test 누수 지적 | 리젝 | cell-level split, time-ordered split 엄격 |
| 단일 chemistry 비판 | 리뷰어 지적 | 공개 데이터셋 다수로 보강 |

---

## 11. 이행 계획 (Milestones, 가이드)

| Week | 작업 | 산출물 |
|---|---|---|
| 1~2 | Cell spec 확정, 데이터 인벤토리, Python env | 데이터 요약, env 세팅 |
| 3~4 | OCV-SOC 추출, ECM 파라미터 식별 | `ecm_model.py`, `ocv_soc.py` |
| 5~6 | Dual EKF 기본(non-adaptive) 구현 | 1차 baseline 결과 |
| 7~8 | Adaptive Q/R scheduler 설계·학습 | Stage 1 완성 |
| 9~10 | NASA/CALCE 확장 + 벤치마크 | 1차 결과 테이블 |
| 11~12 | TCN multi-task (Stage 2) | Stage 2 완성 |
| 13~14 | 전체 비교·플롯·초고 | 논문 draft v1 |
| 15+ | (조건부) Stage 3, 투고 준비 | 논문 draft v2 |

*상기 주차는 유동적. 실 일정은 사용자 가용시간에 따름.*

---

## 12. 다음 즉시 작업 (Immediate Next Actions)

1. ~~**Cell spec 확정**~~ → **완료(v1.1)**. JH3 상세는 §1.4.
2. **Chemistry 최종 확정** — `pouch_SOH` RPT 파일에서 저율(예: 0.1C) 방전 dQ/dV 곡선으로 NMC/NCA/LFP 구분.
3. **OCV–SOC 룩업 추출** — RPT 저율 방전/충전 평균으로 초기 OCV(SOC) 함수 산출 → `ocv_soc.py` 초판.
4. **Python 환경 세팅** — `requirements.txt` 초안 작성 및 가상환경 구성.
5. **공개 데이터셋 다운로드 스크립트** — NASA PCoE 1순위, CALCE 2순위.

---

## 13. 문서 연속성 프로토콜

- 본 Spec은 **v1**. 중요 결정은 이 문서 버전 증가로 기록.
- 대화 중 발생한 결정/이슈/인사이트는 사용자 요청 시 즉시 문서화 (`01_분석보고서_및_사양/` 하위).
- Claude 메모리 시스템(`~/.claude/projects/…/memory/`)에도 상태 반영 → 다음 세션 자동 연속성.
- 변경 이력은 이 파일 하단 `## Changelog` 에 유지.

---

## Changelog

- **2026-04-20 v1** (초판)
  - Gemini 초안 전략 검토·보강
  - Python 선택, 단계형 로드맵 확정
  - Stage 1(Temperature–Aging Coupled Dual Adaptive EKF)을 메인 contribution으로 확정
  - Stage 2/3 포지셔닝
  - 벤치마크 프로토콜·평가 메트릭·target 저널 명시

- **2026-04-20 v1.1**
  - §1.3 업데이트, §1.4 신설: **JH3 Cell(보성파워텍) 스펙 확정**
    - Pouch, 63.0 Ah, 3.7 V nom, 3.0~4.2 V, DCIR 1.03 mΩ, ACIR 0.575 mΩ
    - Chemistry는 전압 프로파일 근거 NMC/NCA 추정(확정 전) — RPT dQ/dV로 검증 예정
  - §12 Immediate Actions 재정렬: Cell spec 완료 → Chemistry 확정·OCV 추출·Python env를 최우선 3건으로
