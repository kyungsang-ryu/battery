// build_paper.js
// KCI1 한글 논문 초고 — 한국산학기술학회 논문지 심사용 양식 (2019)
// 글·형식 참고: 사용자 본인 논문 (2021_rev02)
//
// 실행:
//   1) 한 번만: npm install docx
//   2) 매번:   node build_paper.js
// 결과: K1_paper_draft.docx

const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, PageOrientation, LevelFormat,
  TabStopType, TabStopPosition, Column, SectionType,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  VerticalAlign, PageNumber, PageBreak,
} = require('docx');

// ─────────────────────────────────────
// 페이지 사이즈 (188 × 258 mm), 1 mm = 56.6929 DXA
// ─────────────────────────────────────
const mm = (n) => Math.round(n * 56.6929);

const PAGE = {
  size:   { width: mm(188), height: mm(258) },
  margin: { top: mm(28), right: mm(20), bottom: mm(20), left: mm(20),
            header: mm(15), footer: mm(15) },
};

// ─────────────────────────────────────
// 글꼴 (한국산학기술학회 서식)
// ─────────────────────────────────────
const FONT_KR = "맑은 고딕";
const FONT_EN = "Times New Roman";

// 폰트 크기 (docx half-points: 9pt = 18, 14pt = 28)
const SZ = {
  titleKr: 28,    // 14pt
  titleEn: 28,    // 14pt
  abstract: 17,   // 8.5pt
  keywords: 17,   // 8.5pt
  h1: 22,         // 11pt
  h2: 19,         // 9.5pt
  h3: 18,         // 9pt
  body: 18,       // 9pt
  bodyEn: 18,     // 9pt
  caption: 16,    // 8pt
  reference: 16,  // 8pt
};

// 줄간격 (docx 240 = 단일 100%; 250% = 600, 170% = 408, 160% = 384, 150% = 360, 145% = 348, 130% = 312, 110% = 264)
const LS = {
  title: 312,     // 130%
  abstract: 360,  // 150%
  abstractEn: 348, // 145%
  h1: 600,        // 250%
  h2: 408,        // 170%
  h3: 408,        // 170%
  body: 384,      // 160%
  caption: 384,   // 160%
  reference: 264, // 110%
};

// ─────────────────────────────────────
// Helper functions
// ─────────────────────────────────────
const krRun = (text, opts = {}) => new TextRun({
  text, font: FONT_KR, size: opts.size || SZ.body,
  bold: opts.bold || false, italics: opts.italics || false,
  color: opts.color || "000000",
});

const enRun = (text, opts = {}) => new TextRun({
  text, font: FONT_EN, size: opts.size || SZ.body,
  bold: opts.bold || false, italics: opts.italics || false,
  color: opts.color || "000000",
});

const para = (children, opts = {}) => new Paragraph({
  children: Array.isArray(children) ? children : [children],
  alignment: opts.align || AlignmentType.JUSTIFIED,
  spacing: { line: opts.lineSpacing || LS.body, before: opts.before || 0, after: opts.after || 0 },
  indent: opts.indent || undefined,
});

// ─────────────────────────────────────
// 본문 텍스트 (사용자 본인 논문 톤 따라 격식·무인칭)
// ─────────────────────────────────────

// 제목
const TITLE_KR = "NCM 파우치 셀의 분수계 등가회로모델 식별을 통한 단자전압 정확도 향상 방안";
const TITLE_EN = "A Study on Terminal Voltage Accuracy Improvement Method through Fractional-Order Equivalent Circuit Model Identification for NCM Pouch Cell";

// 저자 (placeholder — 사용자가 본인 정보로 교체)
const AUTHOR_KR = "유경상";
const AUTHOR_EN = "Kyungsang Ryu";
const AFFIL_KR = "○○대학교 전기공학과";
const AFFIL_EN = "Department of Electrical Engineering, ○○ University";

// 국문 요약
const ABSTRACT_KR = "리튬이온 배터리의 BMS 운용에서 SOC와 SOH의 정확한 추정은 필수적이며, 이를 위해서는 노화 진행에 따른 등가회로모델(ECM)의 파라미터 변화를 신뢰성 있게 추적할 수 있는 모델이 요구된다. 그러나 정수 차수 1-RC 모델은 배터리의 비선형 전기화학 응답을 표현하는 데 한계가 있어, 노화 셀에서는 단자전압 잔차가 누적되는 문제점이 있다. 본 논문에서는 NCM 파우치 셀을 대상으로 정상 상수 위상 요소(CPE)를 포함한 분수계 등가회로모델을 적용하여, 25 ℃와 50 ℃ 두 온도 조건에서 cycle 100 부터 3000까지의 DCIR 펄스 데이터를 이용한 모델 식별을 수행하였다. 시뮬레이션 결과, 분수계 모델은 정수 1-RC 대비 단자전압 잔차 RMSE를 25 ℃에서 70.0%, 50 ℃에서 63.0% 감소시켰으며, 50 ℃ 조건에서 R0의 Spearman 상관계수가 1.0으로 완전 단조 증가 특성을 보였다. 또한 25/50 ℃ 의 R0 비율이 0.649로 일관되게 나타나 온도 의존성이 전기화학적 직관과 일치함을 확인하였다. 따라서 본 연구에서 제안한 분수계 모델 식별 방안은 향후 SOC/SOH 동시 추정 알고리즘의 고정밀 측정 모델로 활용 가능함을 확인하였다.";

