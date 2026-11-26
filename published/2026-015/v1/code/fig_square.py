"""Figure: the square system (6 shakers, 6 control gauges). Stress error of band control and of four ways of running
the converted reference, at the realistic and strong sizes. Bars: median over 10 structures; whiskers: quartiles.
Data: ../data/stress_by_structure.csv."""
from style import *

st = stress()
RUNS = [('A1', 'Band\ncontrol'), ('A2', 'Band control,\nstored model'), ('N1', 'Pseudo-inverse,\ndB-fit ref.'),
        ('N3', 'Pseudo-inverse,\nfirst-solve ref.'), ('N5', 'Pseudo-inverse,\nstored-model ref.'),
        ('S1', 'Shape-constrained,\ndB-fit ref.'), ('B1', 'Broyden,\ndB-fit ref.')]
fig, ax = plt.subplots(figsize=(7.4, 3.6)); x = np.arange(len(RUNS)); w = 0.38
for off, size, col, hatch in ((-w / 2, 'realistic', BLUE, None), (w / 2, 'strong', ORANGE, '///')):
    v = [np.array(list(st[('6 x 6', size, r)].values())) for r, _ in RUNS]
    med = [np.median(a) for a in v]; q1 = [np.percentile(a, 25) for a in v]; q3 = [np.percentile(a, 75) for a in v]
    ax.bar(x + off, med, w - 0.04, color=col, hatch=hatch, edgecolor='white', linewidth=0.6, label=f'{size.capitalize()} size')
    ax.errorbar(x + off, med, yerr=[np.subtract(med, q1), np.subtract(q3, med)], fmt='none', ecolor=TEXT, elinewidth=0.9, capsize=2.5)
ax.set_xticks(x); ax.set_xticklabels([n for _, n in RUNS], fontsize=7.5)
ax.set_ylabel('Stress error (dB)\nlower is closer to service'); ax.set_ylim(0, None); clean(ax)
ax.legend(loc='upper left', ncol=2)
save(fig, 'fig_square')
