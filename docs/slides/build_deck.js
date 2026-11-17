// Builds docs/slides/ClaimGuard.pptx   (run: node docs/slides/build_deck.js)
const path = require("path");
const pptxgen = require("pptxgenjs");
const SKILL = process.env.PPTX_SKILL;
const { applyTheme } = require(path.join(SKILL, "scripts/apply_theme.js"));

const ROOT = path.resolve(__dirname, "../..");
const P = (rel) => path.join(ROOT, rel);
const OUT = path.join(__dirname, "ClaimGuard.pptx");

// ---- fill these in -------------------------------------------------------
const TEAM = [["Krishna Bakshi", "24CSU297", "Data, notebook, MLflow training, model choice, report"], ["Naman Sharma", "24CSU287", "API, UI, tests, Docker, CI, deployment, slides"]];
const SECTION = "<Section>";
const LINKS = {
  repo: "https://github.com/<user>/claimguard",
  live: "https://<app>.onrender.com",
  docs: "https://<app>.onrender.com/docs",
  report: "<link to Name_RollNo.pdf>",
};
// --------------------------------------------------------------------------

const THEME = {
  name: "ClaimGuard",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1A1D24", lt1: "FFFFFF", dk2: "14233C", lt2: "EEF1F6",
    accent1: "D99A1E", accent2: "C0392B", accent3: "2E7D6B", accent4: "5B6B82",
    accent5: "8FA3BF", accent6: "F2C56B", hlink: "1F5FAD", folHlink: "6B4FA0",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "ClaimGuard - CSL236 End-Term Project";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: "Title Dark",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.0, w: 11.7, h: 1.3, fontSize: 54, bold: true, color: C.background1, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.4, w: 11.7, h: 0.9, fontSize: 20, color: C.accent1 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "Title Only",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.85, fontSize: 32, bold: true, color: C.text2, valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "ClaimGuard · CSL236 End-Term", options: { x: 0.6, y: 7.05, w: 6, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.05, w: 0.5, h: 0.3, fontSize: 10, color: C.accent4, align: "right" },
});

const card = (s, x, y, w, h, fill = C.background2) =>
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill } });
const txt = (s, text, o) => s.addText(text, { isTextBox: true, margin: 0, fontSize: 15, color: C.text1, valign: "top", ...o });
const bullets = (items, o = {}) => items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 6, ...o } }));
const pic = (s, rel, x, y, w, h) => s.addImage({ path: P(rel), x, y, w, h, sizing: { type: "contain", w, h } });

// 1. Title -----------------------------------------------------------------
pres.addSection({ title: "Intro" });
let s = pres.addSlide({ masterName: "Title Dark", sectionTitle: "Intro" });
s.addText("ClaimGuard", { placeholder: "title" });
s.addText("Vehicle insurance claim fraud detection: an end-to-end ML system", { placeholder: "body" });
txt(s, [{ text: "CSL236 Introduction to AI & ML · End-Term Project · Section " + SECTION, options: { breakLine: true } },
        ...TEAM.map((t, i) => ({ text: `${t[0]}  ·  ${t[1]}`, options: { breakLine: i < TEAM.length - 1 } }))],
    { x: 0.8, y: 4.7, w: 11, h: 1.6, fontSize: 16, color: C.background2, paraSpaceAfter: 4 });
s.addNotes("Introduce the team and the project: a fraud-triage system for vehicle insurance claims, built end to end from data to a live web app.");

// 2. Problem & dataset -----------------------------------------------------
pres.addSection({ title: "Problem and data" });
s = pres.addSlide({ masterName: "Title Only", sectionTitle: "Problem and data" });
s.addText("Ranking claims by fraud risk for investigators", { placeholder: "title" });
txt(s, bullets([
  "Binary classification: is this claim fraudulent (1) or genuine (0)?",
  "Output: a fraud probability plus what the investigator should check",
  "A triage tool: the model ranks, a human decides",
  "Data: Vehicle Insurance Claim Fraud Detection (fraud_oracle.csv, Kaggle / Oracle sample data)",
]), { x: 0.6, y: 1.5, w: 6.6, h: 3.4, fontSize: 17 });
const stats = [["15,419", "claims after cleaning"], ["21", "input features (from 33 raw columns)"], ["6%", "fraud: 923 cases"]];
stats.forEach(([n, l], i) => {
  card(s, 7.7, 1.4 + i * 1.75, 5.0, 1.5);
  txt(s, n, { x: 7.95, y: 1.55 + i * 1.75, w: 4.6, h: 0.75, fontSize: 40, bold: true, color: i === 2 ? C.accent2 : C.text2, fontFace: THEME.headFontFace });
  txt(s, l, { x: 7.95, y: 2.3 + i * 1.75, w: 4.6, h: 0.45, fontSize: 14, color: C.accent4 });
});
txt(s, "Cleaning: Age = 0 (320 rows) treated as missing · 1 row with no claim date dropped · make typos fixed · claim_delay_weeks engineered from dates · IDs and redundant columns removed",
    { x: 0.6, y: 5.3, w: 6.6, h: 1.2, fontSize: 13, color: C.accent4, italic: true });
