"""Figure 1: a sine test with several shakers and its control loop (schematic, not to scale)."""
import csv
import math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE.parent / "data" / "fig1_layout.csv")))
pos = {}
for r in rows:
    pos.setdefault(r["part"], []).append((r["label"], float(r["x"]), float(r["y"])))

BLUE, ORANGE, GREEN, GRAY = "#1f77b4", "#d95f02", "#1b9e77", "0.55"
fig, ax = plt.subplots(figsize=(9.0, 4.6), dpi=150)

# The test article: a beam, and its first bending shape (dashed).
(_, x0, yb), (_, x1, _) = pos["beam"]
ax.add_patch(Rectangle((x0, yb - 0.12), x1 - x0, 0.24, fc="0.8", ec="0.3", lw=1.0))
xs = [x0 + (x1 - x0) * i / 100 for i in range(101)]
ax.plot(xs, [yb + 0.35 * math.sin(math.pi * (x - x0) / (x1 - x0)) for x in xs], color="0.3", ls="--", lw=1.0)
ax.text(2.6, yb - 0.55, "test article (flexible)", ha="center", fontsize=8.5)
ax.text(5.3, yb - 0.55, "dashed: first bending shape", ha="center", fontsize=7.5, color="0.3")

# Shakers: body and armature under the beam.
for label, x, y in pos["shaker"]:
    ax.add_patch(Rectangle((x - 0.45, y), 0.9, 1.3, fc="#cfe0f1", ec=BLUE, lw=1.2, hatch="//"))
    ax.add_patch(Rectangle((x - 0.12, y + 1.3), 0.24, yb - 0.12 - (y + 1.3), fc=BLUE, ec=BLUE))
    ax.text(x, y - 0.3, label, ha="center", fontsize=8.5, color=BLUE)

# Accelerometers: controls (filled orange triangles) and a limit (open green triangle).
for label, x, y in pos["control"]:
    ax.add_patch(Polygon([(x - 0.13, y), (x + 0.13, y), (x, y + 0.22)], closed=True, fc=ORANGE, ec=ORANGE))
    ax.text(x, y + 0.27, label, ha="center", fontsize=8, color=ORANGE)
for label, x, y in pos["limit"]:
    ax.add_patch(Polygon([(x - 0.13, y), (x + 0.13, y), (x, y + 0.22)], closed=True, fc="white", ec=GREEN, lw=1.4))
    ax.text(x, y + 0.27, label, ha="center", fontsize=8, color=GREEN)

# The controller and its three stages.
_, cx, cy = pos["controller"][0]
ax.add_patch(FancyBboxPatch((cx - 0.2, cy - 0.2), 3.7, 3.7, boxstyle="round,pad=0.05", fc="white", ec="0.2"))
ax.text(cx + 1.65, cy + 3.2, "controller", ha="center", fontsize=9, weight="bold")
stages = ["tracking filters: amplitude and\nphase of each channel at the tone",
          "compare with the reference R\n(amplitude and phase at each control)",
          "update the drives D"]
boxes = []
for i, t in enumerate(stages):
    by = cy + 2.15 - i * 0.95
    ax.add_patch(Rectangle((cx, by), 3.3, 0.75, fc="0.95", ec="0.4"))
    ax.text(cx + 1.65, by + 0.37, t, ha="center", va="center", fontsize=7.5)
    boxes.append(by)
for i in range(2):
    ax.annotate("", (cx + 1.65, boxes[i + 1] + 0.75), (cx + 1.65, boxes[i]), arrowprops=dict(arrowstyle="->", color="0.3"))
ax.text(cx + 1.65, cy - 0.85, "C = H D at each frequency;\nH is measured before the test", ha="center", fontsize=8)

# Measurements in (dotted orange), drives out (solid blue).
for label, x, y in pos["control"] + pos["limit"]:
    ax.annotate("", (cx, boxes[0] + 0.5), (x + 0.1, y + 0.15),
                arrowprops=dict(arrowstyle="->", color=ORANGE, ls=":", lw=0.9, connectionstyle="arc3,rad=-0.15"))
for i, (label, x, y) in enumerate(pos["shaker"]):
    ax.annotate("", (x + 0.45, y + 0.5), (cx, boxes[2] + 0.2),
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.1, connectionstyle="arc3,rad=0.12"))
    ax.text(x + 0.62, y + 0.62, f"d{i + 1}", fontsize=8, color=BLUE)

ax.set_xlim(-0.2, 13.0); ax.set_ylim(-1.3, 4.1); ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout()
out = HERE.parent / "figures"; out.mkdir(exist_ok=True)
fig.savefig(out / "fig1_setup.png")
