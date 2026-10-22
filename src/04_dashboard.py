"""09-management-attrition — 04_dashboard.py — single-file people analytics dashboard."""
from pathlib import Path
import json
import sys

import pandas as pd
import plotly.graph_objects as go

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared.dashboard import build_dashboard   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "outputs"


def main() -> None:
    kpis = json.loads((OUT / "kpis.json").read_text())
    model = json.loads((OUT / "model.json").read_text())
    job = pd.read_csv(OUT / "seg_job.csv", index_col=0)
    ten = pd.read_csv(OUT / "seg_tenure.csv", index_col=0)
    inc = pd.read_csv(OUT / "seg_income.csv", index_col=0)

    labels = ["Overtime", "No overtime", "Low satisfaction", "High satisfaction",
              "New hires ≤2y", "Tenured 7y+"]
    vals = [kpis["overtime_flag"], kpis["no_overtime_rate"], kpis["low_sat_rate"],
            kpis["high_sat_rate"], kpis["new_hire_drop"], kpis["tenured_rate"]]
    fig_risk = go.Figure(go.Bar(x=labels, y=[v * 100 for v in vals],
                                marker_color=["#e2584c" if i % 2 == 0 else "#0e7490" for i in range(6)],
                                text=[f"{v:.0%}" for v in vals], textposition="outside"))
    fig_risk.update_layout(xaxis_tickangle=-20, yaxis_title="Attrition rate (%)")

    job = job.sort_values("rate")
    fig_job = go.Figure(go.Bar(y=job.index, x=job.rate * 100, orientation="h", marker_color="#134e5e"))
    fig_job.update_layout(xaxis_title="Attrition rate (%)")

    fig_ten = go.Figure(go.Bar(x=list(ten.index), y=ten.rate * 100, marker_color="#d97706"))
    fig_ten.update_layout(xaxis_title="Tenure band", yaxis_title="Attrition rate (%)")

    fig_inc = go.Figure(go.Bar(x=list(inc.index), y=inc.rate * 100, marker_color="#0e7490"))
    fig_inc.update_layout(xaxis_title="Monthly income band", yaxis_title="Attrition rate (%)")

    build_dashboard(
        str(PROJECT / "dashboard" / "index.html"),
        title="Workforce Attrition & Retention — People Analytics",
        subtitle=("Who is at risk, where, and which retention lever pays for itself. "
                  "IBM HR Analytics dataset (public, 1,470 employees); verified in Python."),
        badges=["Management", "People analytics", "Costed retention ROI", "LLM narration"],
        kpis=[
            {"label": "Employees", "value": f"{kpis['employees']:,}"},
            {"label": "Attrition rate", "value": f"{kpis['attrition_rate']:.0%}"},
            {"label": "Overtime flag", "value": f"{kpis['overtime_flag']:.0%}", "note": f"vs {kpis['no_overtime_rate']:.0%} no-overtime"},
            {"label": "Model AUC", "value": f"{model['auc_test']:.2f}"},
            {"label": "Retention ROI", "value": f"${model['net_uplift']:,.0f}",
             "note": f"cost ${model['program_cost']:,.0f} → savings ${model['expected_savings']:,.0f}"},
        ],
        figures=[
            {"title": "Attrition concentration", "sub": "management levers, not mysteries", "fig": fig_risk},
            {"title": "By job role", "fig": fig_job},
            {"title": "By tenure band", "sub": "onboarding owns the risk", "fig": fig_ten},
            {"title": "By income band", "fig": fig_inc},
        ],
        recommendations=[
            f"Cap overtime on the highest-risk roles first: attrition runs {kpis['overtime_flag']:.0%} with overtime "
            f"vs {kpis['no_overtime_rate']:.0%} without, and pay makes it worse, not better.",
            "Rebuild the first-730-days journey: new hires exit at multiples of tenured staff — mentorship + "
            "30/60/90 check-ins as the standard package.",
            f"Target the ≥50%-risk cohort ({model['n_high_risk']} employees) with the retention package — "
            f"stated-assumption ROI in the header card.",
            "Ethics guardrail: no individual scoring in the open at this stage — aggregate dashboards only, "
            "with an audited, documented feature list (no protected attributes).",
        ],
        footer=("Data: IBM HR Analytics (public mirror, no PII). AI narrates verified metrics only. "
                "Stated assumptions: $45k replacement cost, $3k intervention, 25% save rate."),
    )
    print("dashboard written")


if __name__ == "__main__":
    main()
