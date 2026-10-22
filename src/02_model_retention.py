"""09-management-attrition — 02_model_retention.py

Interpretable attrition risk model + costed retention lever comparison.
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared.utils import mpl_setup, save_png, save_json   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
mpl_setup()

REPLACEMENT_COST = 45000.0   # $ stated replacement/per-employee cost
INTERVENTION_COST = 3000.0   # $ stated per-employee retention package
SAVE_RATE = 0.25             # stated save rate


def main() -> None:
    df = pd.read_csv(PROJECT / "data" / "processed" / "hr_clean.csv")
    drop = ["Attrition", "attrition"]  # target defined both ways
    y = df["attrition"]
    X = pd.get_dummies(df.drop(columns=drop + ["EmployeeNumber"]), drop_first=True).astype(float)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=.25, stratify=y, random_state=11)

    gb = GradientBoostingClassifier(random_state=11).fit(X_tr, y_tr)
    auc = roc_auc_score(y_te, gb.predict_proba(X_te)[:, 1])
    df["p_exit"] = gb.predict_proba(X)[:, 1]
    df.to_csv(PROJECT / "outputs" / "employee_risk.csv", index=False)

    lr = LogisticRegression(max_iter=3000).fit(X_tr, y_tr)
    coefs = pd.Series(lr.coef_[0], index=X.columns).sort_values(ascending=False)
    top = {k: round(float(v), 3) for k, v in coefs.head(10).items()}

    hi = df[df.p_exit >= .5]
    n = len(hi)
    saved_rev = n * REPLACEMENT_COST * SAVE_RATE
    cost = n * INTERVENTION_COST
    out = {
        "auc_test": round(float(auc), 4),
        "n_high_risk": int(n),
        "n_annual_exit_expected": int(round(df.p_exit.sum())),
        "program_cost": round(float(cost), 0),
        "expected_savings": round(float(saved_rev), 0),
        "net_uplift": round(float(saved_rev - cost), 0),
        "top_drivers": top,
        "assumptions": {"replacement_cost": REPLACEMENT_COST, "intervention_cost": INTERVENTION_COST,
                        "save_rate": SAVE_RATE},
    }
    save_json(out, PROJECT / "outputs" / "model.json")

    imp = pd.Series(gb.feature_importances_, index=X.columns).sort_values(ascending=False).head(12)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.barh(imp.index[::-1], imp.values[::-1], color="#134e5e")
    ax.set_xlabel("GBDT importance")
    ax.set_title("Attrition drivers — overtime & comp dominate")
    save_png(fig, PROJECT / "outputs" / "charts" / "drivers.png")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