s.addNotes("Explain why fraud matters, what the dataset contains, and the cleaning steps. Mention that 6% fraud makes accuracy misleading.");

// 3. EDA --------------------------------------------------------------------
s = pres.addSlide({ masterName: "Title Only", sectionTitle: "Problem and data" });
s.addText("Fraud follows the payout: own-car cover, holder at fault", { placeholder: "title" });
const chartOpts = (title) => ({
  x: 0, y: 0, w: 4.0, h: 3.6, barDir: "col", showTitle: true, title, titleFontSize: 14, titleColor: HEX.dk2, titleFontFace: "+mj-lt",
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.0"%"', dataLabelFontSize: 11, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt",
  chartColors: [HEX.accent2], catAxisLabelColor: HEX.accent4, valAxisLabelColor: HEX.accent4, catAxisLabelFontSize: 11, valAxisLabelFontSize: 10,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", valGridLine: { color: "E3E7EE", size: 0.5 }, catGridLine: { style: "none" },
  showLegend: false, valAxisMaxVal: 18, valAxisMinVal: 0, valAxisLabelFormatCode: '0"%"',
});
[
  ["Fraud rate by fault", ["Policy Holder", "Third Party"], [7.9, 0.9]],
  ["Fraud rate by base policy", ["All Perils", "Collision", "Liability"], [10.2, 7.3, 0.7]],
  ["By days from policy start to accident", ["none", "1-7", "8-15", "15-30", "30+"], [16.4, 7.1, 9.1, 6.1, 5.9]],
].forEach(([t, labels, values], i) => {
  s.addChart(pres.charts.BAR, [{ name: t, labels, values }], { ...chartOpts(t), x: 0.6 + i * 4.15, y: 1.4 });
});
txt(s, bullets([
  "Only 6% fraud: \"always genuine\" would score 94% accuracy, so we judge models by ROC-AUC, PR-AUC and recall",
  "Holder at fault: about 8× the fraud rate of third-party fault. Liability-only policies barely see fraud",
  "Accidents right after the policy starts, late reports and recent address changes are red flags",
], { fontSize: 15 }), { x: 0.6, y: 5.15, w: 12.1, h: 1.7 });
s.addNotes("Walk through the three charts. Key point: fraud needs a payout, so liability-only policies show almost none.");

// 4. Data contract & preprocessing -----------------------------------------
s = pres.addSlide({ masterName: "Title Only", sectionTitle: "Problem and data" });
s.addText("A strict data contract: anything outside it gets HTTP 422", { placeholder: "title" });
const hdr = (t) => ({ text: t, options: { bold: true, color: HEX.lt1, fill: { color: HEX.dk2 } } });
s.addTable([
  [hdr("Type"), hdr("Features"), hdr("Contract (Pydantic)"), hdr("Encoding")],
  ["Numeric (4)", "age, deductible, driver_rating, claim_delay_weeks", "StrictInt in 16–80, 300–700, 1–4, 0–52", "Median impute + flag (age)"],
  ["Binary (6)", "fault, sex, accident_area, police_report_filed, witness_present, agent_type", "Literal of 2 values", "0 / 1"],
  ["Ordinal (7)", "vehicle_price, age_of_vehicle, past_number_of_claims, address_change_claim, …", "Literal of listed ranges", "Integers in stated order"],
  ["Nominal (4)", "base_policy, vehicle_category, marital_status, make", "Literal of listed values", "One-hot"],
], { x: 0.6, y: 1.45, w: 12.1, colW: [1.6, 5.0, 3.1, 2.4], fontSize: 13, color: HEX.dk1, fontFace: "Calibri",
     border: { type: "solid", pt: 0.75, color: "D5DBE5" }, fill: { color: "FFFFFF" }, valign: "middle", rowH: 0.55 });