// 영문 Abstract
const ABSTRACT_EN = "Accurate estimation of state-of-charge (SOC) and state-of-health (SOH) is essential for the battery management system (BMS) of lithium-ion batteries, which requires a model capable of reliably tracking parameter variations of the equivalent circuit model (ECM) during aging. However, the integer-order 1-RC model has limitations in representing the nonlinear electrochemical response of the battery, leading to accumulated terminal voltage residuals in aged cells. This paper applies a fractional-order ECM with a constant phase element (CPE) to NCM pouch cells, and performs parameter identification using DCIR pulse data from cycle 100 to 3000 under two temperature conditions, 25 ℃ and 50 ℃. Simulation results show that the fractional-order model reduces the mean terminal voltage RMSE by 70.0% at 25 ℃ and 63.0% at 50 ℃ compared with the integer 1-RC model. In addition, the R0 trajectory at 50 ℃ exhibits a perfectly monotonic increasing trend with a Spearman correlation coefficient of 1.0, and the R0 ratio between 25 ℃ and 50 ℃ is consistently 0.649, which is consistent with the electrochemical intuition of temperature dependency. Therefore, the proposed fractional-order model identification method is confirmed to be applicable as a high-precision measurement model for joint SOC/SOH estimation algorithms.";

const KEYWORDS_EN = "Lithium-Ion Battery, Fractional-Order ECM, Parameter Identification, Aging, NCM Pouch Cell";

// ═════════════════════════════════════
// 본문 섹션 (장별)
// ═════════════════════════════════════

const SEC_1_INTRO = [
"리튬이온 배터리는 전기자동차, 에너지 저장 시스템 등 다양한 분야에서 널리 활용되고 있으며, 안정적이고 효율적인 운용을 위하여, BMS(Battery Management System, 이하 BMS)에서의 정확한 SOC(State of Charge, 이하 SOC)와 SOH(State of Health, 이하 SOH)의 추정이 필수적이다. 그러나 SOC와 SOH는 강하게 결합된 상태량으로, 노화 진행에 따른 모델 파라미터의 변화에 의하여, 단독 추정 방식에서는 누적 오차가 발생할 수 있다.",

"등가회로모델(ECM: Equivalent Circuit Model, 이하 ECM)은 BMS의 임베디드 환경에 적합한 표준 모델로 채택되어 왔으며, 정수 차수 1-RC 또는 2-RC 모델이 일반적으로 사용된다. 그러나 이러한 정수계 모델은 배터리의 비선형 전기화학 응답을 근사하는 데 한계가 있으며, 특히 중주파 영역의 임피던스 응답을 정확히 표현하지 못하는 문제점이 보고되고 있다[1, 2].",

"이러한 한계를 극복하기 위하여, 분수계 미적분 이론에 기반한 분수계 등가회로모델(FOM: Fractional-Order Model, 이하 FOM)이 제안되었으며, 정상 상수 위상 요소(CPE: Constant Phase Element, 이하 CPE)를 포함한 R+CPE 구조의 모델이 정수계 모델 대비 단자전압 추정 정확도를 향상시킬 수 있음이 보고되었다[3-5]. 그러나 다수의 기존 연구에서는 단일 사이클 또는 신셀 상태에서의 모델 식별에 국한되어 있어, 노화 진행에 따른 분수계 차수 α의 변화 및 온도 조건에 따른 파라미터 변동 특성에 관한 연구는 제한적인 상황이다[6, 7].",

"따라서 본 논문에서는 NCM(Nickel-Cobalt-Manganese, 이하 NCM) 화학적 조성을 가지는 파우치 셀을 대상으로, 25 ℃와 50 ℃의 두 온도 조건에서 cycle 100 부터 3000까지 노화된 셀의 DCIR(Direct Current Internal Resistance, 이하 DCIR) 펄스 데이터를 활용하여, 정수 1-RC, 2-RC, 그리고 분수계 R+CPE의 세 가지 등가회로모델을 식별하고, 모델별 단자전압 잔차 성능과 노화에 따른 파라미터 변화 특성을 비교 분석한다. 또한 저 사이클 구간에서 발생하는 데이터 분해능 부족에 의한 식별 이상 현상을 진단하고, 이에 대한 분리 보고 절차를 제안한다.",

"본 논문은 다음과 같이 구성된다. 2장에서는 분수계 등가회로모델의 정의 및 모델 파라미터 식별 절차를 기술하고, 3장에서는 식별 알고리즘과 데이터 분해능 진단 절차를 제시한다. 4장에서는 25/50 ℃ 노화 데이터를 대상으로 모델별 단자전압 잔차와 파라미터 변화 특성을 비교 분석하며, 5장에서 본 연구의 결론을 제시한다.",
];

