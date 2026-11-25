"""Figure: the three runs compared, level against time. Identification at about -20 dB, then loops.
Ladder: 4 loops of 66 s below full level, then 30 at full level. Pretest: 5 loops of 34 s, the last at full level.
Test on the stored model: identification, one soft-start loop, then 30 loops at full level. Times from the runs' manifests."""
import numpy as np
from style import *
ID = 132.0
def steps(levels, loop_s):
    t = [0, ID]; l = [-20, -20]
    for lv in levels:
        t += [t[-1], t[-1] + loop_s]; l += [lv, lv]
    return np.array(t), np.array(l)
fig, axes = plt.subplots(3, 1, figsize=(7.4, 4.6), sharex=True)
rows = [('The ladder (the test as run today)', [-12, -9, -6, -3] + [0] * 6, 66, BLUE, 4),
        ('The pretest: stores the model measured in its last loop', [-12, -9, -6, -3, 0], 34, GREEN, None),
        ('The test started at full level on the stored model', [0] * 8, 66, ORANGE, 1)]
for ax, (name, lv, ls, col, nlow) in zip(axes, rows):
    t, l = steps(lv, ls); ax.fill_between(t, -24, l, step=None, color=col, alpha=0.25, linewidth=0); ax.plot(t, l, color=col, linewidth=1.6)
    ax.set_ylim(-24, 3); ax.set_yticks([-20, -12, -6, 0]); ax.set_title(name, loc='left', fontsize=9, color=TEXT); clean(ax)
    ax.text(ID / 2, -18.5, 'identification', ha='center', va='bottom', fontsize=7.5, color=MUTED)
    if nlow is not None:
        ax.text(632, -2.2, 'continues: 30 loops at full level', ha='right', va='top', fontsize=7.5, color=MUTED)
axes[2].text(ID + 6, -3.2, 'first loop: soft start', ha='left', va='top', fontsize=7.5, color=MUTED)
axes[1].set_ylabel('Level, dB against full level'); axes[2].set_xlabel('Time, s'); axes[2].set_xlim(0, 640)
save(fig, 'fig_method')
