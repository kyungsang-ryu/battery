// SCI 전략 PPT — FOM-AEKF 통합 SOC/SOH 추정 (NCM Pouch 셀·모듈)
// 16 slides, LAYOUT_WIDE (13.3" × 7.5")
//
// 실행:
//   1) 이 폴더에서 'npm install pptxgenjs' (한 번만)
//   2) 'node build_ppt.js'
//   3) 'FOM_AEKF_SCI_strategy.pptx' 파일이 같은 폴더에 생성됨

const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "RYU";
pres.title = "FOM-AEKF: NCM Pouch 셀·모듈 SOC/SOH 통합 추정 — SCI 전략";

// Color palette — Ocean Deep + Coral accent
const C = {
  bgDark:    "0A2540",
  bgLight:   "FFFFFF",
  bgCard:    "F1F5F9",
  primary:   "0E5C7F",
  secondary: "1C7293",
  accent:    "F96E46",
  accent2:   "FFD166",
  textDark:  "1A2B3A",
  textMuted: "64748B",
  border:    "CBD5E1",
  success:   "0D9488",
};

const FONT = { head: "Calibri", body: "Calibri" };

function pageNumber(slide, n, total) {
  slide.addText(`${n} / ${total}`, {
    x: 12.4, y: 7.15, w: 0.7, h: 0.25,
    fontSize: 9, color: C.textMuted, fontFace: FONT.body, align: "right", margin: 0,
  });
}

function topBar(slide, label) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 0.45, w: 0.08, h: 0.35, fill: { color: C.accent }, line: { color: C.accent, width: 0 },
  });
  slide.addText(label, {
    x: 0.7, y: 0.42, w: 8, h: 0.4,
    fontSize: 11, bold: true, color: C.primary, fontFace: FONT.head, charSpacing: 4, margin: 0,
  });
}

function slideTitle(slide, title) {
  slide.addText(title, {
    x: 0.5, y: 0.85, w: 12.3, h: 0.7,
    fontSize: 30, bold: true, color: C.textDark, fontFace: FONT.head, margin: 0,
  });
}

function card(slide, x, y, w, h, fill = C.bgCard) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: fill }, line: { color: C.border, width: 0.5 },
    shadow: { type: "outer", color: "000000", blur: 4, offset: 1, angle: 90, opacity: 0.06 },
  });
}

const TOTAL = 18;

// ============================================================
// Slide 1 — Title (dark)
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgDark };
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.3, w: 0.6, h: 0.08, fill: { color: C.accent }, line: { color: C.accent, width: 0 },
  });
  s.addText("SCI 전략 발표", {
    x: 0.5, y: 1.45, w: 8, h: 0.4,
    fontSize: 13, color: C.accent2, fontFace: FONT.head, charSpacing: 6, margin: 0,
  });
  s.addText("NCM Pouch 셀·모듈을 위한", {
    x: 0.5, y: 2.0, w: 12, h: 0.7,
    fontSize: 26, color: "CADCFC", fontFace: FONT.head, margin: 0,
  });
  s.addText("FOM-AEKF 기반 SOC/SOH 통합 추정", {
    x: 0.5, y: 2.7, w: 12, h: 1.0,
    fontSize: 44, bold: true, color: "FFFFFF", fontFace: FONT.head, margin: 0,
  });
  s.addText("Fractional-Order ECM × Dual Adaptive EKF × Cross-Scale Validation", {
    x: 0.5, y: 3.85, w: 12, h: 0.5,
    fontSize: 17, italic: true, color: "9DC4E0", fontFace: FONT.body, margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.5, y: 5.7, w: 12.3, h: 0, line: { color: "1F4060", width: 0.75 },
  });
  s.addText([
    { text: "발표자  ", options: { color: "9DC4E0", fontSize: 11 } },
    { text: "RYU", options: { color: "FFFFFF", fontSize: 12, bold: true } },
  ], { x: 0.5, y: 6.0, w: 4, h: 0.35, fontFace: FONT.body, margin: 0 });
  s.addText([
    { text: "작성일  ", options: { color: "9DC4E0", fontSize: 11 } },
    { text: "2026-04-23", options: { color: "FFFFFF", fontSize: 12, bold: true } },
  ], { x: 5.0, y: 6.0, w: 4, h: 0.35, fontFace: FONT.body, margin: 0 });
  s.addText([
    { text: "버전  ", options: { color: "9DC4E0", fontSize: 11 } },
    { text: "Strategy v2.2", options: { color: "FFFFFF", fontSize: 12, bold: true } },
  ], { x: 9.0, y: 6.0, w: 4, h: 0.35, fontFace: FONT.body, margin: 0 });
  s.addText("Mid-tier SCI · 1차 타깃: J. Energy Storage / IEEE TTE", {
    x: 0.5, y: 6.45, w: 12, h: 0.35,
    fontSize: 10, color: C.accent2, fontFace: FONT.body, margin: 0, italic: true,
  });
}

// ============================================================
// Slide 2 — Agenda
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "AGENDA");
  slideTitle(s, "발표 개요");

  const items = [
    ["01", "연구 배경 & 문제 정의", "왜 SOC와 SOH를 함께 추정해야 하는가"],
    ["02", "2025-2026 SOTA 갭 분석", "기존 기법의 한계와 빈 공간"],
    ["03", "본 연구 한 줄 답 + 4대 Contribution", "FOM-AEKF + Cross-Scale 일반화"],
    ["04", "데이터셋 — Pouch 셀과 모듈 두 축", "JH3 NCM 단일 chemistry 일관"],
    ["05", "알고리즘 모델링 & 비교 baseline", "FOM-AEKF 구조도와 7종 비교군"],
    ["06", "Split 프로토콜 & 평가 메트릭", "6종 split, 4축 메트릭"],
    ["07", "예상 결과 & 논문 섹션 구성", "수치 시나리오와 IMRaD 매핑"],
    ["08", "Multi-Paper 5편 전략 (SCI 3 + KCI 2)", "한 데이터·코드 베이스에서 5편 산출"],
    ["09", "마일스톤 · 타깃 저널 · 리스크", "24개월 로드맵과 대응 전략"],
  ];

  const startY = 1.85;
  const rowH = 0.6;
  for (let i = 0; i < items.length; i++) {
    const y = startY + i * rowH;
    const [num, title, sub] = items[i];
    s.addShape(pres.shapes.OVAL, {
      x: 0.7, y: y + 0.05, w: 0.45, h: 0.45,
      fill: { color: i % 2 === 0 ? C.primary : C.secondary }, line: { color: C.bgLight, width: 0 },
    });
    s.addText(num, {
      x: 0.7, y: y + 0.05, w: 0.45, h: 0.45,
      fontSize: 11, bold: true, color: "FFFFFF", fontFace: FONT.head,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(title, {
      x: 1.4, y: y, w: 6, h: 0.3,
      fontSize: 14, bold: true, color: C.textDark, fontFace: FONT.head, margin: 0,
    });
    s.addText(sub, {
      x: 1.4, y: y + 0.3, w: 11.5, h: 0.28,
      fontSize: 11, color: C.textMuted, fontFace: FONT.body, margin: 0,
    });
  }
  pageNumber(s, 2, TOTAL);
}

// ============================================================
// Slide 3 — 배경
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "01  ·  BACKGROUND");
  slideTitle(s, "왜 SOC·SOH를 동시에 추정해야 하는가");

  s.addText("BMS의 두 핵심 상태량은 서로 강하게 결합되어 있어 단독 추정 시 누적 오차가 발생한다.", {
    x: 0.5, y: 1.55, w: 12.3, h: 0.4,
    fontSize: 13, italic: true, color: C.textMuted, fontFace: FONT.body, margin: 0,
  });

  const cols = [
    { title: "SOC 단독의 한계",
      points: ["전류적산은 노이즈 누적, 무한 발산", "OCV-Lookup은 휴지 시간 필요, 실시간 부적합", "셀이 노화하면 ECM 파라미터가 어긋나 EKF/UKF 정확도 급락"],
      color: C.primary },
    { title: "SOH 단독의 한계",
      points: ["Direct measurement는 완충/완방 필요 → 실사용 중 불가", "ICA/DVA는 고정 충전 프로파일에 한정", "데이터 기반 회귀는 셀·온도 일반화 부족"],
      color: C.secondary },
    { title: "Joint(동시) 추정의 필요성",
      points: ["SOH가 변하면 가용 용량이 바뀌어 SOC 계산이 틀려진다", "SOC가 틀리면 SOC-OCV 매핑이 어긋나 SOH 저항 추정도 오류", "두 상태를 결합 추정하면 상호 보정이 가능 — 단일 기법보다 우수"],
      color: C.accent },
  ];

  const colW = 4.0, gap = 0.15, startX = 0.5, startY = 2.15, colH = 4.5;
  cols.forEach((col, i) => {
    const x = startX + i * (colW + gap);
    card(s, x, startY, colW, colH, C.bgCard);
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: startY, w: colW, h: 0.18,
      fill: { color: col.color }, line: { color: col.color, width: 0 },
    });
    s.addText(col.title, {
      x: x + 0.3, y: startY + 0.35, w: colW - 0.4, h: 0.5,
      fontSize: 17, bold: true, color: C.textDark, fontFace: FONT.head, margin: 0,
    });
    const bullets = col.points.map((p, j) => ({
      text: p,
      options: { bullet: { code: "25A0" }, breakLine: j < col.points.length - 1, color: C.textDark, fontSize: 11.5 },
    }));
    s.addText(bullets, {
      x: x + 0.3, y: startY + 1.0, w: colW - 0.5, h: colH - 1.2,
      fontFace: FONT.body, paraSpaceAfter: 8, valign: "top",
    });
  });

  s.addText("→ 본 연구는 두 상태를 하나의 알고리즘에서 동시 추정한다.", {
    x: 0.5, y: 6.85, w: 12.3, h: 0.35,
    fontSize: 12, bold: true, italic: true, color: C.accent, fontFace: FONT.body, margin: 0,
  });
  pageNumber(s, 3, TOTAL);
}