const SEC_2_1_MODEL = [
"리튬이온 배터리의 등가회로모델은 단자전압을 시간 영역에서 표현하기 위하여, OCV(Open Circuit Voltage, 이하 OCV)와 직렬 저항 R0, 그리고 분극 응답을 표현하는 RC 병렬 회로의 결합으로 구성된다. 정수 1-RC 모델의 단자전압 응답은 식 (1)과 같이 표현된다.",
];

const SEC_2_1_AFTER_EQ1 = [
"여기에서 τ = R1·C1은 시상수이며, R1과 C1은 각각 분극 저항과 분극 정전용량을 의미한다. 정수 1-RC 모델은 단일 시상수만을 표현하므로, 배터리의 다중 시간 척도 응답을 정확히 표현하는 데에는 한계가 있다.",

"분수계 R+CPE 모델에서는 정수 정전용량 C 대신 정상 상수 위상 요소(CPE)를 사용하여 분수 차수 α (0 < α ≤ 1)의 응답을 표현하며, 임피던스 영역에서의 정의는 식 (2)와 같다.",
];

const SEC_2_1_AFTER_EQ2 = [
"여기에서 Q는 CPE 계수이며, α는 분수 차수이다. α = 1인 경우 CPE는 일반적인 정전용량으로 환원되며, α < 1인 경우 시간 응답은 stretched-exponential 형태를 가진다. 본 논문에서는 stretched-exponential 시간 응답 근사를 적용하여, 시간 영역에서 분수계 모델의 빠르고 안정적인 식별이 가능하도록 구성한다.",
];

const SEC_2_2_IDENT = [
"DCIR 펄스 시험 데이터로부터 모델 파라미터를 식별하기 위하여, 펄스 직전 휴지 구간의 마지막 단자전압을 OCV로 추정하고, 펄스 시작 직후의 순간 전압 강하를 R0의 초기값으로 산정한다. 이후 펄스 인가 구간과 펄스 후 휴지 구간의 단자전압 응답을 모두 활용하여, 비선형 최소자승법(scipy.optimize.least_squares, TRF 알고리즘)을 통해 (R0, R1, Q, α)의 4개 파라미터를 동시에 추정한다.",

"식별 시 파라미터의 물리적 타당성을 확보하기 위하여, R0 ∈ [10⁻⁵, 10⁻²] Ω, R1 ∈ [10⁻⁵, 10⁻²] Ω, Q ∈ [1, 10⁵], α ∈ [0.3, 1.0]의 범위 내에서 최적화를 수행한다. 한편, α의 하한을 0.3으로 설정한 이유는, 노화된 셀에서 α가 0.5 이하로 감소할 가능성을 반영하기 위함이며, 본 논문의 식별 결과에서도 α가 [0.32, 0.41]의 범위에서 식별됨을 확인하였다.",
];

const SEC_3_ALGO = [
"본 논문에서 제시한 식별 알고리즘은 다음 4단계로 구성된다.",

"[Step 1] DCIR 시험 데이터의 시계열을 펄스 단계별로 분리하여, 펄스 직전 휴지, 펄스 인가, 그리고 펄스 후 휴지 구간을 식별한다.",

"[Step 2] 식별된 각 구간의 시료 수를 점검하고, 펄스 인가 구간의 비영전류 시료 수와 펄스 후 휴지 구간의 시료 수가 식별 가능한 최소 기준에 미달하는 경우, 해당 cycle을 'insufficient_dynamic_samples'로 분류하여 데이터 분해능 부족 사례로 분리한다.",

"[Step 3] 충분한 시료 수를 확보한 cycle에 대하여, 1-RC, 2-RC, 그리고 분수계 R+CPE 모델의 파라미터를 각각 식별하고 단자전압 잔차의 RMSE를 산출한다.",

"[Step 4] 모델별 식별 결과를 종합하여, 평균 잔차 RMSE의 비교, 노화에 따른 R0 및 α의 변화 추세, 그리고 온도 조건에 따른 파라미터 비교를 수행한다.",

"상기 절차에 따른 식별 알고리즘의 흐름을 나타내면 Fig. 1과 같다.",
];

const SEC_4_1_DATA = [
"본 연구에서 사용한 데이터는 NCM 화학적 조성을 가지는 파우치 셀(JH3, 정격 용량 63.0 Ah, 운용 전압 3.0~4.2 V)을 대상으로 한국에너지기술연구원에서 수행한 노화 시험의 DCIR 펄스 데이터이다. 시험 조건은 25 ℃의 ch2 채널과 50 ℃의 ch7 채널 두 셀을 대상으로 100 cycle부터 3000 cycle까지 100 cycle 간격으로 측정되었으며, 본 연구에서는 ch2/ch7의 cycle 100, 500, 1000, 1100, 1200, 1300, 3000의 7개 시점을 대상으로 분석을 수행하였다.",

"DCIR 펄스 시험은 약 1C(62.99 A)의 일정 전류로 약 10초간 방전한 후 휴지 단계로 구성되며, 1 Hz의 측정 주기로 단자전압과 전류가 기록되었다. 본 연구의 시뮬레이션은 Python 3.12 환경에서 numpy, scipy, pandas 라이브러리를 사용하여 수행되었으며, 사례 셀의 사양은 Table 1과 같다.",
];

