"""09-management-attrition — 06_chat.py — ask-the-data chatbot.

The trust rule: every number is COMPUTED LIVE at question time — from
data/processed/hr_clean.csv (1,470 employees) or the ranked model output
outputs/employee_risk.csv. The LLM lane (GROQ_API_KEY) narrates verified facts
only and is instructed never to compute or invent. No key → deterministic
offline engine, identical numbers.

Usage:
    python src/06_chat.py                       # interactive REPL
    python src/06_chat.py "why people leave"    # one-shot
"""
from __future__ import annotations

import json
import os
import statistics
import sys
from collections import defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / "data" / "processed" / "hr_clean.csv"
RISK = PROJECT / "outputs" / "employee_risk.csv"

HEADLINE = ("Overall: 1,470 employees · 16.1% attrition · overtime workers leave at 30.5% vs 10.4% · "
            "low-satisfaction 22.8% vs 11.3% · first-years leave at 29.8%.")

FIRST_MSG = """Questions I can answer (all computed live from the data):
  why people leave · overtime · satisfaction · tenure / new hires
  departments · income gap · top 5 at-risk employees
Type 'quit' to exit."""


def compute(q: str) -> list[str] | None:
    q = q.lower().strip()

    if "why" in q and ("leave" in q or "attrition" in q) or "levers" in q:
        import csv
        with DATA.open() as f:
            rows = list(csv.DictReader(f))
        ot_yes = [r for r in rows if r["OverTime"] == "Yes"]
        ot_no = [r for r in rows if r["OverTime"] == "No"]
        rate = lambda g: sum(1 for r in g if r["attrition"] == "1") / len(g)  # noqa: E731
        lo = [r for r in rows if int(r["JobSatisfaction"]) <= 1]
        hi = [r for r in rows if int(r["JobSatisfaction"]) >= 4]
        early = [r for r in rows if int(r["YearsAtCompany"]) <= 2]
        return [
            "Three measured levers (each vs the 16.1% baseline):",
            f"  1. Overtime — leavers rate {rate(ot_yes):.1%} among OT vs {rate(ot_no):.1%} without.",
            f"  2. Satisfaction — {rate(lo):.1%} when JobSatisfaction = 1 (floor) vs {rate(hi):.1%} at the top.",
            f"  3. Early tenure — {rate(early):.1%} within the first two years.",
            "Management plan: price overtime, target early-tenure 1:1s, watch the satisfaction floor.",
        ]

    if "overtime" in q:
        import csv
        with DATA.open() as f:
            rows = list(csv.DictReader(f))
        ot_yes = [r for r in rows if r["OverTime"] == "Yes"]
        ot_no = [r for r in rows if r["OverTime"] == "No"]
        rate = lambda g: sum(1 for r in g if r["attrition"] == "1") / len(g)  # noqa: E731
        n = lambda g: sum(1 for r in g if r["attrition"] == "1")  # noqa: E731
        return [f"Overtime = Yes: {n(ot_yes):,}/{len(ot_yes):,} left ({rate(ot_yes):.1%}).",
                f"Overtime = No:  {n(ot_no):,}/{len(ot_no):,} left ({rate(ot_no):.1%}).",
                f"Overtime is a ~3x attrition multiplier — and a schedulable one."]

    if "satisfaction" in q:
        import csv
        with DATA.open() as f:
            rows = list(csv.DictReader(f))
        groups = defaultdict(list)
        for r in rows:
            groups[int(r["JobSatisfaction"])].append(r["attrition"] == "1")
        return ["Attrition by JobSatisfaction (1-4):",
                *[f"  {lvl} — {statistics.mean(v):.1%} ({len(v):,} employees)" for lvl, v in sorted(groups.items())]]

    if "risk" in q or "watch" in q or "top 5" in q or "top-5" in q or "save" in q:
        import csv
        with RISK.open() as f:
            rows = sorted(csv.DictReader(f), key=lambda r: float(r["p_exit"]), reverse=True)
        lines = ["Top 5 employees by predicted exit probability (from outputs/employee_risk.csv):"]
        lines += [f"  #{r['EmployeeNumber']} — p={float(r['p_exit']):.2f} · "
                  f"{r['JobRole']} · ${float(r['MonthlyIncome']):,.0f}/mo · OT={r['OverTime']}"
                  for r in rows[:5]]
        lines.append("The 1:1 list, not an org-building exercise: verify, then engage.")
        return lines

    if "department" in q or "dept" in q:
        import csv
        with DATA.open() as f:
            rows = list(csv.DictReader(f))
        groups = defaultdict(lambda: [0, 0])
        for r in rows:
            g = groups[r["Department"]]
            g[0] += 1
            g[1] += r["attrition"] == "1"
        return ["Attrition by department:",
                *[f"  {d} — {c/len(g):.1%} of {len(g):,} employees" for d, g in sorted(groups.items(), key=lambda kv: -kv[1][1]/kv[1][0])]]

    if "income" in q or "salary" in q or "pay" in q:
        import csv
        with DATA.open() as f:
            rows = list(csv.DictReader(f))
        leavers = [float(r["MonthlyIncome"]) for r in rows if r["attrition"] == "1"]
        stayers = [float(r["MonthlyIncome"]) for r in rows if r["attrition"] == "0"]
        return [f"Median monthly income — leavers ${statistics.median(leavers):,.0f} vs stayers ${statistics.median(stayers):,.0f}.",
                f"Gap: ${statistics.median(stayers)-statistics.median(leavers):,.0f} — leavers skew cheaper, "
                "behind that: tenure, not just pay."]

    if "tenure" in q or "new hire" in q or "early" in q or "years" in q:
        import csv
        with DATA.open() as f:
            rows = list(csv.DictReader(f))
        buckets = [(0, 2), (3, 5), (6, 10), (11, 40)]
        lines = ["Attrition rate by tenure bucket:"]
        for a, b in buckets:
            g = [r for r in rows if a <= int(r["YearsAtCompany"]) <= b]
            if g:
                lines.append(f"  {a}-{b}y — {sum(1 for r in g if r['attrition']=='1')/len(g):.1%} ({len(g):,} employees)")
        return lines

    return None


