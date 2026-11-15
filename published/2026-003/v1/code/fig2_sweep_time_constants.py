"""Figure 2: the mode's time constants inside its half-power bandwidth against frequency."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE.parent / "data" / "fig2_sweep_n.csv")))
f = [float(r["frequency_hz"]) for r in rows]
styles = [("0.5", "#1f77b4", "-", "o"), ("1", "#d95f02", "--", "s"),
          ("2", "#1b9e77", "-.", "^"), ("4", "#7570b3", ":", "D")]
fig, ax = plt.subplots(figsize=(7.0, 4.4), dpi=150)
ax.axhspan(0.1, 2.0, color="0.88", zorder=0)
ax.text(45, 0.13, "N under 2: the mode does not settle;\nits peak comes late and low", fontsize=8, color="0.25")
ax.axhline(3.5, color="black", ls="--", lw=1.0)
ax.text(150, 2.4, "ISO 7626-2 limit, N = 3.5", fontsize=8)
for s, c, ls, m in styles:
    n = [float(r[f"N_{s}_oct_per_min"]) for r in rows]
    ax.plot(f, n, color=c, ls=ls, marker=m, markevery=10, ms=5, mfc="none", lw=1.6,
            label=f"{s} octave{'s' if s != '1' else ''} a minute")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(5, 500); ax.set_ylim(0.1, 200)
ax.set_xlabel("Frequency of the mode (Hz)")
ax.set_ylabel("N, time constants inside the bandwidth")
ax.set_title("Q = 50", fontsize=9, loc="left")
ax.grid(True, which="both", color="0.85", lw=0.5)
ax.legend(loc="upper left", fontsize=8, frameon=False)
fig.tight_layout()
out = HERE.parent / "figures"; out.mkdir(exist_ok=True)
fig.savefig(out / "fig2_sweep_time_constants.png")