card(s, 0.6, 4.75, 12.1, 1.85);
txt(s, [
  { text: "Rejected with 422 (and tested): ", options: { bold: true, color: HEX.accent2 } },
  { text: "age 15 or 81 · \"45\" as a string · 45.5 · null / NaN · fault = \"Nobody\" · unknown make · missing field · extra field.  ", options: {} },
  { text: "Leakage-safe: ", options: { bold: true } },
  { text: "the train/test split happens first, and all preprocessing is a ColumnTransformer inside the model Pipeline, fitted on training data only. The same code runs in the API.", options: {} },
], { x: 0.85, y: 4.95, w: 11.6, h: 1.5, fontSize: 15 });
s.addNotes("Every row of the README contract table is enforced by the Pydantic schema. Explain strict types and why the split comes before fitting.");

// 5. Architecture ------------------------------------------------------------
pres.addSection({ title: "System" });
s = pres.addSlide({ masterName: "Title Only", sectionTitle: "System" });
s.addText("From CSV to a live, tested, containerised API", { placeholder: "title" });
const steps = [["Data", "fraud_oracle.csv"], ["Preprocess", "features.py"], ["Train", "train.py ×3 algos"], ["MLflow", "SQLite mlflow.db"], ["Model", "model.joblib"],
               ["FastAPI", "/predict · /health · UI"], ["Docker", "python:3.11-slim"], ["CI", "GitHub Actions"], ["Cloud", "Render + restart"]];
steps.forEach(([h, sub], i) => {
  const row = i < 5 ? 0 : 1, col = i < 5 ? i : 9 - i - 1;
  const x = 0.6 + col * 2.5, y = 1.55 + row * 1.9;
  card(s, x, y, 2.1, 1.2, row === 0 ? C.background2 : "FDF3DF");
  txt(s, h, { x: x + 0.15, y: y + 0.18, w: 1.8, h: 0.45, fontSize: 17, bold: true, color: C.text2, align: "center" });
  txt(s, sub, { x: x + 0.1, y: y + 0.65, w: 1.9, h: 0.4, fontSize: 12, color: C.accent4, align: "center" });
  if (row === 0 && col < 4) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.13, y: y + 0.45, w: 0.32, h: 0.3, fill: { color: HEX.accent4 }, line: { color: HEX.accent4 } });
  if (row === 1 && col > 0) s.addShape(pres.shapes.LEFT_ARROW, { x: x - 0.37, y: y + 0.45, w: 0.32, h: 0.3, fill: { color: HEX.accent4 }, line: { color: HEX.accent4 } });
});
s.addShape(pres.shapes.DOWN_ARROW, { x: 10.6 + 0.9, y: 2.8, w: 0.3, h: 0.6, fill: { color: HEX.accent4 }, line: { color: HEX.accent4 } });
txt(s, "Stack: Python 3.11 · pandas · scikit-learn · MLflow · FastAPI + Pydantic · Uvicorn · pytest · Docker · GitHub Actions · Render",
    { x: 0.6, y: 5.55, w: 12.1, h: 0.5, fontSize: 15, bold: true, color: C.text2 });
txt(s, "Model loaded once at startup · every prediction logged to logs/predictions.jsonl · drift_check.py compares live inputs with training data",
    { x: 0.6, y: 6.1, w: 12.1, h: 0.5, fontSize: 14, color: C.accent4 });
s.addNotes("Trace one request: the UI posts to /predict, Pydantic validates, the pipeline preprocesses and scores, and the input is logged. CI rebuilds and tests on every push.");

