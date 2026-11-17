"""ClaimGuard: FastAPI service that scores a vehicle-insurance claim for fraud risk.

Routes
    GET  /          simple UI (static/index.html)
    GET  /health    liveness check + model info
    POST /predict   score one claim (every data-contract rule enforced -> HTTP 422)
    GET  /docs      Swagger UI (built into FastAPI)
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field, StrictInt

from features import FEATURES

ROOT = Path(__file__).resolve().parent
MODEL_PATH = Path(os.getenv("MODEL_PATH", ROOT / "model" / "model.joblib"))
META_PATH = MODEL_PATH.with_name("model_meta.json")
LOG_DIR = Path(os.getenv("LOG_DIR", ROOT / "logs"))

# ---------------------------------------------------------------------------
# Load the model ONCE at startup, never inside a request handler.
# ---------------------------------------------------------------------------
MODEL = joblib.load(MODEL_PATH)
MODEL_META = json.loads(META_PATH.read_text()) if META_PATH.exists() else {}
# Fraud is rare (6%), so the cut-off was tuned on validation data in train.py.
THRESHOLD = float(MODEL_META.get("threshold", 0.5))

# Every prediction input is appended to a JSON-lines file for drift checks.
LOG_DIR.mkdir(parents=True, exist_ok=True)
pred_logger = logging.getLogger("predictions")
pred_logger.setLevel(logging.INFO)
pred_logger.propagate = False
if not pred_logger.handlers:
    _h = RotatingFileHandler(LOG_DIR / "predictions.jsonl", maxBytes=5_000_000, backupCount=3)
    _h.setFormatter(logging.Formatter("%(message)s"))
    pred_logger.addHandler(_h)


# ---------------------------------------------------------------------------
# Data contract: one field per README table row. Literal = only the listed
# values are accepted; StrictInt = "35", 35.5, null or NaN are rejected. Any
# violation, a missing field or an unknown extra field returns HTTP 422.
# ---------------------------------------------------------------------------
class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={"example": {
        "age": 24, "deductible": 400, "driver_rating": 2, "claim_delay_weeks": 3,
        "sex": "Male", "fault": "Policy Holder", "accident_area": "Urban",
        "police_report_filed": "No", "witness_present": "No", "agent_type": "External",
        "vehicle_price": "more than 69000", "age_of_vehicle": "new", "past_number_of_claims": "none",
        "number_of_supplements": "none", "address_change_claim": "under 6 months",
        "number_of_cars": "1 vehicle", "days_policy_accident": "1 to 7",
        "marital_status": "Single", "base_policy": "All Perils", "vehicle_category": "Sedan", "make": "Acura",
    }})

    # numeric
    age: StrictInt = Field(..., ge=16, le=80, description="Age of the policy holder in years")
    deductible: StrictInt = Field(..., ge=300, le=700, description="Policy deductible in USD")
    driver_rating: StrictInt = Field(..., ge=1, le=4, description="Insurer's driver rating, 1 (best) to 4")
    claim_delay_weeks: StrictInt = Field(..., ge=0, le=52, description="Weeks between accident and claim")
    # binary
    sex: Literal["Female", "Male"]
    fault: Literal["Third Party", "Policy Holder"]
    accident_area: Literal["Rural", "Urban"]
    police_report_filed: Literal["No", "Yes"]
    witness_present: Literal["No", "Yes"]
    agent_type: Literal["External", "Internal"]
    # ordinal
    vehicle_price: Literal["less than 20000", "20000 to 29000", "30000 to 39000",
                           "40000 to 59000", "60000 to 69000", "more than 69000"]
    age_of_vehicle: Literal["new", "2 years", "3 years", "4 years", "5 years", "6 years", "7 years", "more than 7"]
    past_number_of_claims: Literal["none", "1", "2 to 4", "more than 4"]
    number_of_supplements: Literal["none", "1 to 2", "3 to 5", "more than 5"]
    address_change_claim: Literal["no change", "under 6 months", "1 year", "2 to 3 years", "4 to 8 years"]
    number_of_cars: Literal["1 vehicle", "2 vehicles", "3 to 4", "5 to 8", "more than 8"]
    days_policy_accident: Literal["none", "1 to 7", "8 to 15", "15 to 30", "more than 30"]
    # nominal
    marital_status: Literal["Single", "Married", "Divorced", "Widow"]
    base_policy: Literal["Liability", "Collision", "All Perils"]
    vehicle_category: Literal["Sedan", "Sport", "Utility"]
    make: Literal["Pontiac", "Toyota", "Honda", "Mazda", "Chevrolet", "Acura", "Ford", "VW",
                  "Dodge", "Saab", "Mercury", "Saturn", "Other"]


class Prediction(BaseModel):
    label: Literal["suspicious", "routine"]
    fraud_probability: float
    threshold: float
    risk_level: Literal["low", "medium", "high"]
    tips: list[str]


# ---------------------------------------------------------------------------
# Rule-based tips for the claims investigator, shown under the score.
# ---------------------------------------------------------------------------
def build_tips(c: Claim, flagged: bool) -> list[str]:
    tips: list[str] = []
    if c.days_policy_accident in ("none", "1 to 7", "8 to 15"):
        tips.append("The accident happened within days of the policy starting. Check when the "
                    "damage really occurred, for example with repair-shop records or dated photos.")
    if c.address_change_claim in ("under 6 months", "1 year"):
        tips.append("The address changed shortly before the claim. Verify the new address and that "
                    "the vehicle was garaged there.")
    if c.police_report_filed == "No" and c.witness_present == "No":
        tips.append("No police report and no witness. Ask for a police report or other independent "
                    "evidence of the accident.")
    if c.fault == "Policy Holder" and c.base_policy != "Liability":
        tips.append("Policy holder at fault on a policy that pays for their own car. Get an independent "
                    "damage assessment before approving the repair cost.")
    if c.claim_delay_weeks >= 4:
        tips.append(f"Reported {c.claim_delay_weeks} weeks after the accident. Ask why it was reported late.")
    if c.past_number_of_claims == "none" and c.age < 26:
        tips.append("Young driver with no claim history. Confirm their identity and policy details.")

    if flagged:
        generic = ["Route this claim to the special investigations team before paying.",
                   "Cross-check the vehicle and policy number against previous claims in your system."]
    else:
        generic = ["Looks routine. Follow standard processing.",
                   "Still verify the repair invoice against the assessor's estimate."]
    for g in generic:
        if len(tips) >= 2:
            break
        tips.append(g)
    return tips[:3]


def risk_level(p: float) -> str:
    if p >= max(THRESHOLD, 0.8):
        return "high"
    return "medium" if p >= THRESHOLD else "low"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ClaimGuard API",
    description="Scores a vehicle-insurance claim for fraud risk. CSL236 end-term project.",
    version="1.0.0",
)


@app.get("/", include_in_schema=False)
def ui() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health")
def health() -> dict:
    m = MODEL_META.get("metrics", {})
    return {"status": "ok", "model_loaded": MODEL is not None, "algorithm": MODEL_META.get("algorithm"),
            "run_id": MODEL_META.get("run_id"), "threshold": round(THRESHOLD, 4),
            "test_roc_auc": round(m.get("roc_auc", 0.0), 4)}


@app.post("/predict", response_model=Prediction)
def predict(claim: Claim) -> Prediction:
    row = pd.DataFrame([claim.model_dump()], columns=FEATURES)
    proba = float(MODEL.predict_proba(row)[0, 1])
    flagged = proba >= THRESHOLD
    pred = Prediction(label="suspicious" if flagged else "routine", fraud_probability=round(proba, 4),
                      threshold=round(THRESHOLD, 4), risk_level=risk_level(proba), tips=build_tips(claim, flagged))
    pred_logger.info(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "input": claim.model_dump(),
                                 "probability": pred.fraud_probability, "label": pred.label}))
    return pred