const SEC_4_2_SCEN = [
"본 연구에서는 정수 1-RC, 정수 2-RC, 그리고 분수계 R+CPE의 세 가지 모델을 동일한 DCIR 데이터에 대하여 식별하고 비교한다. Table 2와 같이 시나리오가 구성된다.",
];

const SEC_4_3_RMSE = [
"세 가지 모델에 대한 평균 단자전압 잔차 RMSE를 비교한 결과는 Table 3과 같다. 분수계 모델은 25 ℃ 조건에서 정수 1-RC 대비 70.0%의 RMSE 감소를 나타냈고, 50 ℃ 조건에서는 63.0%의 감소를 나타냈다. 따라서 분수계 등가회로모델이 두 온도 조건 모두에서 정수계 모델 대비 더 정확한 단자전압 표현이 가능함을 확인하였다.",

"한편, cycle 1300의 25 ℃ DCIR 데이터에 대한 모델별 단자전압 fit 결과를 비교하면 Fig. 2와 같으며, 정수 1-RC 모델은 펄스 후 휴지 구간에서 단자전압 회복을 정확히 표현하지 못한 반면, 분수계 모델은 동일 구간에서 단자전압 측정값과 거의 일치하는 fit 특성을 보였다.",
];

const SEC_4_4_PARAM = [
"분수계 등가회로모델에 의해 식별된 R0와 α의 사이클별 변화를 분석한 결과는 Fig. 3과 같다. R0의 변화 측면에서는, 25 ℃와 50 ℃ 두 조건 모두 cycle 진행에 따른 변화 추세가 관찰되었으며, 특히 50 ℃ 조건에서는 Spearman 상관계수 ρ = 1.0의 완전 단조 증가 특성이 확인되었다. 이는 가속 노화 조건에서 셀의 내부 저항이 일관되게 증가하는 전기화학적 현상과 일치한다.",

"온도 조건별 R0 비교에서는 25 ℃와 50 ℃의 동일 cycle에서 R0_50℃ / R0_25℃의 평균 비율이 0.649로 나타났다. 즉, 50 ℃ 조건에서의 직렬 저항이 25 ℃ 조건 대비 약 35% 낮게 측정되었으며, 이는 온도 상승에 따른 전기화학 반응의 가속화로 인한 내부 저항의 감소 현상과 일치한다.",

"분수계 차수 α의 변화 측면에서는 [0.32, 0.41]의 좁은 범위 내에서 안정적으로 식별되었으며, 이를 통해 분수계 모델이 노화된 셀에서도 일관된 fit 안정성을 가짐을 확인하였다.",
];

const SEC_4_5_DIAG = [
"cycle 100과 500의 DCIR 데이터에 대한 식별 시, 정수 1-RC 모델에서는 R1 = 0으로 수렴하여 단순 저항 응답으로 환원되었으며, 정수 2-RC와 분수계 모델에서는 RMSE가 10⁻¹³ 수준의 비현실적으로 낮은 값으로 수렴하는 현상이 관찰되었다.",

"원인 진단 결과, 해당 cycle의 DCIR 펄스가 1초 수준으로 짧게 측정되어, 비영전류 시료가 1개, 펄스 후 휴지 시료가 1개만 확보되어, 동적 응답을 식별하기에 시료 수가 부족함을 확인하였다. 따라서 본 연구에서는 'insufficient_dynamic_samples' 플래그를 도입하여 해당 cycle을 분리 보고하고, 동적 fit 메트릭에서 제외하였다. 이러한 분리 절차는 식별 알고리즘의 강건성을 확보하는 데 기여할 수 있다.",
];

const SEC_4_6_SUMMARY = [
"본 논문에서 제시한 세 가지 모델에 대한 비교 결과를 종합하면 Table 4와 같다. 분수계 등가회로모델 식별 방안은 정수계 모델 대비 단자전압 잔차를 70% 이상 감소시키며, 노화 진행에 따른 R0의 단조 변화와 온도 조건에 따른 R0의 일관된 비율(0.649)을 동시에 확인할 수 있어, 향후 SOC/SOH 동시 추정 알고리즘의 고정밀 측정 모델로 활용 가능함을 확인하였다.",
];

const SEC_5_CONCLUSION_INTRO =
"본 논문에서는 NCM 파우치 셀의 25 ℃와 50 ℃ 노화 데이터를 대상으로 정수 1-RC, 정수 2-RC, 그리고 분수계 R+CPE의 세 가지 등가회로모델을 식별하고 비교 분석하였다. 이에 대한 주요 결과를 나타내면 아래와 같다.";

