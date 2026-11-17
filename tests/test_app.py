"""pytest suite for ClaimGuard. Run from the repo root:  pytest -v --tb=short"""

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import LOG_DIR, app  # noqa: E402

client = TestClient(app)

# A routine claim: third party at fault, liability-only policy, police report and witness.
ROUTINE = {
    "age": 45, "sex": "Female", "marital_status": "Married", "driver_rating": 1,
    "past_number_of_claims": "2 to 4", "address_change_claim": "no change", "number_of_cars": "1 vehicle",
    "base_policy": "Liability", "deductible": 400, "agent_type": "Internal", "vehicle_category": "Sport",
    "make": "Toyota", "vehicle_price": "20000 to 29000", "age_of_vehicle": "7 years",
    "fault": "Third Party", "accident_area": "Urban", "police_report_filed": "Yes", "witness_present": "Yes",
    "days_policy_accident": "more than 30", "claim_delay_weeks": 0, "number_of_supplements": "more than 5",
}
# Classic red flags: accident in the first week of an all-perils policy, recent address
# change, policy holder at fault, no police report or witness, reported 6 weeks late.
SUSPICIOUS = {
    **ROUTINE, "age": 24, "sex": "Male", "marital_status": "Single", "driver_rating": 2,
    "past_number_of_claims": "none", "address_change_claim": "under 6 months", "base_policy": "All Perils",
    "agent_type": "External", "vehicle_category": "Utility", "make": "Acura", "vehicle_price": "more than 69000",
    "age_of_vehicle": "new", "fault": "Policy Holder", "accident_area": "Rural", "police_report_filed": "No",
    "witness_present": "No", "days_policy_accident": "1 to 7", "claim_delay_weeks": 6,
    "number_of_supplements": "none",
}


# 1. Health check -----------------------------------------------------------
def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["model_loaded"] is True


# 2. UI loads ---------------------------------------------------------------
def test_ui_loads():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "ClaimGuard" in r.text


# 3. Domain logic -------------------------------------------------------------
def test_suspicious_claim_scores_higher_than_routine():
    routine = client.post("/predict", json=ROUTINE).json()
    suspicious = client.post("/predict", json=SUSPICIOUS).json()
    assert suspicious["fraud_probability"] > routine["fraud_probability"]
    assert routine["label"] == "routine"
    assert suspicious["label"] == "suspicious"


def test_policy_holder_at_fault_raises_risk():
    """Same claim, only fault changes: the policy holder being at fault must not lower the risk."""
    third = client.post("/predict", json=ROUTINE).json()["fraud_probability"]
    holder = client.post("/predict", json={**ROUTINE, "fault": "Policy Holder"}).json()["fraud_probability"]
    assert holder > third


# 4. Boundary tests: anything outside the data contract -> 422 -------------
@pytest.mark.parametrize("field,value", [
    ("age", 15),                         # below minimum 16
    ("age", 81),                         # above maximum 80
    ("driver_rating", 5),                # rating is 1-4
    ("claim_delay_weeks", -1),           # cannot be negative
    ("deductible", 1000),                # above 700
    ("age", "45"),                       # wrong type: string
    ("age", 45.5),                       # wrong type: float
    ("age", None),                       # null / missing value
    ("fault", "Nobody"),                 # not an allowed category
    ("vehicle_price", "cheap"),          # not an allowed ordinal level
    ("make", "Tesla"),                   # unknown make (use "Other")
])
def test_out_of_contract_input_returns_422(field, value):
    r = client.post("/predict", json={**ROUTINE, field: value})
    assert r.status_code == 422


def test_missing_and_extra_fields_return_422():
    missing = {k: v for k, v in ROUTINE.items() if k != "fault"}
    assert client.post("/predict", json=missing).status_code == 422
    assert client.post("/predict", json={**ROUTINE, "policy_number": 7}).status_code == 422


# 5. Tips and logging --------------------------------------------------------
def test_two_or_three_tips():
    for claim in (ROUTINE, SUSPICIOUS):
        tips = client.post("/predict", json=claim).json()["tips"]
        assert 2 <= len(tips) <= 3


def test_prediction_is_logged():
    log = LOG_DIR / "predictions.jsonl"
    before = log.read_text().count("\n") if log.exists() else 0
    client.post("/predict", json=ROUTINE)
    lines = log.read_text().strip().splitlines()
    assert len(lines) == before + 1
    assert json.loads(lines[-1])["input"] == ROUTINE