// 6. Model comparison ------------------------------------------------------
s = pres.addSlide({ masterName: "Title Only", sectionTitle: "System" });
s.addText("7 MLflow runs: gradient boosting ranks fraud best", { placeholder: "title" });
s.addChart(pres.charts.BAR, [
  { name: "ROC-AUC", labels: ["LogReg C=1", "LogReg C=0.05", "RF d6", "RF d12", "RF leaf5", "HGB d4", "HGB d6 ★"], values: [0.804, 0.804, 0.823, 0.820, 0.818, 0.833, 0.833] },
  { name: "PR-AUC", labels: ["LogReg C=1", "LogReg C=0.05", "RF d6", "RF d12", "RF leaf5", "HGB d4", "HGB d6 ★"], values: [0.151, 0.150, 0.205, 0.197, 0.201, 0.241, 0.246] },
], { x: 0.6, y: 1.4, w: 7.4, h: 5.3, barDir: "col", barGrouping: "clustered", showTitle: true, title: "Test-set ROC-AUC and PR-AUC per run", titleFontSize: 14,
     titleColor: HEX.dk2, titleFontFace: "+mj-lt", chartColors: [HEX.accent4, HEX.accent1], showValue: true, dataLabelPosition: "outEnd",
     dataLabelFormatCode: "0.00", dataLabelFontSize: 9, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt", catAxisLabelColor: HEX.accent4,
     valAxisLabelColor: HEX.accent4, catAxisLabelFontSize: 10, valAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
     valGridLine: { color: "E3E7EE", size: 0.5 }, catGridLine: { style: "none" }, showLegend: true, legendPos: "b", legendFontSize: 11, legendFontFace: "+mn-lt", valAxisMaxVal: 1 });
card(s, 8.4, 1.4, 4.3, 5.3, "FDF3DF");
txt(s, "Chosen: HistGradientBoosting", { x: 8.65, y: 1.6, w: 3.9, h: 0.5, fontSize: 19, bold: true, color: C.text2, fontFace: THEME.headFontFace });
txt(s, "lr 0.05 · 400 iters · depth 6", { x: 8.65, y: 2.1, w: 3.9, h: 0.35, fontSize: 13, color: C.accent4 });
txt(s, bullets([
  "Best PR-AUC 0.246: 4× random (0.06)",
  "Catches 83% of frauds at a tuned threshold of 0.58",
  "Learns interactions like \"at fault AND own-car cover\"",
  "About 1 MB, millisecond predictions",
  "Threshold tuned on validation data because fraud is only 6%",
], { fontSize: 14 }), { x: 8.65, y: 2.6, w: 3.85, h: 3.9 });
s.addNotes("Why not accuracy: imbalance. Why not run 6 with higher F1: it catches only a third of the frauds. Why not logistic regression: it misses interactions.");

// 7. Screenshots: UI ---------------------------------------------------------
pres.addSection({ title: "Evidence" });
s = pres.addSlide({ masterName: "Title Only", sectionTitle: "Evidence" });
s.addText("The UI scores a claim, explains it, and rejects bad input", { placeholder: "title" });
pic(s, "docs/screenshots/ui_prediction.png", 0.6, 1.35, 6.3, 5.5);
pic(s, "docs/screenshots/ui_422.png", 7.2, 1.35, 5.5, 4.4);
txt(s, "Left: a suspicious claim at 86% with 3 investigator tips. Right: age 12 and fault \"Nobody\" are rejected with HTTP 422.",
    { x: 7.2, y: 5.9, w: 5.5, h: 0.9, fontSize: 13, color: C.accent4 });
s.addNotes("Live demo: load the suspicious example, then the routine one, then send invalid input to show the 422.");

// 8. Screenshots: MLflow, pytest, docs, CI ----------------------------------
s = pres.addSlide({ masterName: "Title Only", sectionTitle: "Evidence" });
s.addText("Tracked, tested and green in CI", { placeholder: "title" });
pic(s, "docs/screenshots/mlflow_runs.png", 0.6, 1.35, 6.0, 3.4);
pic(s, "docs/screenshots/pytest.png", 6.9, 1.35, 5.8, 3.4);
const ph = [["/docs (Swagger UI)", "docs/screenshots/docs.png"], ["Green GitHub Actions check", "docs/screenshots/ci_green.png"]];
const fs = require("fs");
ph.forEach(([label, rel], i) => {
  const x = 0.6 + i * 6.3;
  if (fs.existsSync(P(rel))) pic(s, rel, x, 4.95, 5.8, 1.9);
  else { card(s, x, 4.95, 5.8, 1.9); txt(s, `[ Insert screenshot: ${label} ]`, { x: x + 0.2, y: 5.7, w: 5.4, h: 0.4, fontSize: 14, color: C.accent4, align: "center" }); }
});
s.addNotes("MLflow: 7 runs across 3 algorithms. pytest: 18 tests covering health, UI, domain logic and 422 boundaries. Add the /docs and CI screenshots after deployment.");