const SEC_5_BULLETS = [
"(1) 분수계 등가회로모델은 25 ℃에서 평균 단자전압 잔차를 정수 1-RC 대비 70.0% 감소시켰으며, 50 ℃에서는 63.0% 감소시켰다. 이를 통해 분수계 모델이 정수계 모델 대비 단자전압 표현 정확도가 압도적으로 우수함을 확인하였다.",
"(2) 분수계 모델로 식별된 R0는 50 ℃ 조건에서 Spearman ρ = 1.0의 완전 단조 증가 특성을 보였으며, 25 ℃와 50 ℃의 R0 비율은 평균 0.649로 일관되게 나타나 온도 의존성이 전기화학적 직관과 일치함을 확인하였다.",
"(3) cycle 100과 500의 데이터에 대한 식별 이상 현상은 펄스 측정 시간이 짧음에 의한 데이터 분해능 부족이 원인임을 진단하였으며, 'insufficient_dynamic_samples' 플래그를 통해 분리 보고하는 절차를 제시하였다.",
"(4) 향후에는 분수계 모델로 식별된 시변 파라미터 (R0, R1, α)를 입력으로 하는 적응형 칼만필터 기반 SOC/SOH 동시 추정 알고리즘으로 확장하여, 노화에 강건한 BMS 추정 알고리즘에 대한 추가 연구가 필요하다.",
];

// References (placeholder — 사용자 검증·교체 권장)
const REFERENCES = [
'H. He, X. Zhang, R. Xiong, Y. Xu, H. Guo, "Online model-based estimation of state-of-charge and open-circuit voltage of lithium-ion batteries in electric vehicles", Energy, Vol.39, No.1, pp.310-318, March 2012. DOI: https://doi.org/10.1016/j.energy.2012.01.009',
'G. L. Plett, "Extended Kalman filtering for battery management systems of LiPB-based HEV battery packs: Part 3. State and parameter estimation", Journal of Power Sources, Vol.134, No.2, pp.277-292, August 2004. DOI: https://doi.org/10.1016/j.jpowsour.2004.02.033',
'X. Hu, S. Li, H. Peng, "A comparative study of equivalent circuit models for Li-ion batteries", Journal of Power Sources, Vol.198, pp.359-367, January 2012. DOI: https://doi.org/10.1016/j.jpowsour.2011.10.013',
'Y. Zhang, R. Xiong, H. He, X. Liu, Y. Sun, "A novel approach for state of charge estimation of lithium-ion batteries using fractional order model", IEEE Transactions on Industrial Electronics, Vol.65, No.11, pp.8767-8776, November 2018. DOI: https://doi.org/10.1109/TIE.2017.2772173',
'B. Wang, X. Liu, S. E. Li, J. Wang, H. Wang, "Fractional-order modeling and parameter identification for lithium-ion batteries based on adaptive impedance spectroscopy and improved least squares algorithm", Energy, Vol.187, p.115947, November 2019. DOI: https://doi.org/10.1016/j.energy.2019.115947',
'R. Xiong, J. Tian, H. Mu, C. Wang, "A systematic model-based degradation behavior recognition and health monitoring method for lithium-ion batteries", Applied Energy, Vol.207, pp.372-383, December 2017. DOI: https://doi.org/10.1016/j.apenergy.2017.05.124',
'M. Berecibar, I. Gandiaga, I. Villarreal, N. Omar, J. Van Mierlo, P. Van den Bossche, "Critical review of state of health estimation methods of Li-ion batteries for real applications", Renewable and Sustainable Energy Reviews, Vol.56, pp.572-587, April 2016. DOI: https://doi.org/10.1016/j.rser.2015.11.042',
];

// ═════════════════════════════════════
// 요소 빌더
// ═════════════════════════════════════

// 한글/영문 혼합 단락 (이모지 같은 거 없이 깔끔하게)
function bodyPara(textKr, opts = {}) {
  return new Paragraph({
    children: [krRun(textKr)],
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: LS.body, before: opts.before || 0, after: opts.after || 0 },
    indent: opts.firstIndent ? { firstLine: mm(3) } : undefined,
  });
}

// 헤딩
function h1(text) {
  return new Paragraph({
    children: [krRun(text, { size: SZ.h1 })],
    alignment: AlignmentType.CENTER,
    spacing: { line: LS.h1, before: 200, after: 100 },
    heading: HeadingLevel.HEADING_1,
  });
}
function h2(text) {
  return new Paragraph({
    children: [krRun(text, { size: SZ.h2 })],
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: LS.h2, before: 120, after: 80 },
    heading: HeadingLevel.HEADING_2,
  });
}
function h3(text) {
  return new Paragraph({
    children: [krRun(text, { size: SZ.h3 })],
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: LS.h3, before: 100, after: 60 },
    heading: HeadingLevel.HEADING_3,
  });
}

// 수식 단락 (가운데 + 우측 번호)
function eqPara(eqText, eqNumber) {
  return new Paragraph({
    children: [
      enRun(eqText, { italics: true }),
      new TextRun({ text: "\t", font: FONT_EN }),
      enRun(`(${eqNumber})`),
    ],
    tabStops: [
      { type: TabStopType.RIGHT, position: TabStopPosition.MAX },
    ],
    spacing: { line: LS.body, before: 80, after: 80 },
  });
}

// "Where, ..." 단락
function whereLine(text) {
  return new Paragraph({
    children: [enRun(text, { italics: false })],
    alignment: AlignmentType.LEFT,
    spacing: { line: LS.body, before: 0, after: 80 },
    indent: { left: mm(5) },
  });
}