// ============================================================
// Slide 4 — SOTA 갭
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "02  ·  STATE-OF-THE-ART");
  slideTitle(s, "2025–2026 SOTA 동향과 빈 공간");

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.55, w: 12.3, h: 0.5, fill: { color: "FEE2E2" }, line: { color: "FCA5A5", width: 0.5 },
  });
  s.addText([
    { text: "포화 영역  ", options: { bold: true, color: "991B1B", fontSize: 12 } },
    { text: "Dual EKF/UKF 변종, Multi-time scale fast/slow filter, Aging-aware OCV mapping, Multi-task Transformer — 2024–2025년에 십수 편 게재", options: { color: "7F1D1D", fontSize: 11 } },
  ], { x: 0.65, y: 1.6, w: 12.0, h: 0.4, fontFace: FONT.body, valign: "middle", margin: 0 });

  const headers = ["기법군", "대표 사례 (2025)", "한계"];
  const rows = [
    ["Dual EKF / UKF / FOM AUKF", "Nat. SciRep 2025, IET PE 2025", "Q/R 적응이 innovation 잔차에만 의존"],
    ["Multi-time scale fast/slow", "MDPI Batteries 2025 (FOM)", "온도-노화 결합 모델링 부재"],
    ["Aging-aware OCV-EKF", "J. Power Electron. 2025", "본 연구 v1 메인 컨셉과 정면 충돌"],
    ["Multi-task Transformer", "AIP Advances 2026 (cross-attn)", "데이터 의존, 임베디드 부담"],
    ["PINN for SOH (단독)", "Nat. Commun. 2024, ScienceDirect 2025", "SOC와의 joint 추정 사례 희소"],
  ];

  const tableData = [
    headers.map(h => ({
      text: h,
      options: { bold: true, color: "FFFFFF", fill: { color: C.primary }, fontSize: 12, align: "left" },
    })),
    ...rows.map((r, i) => r.map(c => ({
      text: c,
      options: { color: C.textDark, fill: { color: i % 2 === 0 ? C.bgLight : C.bgCard }, fontSize: 11 },
    }))),
  ];

  s.addTable(tableData, {
    x: 0.5, y: 2.25, w: 12.3, colW: [3.2, 4.5, 4.6], rowH: 0.45,
    border: { pt: 0.5, color: C.border }, fontFace: FONT.body, valign: "middle",
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 5.5, w: 12.3, h: 1.45, fill: { color: "ECFDF5" }, line: { color: C.success, width: 0.75 },
  });
  s.addText("WHITE SPACE — 본 연구의 빈 공간", {
    x: 0.7, y: 5.6, w: 12, h: 0.35,
    fontSize: 12, bold: true, color: C.success, fontFace: FONT.head, charSpacing: 3, margin: 0,
  });
  s.addText([
    { text: "①  ", options: { bold: true, color: C.success, fontSize: 11.5 } },
    { text: "분수계 ECM + 온도×SOH 2D Q/R 스케줄링의 결합", options: { color: C.textDark, fontSize: 11.5, breakLine: true } },
    { text: "②  ", options: { bold: true, color: C.success, fontSize: 11.5 } },
    { text: "동일 chemistry 셀 학습 알고리즘의 14S 모듈 cross-scale 외삽 검증", options: { color: C.textDark, fontSize: 11.5, breakLine: true } },
    { text: "③  ", options: { bold: true, color: C.success, fontSize: 11.5 } },
    { text: "Pouch 단일 폼팩터로 사이클 0~3,800 + 다채널 + 다패턴 일관 벤치", options: { color: C.textDark, fontSize: 11.5 } },
  ], { x: 0.85, y: 5.95, w: 12, h: 1.0, fontFace: FONT.body, paraSpaceAfter: 4, margin: 0 });
  pageNumber(s, 4, TOTAL);
}

// ============================================================
// Slide 5 — 본 연구 한 줄 답
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "03  ·  PROPOSITION");
  slideTitle(s, "본 연구의 한 줄 답 — FOM-AEKF + Cross-Scale");

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.6, w: 12.3, h: 1.5,
    fill: { color: C.bgDark }, line: { color: C.bgDark, width: 0 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.6, w: 0.18, h: 1.5,
    fill: { color: C.accent }, line: { color: C.accent, width: 0 },
  });
  s.addText("Fractional-Order ECM × Dual Adaptive EKF × Cross-Scale Validation", {
    x: 0.95, y: 1.75, w: 11.5, h: 0.55,
    fontSize: 21, bold: true, color: "FFFFFF", fontFace: FONT.head, margin: 0,
  });
  s.addText("분수계 등가회로모델과 이중 적응 칼만필터를 결합하고, 온도×SOH 2D 스케줄러로 보완한 뒤,\n셀에서 학습된 동일 알고리즘을 14S 모듈에 추가 학습 없이 적용해 cross-scale 일반화를 정량화한다.", {
    x: 0.95, y: 2.35, w: 11.5, h: 0.7,
    fontSize: 12, italic: true, color: "CBD5E1", fontFace: FONT.body, margin: 0,
  });

  const pillars = [
    { num: "01", h: "분수계 ECM (FOM)", b: "정수계 1/2-RC 대비 EIS 중주파 arc fit이 우수. 노화 시 voltage fidelity 향상." },
    { num: "02", h: "온도×SOH 2D Q/R 스케줄러", b: "Innovation에만 의존하던 기존 AEKF에 환경·노화 의존성을 명시 모델링." },
    { num: "03", h: "Cross-Scale (Cell → Module)", b: "셀에서 학습한 동일 알고리즘을 14S NCM Pouch 모듈에 추가 학습 없이 검증." },
  ];

  const py = 3.55, ph = 3.2, pw = 4.0, gap = 0.15, sx = 0.5;
  pillars.forEach((p, i) => {
    const x = sx + i * (pw + gap);
    card(s, x, py, pw, ph, C.bgCard);
    s.addText(p.num, {
      x: x + 0.3, y: py + 0.2, w: 1.5, h: 0.9,
      fontSize: 48, bold: true, color: C.accent, fontFace: FONT.head, margin: 0,
    });
    s.addText(p.h, {
      x: x + 0.3, y: py + 1.15, w: pw - 0.4, h: 0.8,
      fontSize: 16, bold: true, color: C.primary, fontFace: FONT.head, margin: 0,
    });
    s.addText(p.b, {
      x: x + 0.3, y: py + 2.0, w: pw - 0.5, h: 1.1,
      fontSize: 12, color: C.textDark, fontFace: FONT.body, margin: 0,
    });
  });
  pageNumber(s, 5, TOTAL);
}

// ============================================================
// Slide 6 — 4대 Contribution
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "03  ·  CONTRIBUTION");
  slideTitle(s, "4대 Contribution Statement");

  const items = [
    { tag: "ARCHITECTURAL", title: "분수계 ECM × Dual AEKF × 2D Q/R 스케줄러",
      body: "정수계 ECM의 voltage 잔차 한계를 분수계 (R + CPE)로 보완. AEKF의 Q/R을 온도와 추정 SOH의 2D 룩업 surface에서 조정.",
      color: C.primary },
    { tag: "EMPIRICAL · CELL", title: "광범위 외삽 벤치마크 프로토콜",
      body: "NCM Pouch 단일 chemistry로 cycle 0~3,800, 온도 0/25/40/50 °C, 다채널(ch1~ch8) × 3종 패턴(MG/PVS/PQ) 일관 비교.",
      color: C.secondary },
    { tag: "EMPIRICAL · CROSS-SCALE", title: "셀 학습 → 14S 모듈 적용 검증",
      body: "동일 chemistry/폼팩터 14S 모듈에서 추가 학습 없이 SOC/SOH RMSE 유지 — SOC/SOH joint 분야 사례 희소.",
      color: C.accent },
    { tag: "RELIABILITY  ·  P4 STRETCH", title: "Calibrated UQ + 안전 마진",
      body: "Ensemble/variational 변형으로 PICP_95 calibration. BMS 안전 SOC envelope 설계에 직접 활용 가능.",
      color: "8B5CF6" },
  ];

  const cw = 6.05, ch = 2.55, gap = 0.2, sx = 0.5, sy = 1.65;
  items.forEach((it, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = sx + col * (cw + gap);
    const y = sy + row * (ch + gap);
    card(s, x, y, cw, ch, "FFFFFF");
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.12, h: ch, fill: { color: it.color }, line: { color: it.color, width: 0 },
    });
    s.addText(it.tag, {
      x: x + 0.4, y: y + 0.25, w: cw - 0.5, h: 0.3,
      fontSize: 10, bold: true, color: it.color, fontFace: FONT.head, charSpacing: 5, margin: 0,
    });
    s.addText(it.title, {
      x: x + 0.4, y: y + 0.6, w: cw - 0.5, h: 0.65,
      fontSize: 17, bold: true, color: C.textDark, fontFace: FONT.head, margin: 0,
    });
    s.addText(it.body, {
      x: x + 0.4, y: y + 1.3, w: cw - 0.6, h: ch - 1.4,
      fontSize: 12, color: C.textMuted, fontFace: FONT.body, margin: 0,
    });
  });
  pageNumber(s, 6, TOTAL);
}

