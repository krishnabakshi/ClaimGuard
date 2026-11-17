"""Shared data definitions for the notebook, train.py, app.py and the tests.

Dataset: Vehicle Insurance Claim Fraud Detection (Oracle sample data, published on
Kaggle by Shivam Bansal as `fraud_oracle.csv`). 15,420 claims, 923 fraudulent (6%).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

TARGET = "fraud"

# ---------------------------------------------------------------------------
# Allowed values. These ARE the data contract: app.py builds its Pydantic
# schema from them, so the README table, the API and the model always agree.
# ---------------------------------------------------------------------------
# Ordinal columns, values listed from lowest to highest (the order is the encoding).
ORDINAL: dict[str, list] = {
    "vehicle_price": ["less than 20000", "20000 to 29000", "30000 to 39000",
                      "40000 to 59000", "60000 to 69000", "more than 69000"],
    "age_of_vehicle": ["new", "2 years", "3 years", "4 years", "5 years", "6 years", "7 years", "more than 7"],
    "past_number_of_claims": ["none", "1", "2 to 4", "more than 4"],
    "number_of_supplements": ["none", "1 to 2", "3 to 5", "more than 5"],
    "address_change_claim": ["no change", "under 6 months", "1 year", "2 to 3 years", "4 to 8 years"],
    "number_of_cars": ["1 vehicle", "2 vehicles", "3 to 4", "5 to 8", "more than 8"],
    "days_policy_accident": ["none", "1 to 7", "8 to 15", "15 to 30", "more than 30"],
}
# Binary columns: first value -> 0, second -> 1.
BINARY: dict[str, list[str]] = {
    "sex": ["Female", "Male"],
    "fault": ["Third Party", "Policy Holder"],
    "accident_area": ["Rural", "Urban"],
    "police_report_filed": ["No", "Yes"],
    "witness_present": ["No", "Yes"],
    "agent_type": ["External", "Internal"],
}
# Nominal columns: no order, one-hot encoded.
NOMINAL: dict[str, list[str]] = {
    "marital_status": ["Single", "Married", "Divorced", "Widow"],
    "base_policy": ["Liability", "Collision", "All Perils"],
    "vehicle_category": ["Sedan", "Sport", "Utility"],
    "make": ["Pontiac", "Toyota", "Honda", "Mazda", "Chevrolet", "Acura", "Ford", "VW",
             "Dodge", "Saab", "Mercury", "Saturn", "Other"],
}
# Numeric columns: (min, max).
NUMERIC: dict[str, tuple[int, int]] = {
    "age": (16, 80),
    "deductible": (300, 700),
    "driver_rating": (1, 4),
    "claim_delay_weeks": (0, 52),
}
FEATURES: list[str] = list(NUMERIC) + list(BINARY) + list(ORDINAL) + list(NOMINAL)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MAKE_TYPOS = {"Accura": "Acura", "Nisson": "Nissan", "Mecedes": "Mercedes", "Porche": "Porsche"}


def load_clean(path) -> pd.DataFrame:
    """Stateless cleaning of the raw CSV (nothing is learned from the data, so it
    is safe before the train/test split). Returns FEATURES + TARGET."""
    raw = pd.read_csv(path, encoding="utf-8-sig")
    df = raw.iloc[:, :33].copy()               # columns 34-36 are not in the original dataset
    df = df[(df.DayOfWeekClaimed != "0") & (df.MonthClaimed != "0")]   # 1 row with no claim date

    out = pd.DataFrame(index=df.index)
    out["age"] = df["Age"].replace(0, np.nan)  # age 0 is impossible -> missing (imputed in the pipeline)
    out["deductible"] = df["Deductible"]
    out["driver_rating"] = df["DriverRating"]
    # Weeks between accident and claim, from month + week-of-month (year wrap handled by % 12).
    months = (df["MonthClaimed"].map(MONTHS.index) - df["Month"].map(MONTHS.index)) % 12
    out["claim_delay_weeks"] = (months * 4 + (df["WeekOfMonthClaimed"] - df["WeekOfMonth"])).clip(0, 52)

    rename = {"sex": "Sex", "fault": "Fault", "accident_area": "AccidentArea",
              "police_report_filed": "PoliceReportFiled", "witness_present": "WitnessPresent",
              "agent_type": "AgentType", "vehicle_price": "VehiclePrice", "age_of_vehicle": "AgeOfVehicle",
              "past_number_of_claims": "PastNumberOfClaims", "number_of_supplements": "NumberOfSuppliments",
              "address_change_claim": "AddressChange_Claim", "number_of_cars": "NumberOfCars",
              "days_policy_accident": "Days_Policy_Accident", "marital_status": "MaritalStatus",
              "base_policy": "BasePolicy", "vehicle_category": "VehicleCategory"}
    for new, old in rename.items():
        out[new] = df[old]
    make = df["Make"].replace(MAKE_TYPOS)
    out["make"] = make.where(make.isin(NOMINAL["make"]), "Other")   # rare makes (<0.5%) grouped
    out[TARGET] = df["FraudFound_P"]
    return out[FEATURES + [TARGET]]


def build_preprocessor(scale: bool) -> ColumnTransformer:
    """Fitted on the training data only, inside the model Pipeline."""
    numeric_steps = [("impute", SimpleImputer(strategy="median", add_indicator=True))]
    if scale:
        numeric_steps.append(("scale", StandardScaler()))
    ordinal_steps = [("encode", OrdinalEncoder(categories=[ORDINAL[c] for c in ORDINAL]))]
    if scale:
        ordinal_steps.append(("scale", StandardScaler()))
    return ColumnTransformer([
        ("num", Pipeline(numeric_steps), list(NUMERIC)),
        ("bin", OrdinalEncoder(categories=[BINARY[c] for c in BINARY]), list(BINARY)),
        ("ord", Pipeline(ordinal_steps), list(ORDINAL)),
        ("nom", OneHotEncoder(categories=[NOMINAL[c] for c in NOMINAL], handle_unknown="ignore"), list(NOMINAL)),
    ], verbose_feature_names_out=False)


__all__ = ["FEATURES", "TARGET", "ORDINAL", "BINARY", "NOMINAL", "NUMERIC", "load_clean", "build_preprocessor"]
