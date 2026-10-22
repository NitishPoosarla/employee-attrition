"""09-management-attrition — 03_ai_insights.py — measured AI people-analytics narrative."""
from pathlib import Path
import json
import sys

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared import llm   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
OUT = PROJECT / "outputs"


def main() -> None:
    kpis = json.loads((OUT / "kpis.json").read_text())
    model = json.loads((OUT / "model.json").read_text())
    drivers = {
        "Overtime is the sharpest flag": (f"Attrition rate with overtime {kpis['overtime_flag']:.0%} vs "
                                          f"{kpis['no_overtime_rate']:.0%} without — and overtime payers earn "
                                          f"${kpis['income_gap']:,.0f} MORE on average: money isn't the lever."),
        "First two years decide": (f"New hires (≤2y) exit at {kpis['new_hire_drop']:.0%} vs "
                                   f"{kpis['tenured_rate']:.0%} for 7y+ staff — onboarding owns the risk."),
        "Model & economics": (f"AUC {model['auc_test']:.2f}; {model['n_high_risk']} employees at ≥50% risk. "
                              f"Retention package: cost ${model['program_cost']:,.0f} vs savings "
                              f"${model['expected_savings']:,.0f} → net ${model['net_uplift']:,.0f} "
                              f"(stated assumptions)."),
    }
    prompt = f"""You are advising an HR director. Use ONLY the verified metrics.
Deliver: (1) two-sentence situation read, (2) ranked retention actions with $,
(3) right-to-privacy/ethics note for people-data use.
Metrics: {json.dumps({**kpis, **model}, indent=1)}"""
    md = llm.write_insights(str(OUT / "insights.md"), "Workforce attrition & retention", kpis, drivers, prompt)
    print(md[:900])


if __name__ == "__main__":
    main()