// ============================================================
// Slide 7 — 데이터셋 두 축
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "04  ·  DATASET");
  slideTitle(s, "데이터셋 — Pouch 폼팩터 일관, 두 축");

  card(s, 0.5, 1.6, 6.1, 5.2, C.bgCard);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.6, w: 6.1, h: 0.55, fill: { color: C.primary }, line: { color: C.primary, width: 0 },
  });
  s.addText("AXIS 1  ·  Pouch 셀 (메인 학습·검증)", {
    x: 0.7, y: 1.65, w: 6, h: 0.45,
    fontSize: 14, bold: true, color: "FFFFFF", fontFace: FONT.head, valign: "middle", margin: 0,
  });

  s.addText([
    { text: "main_cell", options: { bold: true, color: C.primary, fontSize: 13, breakLine: true } },
    { text: "  · ch2 / 25 °C / cycle 0–3,000", options: { color: C.textDark, fontSize: 11.5, breakLine: true } },
    { text: "  · ch7 / 50 °C / cycle 0–3,800 (가속 노화)", options: { color: C.textDark, fontSize: 11.5, breakLine: true } },
    { text: "  · ch3 / 0 °C / cycle 0–101 (전압하한)", options: { color: C.textDark, fontSize: 11.5, breakLine: true } },
    { text: "  · type: RPT / DCIR / ACIR / Pattern", options: { color: C.textMuted, fontSize: 11, breakLine: true } },
    { text: " ", options: { fontSize: 6, breakLine: true } },
    { text: "pouch_SOH (다채널)", options: { bold: true, color: C.primary, fontSize: 13, breakLine: true } },
    { text: "  · ch1~ch8 × 25/40 °C × 5–30 weeks", options: { color: C.textDark, fontSize: 11.5, breakLine: true } },
    { text: "  · 패턴 3종: MG, PVSmoothing, PowerQuality", options: { color: C.textDark, fontSize: 11.5, breakLine: true } },
    { text: "  · multi-cell + multi-pattern 외삽 1순위", options: { color: C.textMuted, fontSize: 11 } },
  ], {
    x: 0.7, y: 2.35, w: 5.8, h: 4.4, fontFace: FONT.body, paraSpaceAfter: 3, margin: 0, valign: "top",
  });

  card(s, 6.7, 1.6, 6.1, 5.2, C.bgCard);
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.7, y: 1.6, w: 6.1, h: 0.55, fill: { color: C.accent }, line: { color: C.accent, width: 0 },
  });
  s.addText("AXIS 2  ·  Pouch 모듈 (Cross-Scale 검증)", {
    x: 6.9, y: 1.65, w: 6, h: 0.45,
    fontSize: 14, bold: true, color: "FFFFFF", fontFace: FONT.head, valign: "middle", margin: 0,
  });

  s.addText([
    { text: "module CH1 (14S)", options: { bold: true, color: C.accent, fontSize: 13, breakLine: true } },
    { text: "  · 14 셀 직렬, NCM Pouch 동일 chemistry", options: { color: C.textDark, fontSize: 11.5, breakLine: true } },
    { text: "  · 25 °C × ~3,000 cycle", options: { color: C.textDark, fontSize: 11.5, breakLine: true } },
    { text: "  · type: RPT / DCIR / ACIR / Pattern", options: { color: C.textDark, fontSize: 11.5, breakLine: true } },
    { text: "  · Pattern은 cycle별 폴더 + 분할 청크 자동 merge", options: { color: C.textMuted, fontSize: 11, breakLine: true } },
    { text: " ", options: { fontSize: 6, breakLine: true } },
    { text: "역할", options: { bold: true, color: C.accent, fontSize: 13, breakLine: true } },
    { text: "  · 셀 학습 알고리즘을 모듈에 추가 학습 없이 적용", options: { color: C.textDark, fontSize: 11.5, breakLine: true } },
    { text: "  · 두 시나리오 비교: cell-equiv vs module-direct", options: { color: C.textDark, fontSize: 11.5, breakLine: true } },
    { text: "  · 본 논문 두 번째 메인 contribution 축", options: { color: C.textMuted, fontSize: 11 } },
  ], {
    x: 6.9, y: 2.35, w: 5.8, h: 4.4, fontFace: FONT.body, paraSpaceAfter: 3, margin: 0, valign: "top",
  });

  s.addText("의도적 제외: 18650_SOH (폼팩터 차이), Cell 데이터★★★★★ (2018 다른 시리즈), −15·45 °C 데이터 부재", {
    x: 0.5, y: 6.95, w: 12.3, h: 0.3,
    fontSize: 10, italic: true, color: C.textMuted, fontFace: FONT.body, margin: 0,
  });
  pageNumber(s, 7, TOTAL);
}

// ============================================================
// Slide 8 — FOM-AEKF 구조도
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "05  ·  ALGORITHM");
  slideTitle(s, "FOM-AEKF 알고리즘 구조도");

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 2.5, w: 1.8, h: 0.9, fill: { color: C.primary }, line: { color: C.primary, width: 0 },
  });
  s.addText("입력\n[V, I, T]_t", {
    x: 0.5, y: 2.5, w: 1.8, h: 0.9,
    fontSize: 13, bold: true, color: "FFFFFF", fontFace: FONT.head,
    align: "center", valign: "middle", margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 2.3, y: 2.95, w: 0.6, h: 0, line: { color: C.textDark, width: 1.5, endArrowType: "triangle" },
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 2.95, y: 1.85, w: 3.0, h: 1.0, fill: { color: C.secondary }, line: { color: C.secondary, width: 0 },
  });
  s.addText("Fractional-Order ECM\nR0 + R1 ∥ CPE(α)", {
    x: 2.95, y: 1.85, w: 3.0, h: 1.0,
    fontSize: 12, bold: true, color: "FFFFFF", fontFace: FONT.head,
    align: "center", valign: "middle", margin: 0,
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 2.95, y: 3.05, w: 3.0, h: 1.0, fill: { color: "DBEAFE" }, line: { color: C.primary, width: 1 },
  });
  s.addText("Fast Filter (1 Hz)\nState x = [SOC, V1, V2]", {
    x: 2.95, y: 3.05, w: 3.0, h: 1.0,
    fontSize: 12, bold: true, color: C.primary, fontFace: FONT.head,
    align: "center", valign: "middle", margin: 0,
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 2.95, y: 4.25, w: 3.0, h: 1.0, fill: { color: "FEE4D6" }, line: { color: C.accent, width: 1 },
  });
  s.addText("Slow Filter (per-cycle)\nθ = [R0, R1, Cn]", {
    x: 2.95, y: 4.25, w: 3.0, h: 1.0,
    fontSize: 12, bold: true, color: "9A3412", fontFace: FONT.head,
    align: "center", valign: "middle", margin: 0,
  });

  s.addShape(pres.shapes.LINE, {
    x: 4.45, y: 4.05, w: 0, h: 0.2,
    line: { color: C.textMuted, width: 1.5, dashType: "dash", beginArrowType: "triangle", endArrowType: "triangle" },
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 6.4, y: 1.85, w: 2.8, h: 1.4, fill: { color: "FEF3C7" }, line: { color: C.accent2, width: 1.5 },
    rectRadius: 0.1,
  });
  s.addText("Adaptive Q/R Scheduler\n(2D surface)\nf(T_k, ŜOH_k)", {
    x: 6.4, y: 1.85, w: 2.8, h: 1.4,
    fontSize: 12, bold: true, color: "92400E", fontFace: FONT.head,
    align: "center", valign: "middle", margin: 0,
  });

  s.addShape(pres.shapes.LINE, {
    x: 6.4, y: 3.0, w: 0, h: 1.0, line: { color: C.accent, width: 1.5 },
  });
  s.addShape(pres.shapes.LINE, {
    x: 6.4, y: 4.0, w: -0.4, h: 0, line: { color: C.accent, width: 1.5, endArrowType: "triangle" },
  });
  s.addText("Q_k, R_k", {
    x: 5.3, y: 3.85, w: 1.0, h: 0.3,
    fontSize: 10, italic: true, color: C.accent, fontFace: FONT.body, margin: 0,
  });

  s.addShape(pres.shapes.LINE, {
    x: 5.95, y: 3.55, w: 0.6, h: 0, line: { color: C.textDark, width: 1.5, endArrowType: "triangle" },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.6, y: 3.25, w: 1.6, h: 0.6, fill: { color: C.bgDark }, line: { color: C.bgDark, width: 0 },
  });
  s.addText("SOC ± σ", {
    x: 6.6, y: 3.25, w: 1.6, h: 0.6,
    fontSize: 13, bold: true, color: "FFFFFF", fontFace: FONT.head,
    align: "center", valign: "middle", margin: 0,
  });

  s.addShape(pres.shapes.LINE, {
    x: 5.95, y: 4.75, w: 0.6, h: 0, line: { color: C.textDark, width: 1.5, endArrowType: "triangle" },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.6, y: 4.45, w: 1.6, h: 0.6, fill: { color: C.bgDark }, line: { color: C.bgDark, width: 0 },
  });
  s.addText("SOH ± σ", {
    x: 6.6, y: 4.45, w: 1.6, h: 0.6,
    fontSize: 13, bold: true, color: "FFFFFF", fontFace: FONT.head,
    align: "center", valign: "middle", margin: 0,
  });

  s.addShape(pres.shapes.LINE, {
    x: 7.4, y: 4.45, w: 0, h: -1.2, line: { color: C.success, width: 1, dashType: "dash", endArrowType: "triangle" },
  });
  s.addText("ŜOH 피드백", {
    x: 7.5, y: 3.4, w: 1.5, h: 0.3,
    fontSize: 9, italic: true, color: C.success, fontFace: FONT.body, margin: 0,
  });

  card(s, 9.5, 1.85, 3.3, 5.0, C.bgCard);
  s.addText("핵심 수식", {
    x: 9.7, y: 1.95, w: 3.0, h: 0.4,
    fontSize: 13, bold: true, color: C.primary, fontFace: FONT.head, margin: 0,
  });
  s.addText([
    { text: "ECM 출력 식", options: { bold: true, color: C.textDark, fontSize: 11, breakLine: true } },
    { text: "V_pred = OCV(SOC,T) − I·R0 − ΣV_RC^α", options: { color: C.textMuted, fontSize: 10, breakLine: true, italic: true } },
    { text: " ", options: { fontSize: 6, breakLine: true } },
    { text: "Adaptive 스케줄링", options: { bold: true, color: C.textDark, fontSize: 11, breakLine: true } },
    { text: "Q_k = Q0 · f_Q(T_k, ŜOH_k)", options: { color: C.textMuted, fontSize: 10, breakLine: true, italic: true } },
    { text: "R_k = R0 · f_R(T_k, ŜOH_k)", options: { color: C.textMuted, fontSize: 10, breakLine: true, italic: true } },
    { text: " ", options: { fontSize: 6, breakLine: true } },
    { text: "Time-scale 분리", options: { bold: true, color: C.textDark, fontSize: 11, breakLine: true } },
    { text: "Fast: 1 Hz · Slow: per-cycle", options: { color: C.textMuted, fontSize: 10, italic: true } },
  ], {
    x: 9.7, y: 2.4, w: 3.0, h: 4.3, fontFace: FONT.body, paraSpaceAfter: 2, margin: 0, valign: "top",
  });

  s.addText("Fast Filter는 SOC를 실시간 추적하고, Slow Filter는 per-cycle ECM 파라미터를 갱신해 SOH를 산출. 두 필터는 시간 척도 분리로 안정성 확보.", {
    x: 0.5, y: 6.85, w: 12.3, h: 0.3,
    fontSize: 11, italic: true, color: C.textMuted, fontFace: FONT.body, align: "center", margin: 0,
  });
  pageNumber(s, 8, TOTAL);
}