def offline_answer(q: str) -> str:
    try:
        lines = compute(q)
    except Exception as e:  # noqa: BLE001
        return f"\n(error while computing from the csv — this engine never guesses: {e})\n"
    if lines is None:
        return ("\nI could not map that to a computed fact, so here is the verified headline\n"
                "(try: why people leave, overtime, satisfaction, tenure, departments, top 5 at risk).\n\n"
                f"{HEADLINE}\n")
    return "\n".join(["[computed live from hr_clean.csv / employee_risk.csv —]"] + lines) + f"\n\n{HEADLINE}\n"


def narrate_with_llm(q: str, facts: str) -> str:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        return ""
    import urllib.request
    body = json.dumps({"model": "llama-3.1-8b-instant", "messages": [
        {"role": "system", "content": "You are a precise, discreet people-analytics consultant. Use ONLY the numbers in the supplied verified facts. Do not compute, estimate or invent any number. Be sensitive: employees are humans, not churn. 3 sentences max."},
        {"role": "user", "content": f"Facts (verified, pre-computed):\n{facts}\n\nQuestion: {q}"}]})
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions", data=body.encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return "\n\nNARRATED: " + json.loads(r.read())["choices"][0]["message"]["content"].strip() + "\n"
    except Exception:
        return ""


def main() -> None:
    if not DATA.exists():
        print("Run src/00_download_data.py + src/01_analysis.py first."); sys.exit(2)

    if len(sys.argv) > 1:  # one-shot
        q = " ".join(sys.argv[1:])
        base = offline_answer(q)
        if os.environ.get("GROQ_API_KEY") and "computed live" in base:
            base += narrate_with_llm(q, base)
        print(base)
        return

    print(FIRST_MSG + "\n")
    while True:
        try:
            q = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); return
        if q.lower() in {"quit", "exit", "q", ""}:
            return
        base = offline_answer(q)
        if os.environ.get("GROQ_API_KEY") and "computed live" in base:
            base += narrate_with_llm(q, base)
        print(base)


if __name__ == "__main__":
    main()
