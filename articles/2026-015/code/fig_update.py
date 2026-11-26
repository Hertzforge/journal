"""Figure: the pseudo-inverse law with its model updated during the run against kept, on each of the three
converted references. Bars: median of (updated minus kept) over the study's structures; whiskers: quartiles;
diamonds: the median on the five held-back structures, where the rule wrote a claim. The word over each bar is the
audit's verdict on that claim. Data: ../data/stress_by_structure.csv, ../data/claims.csv."""
from style import *

st = stress(); cl = claims()
PAIRS = [(('N2', 'N1'), 'dB-fit reference', BLUE, None), (('N4', 'N3'), 'First-solve reference', ORANGE, '///'),
         (('N6', 'N5'), 'Stored-model reference', GREEN, '...')]
CELLS = [(s, z) for s in SYSTEMS for z in SIZES]
fig, ax = plt.subplots(figsize=(7.4, 3.9)); x = np.arange(len(CELLS)); w = 0.26
for k, ((a, b), name, col, hatch) in enumerate(PAIRS):
    off = (k - 1) * w
    for i, (system, size) in enumerate(CELLS):
        d = paired(st, system, size, a, b); m, q1, q3 = quart(d)
        ax.bar(x[i] + off, m, w - 0.03, color=col, hatch=hatch, edgecolor='white', linewidth=0.6, label=name if i == 0 else None)
        ax.errorbar(x[i] + off, m, yerr=[[m - q1], [q3 - m]], fmt='none', ecolor=TEXT, elinewidth=0.9, capsize=2.5)
        c, sign = claim_for(cl, system, size, a, b)
        diff = [r for r in c if r['kind'] == 'difference']
        if diff:
            ax.scatter([x[i] + off], [sign * float(diff[0]['held_back_median_db'])], marker='D', s=22, facecolor='white',
                       edgecolor=TEXT, lw=1.0, zorder=4, label='Held-back median' if (k, i) == (0, 1) else None)
        word = {'holds': 'holds', 'weaker': 'weaker', 'does not hold': 'does not hold'}[diff[0]['verdict']] if diff else (
            'same test' if c else 'no claim')
        ax.text(x[i] + off, max(q3, 0) + 0.12, word, rotation=90, ha='center', va='bottom', fontsize=6.3, color=TEXT)
ax.axhline(0, color=MUTED, lw=0.8)
ax.set_xticks(x); ax.set_xticklabels([f'{s} system\n{z} size' for s, z in CELLS], fontsize=7.5)
ax.set_ylabel('Updated minus kept, stress error (dB)\nabove zero: updating is worse'); clean(ax)
ax.set_ylim(-1.5, 4.6); ax.legend(loc='upper left', fontsize=7, ncol=2)
save(fig, 'fig_update')