// ============================================================
// Slide 9 — Adaptive Q/R Scheduling
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "05  ·  NOVELTY DETAIL");
  slideTitle(s, "온도 × SOH 2D Q/R 스케줄링 — 핵심 차별점");

  card(s, 0.5, 1.65, 6.0, 5.2, "FFFFFF");
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.65, w: 0.12, h: 5.2, fill: { color: C.accent }, line: { color: C.accent, width: 0 },
  });
  s.addText("기존 AEKF의 한계", {
    x: 0.85, y: 1.85, w: 5.5, h: 0.4,
    fontSize: 14, bold: true, color: C.primary, fontFace: FONT.head, margin: 0,
  });
  s.addText([
    { text: "Q/R을 ", options: { color: C.textDark, fontSize: 12 } },
    { text: "innovation 잔차 단일 신호", options: { bold: true, color: C.textDark, fontSize: 12 } },
    { text: "에만 의존해 적응시킴 — 환경 변화·노화 정보를 명시적으로 활용하지 못함.", options: { color: C.textDark, fontSize: 12 } },
  ], { x: 0.85, y: 2.3, w: 5.5, h: 1.0, fontFace: FONT.body, margin: 0 });

  s.addText("본 연구의 접근", {
    x: 0.85, y: 3.55, w: 5.5, h: 0.4,
    fontSize: 14, bold: true, color: C.primary, fontFace: FONT.head, margin: 0,
  });
  s.addText([
    { text: "온도 T 와 추정 SOH 의 ", options: { color: C.textDark, fontSize: 12 } },
    { text: "2D 스케줄링 surface", options: { bold: true, color: C.accent, fontSize: 12 } },
    { text: "를 KIER 데이터의 (T, cycle) 그리드 위에서 ", options: { color: C.textDark, fontSize: 12 } },
    { text: "오프라인 학습", options: { bold: true, color: C.textDark, fontSize: 12 } },
    { text: " — 룩업 또는 얕은 MLP. 추론 단계에서는 매 스텝 (T, ŜOH) 입력으로 Q/R 스케일을 즉시 인출.", options: { color: C.textDark, fontSize: 12 } },
  ], { x: 0.85, y: 4.0, w: 5.5, h: 2.0, fontFace: FONT.body, margin: 0 });

  s.addText("→ 이로써 셀이 노화하거나 온도가 급변해도 필터가 자동으로 가중치를 재조정.", {
    x: 0.85, y: 6.15, w: 5.5, h: 0.6,
    fontSize: 11, italic: true, color: C.success, fontFace: FONT.body, margin: 0,
  });

  card(s, 6.7, 1.65, 6.1, 5.2, C.bgCard);
  s.addText("Q-scale 스케줄러 surface (개념도)", {
    x: 6.9, y: 1.85, w: 5.7, h: 0.4,
    fontSize: 12, bold: true, color: C.primary, fontFace: FONT.head, margin: 0,
  });

  const cellW = 0.62, cellH = 0.55;
  const startX = 7.4, startY = 2.6;
  const matrix = [
    [0.20, 0.30, 0.45, 0.62, 0.85, 1.00],
    [0.10, 0.18, 0.30, 0.45, 0.65, 0.85],
    [0.18, 0.28, 0.40, 0.55, 0.78, 0.95],
  ];
  const tempLabels = ["50 °C", "25 °C", "0 °C"];
  const sohLabels  = ["100", "90", "80", "70", "60", "50"];

  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 6; c++) {
      const intensity = matrix[r][c];
      const r1 = Math.round(254 - (254 - 249) * intensity);
      const g1 = Math.round(243 - (243 - 110) * intensity);
      const b1 = Math.round(199 - (199 - 70)  * intensity);
      const hex = ((r1 << 16) | (g1 << 8) | b1).toString(16).padStart(6, "0").toUpperCase();
      s.addShape(pres.shapes.RECTANGLE, {
        x: startX + c * cellW, y: startY + r * cellH, w: cellW - 0.03, h: cellH - 0.03,
        fill: { color: hex }, line: { color: "FFFFFF", width: 0.5 },
      });
      s.addText(intensity.toFixed(2), {
        x: startX + c * cellW, y: startY + r * cellH, w: cellW - 0.03, h: cellH - 0.03,
        fontSize: 9, color: intensity > 0.55 ? "FFFFFF" : C.textDark, fontFace: FONT.body,
        align: "center", valign: "middle", margin: 0,
      });
    }
    s.addText(tempLabels[r], {
      x: startX - 0.85, y: startY + r * cellH, w: 0.8, h: cellH - 0.03,
      fontSize: 10, bold: true, color: C.textDark, fontFace: FONT.body,
      align: "right", valign: "middle", margin: 0,
    });
  }
  for (let c = 0; c < 6; c++) {
    s.addText(sohLabels[c], {
      x: startX + c * cellW, y: startY - 0.32, w: cellW - 0.03, h: 0.28,
      fontSize: 10, color: C.textDark, fontFace: FONT.body,
      align: "center", valign: "middle", margin: 0,
    });
  }

  s.addText("← SOH (% 잔존)", {
    x: startX, y: startY - 0.6, w: 4, h: 0.25,
    fontSize: 10, italic: true, color: C.textMuted, fontFace: FONT.body, margin: 0,
  });
  s.addText("온도 →", {
    x: startX - 1.0, y: startY + 1.7, w: 0.95, h: 0.25,
    fontSize: 10, italic: true, color: C.textMuted, fontFace: FONT.body, align: "right", margin: 0,
  });

  s.addText("값이 클수록 process noise(Q)를 키워 필터의 추적성을 강화.\n노화 진행(SOH↓) + 극온도일수록 Q를 더 크게 스케줄링.", {
    x: 6.9, y: 5.4, w: 5.7, h: 0.9,
    fontSize: 10.5, italic: true, color: C.textMuted, fontFace: FONT.body, margin: 0,
  });

  s.addText("(실제 surface는 KIER 데이터로 학습 — 위는 컨셉 예시)", {
    x: 6.9, y: 6.4, w: 5.7, h: 0.3,
    fontSize: 9, italic: true, color: C.textMuted, fontFace: FONT.body, margin: 0,
  });
  pageNumber(s, 9, TOTAL);
}

