"""Train an insurance-claim fraud classifier and track the run in MLflow.

Examples
    python train.py --n_estimators 100 --max_depth 6                # random forest (default)
    python train.py --model logreg --C 0.1
    python train.py --model hgb --learning_rate 0.05 --max_iter 300

Each run logs hyperparameters, metrics and the fitted Pipeline to MLflow (SQLite
backend, ./mlflow.db). Only 6% of claims are fraud, so a 0.5 cut-off would flag
almost nothing: the decision threshold is tuned on a validation slice of the
training data (max F1) and saved with the model. model/model.joblib is replaced
only when the new run's test PR-AUC beats the saved model, or with --force.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, f1_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from features import FEATURES, TARGET, build_preprocessor, load_clean

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "fraud_oracle.csv"
MODEL_PATH = ROOT / "model" / "model.joblib"
META_PATH = ROOT / "model" / "model_meta.json"
SEED = 42


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", choices=["rf", "logreg", "hgb"], default="rf",
                   help="rf = RandomForest, logreg = LogisticRegression, hgb = HistGradientBoosting")
    p.add_argument("--n_estimators", type=int, default=100, help="rf: number of trees")
    p.add_argument("--max_depth", type=int, default=None, help="rf/hgb: max tree depth")
    p.add_argument("--min_samples_leaf", type=int, default=1, help="rf/hgb: min samples per leaf")
    p.add_argument("--C", type=float, default=1.0, help="logreg: inverse regularisation strength")
    p.add_argument("--learning_rate", type=float, default=0.1, help="hgb: learning rate")
    p.add_argument("--max_iter", type=int, default=200, help="hgb: boosting rounds")
    p.add_argument("--test_size", type=float, default=0.2)
    p.add_argument("--run_name", default=None)
    p.add_argument("--experiment", default="claimguard")
    p.add_argument("--tracking_uri", default=f"sqlite:///{ROOT / 'mlflow.db'}")
    p.add_argument("--force", action="store_true", help="save to model/model.joblib even if not the best")
    return p.parse_args()


def build_pipeline(args: argparse.Namespace) -> tuple[Pipeline, dict]:
    if args.model == "rf":
        params = {"n_estimators": args.n_estimators, "max_depth": args.max_depth,
                  "min_samples_leaf": args.min_samples_leaf}
        clf = RandomForestClassifier(**params, class_weight="balanced_subsample", n_jobs=-1, random_state=SEED)
        scale = False
    elif args.model == "logreg":
        params = {"C": args.C}
        clf = LogisticRegression(**params, class_weight="balanced", max_iter=5000, random_state=SEED)
        scale = True   # gradient-based + L2 penalty: features must be on the same scale
    else:
        params = {"learning_rate": args.learning_rate, "max_iter": args.max_iter,
                  "max_depth": args.max_depth, "min_samples_leaf": max(args.min_samples_leaf, 20)}
        clf = HistGradientBoostingClassifier(**params, class_weight="balanced", random_state=SEED)
        scale = False  # trees split on thresholds, scale doesn't matter
    return Pipeline([("prep", build_preprocessor(scale=scale)), ("clf", clf)]), params


def best_threshold(y_true, proba) -> float:
    prec, rec, thr = precision_recall_curve(y_true, proba)
    f1 = 2 * prec * rec / np.clip(prec + rec, 1e-9, None)
    return float(thr[np.argmax(f1[:-1])])


def evaluate(y_true, proba, threshold: float) -> dict[str, float]:
    pred = (proba >= threshold).astype(int)
    return {
        "roc_auc": roc_auc_score(y_true, proba),
        "pr_auc": average_precision_score(y_true, proba),
        "f1": f1_score(y_true, pred),
        "precision": precision_score(y_true, pred, zero_division=0),
        "recall": recall_score(y_true, pred),
        "accuracy": accuracy_score(y_true, pred),
    }


def main() -> None:
    args = parse_args()
    df = load_clean(DATA)
    X, y = df[FEATURES], df[TARGET].to_numpy()
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=args.test_size, stratify=y, random_state=SEED)

    pipe, params = build_pipeline(args)
    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experiment)
    run_name = args.run_name or f"{args.model}-" + "-".join(f"{k}{v}" for k, v in params.items())

    with mlflow.start_run(run_name=run_name) as run:
        # 1) Tune the decision threshold on a validation slice of the TRAINING data.
        X_fit, X_val, y_fit, y_val = train_test_split(X_tr, y_tr, test_size=0.25, stratify=y_tr, random_state=SEED)
        pipe.fit(X_fit, y_fit)
        threshold = best_threshold(y_val, pipe.predict_proba(X_val)[:, 1])
        # 2) Refit on all training data and score the untouched test set.
        t0 = time.time()
        pipe.fit(X_tr, y_tr)
        train_seconds = time.time() - t0
        metrics = evaluate(y_te, pipe.predict_proba(X_te)[:, 1], threshold)
        metrics["threshold"] = threshold
        metrics["train_seconds"] = train_seconds

        mlflow.log_params({"algorithm": args.model, **params, "test_size": args.test_size,
                           "n_features": len(FEATURES), "n_train": len(y_tr)})
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(pipe, artifact_path="model", input_example=X_tr.head(3))

        print(f"Run {run.info.run_id} ({run_name})")
        for k, v in metrics.items():
            print(f"  {k:<14} {v:.4f}")

    best = -1.0
    if META_PATH.exists():
        best = json.loads(META_PATH.read_text()).get("metrics", {}).get("pr_auc", -1.0)
    if args.force or metrics["pr_auc"] > best:
        MODEL_PATH.parent.mkdir(exist_ok=True)
        joblib.dump(pipe, MODEL_PATH, compress=3)
        META_PATH.write_text(json.dumps({
            "run_id": run.info.run_id, "run_name": run_name, "algorithm": args.model, "params": params,
            "threshold": threshold, "features": FEATURES, "metrics": metrics,
        }, indent=2, default=str))
        print(f"Saved model to {MODEL_PATH} (test PR-AUC {metrics['pr_auc']:.4f}, previous best {best:.4f})")
    else:
        print(f"Not saved: test PR-AUC {metrics['pr_auc']:.4f} does not beat saved model ({best:.4f}). Use --force.")


if __name__ == "__main__":
    main()
