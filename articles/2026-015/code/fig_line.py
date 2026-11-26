"""Figure: the line yardstick against the stress. For each system and size, each run's median error line by line
against the low-level dB-fit reference (horizontal) and its median stress error (vertical), over the study's
structures. A yardstick that tracked the stress would put the points on a rising line.
Data: ../data/scores_by_run.csv (scores line_dbfit and stress_rms)."""
from style import *

sc = {(r['system'], r['size'], r['run'], r['score']): float(r['median']) for r in rows('scores_by_run.csv')}
RUNS = [('A1', BLUE, 'o', BLUE), ('N1', ORANGE, 's', 'white'), ('N2', ORANGE, 's', ORANGE),
        ('B1', GREEN, '^', 'white'), ('S1', PURPLE, 'D', 'white')]
fig, axes = plt.subplots(2, 2, figsize=(7.4, 5.8))
for i, system in enumerate(SYSTEMS):
    for j, size in enumerate(SIZES):
        ax = axes[i, j]
        for r, col, mk, face in RUNS:
            k = (system, size, r)
            if k + ('stress_rms',) in sc:
                ax.scatter([sc[k + ('line_dbfit',)]], [sc[k + ('stress_rms',)]], s=48, marker=mk, facecolor=face,
                           edgecolor=col, lw=1.4, label=NAME[r] if (i, j) == (1, 0) else None, zorder=3)
        ax.set_title(f'{system} system, {size} size', fontsize=8.5, loc='left')
        ax.set_xlim(1.5, 9); ax.set_ylim(0, 12.5)
        if i == 1: ax.set_xlabel('Line error against the dB-fit reference (dB)')
        if j == 0: ax.set_ylabel('Stress error (dB)')
        for s_ in ('top', 'right'): ax.spines[s_].set_visible(False)
fig.legend(loc='lower center', ncol=3, fontsize=7, bbox_to_anchor=(0.5, -0.06))
save(fig, 'fig_line')