// ============================================================
// Slide 10 — Baseline 7종
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "06  ·  BASELINES");
  slideTitle(s, "비교 baseline 7종");

  s.addText("동일 데이터·동일 split·동일 메트릭으로 본 연구 FOM-AEKF 와 정량 비교한다.", {
    x: 0.5, y: 1.55, w: 12.3, h: 0.35,
    fontSize: 12, italic: true, color: C.textMuted, fontFace: FONT.body, margin: 0,
  });

  const headers = ["#", "기법", "분류", "장점", "약점", "BMS 친화"];
  const rows = [
    ["1", "Ah Counting",       "비-필터",   "구현 단순, 연산 ↓",          "초기·노이즈 누적, 단독 사용 불가",  "★★★"],
    ["2", "OCV Look-up",       "비-필터",   "휴지 시점 정확도 ↑",          "동적 환경 부적합",              "★★★"],
    ["3", "EKF (1-RC)",        "정수 필터",  "고전, 안정·구현 쉬움",         "노화 시 ECM 어긋남, 단일 SOC", "★★★"],
    ["4", "UKF (1-RC)",        "정수 필터",  "EKF 대비 비선형 강건",        "연산 ↑, 단일 SOC",              "★★"],
    ["5", "Dual EKF",          "정수 dual",  "SOC + 파라미터 분리 추정",     "Q/R 고정 한계, 적응 X",         "★★★"],
    ["6", "Dual UKF",          "정수 dual",  "강비선형 대응",                "연산 ↑",                        "★★"],
    ["7", "AEKF (innov-only)", "적응 필터",  "노이즈 시변 대응",             "환경·노화 정보 미활용",         "★★★"],
    ["★", "FOM-AEKF (제안)",    "분수 dual+적응", "본 연구 — FOM + 2D Q/R",   "구현·튜닝 비용 (단발성)",       "★★★"],
  ];

  const tableData = [
    headers.map(h => ({
      text: h,
      options: { bold: true, color: "FFFFFF", fill: { color: C.primary }, fontSize: 11, align: "center", valign: "middle" },
    })),
    ...rows.map((r, i) => {
      const isOurs = i === rows.length - 1;
      return r.map((c, j) => ({
        text: c,
        options: {
          color: isOurs ? "FFFFFF" : C.textDark,
          fill: { color: isOurs ? C.accent : (i % 2 === 0 ? C.bgLight : C.bgCard) },
          fontSize: 10.5,
          bold: isOurs || j === 0,
          align: (j === 0 || j === 5) ? "center" : "left",
          valign: "middle",
        },
      }));
    }),
  ];

  s.addTable(tableData, {
    x: 0.5, y: 2.05, w: 12.3,
    colW: [0.6, 2.7, 1.6, 3.2, 3.2, 1.0], rowH: 0.55,
    border: { pt: 0.5, color: C.border }, fontFace: FONT.body,
  });

  s.addText("BMS 친화: 추론 시간·메모리 기준 정성 평가 (★ 많을수록 임베디드 적합).", {
    x: 0.5, y: 7.0, w: 12.3, h: 0.3,
    fontSize: 9, italic: true, color: C.textMuted, fontFace: FONT.body, margin: 0,
  });
  pageNumber(s, 10, TOTAL);
}

// ============================================================
// Slide 11 — Split 6종
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "06  ·  EVALUATION");
  slideTitle(s, "Split 프로토콜 6종 — 외삽 능력 다각 측정");

  const splits = [
    { id: "1", title: "Aging Extrapolation", train: "25/50 °C × cycle 100~1500", test: "25/50 °C × cycle 2000~3800", note: "메인. 노화 외삽", color: C.primary },
    { id: "2", title: "Temperature Extrap.", train: "25/50 °C 전체",            test: "0 °C 전체 (cycle 0~101)", note: "이중 외삽 (cell+temp)", color: C.secondary },
    { id: "3", title: "Cell Extrapolation",  train: "ch2 (25 °C)",              test: "ch7 (50 °C)",            note: "한계: cell+temp 혼합",   color: "8B5CF6" },
    { id: "4", title: "Cross-Dataset",       train: "main_cell ch2/ch7",        test: "pouch_SOH ch1~ch8",      note: "multi-cell + 패턴",      color: C.success },
    { id: "5", title: "Cross-Pattern",       train: "MG + PVSmoothing",          test: "PowerQuality",            note: "unseen 주행 패턴",        color: "EAB308" },
    { id: "6", title: "Cross-Scale (Cell→Module)", train: "main_cell ch2/ch7",  test: "module CH1 (14S)",       note: "본 연구 두 번째 contribution", color: C.accent },
  ];

  const cw = 4.0, ch = 1.6, gap = 0.15, sx = 0.5, sy = 1.7;
  splits.forEach((sp, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = sx + col * (cw + gap);
    const y = sy + row * (ch + gap + 1.0);
    card(s, x, y, cw, ch + 1.0, "FFFFFF");
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: cw, h: 0.45, fill: { color: sp.color }, line: { color: sp.color, width: 0 },
    });
    s.addText(`SPLIT  ${sp.id}`, {
      x: x + 0.2, y, w: 1.2, h: 0.45,
      fontSize: 10, bold: true, color: "FFFFFF", fontFace: FONT.head,
      charSpacing: 4, valign: "middle", margin: 0,
    });
    s.addText(sp.title, {
      x: x + 0.2, y: y + 0.55, w: cw - 0.3, h: 0.45,
      fontSize: 14, bold: true, color: C.textDark, fontFace: FONT.head, margin: 0,
    });
    s.addText([
      { text: "TRAIN  ", options: { bold: true, color: sp.color, fontSize: 9.5 } },
      { text: sp.train, options: { color: C.textDark, fontSize: 10.5, breakLine: true } },
      { text: "TEST  ", options: { bold: true, color: sp.color, fontSize: 9.5 } },
      { text: sp.test, options: { color: C.textDark, fontSize: 10.5, breakLine: true } },
      { text: " ", options: { fontSize: 4, breakLine: true } },
      { text: sp.note, options: { italic: true, color: C.textMuted, fontSize: 10 } },
    ], {
      x: x + 0.2, y: y + 1.05, w: cw - 0.3, h: ch + 0.4,
      fontFace: FONT.body, paraSpaceAfter: 2, margin: 0, valign: "top",
    });
  });
  pageNumber(s, 11, TOTAL);
}

// ============================================================
// Slide 12 — 평가 메트릭
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "06  ·  METRICS");
  slideTitle(s, "평가 메트릭 — 정확도 + 강건성 + 외삽 + 임베디드");

  const metrics = [
    { tag: "정확도", color: C.primary, big: "RMSE / MAE / MAX",
      body: "SOC, SOH 각각 산출. SOC RMSE < 2% 목표. SOH MAE < 1.5% 목표." },
    { tag: "강건성", color: C.secondary, big: "초기 오차 회복 (s)",
      body: "초기 SOC 섭동 ±10/20/30%에서 5% 이내 수렴까지 걸리는 시간 측정." },
    { tag: "외삽", color: C.accent, big: "RMSE 증가율",
      body: "학습 영역 RMSE 대비 외삽 영역 RMSE의 비율. 1.0 에 가까울수록 일반화 우수." },
    { tag: "임베디드성", color: "8B5CF6", big: "μs/step · KB",
      body: "1 스텝 추론 시간(μs)과 메모리(KB). BMS 탑재성 논의 자료." },
  ];

  const cw = 6.05, ch = 2.55, gap = 0.2, sx = 0.5, sy = 1.65;
  metrics.forEach((m, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = sx + col * (cw + gap);
    const y = sy + row * (ch + gap);
    card(s, x, y, cw, ch, "FFFFFF");
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: y, w: cw, h: 0.05, fill: { color: m.color }, line: { color: m.color, width: 0 },
    });
    s.addText(m.tag, {
      x: x + 0.4, y: y + 0.25, w: cw - 0.5, h: 0.35,
      fontSize: 11, bold: true, color: m.color, fontFace: FONT.head, charSpacing: 6, margin: 0,
    });
    s.addText(m.big, {
      x: x + 0.4, y: y + 0.7, w: cw - 0.5, h: 0.7,
      fontSize: 24, bold: true, color: C.textDark, fontFace: FONT.head, margin: 0,
    });
    s.addText(m.body, {
      x: x + 0.4, y: y + 1.55, w: cw - 0.6, h: ch - 1.7,
      fontSize: 12, color: C.textMuted, fontFace: FONT.body, margin: 0,
    });
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 6.85, w: 12.3, h: 0.35, fill: { color: C.bgCard }, line: { color: C.border, width: 0 },
  });
  s.addText("[P4 stretch] PICP_95 (예측구간 적중률) + NLL 추가 — calibrated UQ 동반", {
    x: 0.65, y: 6.85, w: 12.0, h: 0.35,
    fontSize: 10.5, italic: true, color: C.textMuted, fontFace: FONT.body, valign: "middle", margin: 0,
  });
  pageNumber(s, 12, TOTAL);
}

