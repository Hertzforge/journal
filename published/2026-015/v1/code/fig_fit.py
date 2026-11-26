"""Figure: the two low-level conversions, 6 x 12 system. Each structure's stress error under the pseudo-inverse law on the two
low-level conversions, against band control's on the same structure. On the diagonal the two are equal; above it
the converted reference is further from service. Data: ../data/stress_by_structure.csv."""
from style import *

st = stress()
fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.7), sharex=True, sharey=True)
for ax, size in zip(axes, SIZES):
    a = st[('6 x 12', size, 'A1')]
    for r, col, mk, face, name in (('N1', ORANGE, 'o', ORANGE, 'dB-fit reference'),
                                   ('N3', BLUE, '^', 'white', 'First-solve reference')):
        b = st[('6 x 12', size, r)]; s = sorted(set(a) & set(b))
        ax.scatter([a[k] for k in s], [b[k] for k in s], s=26, marker=mk, facecolor=face, edgecolor=col, lw=1.2, label=name, zorder=3)
    ax.plot([1.5, 9], [1.5, 9], color=MUTED, lw=0.9, ls='--', label='Equal to band control')
    ax.set_xlim(1.5, 9); ax.set_ylim(1.5, 9); ax.set_aspect('equal')
    ax.set_title(f'6 x 12 system, {size} size', fontsize=8.5, loc='left')
    ax.set_xlabel('Band control, stress error (dB)')
    for s_ in ('top', 'right'): ax.spines[s_].set_visible(False)
axes[0].set_ylabel('Pseudo-inverse law, stress error (dB)')
axes[0].legend(loc='upper left', fontsize=7.5)
save(fig, 'fig_fit')