// 9. Testing, CI, Docker, deployment -----------------------------------------
s = pres.addSlide({ masterName: "Title Only", sectionTitle: "Evidence" });
s.addText("Every push is trained, tested, built and smoke-tested", { placeholder: "title" });
const blocks = [
  ["18 pytest tests", ["Health and UI load", "Domain logic: red-flag claim > routine claim; holder at fault > third party", "11 boundary cases + missing/extra field → 422", "Tips (2–3) and prediction logging"]],
  ["GitHub Actions", ["On every push to main", "pip install → train baseline → pytest -v", "docker build → run → /health, 422 check", "Image size printed in the log"]],
  ["Docker + deploy", ["python:3.11-slim + requirements-serve.txt", "No MLflow, pytest or Jupyter in the image", "Non-root user, HEALTHCHECK, $PORT", "Render free tier, auto-restart, JSON prediction log"]],
];
blocks.forEach(([h, items], i) => {
  const x = 0.6 + i * 4.1;
  card(s, x, 1.45, 3.85, 4.6);
  txt(s, h, { x: x + 0.25, y: 1.65, w: 3.4, h: 0.5, fontSize: 19, bold: true, color: C.text2, fontFace: THEME.headFontFace });
  txt(s, bullets(items, { fontSize: 14 }), { x: x + 0.25, y: 2.3, w: 3.4, h: 3.6 });
});
txt(s, "Bonus: drift_check.py compares logged inputs with training data (means and category shares) and exits 1 on drift, so it could trigger retraining",
    { x: 0.6, y: 6.25, w: 12.1, h: 0.6, fontSize: 14, color: C.accent3, bold: true });
s.addNotes("Two requirements files: the full environment for training and tests, a lean one for serving, which keeps the image smaller and safer.");

// 10. Links --------------------------------------------------------------------
pres.addSection({ title: "Wrap-up" });
s = pres.addSlide({ masterName: "Title Only", sectionTitle: "Wrap-up" });
s.addText("Links", { placeholder: "title" });
[["GitHub repository", LINKS.repo], ["Live deployment", LINKS.live], ["API docs (/docs)", LINKS.docs], ["PDF report", LINKS.report]].forEach(([l, u], i) => {
  card(s, 0.6, 1.5 + i * 1.25, 12.1, 1.0);
  txt(s, l, { x: 0.9, y: 1.78 + i * 1.25, w: 3.3, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
  const isUrl = /^https?:\/\//.test(u);
  txt(s, isUrl ? [{ text: u, options: { hyperlink: { url: u }, color: HEX.hlink, underline: { style: "sng" } } }] : u,
      { x: 4.3, y: 1.78 + i * 1.25, w: 8.2, h: 0.45, fontSize: 18 });
});
s.addNotes("Click each link before the demo to check that it opens.");

// 11. Limitations + contributions ---------------------------------------------
s = pres.addSlide({ masterName: "Title Only", sectionTitle: "Wrap-up" });
s.addText("Limitations, next steps and who did what", { placeholder: "title" });
txt(s, "Limitations", { x: 0.6, y: 1.45, w: 5.8, h: 0.45, fontSize: 19, bold: true, color: C.text2, fontFace: THEME.headFontFace });
txt(s, bullets([
  "Old (1994–96) US sample data, so it needs retraining on current data",
  "Only 923 frauds and pre-bucketed fields: precision is about 15%, so use it as a triage aid only",
  "sex and marital_status need a fairness review",
], { fontSize: 14 }), { x: 0.6, y: 2.0, w: 5.8, h: 2.2 });
txt(s, "Next steps", { x: 0.6, y: 4.3, w: 5.8, h: 0.45, fontSize: 19, bold: true, color: C.text2, fontFace: THEME.headFontFace });
txt(s, bullets(["Scheduled drift check + automatic deploy after CI", "SHAP explanation per prediction", "Feed investigators' outcomes back as new labels"], { fontSize: 14 }),
    { x: 0.6, y: 4.85, w: 5.8, h: 1.8 });
s.addTable([[hdr("Member"), hdr("Roll No"), hdr("Contribution")], ...TEAM.map((t) => t.slice())],
  { x: 6.9, y: 1.45, w: 5.8, colW: [1.8, 1.3, 2.7], fontSize: 13, color: HEX.dk1, fontFace: "Calibri", border: { type: "solid", pt: 0.75, color: "D5DBE5" }, rowH: 0.6, valign: "middle" });
s.addNotes("Each member explains their own part. Thank the panel and invite questions.");

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
