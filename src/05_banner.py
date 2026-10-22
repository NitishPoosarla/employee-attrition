"""09 — banner: two-panel split — the overtime delta is the story."""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

k = json.loads((Path(__file__).resolve().parents[1] / "outputs" / "kpis.json").read_text())

fig, ax = plt.subplots(figsize=(12, 6.75), dpi=100)
ax.set_xlim(0, 12); ax.set_ylim(0, 6.75); ax.axis("off")
fig.patch.set_facecolor("#22262b")

ax.add_patch(plt.Rectangle((0, 0), 6.0, 6.75, color="#b34a3e"))
ax.add_patch(plt.Rectangle((6.0, 0), 6.0, 6.75, color="#3f4d43"))

ax.text(3.0, 4.6, f"{k['overtime_flag']:.1%}", fontsize=46, fontweight="bold",
        color="#fff5f2", ha="center")
ax.text(3.0, 3.55, "attrition among\nthe overtime pool", fontsize=12, color="#f3d9d3",
        ha="center", linespacing=1.4)

ax.text(9.0, 4.6, f"{k['no_overtime_rate']:.1%}", fontsize=46, fontweight="bold",
        color="#eef4ee", ha="center")
ax.text(9.0, 3.55, "everyone else —\nroughly a third of the risk", fontsize=12,
        color="#cfe0cf", ha="center", linespacing=1.4)

ax.text(6.0, 6.15, "AND THE OVERTIME POOL EARNS MORE ON AVERAGE", fontsize=13.5,
        fontweight="bold", color="white", ha="center")
ax.text(6.0, 5.62, f"{k['employees']:,} employees, public IBM HR snapshot — so the lever is workload",
        fontsize=11, color="#d8dde2", ha="center")

ax.text(3.0, 1.45, "≤2y tenure: ~30% exit —\nown the first 730 days", fontsize=11.5,
        color="#fff5f2", ha="center", linespacing=1.4)
ax.text(9.0, 1.45, "model-ranked one-to-one watch list;\naggregate-only dashboards by default", fontsize=11,
        color="#cfe0cf", ha="center", linespacing=1.4)
fig.savefig(Path(__file__).resolve().parents[1] / "outputs" / "banner.png",
            dpi=100, facecolor=fig.get_facecolor())
print("banner written")
