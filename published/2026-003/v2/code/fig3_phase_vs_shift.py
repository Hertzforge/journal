"""Figure 3: the largest phase difference between a low-level model and a moved resonance."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE.parent / "data" / "fig3_phase_vs_shift.csv")))
marks = list(csv.DictReader(open(HERE.parent / "data" / "fig3_one_percent_marks.csv")))
d = [float(r["shift_bandwidths"]) for r in rows]
p = [float(r["max_phase_difference_deg"]) for r in rows]
fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=150)
ax.plot(d, p, color="#1f77b4", lw=1.8, ls="-", label="2 arctan(shift)")
ax.axhline(90, color="black", ls="--", lw=1.0)
ax.text(2.6, 82, "90 degrees: a one-channel correction stops converging", fontsize=8)
for m in marks:
    x, y = float(m["shift_bandwidths"]), float(m["max_phase_difference_deg"])
    ax.plot([x], [y], marker="o", ms=7, mfc="none", mec="#d95f02", mew=1.6, ls="none")
    ax.annotate(f"1 % shift, Q = {float(m['Q']):g}", (x, y), xytext=(x + 0.25, y - 14), fontsize=8,
                arrowprops=dict(arrowstyle="-", color="0.4", lw=0.6))
ax.set_xlim(0, 5); ax.set_ylim(0, 180); ax.set_yticks(range(0, 181, 30))
ax.set_xlabel("How far the resonance has moved (half-power bandwidths)")
ax.set_ylabel("Largest phase difference (degrees)")
ax.grid(True, color="0.85", lw=0.5)
fig.tight_layout()
out = HERE.parent / "figures"; out.mkdir(exist_ok=True)
fig.savefig(out / "fig3_phase_vs_shift.png")
