"""Figure: each way of running the test against band control, structure by structure, in stress error.
d = the run minus band control (dB): positive means further from the stress in service than band control.
Dots: one per structure. Large marker: the median; bar: the quartiles. Shaded: +/-0.5 dB, the margin for
"the same test on average". The text at the right of each row gives the structures on which the run was
higher than band control, and the claim the rule wrote with the audit's verdict on the held-back structures.
Data: ../data/stress_by_structure.csv and ../data/claims.csv."""
from style import *

st = stress(); cl = claims()
RUNS = ['A2', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'S1', 'B1']
fig, axes = plt.subplots(2, 2, figsize=(7.6, 7.6), gridspec_kw={'wspace': 0.62, 'hspace': 0.32})
XLIM = {'6 x 12': (-3, 6), '6 x 6': (-4, 17)}
for i, system in enumerate(SYSTEMS):
    for j, size in enumerate(SIZES):
        ax = axes[i, j]
        runs = [r for r in RUNS if (system, size, r) in st]
        ax.axvspan(-0.5, 0.5, color=GRID, alpha=0.7, lw=0)
        ax.axvline(0, color=MUTED, lw=0.8)
        for k, r in enumerate(runs):
            y = len(runs) - 1 - k
            d = paired(st, system, size, r, 'A1')
            jit = (np.arange(d.size) % 5 - 2) * 0.06
            ax.scatter(d, y + jit, s=7, color=MUTED, alpha=0.55, lw=0, zorder=2)
            med, q1, q3 = quart(d)
            c, sign = claim_for(cl, system, size, r, 'A1')
            kinds = {x['kind'] for x in c}
            if 'difference' in kinds:
                mk, col, face = 'o', ORANGE, ORANGE
            elif 'same test' in kinds:
                mk, col, face = 's', BLUE, 'white'
            else:
                mk, col, face = 'D', MUTED, 'white'
            ax.plot([q1, q3], [y, y], color=col, lw=2.2, zorder=3)
            ax.scatter([med], [y], s=46, marker=mk, facecolor=face, edgecolor=col, lw=1.6, zorder=4)
            verdict = '; '.join(x['verdict'] for x in c) if c else 'no claim'
            ax.annotate(f"{int((d > 0).sum())} of {d.size} worse; {verdict}", xy=(1.0, y), xycoords=('axes fraction', 'data'),
                        xytext=(3, 0), textcoords='offset points', va='center', fontsize=6.2, color=TEXT)
        ax.set_yticks(range(len(runs)))
        ax.set_yticklabels([NAME[r] for r in reversed(runs)] if j == 0 else [''] * len(runs), fontsize=7)
        ax.set_ylim(-0.6, len(runs) - 0.4)
        ax.set_title(f'{system} system, {size} size', fontsize=8, loc='left'); ax.set_xlim(*XLIM[system])
        clean(ax, grid_axis='x')
        ax.set_xlabel('Run minus band control (dB)', fontsize=7.5)
h = [plt.Line2D([], [], marker='o', color=ORANGE, mfc=ORANGE, lw=2, label='Median, a difference claimed'),
     plt.Line2D([], [], marker='s', color=BLUE, mfc='white', lw=2, label='Median, "the same test" claimed'),
     plt.Line2D([], [], marker='D', color=MUTED, mfc='white', lw=2, label='Median, no claim'),
     plt.Line2D([], [], marker='o', color=MUTED, lw=0, ms=3, label='One structure')]
fig.legend(handles=h, loc='lower center', ncol=4, fontsize=7, bbox_to_anchor=(0.5, -0.02))
fig.savefig(os.path.join(FIGURES, 'fig_paired.png'), bbox_inches='tight')
print(os.path.join(FIGURES, 'fig_paired.png'))