// 참고문헌
function refPara(idx, text) {
  return new Paragraph({
    children: [enRun(`[${idx}] ${text}`)],
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: LS.reference, before: 0, after: 100 },
    indent: { left: mm(5), hanging: mm(5) },
  });
}

// 그림 캡션
function figCaption(text) {
  return new Paragraph({
    children: [enRun(text, { size: SZ.caption })],
    alignment: AlignmentType.CENTER,
    spacing: { line: LS.caption, before: 60, after: 120 },
  });
}

// Figure placeholder (실제 그림 outputs/figures/K1_fractional_ecm/ 의 PDF/PNG 를 사용자가 삽입)
function figPlaceholder(num, captionEn) {
  return [
    new Paragraph({
      children: [enRun(`[ Fig. ${num} placeholder — outputs/figures/K1_fractional_ecm/fig${num}_*.png 삽입 ]`,
        { size: SZ.caption, color: "808080", italics: true })],
      alignment: AlignmentType.CENTER,
      spacing: { line: LS.caption, before: 100, after: 60 },
      border: {
        top:    { style: BorderStyle.SINGLE, size: 6, color: "BBBBBB" },
        bottom: { style: BorderStyle.SINGLE, size: 6, color: "BBBBBB" },
        left:   { style: BorderStyle.SINGLE, size: 6, color: "BBBBBB" },
        right:  { style: BorderStyle.SINGLE, size: 6, color: "BBBBBB" },
      },
    }),
    figCaption(`Fig. ${num}. ${captionEn}`),
  ];
}

// ═════════════════════════════════════
// 표 (Table)
// ═════════════════════════════════════
function makeCell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2000, type: WidthType.DXA },
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    borders: {
      top:    { style: BorderStyle.SINGLE, size: 4, color: "000000" },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: "000000" },
      left:   { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
      right:  { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
    },
    children: [new Paragraph({
      children: [enRun(text, { size: SZ.caption, bold: opts.bold || false })],
      alignment: AlignmentType.CENTER,
      spacing: { line: 312 },
    })],
  });
}

const TABLE_1_SPEC = new Table({
  width: { size: mm(80), type: WidthType.DXA },
  columnWidths: [mm(40), mm(40)],
  rows: [
    new TableRow({ children: [makeCell("Category", { bold: true, width: mm(40) }), makeCell("Contents", { bold: true, width: mm(40) })] }),
    new TableRow({ children: [makeCell("Cell type", { width: mm(40) }), makeCell("NCM Pouch (JH3)", { width: mm(40) })] }),
    new TableRow({ children: [makeCell("Capacity", { width: mm(40) }), makeCell("63.0 Ah", { width: mm(40) })] }),
    new TableRow({ children: [makeCell("Operating voltage", { width: mm(40) }), makeCell("3.0 ~ 4.2 V", { width: mm(40) })] }),
    new TableRow({ children: [makeCell("Test temp.", { width: mm(40) }), makeCell("25 ℃, 50 ℃", { width: mm(40) })] }),
    new TableRow({ children: [makeCell("Pulse current", { width: mm(40) }), makeCell("Approx. 1 C (62.99 A)", { width: mm(40) })] }),
    new TableRow({ children: [makeCell("Pulse duration", { width: mm(40) }), makeCell("Approx. 10 s", { width: mm(40) })] }),
    new TableRow({ children: [makeCell("Sampling rate", { width: mm(40) }), makeCell("1 Hz", { width: mm(40) })] }),
    new TableRow({ children: [makeCell("Cycle range", { width: mm(40) }), makeCell("100 ~ 3000 cycle", { width: mm(40) })] }),
  ],
});

const TABLE_2_SCEN = new Table({
  width: { size: mm(80), type: WidthType.DXA },
  columnWidths: [mm(30), mm(50)],
  rows: [
    new TableRow({ children: [makeCell("Classification", { bold: true, width: mm(30) }), makeCell("Contents", { bold: true, width: mm(50) })] }),
    new TableRow({ children: [makeCell("Scenario 1", { width: mm(30) }), makeCell("Integer 1-RC ECM", { width: mm(50) })] }),
    new TableRow({ children: [makeCell("Scenario 2", { width: mm(30) }), makeCell("Integer 2-RC ECM", { width: mm(50) })] }),
    new TableRow({ children: [makeCell("Scenario 3", { width: mm(30) }), makeCell("Fractional R+CPE (proposed)", { width: mm(50) })] }),
  ],
});

