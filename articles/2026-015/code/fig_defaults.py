"""Figure: the runs made with the controller's checks at their defaults (structures 0 and 1, both systems, both
sizes, 76 runs). For each way of running the test, the number of full-level loops each run completed before a check
stopped it; a run that completed has 30. Data: ../data/default_checks.csv (the audit's table)."""
from style import *

R = rows('default_checks.csv')
ORDER = ['A1', 'A2', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'S1', 'B1']
STY = {('6 x 12', 'realistic'): ('o', BLUE, BLUE), ('6 x 12', 'strong'): ('s', ORANGE, 'white'),
       ('6 x 6', 'realistic'): ('^', GREEN, GREEN), ('6 x 6', 'strong'): ('D', PURPLE, 'white')}
fig, ax = plt.subplots(figsize=(7.4, 4.2)); seen = set()
for k, run in enumerate(ORDER):
    y0 = len(ORDER) - 1 - k; mine = [r for r in R if r['run'] == run]
    for n, r in enumerate(mine):
        mk, col, face = STY[(r['system'], r['size'])]; lab = f"{r['system']} system, {r['size']} size"
        y = y0 + (n - (len(mine) - 1) / 2) * 0.09
        ax.scatter([int(r['full_level_loops'])], [y], marker=mk, s=26, facecolor=face, edgecolor=col, lw=1.2,
                   label=None if lab in seen else lab, zorder=3)
        seen.add(lab)
    done = sum(r['at_defaults'] == 'completed' for r in mine)
    ax.annotate(f'{done} of {len(mine)} completed', xy=(1.0, y0), xycoords=('axes fraction', 'data'), xytext=(4, 0),
                textcoords='offset points', va='center', fontsize=7)
ax.axvline(30, color=MUTED, lw=0.8, ls='--')
ax.set_yticks(range(len(ORDER))); ax.set_yticklabels([NAME[r] for r in reversed(ORDER)], fontsize=7)
ax.set_xlabel('Full-level loops completed before the run was stopped (30: the run completed)')
ax.set_xlim(-1.5, 31.5); clean(ax, grid_axis='x')
ax.legend(loc='lower center', ncol=2, fontsize=7, bbox_to_anchor=(0.5, -0.3))
save(fig, 'fig_defaults')