// ============================================================
// Slide 13 — 예상 결과
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "07  ·  EXPECTED RESULTS");
  slideTitle(s, "예상 결과 — 정량 시나리오");

  s.addText("Split 1 (Aging Extrapolation, 50 °C × cycle 2500~3800 테스트) 가상 결과. 본 차트는 보고서 작성 가이드용.", {
    x: 0.5, y: 1.55, w: 12.3, h: 0.4,
    fontSize: 11, italic: true, color: C.textMuted, fontFace: FONT.body, margin: 0,
  });

  const socData = [{
    name: "SOC RMSE (%)",
    labels: ["AhCount", "OCV-LU", "EKF", "UKF", "DEKF", "DUKF", "AEKF", "FOM-AEKF"],
    values: [4.8, 3.6, 2.9, 2.7, 2.4, 2.3, 2.1, 1.4],
  }];
  s.addChart(pres.charts.BAR, socData, {
    x: 0.5, y: 2.1, w: 6.1, h: 3.2,
    barDir: "col",
    chartColors: [C.primary, C.primary, C.primary, C.primary, C.primary, C.primary, C.primary, C.accent],
    chartColorsOpacity: 80,
    chartArea: { fill: { color: "FFFFFF" }, roundedCorners: false },
    catAxisLabelColor: C.textMuted, catAxisLabelFontSize: 10,
    valAxisLabelColor: C.textMuted, valAxisLabelFontSize: 10,
    valGridLine: { color: C.border, size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.textDark, dataLabelFontSize: 10,
    showLegend: false,
    showTitle: true, title: "SOC RMSE (낮을수록 좋음)", titleFontSize: 12, titleColor: C.textDark,
  });

  const sohData = [{
    name: "SOH MAE (%)",
    labels: ["AhCount", "OCV-LU", "EKF", "UKF", "DEKF", "DUKF", "AEKF", "FOM-AEKF"],
    values: [5.5, 4.2, 3.8, 3.5, 2.6, 2.4, 2.2, 1.3],
  }];
  s.addChart(pres.charts.BAR, sohData, {
    x: 6.7, y: 2.1, w: 6.1, h: 3.2,
    barDir: "col",
    chartColors: [C.secondary, C.secondary, C.secondary, C.secondary, C.secondary, C.secondary, C.secondary, C.accent],
    chartColorsOpacity: 80,
    chartArea: { fill: { color: "FFFFFF" }, roundedCorners: false },
    catAxisLabelColor: C.textMuted, catAxisLabelFontSize: 10,
    valAxisLabelColor: C.textMuted, valAxisLabelFontSize: 10,
    valGridLine: { color: C.border, size: 0.5 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.textDark, dataLabelFontSize: 10,
    showLegend: false,
    showTitle: true, title: "SOH MAE (낮을수록 좋음)", titleFontSize: 12, titleColor: C.textDark,
  });

  const stats = [
    { v: "−33%", l: "vs AEKF (SOC RMSE)" },
    { v: "−41%", l: "vs AEKF (SOH MAE)" },
    { v: "≤ 80 μs", l: "1 스텝 추론" },
    { v: "≤ 5%", l: "Cross-Scale RMSE 손실" },
  ];
  const stw = 2.95, stx = 0.5, sty = 5.6, stgap = 0.15;
  stats.forEach((st, i) => {
    const x = stx + i * (stw + stgap);
    card(s, x, sty, stw, 1.45, "FFFFFF");
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: sty, w: 0.08, h: 1.45, fill: { color: C.accent }, line: { color: C.accent, width: 0 },
    });
    s.addText(st.v, {
      x: x + 0.25, y: sty + 0.2, w: stw - 0.3, h: 0.7,
      fontSize: 32, bold: true, color: C.accent, fontFace: FONT.head, margin: 0,
    });
    s.addText(st.l, {
      x: x + 0.25, y: sty + 0.95, w: stw - 0.3, h: 0.4,
      fontSize: 11, color: C.textMuted, fontFace: FONT.body, margin: 0,
    });
  });

  s.addText("(차트 수치는 SOTA 문헌 통상 범위 + 본 연구 목표치로 구성한 시나리오. 실제 값은 P2~P3에서 측정.)", {
    x: 0.5, y: 7.15, w: 12.3, h: 0.25,
    fontSize: 9, italic: true, color: C.textMuted, fontFace: FONT.body, align: "center", margin: 0,
  });
  pageNumber(s, 13, TOTAL);
}

// ============================================================
// Slide 14 — IMRaD
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "07  ·  PAPER STRUCTURE");
  slideTitle(s, "논문 섹션 구성 — IMRaD 매핑");

  const sections = [
    { n: "Abstract", body: "FOM-AEKF + Cross-Scale 한 단락. Quantitative claim: SOC RMSE [X]%↓, SOH MAE [Y]%↓, cross-scale 손실 ≤ 5%.", color: C.primary },
    { n: "1  Introduction", body: "BMS의 SOC/SOH 결합 문제 → 단독 한계 → joint 동향 → SOTA 갭(2025 dual AUKF, multi-task transformer) → 본 contribution 4건 enumerate.", color: C.primary },
    { n: "2  Related Work", body: "기존 dual filter, AEKF, FOM-EKF, multi-task DL, PINN-SOH 분류 비교. 본 연구의 차별화 위치.", color: C.secondary },
    { n: "3  Methods", body: "3.1 분수계 ECM 정의 · 3.2 Dual filter 시간 척도 분리 · 3.3 2D Q/R 스케줄러 학습 · 3.4 Cross-scale 적용 절차.", color: C.secondary },
    { n: "4  Experimental Setup", body: "4.1 데이터셋 (Pouch 셀+모듈) · 4.2 Split 6종 · 4.3 Baseline 7종 · 4.4 메트릭 4축 · 4.5 구현 세부.", color: C.accent },
    { n: "5  Results", body: "5.1 Aging 외삽 (Split 1) · 5.2 Temperature/Cell/Cross-pattern (Split 2/3/5) · 5.3 Cross-Scale 셀→모듈 (Split 6) · 5.4 임베디드성.", color: C.accent },
    { n: "6  Discussion", body: "Q/R surface 학습된 형태 해석 · 분수계 α 의 노화 추적 능력 · cross-scale 손실 분해 · 한계와 향후.", color: C.success },
    { n: "7  Conclusion", body: "Pouch 셀+모듈 두 축 일관 검증된 FOM-AEKF — 미드티어 SCI에 적합. P4 PINN-AEKF + UQ는 stretch.", color: C.success },
  ];

  const startY = 1.65, rowH = 0.66;
  sections.forEach((sec, i) => {
    const y = startY + i * rowH;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 2.0, h: rowH - 0.06,
      fill: { color: sec.color }, line: { color: sec.color, width: 0 },
    });
    s.addText(sec.n, {
      x: 0.5, y, w: 2.0, h: rowH - 0.06,
      fontSize: 12, bold: true, color: "FFFFFF", fontFace: FONT.head,
      align: "center", valign: "middle", margin: 0,
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 2.6, y, w: 10.2, h: rowH - 0.06,
      fill: { color: i % 2 === 0 ? "FFFFFF" : C.bgCard }, line: { color: C.border, width: 0.5 },
    });
    s.addText(sec.body, {
      x: 2.75, y, w: 10.0, h: rowH - 0.06,
      fontSize: 11, color: C.textDark, fontFace: FONT.body, valign: "middle", margin: 0,
    });
  });
  pageNumber(s, 14, TOTAL);
}

// ============================================================
// Slide 15 — Multi-Paper 전략 (5편 매트릭스)
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "08  ·  MULTI-PAPER STRATEGY");
  slideTitle(s, "한 데이터·코드 베이스에서 5편 산출");

  s.addText("SCI 3편 + KCI 2편. KCI 2편을 SCI 의 사전·보조 작업으로 위치시켜 글쓰기 leverage 확보.", {
    x: 0.5, y: 1.55, w: 12.3, h: 0.35,
    fontSize: 12, italic: true, color: C.textMuted, fontFace: FONT.body, margin: 0,
  });

  const headers = ["#", "등급", "제목 (가제)", "핵심 contribution", "타깃 저널", "투고 시점"];
  const rows = [
    ["K1", "KCI", "NCM Pouch 셀의 분수계 등가회로모델 식별 및 노화 추적 (한글)",
       "분수계 R+CPE 식별 + α 노화 추적성", "한국산학기술학회 / 대한전기학회", "T+3"],
    ["K2", "KCI", "14S 모듈 내 셀간 전압편차 분석 및 SOC 추정 영향 (한글)",
       "셀간 σ가 SOC 정확도에 미치는 정량 영향", "한국산학기술학회 / 대한전기학회", "T+6"],
    ["S1", "SCI", "FOM-AEKF: Joint SOC/SOH for NCM Pouch Cells",
       "분수계 ECM × Dual AEKF × 2D Q/R lookup", "J. Energy Storage IF 8~9 / IEEE TTE", "T+5~6"],
    ["S2", "SCI", "Cross-Scale Generalization: Cell → 14S Module",
       "셀 학습 알고리즘의 모듈 적용 + 셀간 편차 영향", "IEEE TTE IF 7 / J. Power Sources IF 8", "T+8~9"],
    ["S3", "SCI", "Hybrid Physics-Data Estimator with Calibrated UQ",
       "FOM-AEKF + NN/GPR + PICP/NLL", "Applied Energy IF 11 / eTransportation IF 13", "T+14"],
  ];

  const tableData = [
    headers.map(h => ({
      text: h,
      options: { bold: true, color: "FFFFFF", fill: { color: C.primary }, fontSize: 11, align: "center", valign: "middle" },
    })),
    ...rows.map((r, i) => {
      const isKCI = r[1] === "KCI";
      return r.map((c, j) => ({
        text: c,
        options: {
          color: C.textDark,
          fill: { color: j === 1
            ? (isKCI ? "FEF3C7" : "DBEAFE")
            : (i % 2 === 0 ? C.bgLight : C.bgCard)
          },
          fontSize: 10,
          bold: j === 0 || j === 1,
          align: (j === 0 || j === 1 || j === 5) ? "center" : "left",
          valign: "middle",
        },
      }));
    }),
  ];

  s.addTable(tableData, {
    x: 0.5, y: 2.0, w: 12.3,
    colW: [0.6, 0.7, 4.0, 3.4, 2.6, 1.0], rowH: 0.7,
    border: { pt: 0.5, color: C.border }, fontFace: FONT.body,
  });

  // Bottom — leverage diagram
  card(s, 0.5, 5.7, 12.3, 1.5, C.bgCard);
  s.addText("Leverage 흐름", {
    x: 0.7, y: 5.8, w: 12, h: 0.3,
    fontSize: 12, bold: true, color: C.primary, fontFace: FONT.head, margin: 0,
  });
  s.addText([
    { text: "K1", options: { bold: true, color: "92400E", fontSize: 12 } },
    { text: " (분수계 ECM 식별) → ", options: { color: C.textDark, fontSize: 11 } },
    { text: "S1", options: { bold: true, color: C.primary, fontSize: 12 } },
    { text: " 메소드 §3.1 압축 + 자기 인용  ·  ", options: { color: C.textDark, fontSize: 11 } },
    { text: "K2", options: { bold: true, color: "92400E", fontSize: 12 } },
    { text: " (셀간 편차) → ", options: { color: C.textDark, fontSize: 11 } },
    { text: "S2", options: { bold: true, color: C.primary, fontSize: 12 } },
    { text: " cell-equiv 한계 사전 입증  ·  ", options: { color: C.textDark, fontSize: 11 } },
    { text: "S1·S2 → S3", options: { bold: true, color: C.primary, fontSize: 12 } },
    { text: " \"Building on our prior works\" 로 reviewer 신뢰도 ↑", options: { color: C.textDark, fontSize: 11 } },
  ], {
    x: 0.7, y: 6.2, w: 12.0, h: 0.9, fontFace: FONT.body, margin: 0,
  });

  pageNumber(s, 15, TOTAL);
}

