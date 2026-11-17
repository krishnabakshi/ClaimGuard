"""Builds docs/report/report.html; render it to PDF with render_pdf.js (or print from a browser).
Edit TEAM below, then run:  python docs/report/build_report.py"""

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "report.html"

TEAM = [  # (name, roll number, contribution)
    ("Krishna Bakshi", "24CSU297", "Data cleaning and EDA notebook, data contract, train.py and MLflow experiments, model selection, report"),
    ("Naman Sharma", "24CSU287", "FastAPI app and Pydantic validation, UI, pytest suite, Dockerfile, GitHub Actions CI, deployment and drift check, slides"),
]
SECTION = "&lt;Section&gt;"
LIVE_URL = "&lt;live URL&gt;"
REPO_URL = "&lt;GitHub repository URL&gt;"


def img(rel, width="100%"):
    data = base64.b64encode((ROOT / rel).read_bytes()).decode()
    return f'<img src="data:image/png;base64,{data}" style="width:{width}">'


meta = json.loads((ROOT / "model" / "model_meta.json").read_text())
m = meta["metrics"]

ARCH = """
<svg viewBox="0 0 800 250" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica, Arial, sans-serif" font-size="12">
  <defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#475569"/></marker></defs>
  <g fill="#eef2fb" stroke="#2b59c3" stroke-width="1.4">
    <rect x="10" y="20" width="110" height="56" rx="8"/><rect x="160" y="20" width="120" height="56" rx="8"/>
    <rect x="320" y="20" width="120" height="56" rx="8"/><rect x="480" y="20" width="120" height="56" rx="8"/>
    <rect x="630" y="20" width="120" height="56" rx="8"/>
    <rect x="630" y="160" width="120" height="56" rx="8"/><rect x="480" y="160" width="120" height="56" rx="8"/>
    <rect x="320" y="160" width="120" height="56" rx="8"/><rect x="160" y="160" width="120" height="56" rx="8"/>
  </g>
  <g text-anchor="middle" fill="#14171f">
    <text x="65" y="44" font-weight="bold">Data</text><text x="65" y="62">fraud_oracle.csv</text>
    <text x="220" y="44" font-weight="bold">Preprocessing</text><text x="220" y="62">features.py</text>
    <text x="380" y="44" font-weight="bold">Training</text><text x="380" y="62">train.py (3 algos)</text>
    <text x="540" y="44" font-weight="bold">MLflow</text><text x="540" y="62">SQLite: mlflow.db</text>
    <text x="690" y="44" font-weight="bold">Best model</text><text x="690" y="62">model.joblib</text>
    <text x="690" y="184" font-weight="bold">FastAPI app</text><text x="690" y="202">/predict /health / UI</text>
    <text x="540" y="184" font-weight="bold">Docker image</text><text x="540" y="202">python:3.11-slim</text>
    <text x="380" y="184" font-weight="bold">GitHub Actions</text><text x="380" y="202">train + pytest + build</text>
    <text x="220" y="184" font-weight="bold">Cloud host</text><text x="220" y="202">Render, restart policy</text>
  </g>
  <g stroke="#475569" stroke-width="1.4" marker-end="url(#a)" fill="none">
    <path d="M120,48 H158"/><path d="M280,48 H318"/><path d="M440,48 H478"/><path d="M600,48 H628"/>
    <path d="M690,76 V158"/><path d="M630,188 H602"/><path d="M480,188 H442"/><path d="M320,188 H282"/>
  </g>
  <g fill="#475569" font-size="11" text-anchor="middle">
    <text x="704" y="122" text-anchor="start">loaded once</text><text x="704" y="136" text-anchor="start">at startup</text>
    <text x="220" y="240">users / investigators → predictions logged to logs/predictions.jsonl → drift_check.py</text>
  </g>
</svg>"""

runs = [
    ("1", "Logistic Regression", "C=1.0", .804, .151, .486, .163, .244),
    ("2", "Logistic Regression", "C=0.05", .804, .150, .530, .157, .242),
    ("3", "Random Forest", "n_estimators=100, max_depth=6", .823, .205, .751, .154, .255),
    ("4", "Random Forest", "n_estimators=300, max_depth=12, leaf=3", .820, .197, .562, .160, .249),
    ("5", "Random Forest", "n_estimators=500, leaf=5", .818, .201, .611, .156, .248),
    ("6", "HistGradientBoosting", "lr=0.1, iter=200, depth=4", .833, .241, .335, .218, .264),
    ("7", "HistGradientBoosting", "lr=0.05, iter=400, depth=6", .833, .246, .832, .145, .247),
]
run_rows = "\n".join(
    f"<tr{' class=best' if r[0]=='7' else ''}><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td>"
    + "".join(f"<td>{v:.3f}</td>" for v in r[3:]) + "</tr>" for r in runs)