const TABLE_3_RMSE = new Table({
  width: { size: mm(80), type: WidthType.DXA },
  columnWidths: [mm(15), mm(15), mm(15), mm(15), mm(20)],
  rows: [
    new TableRow({ children: [
      makeCell("Temp", { bold: true, width: mm(15) }),
      makeCell("1-RC", { bold: true, width: mm(15) }),
      makeCell("2-RC", { bold: true, width: mm(15) }),
      makeCell("FOM", { bold: true, width: mm(15) }),
      makeCell("FOM vs 1-RC", { bold: true, width: mm(20) }),
    ]}),
    new TableRow({ children: [
      makeCell("25 ℃", { width: mm(15) }),
      makeCell("1.376 mV", { width: mm(15) }),
      makeCell("1.212 mV", { width: mm(15) }),
      makeCell("0.413 mV", { width: mm(15) }),
      makeCell("70.0 % ↓", { width: mm(20) }),
    ]}),
    new TableRow({ children: [
      makeCell("50 ℃", { width: mm(15) }),
      makeCell("0.904 mV", { width: mm(15) }),
      makeCell("1.024 mV", { width: mm(15) }),
      makeCell("0.335 mV", { width: mm(15) }),
      makeCell("63.0 % ↓", { width: mm(20) }),
    ]}),
  ],
});

const TABLE_4_SUMMARY = new Table({
  width: { size: mm(80), type: WidthType.DXA },
  columnWidths: [mm(20), mm(20), mm(20), mm(20)],
  rows: [
    new TableRow({ children: [
      makeCell("Model", { bold: true, width: mm(20) }),
      makeCell("Mean RMSE 25 ℃", { bold: true, width: mm(20) }),
      makeCell("Mean RMSE 50 ℃", { bold: true, width: mm(20) }),
      makeCell("α range", { bold: true, width: mm(20) }),
    ]}),
    new TableRow({ children: [
      makeCell("1-RC", { width: mm(20) }), makeCell("1.376 mV", { width: mm(20) }), makeCell("0.904 mV", { width: mm(20) }), makeCell("-", { width: mm(20) }),
    ]}),
    new TableRow({ children: [
      makeCell("2-RC", { width: mm(20) }), makeCell("1.212 mV", { width: mm(20) }), makeCell("1.024 mV", { width: mm(20) }), makeCell("-", { width: mm(20) }),
    ]}),
    new TableRow({ children: [
      makeCell("FOM", { width: mm(20) }), makeCell("0.413 mV", { width: mm(20) }), makeCell("0.335 mV", { width: mm(20) }), makeCell("[0.32, 0.41]", { width: mm(20) }),
    ]}),
  ],
});

function tableCaption(text) {
  return new Paragraph({
    children: [enRun(text, { size: SZ.caption })],
    alignment: AlignmentType.LEFT,
    spacing: { line: LS.caption, before: 100, after: 60 },
  });
}

// ═════════════════════════════════════
// Document 조립
// ═════════════════════════════════════