// ============================================================
// Slide 16 — Multi-Paper 타임라인 (Gantt)
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "08  ·  MULTI-PAPER TIMELINE");
  slideTitle(s, "5편 자료 확보 · 글쓰기 · 투고 타임라인");

  s.addText("자료 확보 ~14개월, 게재까지 ~24개월. K1·K2 (한글) 빠르게 빼서 자기 인용 풀 확보 + S1·S2·S3 시계열 leverage.", {
    x: 0.5, y: 1.55, w: 12.3, h: 0.35,
    fontSize: 11, italic: true, color: C.textMuted, fontFace: FONT.body, margin: 0,
  });

  // Timeline axis (months 0 ~ 14)
  const axisY = 6.4;
  const axisStartX = 1.8;
  const axisEndX = 12.6;
  const axisLen = axisEndX - axisStartX;
  const monthMax = 14;

  s.addShape(pres.shapes.LINE, {
    x: axisStartX, y: axisY, w: axisLen, h: 0,
    line: { color: C.textDark, width: 1.5, endArrowType: "triangle" },
  });
  // Tick labels
  for (let m = 0; m <= 14; m += 2) {
    const x = axisStartX + (m / monthMax) * axisLen;
    s.addShape(pres.shapes.LINE, {
      x, y: axisY, w: 0, h: 0.08, line: { color: C.textDark, width: 1 },
    });
    s.addText(`T+${m}`, {
      x: x - 0.3, y: axisY + 0.12, w: 0.6, h: 0.25,
      fontSize: 9, color: C.textMuted, fontFace: FONT.body, align: "center", margin: 0,
    });
  }
  s.addText("개월", {
    x: axisEndX - 0.05, y: axisY + 0.12, w: 0.6, h: 0.25,
    fontSize: 9, italic: true, color: C.textMuted, fontFace: FONT.body, margin: 0,
  });

  // Bars: each paper has [data-prep span, write span, submit point]
  const papers = [
    { tag: "K1", color: "EAB308", grade: "KCI", dataStart: 1.0, dataEnd: 3.0, writeStart: 3.0, writeEnd: 3.5, submit: 3.5 },
    { tag: "S1", color: C.primary, grade: "SCI", dataStart: 0.0, dataEnd: 5.0, writeStart: 5.0, writeEnd: 6.0, submit: 6.0 },
    { tag: "K2", color: "EAB308", grade: "KCI", dataStart: 5.0, dataEnd: 6.0, writeStart: 6.0, writeEnd: 6.5, submit: 6.5 },
    { tag: "S2", color: C.secondary, grade: "SCI", dataStart: 6.0, dataEnd: 7.5, writeStart: 7.5, writeEnd: 9.0, submit: 9.0 },
    { tag: "S3", color: C.accent, grade: "SCI", dataStart: 8.0, dataEnd: 12.5, writeStart: 12.5, writeEnd: 14.0, submit: 14.0 },
  ];

  const rowStart = 2.1;
  const rowH = 0.75;
  papers.forEach((p, i) => {
    const y = rowStart + i * rowH;

    // Label on left
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y: y + 0.05, w: 1.2, h: 0.55,
      fill: { color: p.color }, line: { color: p.color, width: 0 },
    });
    s.addText(`${p.tag}\n${p.grade}`, {
      x: 0.5, y: y + 0.05, w: 1.2, h: 0.55,
      fontSize: 11, bold: true, color: "FFFFFF", fontFace: FONT.head,
      align: "center", valign: "middle", margin: 0,
    });

    // Data prep bar (lighter)
    const dx1 = axisStartX + (p.dataStart / monthMax) * axisLen;
    const dx2 = axisStartX + (p.dataEnd / monthMax) * axisLen;
    s.addShape(pres.shapes.RECTANGLE, {
      x: dx1, y: y + 0.18, w: dx2 - dx1, h: 0.3,
      fill: { color: p.color, transparency: 60 }, line: { color: p.color, width: 0.5 },
    });
    s.addText("자료 확보", {
      x: dx1, y: y + 0.18, w: dx2 - dx1, h: 0.3,
      fontSize: 8, color: C.textDark, fontFace: FONT.body,
      align: "center", valign: "middle", margin: 0,
    });

    // Writing bar (solid)
    const wx1 = axisStartX + (p.writeStart / monthMax) * axisLen;
    const wx2 = axisStartX + (p.writeEnd / monthMax) * axisLen;
    s.addShape(pres.shapes.RECTANGLE, {
      x: wx1, y: y + 0.18, w: wx2 - wx1, h: 0.3,
      fill: { color: p.color }, line: { color: p.color, width: 0 },
    });
    s.addText("글쓰기", {
      x: wx1, y: y + 0.18, w: wx2 - wx1, h: 0.3,
      fontSize: 8, bold: true, color: "FFFFFF", fontFace: FONT.body,
      align: "center", valign: "middle", margin: 0,
    });

    // Submit marker (downward triangle / star)
    const sx = axisStartX + (p.submit / monthMax) * axisLen;
    s.addShape(pres.shapes.OVAL, {
      x: sx - 0.13, y: y + 0.13, w: 0.26, h: 0.26,
      fill: { color: "FFFFFF" }, line: { color: p.color, width: 2 },
    });
    s.addText("✓", {
      x: sx - 0.13, y: y + 0.13, w: 0.26, h: 0.26,
      fontSize: 12, bold: true, color: p.color, fontFace: FONT.head,
      align: "center", valign: "middle", margin: 0,
    });

    // Submit label below
    s.addText(`투고 T+${p.submit}`, {
      x: sx - 0.7, y: y + 0.42, w: 1.4, h: 0.2,
      fontSize: 8, italic: true, color: p.color, fontFace: FONT.body,
      align: "center", margin: 0,
    });
  });

  // Legend
  card(s, 0.5, 5.55, 12.3, 0.55, "FFFFFF");
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 5.7, w: 0.4, h: 0.25, fill: { color: C.textMuted, transparency: 60 }, line: { color: C.textMuted, width: 0.5 },
  });
  s.addText("자료 확보 (P0~P4)", {
    x: 1.2, y: 5.7, w: 2.5, h: 0.25,
    fontSize: 10, color: C.textDark, fontFace: FONT.body, valign: "middle", margin: 0,
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 4.0, y: 5.7, w: 0.4, h: 0.25, fill: { color: C.textMuted }, line: { color: C.textMuted, width: 0 },
  });
  s.addText("글쓰기·revision", {
    x: 4.5, y: 5.7, w: 2.5, h: 0.25,
    fontSize: 10, color: C.textDark, fontFace: FONT.body, valign: "middle", margin: 0,
  });
  s.addShape(pres.shapes.OVAL, {
    x: 7.3, y: 5.68, w: 0.28, h: 0.28, fill: { color: "FFFFFF" }, line: { color: C.textMuted, width: 1.5 },
  });
  s.addText("✓ 투고", {
    x: 7.7, y: 5.7, w: 2.0, h: 0.25,
    fontSize: 10, color: C.textDark, fontFace: FONT.body, valign: "middle", margin: 0,
  });
  s.addText("게재까지 추가 6~12개월 (저널별)", {
    x: 9.5, y: 5.7, w: 3.2, h: 0.25,
    fontSize: 10, italic: true, color: C.textMuted, fontFace: FONT.body, valign: "middle", align: "right", margin: 0,
  });

  pageNumber(s, 16, TOTAL);
}