team_rows = "\n".join(f"<tr><td>{n}</td><td>{r}</td><td>{c}</td></tr>" for n, r, c in TEAM)

html = f"""<!doctype html><html><head><meta charset="utf-8"><title>ClaimGuard Report</title>
<style>
@page {{ size: A4; margin: 18mm 17mm 18mm 17mm; }}
body {{ font: 10.5pt/1.5 "Helvetica Neue", Helvetica, Arial, sans-serif; color: #1a1d24; }}
h1 {{ font-size: 26pt; margin: 0 0 6px; color: #1b3f91; }}
h2 {{ font-size: 15pt; color: #1b3f91; border-bottom: 2px solid #dbe3f5; padding-bottom: 3px; margin: 22px 0 8px; page-break-after: avoid; }}
h3 {{ font-size: 11.5pt; margin: 14px 0 4px; page-break-after: avoid; }}
p {{ margin: 6px 0; text-align: justify; }}
table {{ border-collapse: collapse; width: 100%; font-size: 9pt; margin: 8px 0; page-break-inside: avoid; }}
th, td {{ border: 1px solid #cfd6e4; padding: 4px 6px; text-align: left; vertical-align: top; }}
th {{ background: #eef2fb; }}
tr.best td {{ background: #e7f6ee; font-weight: bold; }}
.title {{ height: 250mm; display: flex; flex-direction: column; justify-content: center; page-break-after: always; }}
.title .sub {{ font-size: 13pt; color: #475569; margin-bottom: 30px; }}
.fig {{ text-align: center; margin: 10px 0; page-break-inside: avoid; }}
.fig .cap {{ font-size: 8.5pt; color: #5b6270; margin-top: 2px; }}
.two {{ display: flex; gap: 10px; }} .two > div {{ flex: 1; }}
code {{ font-size: 9pt; background: #f1f3f7; padding: 0 3px; border-radius: 3px; }}
.pb {{ page-break-before: always; }}
ul {{ margin: 4px 0 6px 0; padding-left: 20px; }} li {{ margin: 2px 0; }}
</style></head><body>

<div class="title">
  <h1>ClaimGuard</h1>
  <div class="sub">Vehicle Insurance Claim Fraud Detection: an end-to-end ML system<br>
  CSL236 Introduction to AI &amp; Machine Learning · End-Term Project Report</div>
  <table style="width:75%">
    <tr><th>Course</th><td>CSL236, B.Tech CSE, Semester 5, The NorthCap University</td></tr>
    <tr><th>Section</th><td>{SECTION}</td></tr>
    {''.join(f'<tr><th>Team member</th><td>{n} · {r}</td></tr>' for n, r, _ in TEAM)}
    <tr><th>GitHub repository</th><td>{REPO_URL}</td></tr>
    <tr><th>Live deployment</th><td>{LIVE_URL}</td></tr>
  </table>
</div>

<h2>1. Problem and dataset</h2>
<p><b>Problem.</b> Insurance fraud, such as staged accidents, claims for damage that happened before the policy started, or inflated repair bills, is a large hidden cost for insurers and their honest customers. Investigators cannot examine every claim, so they need a way to decide <i>which claims to look at first</i>. ClaimGuard is a binary classifier that estimates the probability that a vehicle-insurance claim is fraudulent, plus a web service that shows that score with concrete checks for the investigator. It is a triage tool: the model ranks, and a human decides.</p>
<p><b>Dataset.</b> We use the public <i>Vehicle Insurance Claim Fraud Detection</i> dataset (<code>fraud_oracle.csv</code>, Oracle sample data, published on Kaggle by Shivam Bansal). It has 15,420 claims × 33 columns describing the policy holder (age, sex, marital status, driver rating, past claims, address change), the policy (base policy, deductible, agent type, days from policy start to accident), the vehicle (make, category, price band, age) and the accident (fault, area, police report, witness, dates). The label <code>FraudFound_P</code> is 1 for 923 claims (<b>6.0%</b>).</p>

<h3>Data cleaning</h3>
<ul>
<li><b>Hidden missing values:</b> <code>Age = 0</code> in 320 rows (all in the youngest age band) is impossible. We set it to missing, then impute it with the training median plus an indicator flag.</li>
<li><b>One row with no claim date</b> (<code>DayOfWeekClaimed = '0'</code>) was dropped. The copy we downloaded also had 3 extra columns that are not in the original data; we dropped them.</li>
<li><b>Category cleaning:</b> misspelt makes (Accura, Nisson, Mecedes, Porche) were corrected, and makes with fewer than 0.5% of rows were grouped as "Other".</li>
<li><b>Feature engineering:</b> <code>claim_delay_weeks</code>, the weeks between accident and claim, was built from six calendar columns.</li>
<li><b>Feature selection:</b> we removed ID-like columns (<code>PolicyNumber</code>, <code>RepNumber</code>), redundant ones (<code>PolicyType</code> = vehicle category + base policy; <code>AgeOfPolicyHolder</code> = banded <code>Age</code>), a near-constant one (<code>Days_Policy_Claim</code>, 99.5% one value) and <code>Year</code>, which cannot generalise to future claims. That leaves <b>21 input features</b>: 4 numeric, 6 binary, 7 ordinal and 4 nominal.</li>
</ul>

<h3>EDA highlights</h3>
<div class="two">
  <div class="fig">{img("docs/figures/class_balance.png")}<div class="cap">Figure 1. Class balance: 6% fraud.</div></div>
  <div class="fig">{img("docs/figures/age_and_delay.png")}<div class="cap">Figure 2. Age by class; fraud rate by claim delay.</div></div>
</div>
<div class="fig">{img("docs/figures/fraud_rate_by_category.png", "95%")}<div class="cap">Figure 3. Fraud rate by fault, base policy and days from policy start to accident (dashed line: overall 6%).</div></div>
<ul>
<li><b>Severe imbalance (6%):</b> accuracy is misleading, since "always genuine" scores 94%. We evaluate with ROC-AUC, PR-AUC, recall and F1, use class weights, and tune the decision threshold.</li>
<li><b>Fault and policy type dominate:</b> fraud is about 8% when the holder is at fault but about 1% for third-party fault. On liability-only policies, which never pay for the holder's own car, fraud almost disappears (0.7%).</li>
<li><b>Timing:</b> claims for accidents within days of a policy starting, and claims reported a week or more late, are riskier. A recent address change is also a red flag.</li>
</ul>

<h2>2. Data contract and preprocessing</h2>
<p>The data contract is defined once in <code>features.py</code> and enforced by the Pydantic schema in <code>app.py</code>. For example, <code>age</code> is an int in 16–80, <code>driver_rating</code> 1–4, <code>deductible</code> 300–700 and <code>claim_delay_weeks</code> 0–52. Categorical fields accept only the listed values, typed as <code>Literal[...]</code>. Integers are strict, so <code>"45"</code>, <code>45.5</code>, <code>null</code> and NaN are rejected, as are missing and unknown extra fields. Every violation returns HTTP 422. The full table is in the README.</p>
<p>Preprocessing is a scikit-learn <code>ColumnTransformer</code> inside the model <code>Pipeline</code>, so it is fitted only on training data, and the identical steps run in the API:</p>
<table>
<tr><th>Step</th><th>Columns</th><th>Technique</th><th>Reason</th></tr>
<tr><td>Missing values</td><td>age</td><td>Median imputation + missing-indicator</td><td>Robust to skew; the flag keeps the "unknown" signal</td></tr>
<tr><td>Binary encoding</td><td>sex, fault, accident_area, police_report_filed, witness_present, agent_type</td><td>0/1 with a fixed order</td><td>Two values need only one column</td></tr>
<tr><td>Ordinal encoding</td><td>vehicle_price, age_of_vehicle, past_number_of_claims, number_of_supplements, address_change_claim, number_of_cars, days_policy_accident</td><td>Integers in an explicitly stated order</td><td>The ranges have a natural order</td></tr>
<tr><td>One-hot encoding</td><td>marital_status, base_policy, vehicle_category, make</td><td>OneHotEncoder(handle_unknown="ignore")</td><td>No order between categories</td></tr>
<tr><td>Scaling</td><td>numeric + ordinal (logistic regression only)</td><td>StandardScaler</td><td>Gradient descent with an L2 penalty needs comparable scales; trees do not</td></tr>
<tr><td>Outliers</td><td>age, claim_delay_weeks, deductible</td><td>IQR check, all kept</td><td>Values are genuine (older drivers, late reports, real deductible options)</td></tr>
<tr><td>Binning</td><td>age</td><td>Tested, not used</td><td>CV ROC-AUC was 0.8125 continuous vs 0.8117 binned; trees learn their own cut points</td></tr>
</table>

<h2 class="pb">3. System architecture</h2>
<div class="fig">{ARCH}<div class="cap">Figure 4. Data → preprocessing → training → MLflow → model → FastAPI → Docker → CI → cloud.</div></div>
<table>
<tr><th>Layer</th><th>Tool</th><th>What it does</th></tr>
<tr><td>Environment</td><td>venv, pinned <code>requirements.txt</code></td><td>Reproducible Python 3.11 environment; <code>venv/</code> and <code>mlruns/</code> are git-ignored</td></tr>
<tr><td>Experiment tracking</td><td>MLflow 2.17 (SQLite <code>mlflow.db</code>)</td><td>Logs every run's hyperparameters (CLI arguments), metrics and fitted pipeline</td></tr>
<tr><td>Serialization</td><td>joblib</td><td>Best pipeline saved to <code>model/model.joblib</code> (about 1 MB) with <code>model_meta.json</code> (threshold, metrics)</td></tr>
<tr><td>Serving</td><td>FastAPI + Pydantic + Uvicorn</td><td><code>GET /health</code>, <code>POST /predict</code>, UI at <code>/</code>, Swagger at <code>/docs</code>. The model is loaded once at startup</td></tr>
<tr><td>Testing</td><td>pytest + TestClient</td><td>18 tests: health, UI, domain logic, 422 boundaries, tips, logging</td></tr>
<tr><td>Container</td><td>Docker, <code>python:3.11-slim</code></td><td>Serve-only dependencies, non-root user, health check</td></tr>
<tr><td>CI</td><td>GitHub Actions</td><td>On every push: install, train a baseline, run pytest, build and smoke-test the image</td></tr>
<tr><td>Deployment</td><td>Render free tier (Docker)</td><td>Public URL, automatic restart; predictions logged for drift checks</td></tr>
</table>

<h2>4. Experiments and model comparison</h2>
<p><code>train.py</code> takes the algorithm and hyperparameters as command-line arguments. It uses a stratified 80/20 split with a fixed seed. For each run, the decision threshold is tuned for maximum F1 on a validation slice (25%) of the <i>training</i> data. The model is then refitted on the full training set and scored once on the test set. We ran <b>7 configurations of 3 algorithms</b>:</p>
<table>
<tr><th>Run</th><th>Algorithm</th><th>Hyperparameters</th><th>ROC-AUC</th><th>PR-AUC</th><th>Recall</th><th>Precision</th><th>F1</th></tr>
{run_rows}
</table>
<div class="fig">{img("docs/screenshots/mlflow_runs.png", "88%")}<div class="cap">Figure 5. MLflow UI showing the 7 tracked runs.</div></div>
<div class="two">
  <div class="fig">{img("docs/figures/roc_curves.png")}<div class="cap">Figure 6. Test ROC curves (notebook models).</div></div>
  <div class="fig">{img("docs/figures/permutation_importance.png")}<div class="cap">Figure 7. Permutation importance of the chosen model.</div></div>
</div>
<h3>Model choice: HistGradientBoosting (run 7)</h3>
<ul>
<li><b>Best PR-AUC ({m['pr_auc']:.3f})</b>, about 4× the 0.06 a random ranking would get, and the best ROC-AUC ({m['roc_auc']:.3f}). For a rare positive class, PR-AUC is the most honest summary of ranking quality.</li>
<li><b>Highest recall ({m['recall']:.0%})</b> at the tuned threshold ({meta['threshold']:.2f}). In triage, a missed fraud costs far more than sending an extra genuine claim to an investigator. Run 6 has a slightly higher F1 but catches only 34% of frauds.</li>
<li><b>It captures interactions</b> such as "holder at fault <i>and</i> policy covers own car", which logistic regression cannot represent without hand-made features. Random forest came second.</li>
<li><b>Small and fast:</b> about 1 MB on disk, with millisecond predictions.</li>
</ul>
<p>The confusion matrix (test set, tuned threshold) is in the notebook. Precision is about 15%: roughly one flagged claim in seven is fraud, against one in seventeen at random. For an investigation queue this is a useful 2.4× lift, but it confirms the model should not reject claims automatically.</p>

<h2 class="pb">5. Testing, CI and deployment</h2>
<h3>Automated tests (18, all passing)</h3>
<ul>
<li><b>Health:</b> <code>/health</code> returns 200 and <code>model_loaded: true</code>. <b>UI:</b> <code>/</code> serves the HTML page.</li>
<li><b>Domain logic:</b> a claim with red flags (accident in the first week of an all-perils policy, address changed under 6 months ago, holder at fault, no police report or witness, reported 6 weeks late) must score higher than a routine third-party, liability-only claim. Changing <i>only</i> <code>fault</code> to "Policy Holder" must raise the risk.</li>
<li><b>Boundary (422):</b> age 15 and 81, driver rating 5, negative delay, deductible 1000, <code>"45"</code>, <code>45.5</code>, <code>null</code>, unknown fault, unknown price band, unknown make, missing field, extra field.</li>
<li><b>Tips:</b> every response carries 2–3 rule-based tips. <b>Logging:</b> each prediction adds one line to the log.</li>
</ul>
<div class="fig">{img("docs/screenshots/pytest.png", "80%")}<div class="cap">Figure 8. pytest -v output.</div></div>
<h3>Continuous integration</h3>
<p><code>.github/workflows/ci.yml</code> runs on every push to <code>main</code>. Job 1 sets up Python 3.11, installs <code>requirements.txt</code>, trains a baseline random forest (<code>--n_estimators 100 --max_depth 6</code>) into a throwaway MLflow database, and runs <code>pytest -v</code>. Job 2 builds the Docker image, starts it, checks <code>/health</code> and <code>/</code>, asserts that invalid input returns 422, and prints the image size. <i>[Insert screenshot of the green check.]</i></p>
<h3>Docker</h3>
<p>The image uses <code>python:3.11-slim</code> and installs only <code>requirements-serve.txt</code> (FastAPI, Uvicorn, Pydantic, scikit-learn, pandas, NumPy, joblib). MLflow, pytest, matplotlib and Jupyter stay out, so the image is smaller, builds faster and has less attack surface. That is the reason for having two requirements files. Size: about 695 MB on disk (about 140 MB compressed). It runs as a non-root user, has a <code>HEALTHCHECK</code>, and honours <code>$PORT</code>.</p>
<h3>Deployment and monitoring</h3>
<p>The container is deployed on Render's free tier from the GitHub repository, with automatic restarts. Every <code>/predict</code> request is logged as JSON (timestamp, input, probability, label) to <code>logs/predictions.jsonl</code>; a sample is in <code>docs/sample_predictions.jsonl</code>. <code>drift_check.py</code> (bonus) compares the logged inputs with the training data. It flags a numeric feature whose mean moves more than 0.5 training standard deviations, or a category whose share moves more than 15 percentage points, and exits with code 1 so it can trigger retraining.</p>
<div class="two">
  <div class="fig">{img("docs/screenshots/ui_prediction.png")}<div class="cap">Figure 9. UI: a suspicious claim with tips.</div></div>
  <div class="fig">{img("docs/screenshots/ui_422.png")}<div class="cap">Figure 10. Invalid input rejected with HTTP 422.</div></div>
</div>

<h2>6. Limitations and next steps</h2>
<ul>
<li><b>Old, narrow data:</b> US claims from 1994–1996. Prices, cars and fraud tactics have changed, so the model needs retraining on current, local data before real use.</li>
<li><b>Few positives and coarse inputs:</b> only 923 frauds, and many fields are pre-bucketed ranges. This caps precision at about 15%. More data, exact values (amounts, dates, repair-shop IDs) and network features (shared phone numbers or garages) would help most.</li>
<li><b>Fairness:</b> <code>sex</code> and <code>marital_status</code> are protected attributes. A production system should test for disparate impact and probably drop them.</li>
<li><b>Monitoring:</b> the drift check is manual today. Next steps: run it on a schedule, add continuous deployment after CI passes, add SHAP explanations per prediction, and record investigators' outcomes as fresh labels for retraining.</li>
</ul>

<h2>7. Individual contributions</h2>
<table><tr><th>Name</th><th>Roll number</th><th>Contribution</th></tr>{team_rows}</table>
<p style="font-size:9pt;color:#5b6270">References: Vehicle Insurance Claim Fraud Detection dataset, https://www.kaggle.com/datasets/shivamb/vehicle-claim-fraud-detection · scikit-learn, FastAPI, MLflow documentation · CSL236 workshop reference project (PlacementChancePredictor / mlops-starter). An AI assistant (Claude) was used for coding help; the team reviewed and can explain all code.</p>
</body></html>"""
OUT.write_text(html)
print("wrote", OUT)
