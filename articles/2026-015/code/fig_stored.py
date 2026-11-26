"""Figure: what the stored full-level model changes. For each system and size, the change in stress error when the
stored model replaces the low-level identification: band control (band control on the stored model minus band
control), and the pseudo-inverse law with its model kept and with it updated (the stored-model reference minus the
low-level dB-fit reference). Bars: median of the per-structure change; whiskers: quartiles; diamonds: the median on
the five held-back structures, where the rule wrote a claim. Data: ../data/stress_by_structure.csv, ../data/claims.csv."""
from style import *

st = stress(); cl = claims()
PAIRS = [(('A2', 'A1'), 'Band control', BLUE, None), (('N5', 'N1'), 'Pseudo-inverse, model kept', ORANGE, '///'),
         (('N6', 'N2'), 'Pseudo-inverse, model updated', GREEN, '...')]
CELLS = [(s, z) for s in SYSTEMS for z in SIZES]
fig, ax = plt.subplots(figsize=(7.4, 3.7)); x = np.arange(len(CELLS)); w = 0.26
for k, ((a, b), name, col, hatch) in enumerate(PAIRS):
    off = (k - 1) * w; med, lo, hi, hb = [], [], [], []
    for system, size in CELLS:
        d = paired(st, system, size, a, b); m, q1, q3 = quart(d); med.append(m); lo.append(m - q1); hi.append(q3 - m)
        c, sign = claim_for(cl, system, size, a, b)
        hb.append(sign * float(c[0]['held_back_median_db']) if c else np.nan)
    ax.bar(x + off, med, w - 0.03, color=col, hatch=hatch, edgecolor='white', linewidth=0.6, label=name)
    ax.errorbar(x + off, med, yerr=[lo, hi], fmt='none', ecolor=TEXT, elinewidth=0.9, capsize=2.5)
    ax.scatter(x + off, hb, marker='D', s=22, facecolor='white', edgecolor=TEXT, lw=1.0, zorder=4,
               label='Held-back median' if k == 0 else None)
ax.axhline(0, color=MUTED, lw=0.8)
ax.set_xticks(x); ax.set_xticklabels([f'{s} system\n{z} size' for s, z in CELLS], fontsize=7.5)
ax.set_ylabel('Change in stress error (dB)\nbelow zero: the stored model helps'); clean(ax)
ax.legend(loc='lower left', fontsize=7, ncol=2)
save(fig, 'fig_stored')
