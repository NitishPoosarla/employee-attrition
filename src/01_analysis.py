"""09-management-attrition — 01_analysis.py

People-analytics / management readout: where attrition concentrates and which
management-lever matters most (overtime, tenure, level, income).

Outputs: processed data, kpis.json, segments, charts.
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared.utils import mpl_setup, save_png, save_json   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "outputs"
mpl_setup()


def main() -> None:
    (PROJECT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(PROJECT / "data" / "raw" / "hr_attrition.csv")
    df["attrition"] = (df.Attrition == "Yes").astype(int)
    df.to_csv(PROJECT / "data" / "processed" / "hr_clean.csv", index=False)

    kpis = {
        "employees": int(len(df)),
        "attrition_rate": round(float(df.attrition.mean()), 4),
        "overtime_flag": round(float(df[df.OverTime == "Yes"].attrition.mean()), 4),
        "no_overtime_rate": round(float(df[df.OverTime == "No"].attrition.mean()), 4),
        "low_sat_rate": round(float(df[df.JobSatisfaction <= 1].attrition.mean()), 4),
        "high_sat_rate": round(float(df[df.JobSatisfaction >= 4].attrition.mean()), 4),
        "new_hire_drop": round(float(df[df.YearsAtCompany <= 2].attrition.mean()), 4),
        "tenured_rate": round(float(df[df.YearsAtCompany >= 7].attrition.mean()), 4),
        "income_gap": round(float(
            df[df.OverTime == "Yes"].MonthlyIncome.mean() - df[df.OverTime == "No"].MonthlyIncome.mean()), 0),
    }
    save_json(kpis, OUT / "kpis.json")

    seg_dept = df.groupby("Department").agg(
        employees=("attrition", "count"), rate=("attrition", "mean")).round(4)
    seg_dept.to_csv(OUT / "seg_dept.csv")
    seg_job = df.groupby("JobRole").agg(employees=("attrition", "count"), rate=("attrition", "mean")).round(4).sort_values("rate")
    seg_job.to_csv(OUT / "seg_job.csv")
    seg_ten = df.groupby(pd.cut(df.YearsAtCompany, [-1, 2, 5, 10, 40], labels=["0-2y", "3-5y", "6-10y", "10y+"]).rename("tenure_band")).agg(
        employees=("attrition", "count"), rate=("attrition", "mean")).round(4)
    seg_ten.to_csv(OUT / "seg_tenure.csv")
    inc = df.groupby(pd.cut(df.MonthlyIncome, [0, 2500, 5000, 7500, 20000], labels=["<2.5k", "2.5-5k", "5-7.5k", ">7.5k"])).agg(
        employees=("attrition", "count"), rate=("attrition", "mean")).round(4)
    inc.to_csv(OUT / "seg_income.csv")

    fig, ax = plt.subplots(figsize=(7.2, 4))
    labels = ["Overtime yes", "Overtime no", "Low satisfaction", "High satisfaction", "New hires (≤2y)", "Tenured (7y+)"]
    vals = [kpis["overtime_flag"], kpis["no_overtime_rate"], kpis["low_sat_rate"],
            kpis["high_sat_rate"], kpis["new_hire_drop"], kpis["tenured_rate"]]
    ax.bar(labels, [v * 100 for v in vals], color="#e2584c")
    ax.tick_params(axis="x", rotation=20)
    ax.set_ylabel("Attrition (%)")
    ax.set_title("Where attrition concentrates — management levers, not mysteries")
    save_png(fig, OUT / "charts" / "risk_bars.png")

    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.bar(seg_job.index, seg_job.rate * 100, color="#134e5e")
    ax.tick_params(axis="x", rotation=60)
    ax.set_ylabel("Attrition (%)")
    ax.set_title("Attrition by job role")
    save_png(fig, OUT / "charts" / "job_roles.png")
    print(json.dumps(kpis, indent=2))


if __name__ == "__main__":
    main()
