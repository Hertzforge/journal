"""Figure 2: one loop of the run, and which part the control law owns.

Reads ../data/fig2_one_loop.csv only. Copyright 2026 Kevin Cross. MIT license.
"""
import textwrap

from matplotlib.patches import FancyBboxPatch

from style import BLUE, ORANGE, TEXT, plt, rows, save

t = rows('fig2_one_loop.csv')
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.set_axis_off()
ax.set_xlim(0, 10)
ax.set_ylim(0, 8.6)
y = 8.0
centres = []
for r in t:
    law = r['owner'] == 'law'
    x0, w = 1.4, 7.2
    box = FancyBboxPatch((x0, y - 0.72), w, 0.62, boxstyle='round,pad=0.02,rounding_size=0.12',
                         fc='#fff3e8' if law else '#edf2f9', ec=ORANGE if law else BLUE,
                         lw=2.0 if law else 1.2, ls='--' if law else '-')
    ax.add_patch(box)
    ax.text(x0 + w / 2, y - 0.41, f"{r['order']}. " + textwrap.fill(r['step'], 78), ha='center',
            va='center', fontsize=8, color=TEXT)
    centres.append(y - 0.41)
    y -= 0.98
for a, b in zip(centres[:-1], centres[1:]):
    ax.annotate('', xy=(5, b + 0.31), xytext=(5, a - 0.31),
                arrowprops=dict(arrowstyle='->', color=TEXT, lw=1))
ax.annotate('', xy=(1.4, centres[0]), xytext=(1.4, centres[-1]),
            arrowprops=dict(arrowstyle='->', color=TEXT, lw=1, connectionstyle='arc3,rad=-0.35'))
ax.text(0.35, (centres[0] + centres[-1]) / 2, 'next\nloop', ha='center', va='center', fontsize=8)
ax.plot([], [], color=BLUE, lw=1.2, label='The core: the same for every law')
ax.plot([], [], color=ORANGE, lw=2.0, ls='--', label='The control law')
ax.legend(loc='upper center', fontsize=8, ncol=2, bbox_to_anchor=(0.5, 0.02))
save(fig, 'fig2_one_loop.png')
