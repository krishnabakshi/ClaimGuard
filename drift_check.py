"""Bonus: simple input-drift check.

Compares the inputs logged by the API (logs/predictions.jsonl) with the training data:
  * numeric features: mean and standard deviation, flagged when the live mean moves more
    than THRESHOLD training standard deviations (standardised mean difference);
  * categorical features: share of each category, flagged when any share moves by more
    than 15 percentage points.

    python drift_check.py
    python drift_check.py --log docs/sample_predictions.jsonl

Exit code 1 if anything drifted, so a scheduled job could trigger retraining.
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from features import BINARY, FEATURES, NOMINAL, NUMERIC, ORDINAL, load_clean

ROOT = Path(__file__).resolve().parent


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--log", default=ROOT / "logs" / "predictions.jsonl", type=Path)
    p.add_argument("--threshold", default=0.5, type=float)
    p.add_argument("--share_pp", default=15.0, type=float)
    args = p.parse_args()
    if not args.log.exists():
        print(f"No log at {args.log}. Make some predictions first.")
        return 0

    live = pd.DataFrame([json.loads(l)["input"] for l in args.log.read_text().splitlines() if l.strip()], columns=FEATURES)
    train = load_clean(ROOT / "data" / "fraud_oracle.csv")[FEATURES]
    print(f"Live predictions: {len(live)}   Training rows: {len(train)}\n")

    num = pd.DataFrame({"train_mean": train[list(NUMERIC)].mean(), "train_std": train[list(NUMERIC)].std(),
                        "live_mean": live[list(NUMERIC)].mean(), "live_std": live[list(NUMERIC)].std()})
    num["std_mean_diff"] = (num.live_mean - num.train_mean).abs() / num.train_std
    num["drift"] = num.std_mean_diff > args.threshold
    print("Numeric features\n", num.round(3).to_string(), "\n")

    drifted = num.index[num.drift].tolist()
    rows = []
    for col in list(BINARY) + list(ORDINAL) + list(NOMINAL):
        t = train[col].value_counts(normalize=True) * 100
        l = live[col].value_counts(normalize=True) * 100
        diff = (l.reindex(t.index.union(l.index), fill_value=0) - t.reindex(t.index.union(l.index), fill_value=0)).abs()
        rows.append({"feature": col, "max_share_change_pp": round(diff.max(), 1), "category": diff.idxmax(),
                     "drift": diff.max() > args.share_pp})
    cat = pd.DataFrame(rows).set_index("feature")
    print("Categorical features\n", cat.to_string())
    drifted += cat.index[cat.drift].tolist()

    if len(live) < 30:
        print(f"\nOnly {len(live)} logged inputs; treat the result as indicative.")
    if drifted:
        print(f"\nDRIFT in {len(drifted)} feature(s): {', '.join(drifted)}. Consider retraining.")
        return 1
    print("\nNo drift detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