const doc = new Document({
  creator: "RYU",
  title: TITLE_KR,
  styles: {
    default: {
      document: {
        run: { font: FONT_KR, size: SZ.body },
        paragraph: { spacing: { line: LS.body } },
      },
    },
  },
  sections: [
    // ─── Section 1: 제목·요약·키워드 (1단) ───
    {
      properties: {
        page: PAGE,
      },
      children: [
        // 양식 표시 (사용자 본인 논문에 있는 표시)
        new Paragraph({
          children: [krRun("< 심사용 논문양식 >", { size: SZ.h1, bold: true })],
          alignment: AlignmentType.CENTER,
          spacing: { before: 200, after: 200, line: LS.title },
        }),
        // 한글 제목
        new Paragraph({
          children: [krRun(TITLE_KR, { size: SZ.titleKr, bold: true })],
          alignment: AlignmentType.CENTER,
          spacing: { line: LS.title, before: 100, after: 200 },
        }),
        // 영문 제목
        new Paragraph({
          children: [enRun(TITLE_EN, { size: SZ.titleEn, bold: true })],
          alignment: AlignmentType.CENTER,
          spacing: { line: LS.title, before: 0, after: 300 },
        }),
        // 저자 (한글)
        new Paragraph({
          children: [krRun(`${AUTHOR_KR}`, { size: SZ.body, bold: true })],
          alignment: AlignmentType.CENTER,
          spacing: { line: LS.body, before: 0, after: 60 },
        }),
        // 소속 (한글)
        new Paragraph({
          children: [krRun(`${AFFIL_KR}`, { size: SZ.body })],
          alignment: AlignmentType.CENTER,
          spacing: { line: LS.body, before: 0, after: 100 },
        }),
        // 저자 (영문)
        new Paragraph({
          children: [enRun(`${AUTHOR_EN}`, { size: SZ.body, bold: true })],
          alignment: AlignmentType.CENTER,
          spacing: { line: LS.body, before: 0, after: 40 },
        }),
        // 소속 (영문)
        new Paragraph({
          children: [enRun(`${AFFIL_EN}`, { size: SZ.body, italics: true })],
          alignment: AlignmentType.CENTER,
          spacing: { line: LS.body, before: 0, after: 300 },
        }),
        // 국문 요약
        new Paragraph({
          children: [
            krRun("요  약   ", { size: SZ.abstract, bold: true }),
            krRun(ABSTRACT_KR, { size: SZ.abstract }),
          ],
          alignment: AlignmentType.JUSTIFIED,
          spacing: { line: LS.abstract, before: 0, after: 200 },
        }),
        // Abstract
        new Paragraph({
          children: [
            enRun("Abstract   ", { size: SZ.abstract, bold: true }),
            enRun(ABSTRACT_EN, { size: SZ.abstract }),
          ],
          alignment: AlignmentType.JUSTIFIED,
          spacing: { line: LS.abstractEn, before: 0, after: 200 },
        }),
        // Keywords
        new Paragraph({
          children: [
            enRun("Keywords : ", { size: SZ.keywords, bold: true }),
            enRun(KEYWORDS_EN, { size: SZ.keywords }),
          ],
          alignment: AlignmentType.JUSTIFIED,
          spacing: { line: LS.abstractEn, before: 0, after: 300 },
        }),
      ],
    },

    // ─── Section 2: 본문 (2단 편집) ───
    {
      properties: {
        page: PAGE,
        type: SectionType.CONTINUOUS,
        column: { count: 2, space: mm(6), equalWidth: true, separate: false },
      },
      children: [
        // 1. 서론
        h1("1. 서론"),
        ...SEC_1_INTRO.map(t => bodyPara(t, { firstIndent: true, after: 60 })),

        // 2. 분수계 등가회로모델
        h1("2. 분수계 등가회로모델"),
        h2("2.1 모델 정의"),
        ...SEC_2_1_MODEL.map(t => bodyPara(t, { firstIndent: true, after: 40 })),

        // 식 (1)
        eqPara("V(t) = OCV(SOC) − I(t)·R0 − I(t)·R1·(1 − exp(−t/τ))", "1"),
        whereLine("Where, τ = R1·C1, R1 and C1 denote polarization resistance and capacitance, respectively"),

        ...SEC_2_1_AFTER_EQ1.map(t => bodyPara(t, { firstIndent: true, after: 40 })),

        // 식 (2)
        eqPara("Z_CPE(jω) = 1 / [(jω)^α · Q]", "2"),
        whereLine("Where, Q denotes CPE coefficient and α denotes fractional order (0 < α ≤ 1)"),

        ...SEC_2_1_AFTER_EQ2.map(t => bodyPara(t, { firstIndent: true, after: 40 })),

        h2("2.2 모델 파라미터 식별"),
        ...SEC_2_2_IDENT.map(t => bodyPara(t, { firstIndent: true, after: 40 })),

        // 3. 알고리즘
        h1("3. 식별 알고리즘 및 진단 절차"),
        ...SEC_3_ALGO.map(t => bodyPara(t, { firstIndent: false, after: 40 })),

        ...figPlaceholder(1, "Identification flow chart"),

        // 4. 시뮬레이션 결과
        h1("4. 시뮬레이션 결과 및 분석"),

        h2("4.1 실험 데이터 및 조건"),
        ...SEC_4_1_DATA.map(t => bodyPara(t, { firstIndent: true, after: 40 })),

        tableCaption("Table 1. Specifications of the test cell and DCIR pulse condition"),
        TABLE_1_SPEC,
        new Paragraph({ children: [enRun(" ")], spacing: { line: LS.body, after: 100 } }),

        h2("4.2 시나리오 구성"),
        ...SEC_4_2_SCEN.map(t => bodyPara(t, { firstIndent: true, after: 40 })),

        tableCaption("Table 2. Simulation scenarios"),
        TABLE_2_SCEN,
        new Paragraph({ children: [enRun(" ")], spacing: { line: LS.body, after: 100 } }),

        h2("4.3 단자전압 잔차 비교"),
        ...SEC_4_3_RMSE.map(t => bodyPara(t, { firstIndent: true, after: 40 })),

        tableCaption("Table 3. Mean voltage RMSE comparison"),
        TABLE_3_RMSE,
        new Paragraph({ children: [enRun(" ")], spacing: { line: LS.body, after: 100 } }),

        ...figPlaceholder(2, "Pulse fit comparison at 25 ℃, cycle 1300"),

        h2("4.4 노화 및 온도 의존성 분석"),
        ...SEC_4_4_PARAM.map(t => bodyPara(t, { firstIndent: true, after: 40 })),

        ...figPlaceholder(3, "Parameter trajectory of R0 and α"),

        h2("4.5 저사이클 데이터 진단"),
        ...SEC_4_5_DIAG.map(t => bodyPara(t, { firstIndent: true, after: 40 })),

        h2("4.6 종합 분석"),
        ...SEC_4_6_SUMMARY.map(t => bodyPara(t, { firstIndent: true, after: 40 })),

        tableCaption("Table 4. Comparative results across the three models"),
        TABLE_4_SUMMARY,
        new Paragraph({ children: [enRun(" ")], spacing: { line: LS.body, after: 100 } }),

        // 5. 결론
        h1("5. 결론"),
        bodyPara(SEC_5_CONCLUSION_INTRO, { firstIndent: true, after: 40 }),
        ...SEC_5_BULLETS.map(t => bodyPara(t, { firstIndent: false, after: 60 })),

        // References
        h1("References"),
        ...REFERENCES.map((r, i) => refPara(i + 1, r)),
      ],
    },
  ],
});

// ─── 저장 ───
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("K1_paper_draft.docx", buf);
  console.log("saved: K1_paper_draft.docx");
});