// ============================================================
// Slide 17 — 마일스톤 + 저널 (구 15)
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgLight };
  topBar(s, "09  ·  ROADMAP");
  slideTitle(s, "코드 마일스톤 (≈ 14개월) · 저널별 우선순위");

  const phases = [
    { tag: "P0", w: "1개월", title: "데이터·환경", body: "마이그레이션, OCV·ECM, 카탈로그", color: C.primary, paper: "" },
    { tag: "P1", w: "1개월", title: "Baseline 7종+LSTM", body: "bench-baseline 결과", color: C.secondary, paper: "" },
    { tag: "P2", w: "3개월", title: "Stage A — FOM-AEKF", body: "분수계 ECM, dual AEKF, 2D Q/R", color: C.accent, paper: "→ K1 / S1 자료" },
    { tag: "P3", w: "2개월", title: "외삽·Cross-Scale", body: "Split 1~6, cell→module + 셀간 편차", color: C.success, paper: "→ K2 / S2 자료" },
    { tag: "P4*", w: "+5개월", title: "Stretch — Hybrid+UQ", body: "NN/GPR residual, PICP/NLL", color: "8B5CF6", paper: "→ S3 자료" },
  ];

  const tlY = 1.7, totalW = 12.3, sx = 0.5;
  const segW = totalW / phases.length;
  phases.forEach((p, i) => {
    const x = sx + i * segW;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.05, y: tlY, w: segW - 0.1, h: 0.5,
      fill: { color: p.color }, line: { color: p.color, width: 0 },
    });
    s.addText(`${p.tag}  ·  ${p.w}`, {
      x: x + 0.05, y: tlY, w: segW - 0.1, h: 0.5,
      fontSize: 12, bold: true, color: "FFFFFF", fontFace: FONT.head,
      align: "center", valign: "middle", margin: 0,
    });
    card(s, x + 0.05, tlY + 0.55, segW - 0.1, 1.55, C.bgCard);
    s.addText(p.title, {
      x: x + 0.15, y: tlY + 0.65, w: segW - 0.3, h: 0.35,
      fontSize: 12, bold: true, color: C.textDark, fontFace: FONT.head, margin: 0,
    });
    s.addText(p.body, {
      x: x + 0.15, y: tlY + 1.0, w: segW - 0.3, h: 0.6,
      fontSize: 9.5, color: C.textMuted, fontFace: FONT.body, margin: 0,
    });
    if (p.paper) {
      s.addText(p.paper, {
        x: x + 0.15, y: tlY + 1.65, w: segW - 0.3, h: 0.4,
        fontSize: 10, bold: true, italic: true, color: p.color, fontFace: FONT.body, margin: 0,
      });
    }
  });

  s.addText("논문별 타깃 저널 우선순위 (자세한 매핑은 §08 슬라이드)", {
    x: 0.5, y: 4.35, w: 12, h: 0.4,
    fontSize: 14, bold: true, color: C.primary, fontFace: FONT.head, margin: 0,
  });

  const headers = ["우선", "저널", "IF (대략)", "핏 — 본 연구 적합 사유"];
  const rows = [
    ["1차", "Journal of Energy Storage (Elsevier)", "8~9", "범용·채택 폭 넓음, Stage A만으로 충분"],
    ["1차 대안", "IEEE Transactions on Transportation Electrification", "7", "EV BMS 앵글 강조, joint estimation 적합"],
    ["2차", "Journal of Power Sources", "8", "전기화학·ECM 강조 시"],
    ["2차", "IEEE Trans. on Industrial Electronics / TPEL", "7~8", "필터·제어공학 강조 시"],
    ["스트레치", "Applied Energy", "11", "P3 외삽 + Cross-Scale + (P4 시) UQ 동반 시"],
  ];
  const tableData = [
    headers.map(h => ({
      text: h,
      options: { bold: true, color: "FFFFFF", fill: { color: C.primary }, fontSize: 11, align: "center", valign: "middle" },
    })),
    ...rows.map((r, i) => r.map((c, j) => ({
      text: c,
      options: {
        color: C.textDark,
        fill: { color: i % 2 === 0 ? C.bgLight : C.bgCard },
        fontSize: 10.5, valign: "middle",
        align: (j === 0 || j === 2) ? "center" : "left",
        bold: j === 0,
      },
    }))),
  ];
  s.addTable(tableData, {
    x: 0.5, y: 4.85, w: 12.3,
    colW: [1.2, 4.5, 1.5, 5.1], rowH: 0.42,
    border: { pt: 0.5, color: C.border }, fontFace: FONT.body,
  });
  pageNumber(s, 17, TOTAL);
}

// ============================================================
// Slide 18 — Conclusion + 리스크 (dark)
// ============================================================
{
  const s = pres.addSlide();
  s.background = { color: C.bgDark };
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 0.45, w: 0.08, h: 0.35, fill: { color: C.accent }, line: { color: C.accent, width: 0 },
  });
  s.addText("CONCLUSION  ·  RISKS  ·  NEXT STEPS", {
    x: 0.7, y: 0.42, w: 8, h: 0.4,
    fontSize: 11, bold: true, color: C.accent2, fontFace: FONT.head, charSpacing: 4, margin: 0,
  });
  s.addText("결론 — 무엇을 입증할 것인가", {
    x: 0.5, y: 0.95, w: 12, h: 0.6,
    fontSize: 26, bold: true, color: "FFFFFF", fontFace: FONT.head, margin: 0,
  });

  s.addText([
    { text: "1.  ", options: { bold: true, color: C.accent, fontSize: 14 } },
    { text: "한 데이터·코드 베이스에서 5편 산출", options: { bold: true, color: "FFFFFF", fontSize: 14 } },
    { text: " — SCI 3편 (FOM-AEKF / Cross-Scale / Hybrid+UQ) + KCI 2편 (분수계 ECM 식별 / 모듈 셀간 편차).", options: { color: "CBD5E1", fontSize: 13, breakLine: true } },
    { text: "2.  ", options: { bold: true, color: C.accent, fontSize: 14 } },
    { text: "K1·K2 → S1·S2·S3 시계열 leverage", options: { bold: true, color: "FFFFFF", fontSize: 14 } },
    { text: " — 한글 KCI 빠르게 빼서 자기 인용 풀 + reviewer 신뢰도 확보.", options: { color: "CBD5E1", fontSize: 13, breakLine: true } },
    { text: "3.  ", options: { bold: true, color: C.accent, fontSize: 14 } },
    { text: "Fallback 안전판", options: { bold: true, color: "FFFFFF", fontSize: 14 } },
    { text: " — P4 학습 발산 시에도 K1+K2+S1 (KCI 2 + SCI 1) 거의 확실 확보. 자료 ~14개월 / 게재 ~24개월.", options: { color: "CBD5E1", fontSize: 13 } },
  ], {
    x: 0.5, y: 1.7, w: 12.3, h: 2.0, fontFace: FONT.body, paraSpaceAfter: 8, margin: 0,
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.0, w: 12.3, h: 1.85, fill: { color: "11305A" }, line: { color: "1F4060", width: 0 },
  });
  s.addText("주요 리스크 & 완화", {
    x: 0.7, y: 4.1, w: 12, h: 0.35,
    fontSize: 14, bold: true, color: C.accent2, fontFace: FONT.head, margin: 0,
  });
  s.addText([
    { text: "● 분수계 ECM 식별 불안정", options: { bold: true, color: "FFFFFF", fontSize: 11 } },
    { text: "  → 정수 2-RC를 fallback으로 병행 구현 / ", options: { color: "9DC4E0", fontSize: 11 } },
    { text: "● 모듈 셀간 전압편차", options: { bold: true, color: "FFFFFF", fontSize: 11 } },
    { text: "  → cell-equiv vs module-direct 두 시나리오 모두 보고 / ", options: { color: "9DC4E0", fontSize: 11, breakLine: true } },
    { text: "● Pouch 단일 chemistry 비판", options: { bold: true, color: "FFFFFF", fontSize: 11 } },
    { text: "  → cross-scale 일반화로 부분 상쇄, NASA PCoE 옵션 보강 / ", options: { color: "9DC4E0", fontSize: 11 } },
    { text: "● Stage A 단독 incremental 평가", options: { bold: true, color: "FFFFFF", fontSize: 11 } },
    { text: "  → 2D Q/R 스케줄러의 데이터 기반 학습 + cross-scale 두 축으로 차별화", options: { color: "9DC4E0", fontSize: 11 } },
  ], {
    x: 0.7, y: 4.5, w: 12.0, h: 1.3, fontFace: FONT.body, paraSpaceAfter: 4, margin: 0,
  });

  s.addText("다음 단계 (Day 1)", {
    x: 0.5, y: 6.05, w: 12, h: 0.35,
    fontSize: 14, bold: true, color: C.accent2, fontFace: FONT.head, margin: 0,
  });
  s.addText([
    { text: "①  ", options: { bold: true, color: C.accent, fontSize: 12 } },
    { text: "Codex가 ", options: { color: "FFFFFF", fontSize: 12 } },
    { text: "Codex_TODO_v1.md", options: { bold: true, color: C.accent2, fontSize: 12 } },
    { text: " §12 정독 후 디렉터리 마이그레이션 → 정찰 → OCV 추출  /  ", options: { color: "9DC4E0", fontSize: 11 } },
    { text: "②  ", options: { bold: true, color: C.accent, fontSize: 12 } },
    { text: "Antigravity가 ", options: { color: "FFFFFF", fontSize: 12 } },
    { text: "Antigravity_TODO_v1.md", options: { bold: true, color: C.accent2, fontSize: 12 } },
    { text: " §12 정독 후 환경 셋업 + ui/ 골격", options: { color: "9DC4E0", fontSize: 11 } },
  ], {
    x: 0.5, y: 6.5, w: 12.3, h: 0.7, fontFace: FONT.body, margin: 0,
  });
  pageNumber(s, 18, TOTAL);
}

pres.writeFile({ fileName: "FOM_AEKF_SCI_strategy.pptx" }).then((name) => {
  console.log(`saved: ${name}`);
});
