"""Figure: the low-level reconciliation check. Left: the check's reading (median over frequency lines of the relative
difference between the new low-level identification and the stored one, one common delay removed) for the unchanged
structure and four changed ones; one point a structure, 20 a condition; the line is the gate. Right: what starting at
full level on the stored model cost on the changed structure, as control error against the unchanged structure; bars
are medians, whiskers quartiles. Data: ../data/e31_cells.json (e31_analyze.py)."""
import json, os
import numpy as np
from style import *
J = json.load(open(os.path.join(DATA, 'e31_cells.json'))); M = J['cells']['m1']; C = J['cells']['jump']; gate = J['gates']['m1']['gate']
COND = [('fresh', 'Unchanged'), ('shift0.5', 'Shifted\n0.5%'), ('shift1', 'Shifted\n1%'), ('shift2', 'Shifted\n2%'), ('drop1.5', 'Level effects\n1.5 times')]
CELLS = [('6x6-realistic', BLUE, 'o', '6 x 6'), ('12x12-realistic', ORANGE, 's', '12 x 12')]
plt.rcParams['savefig.dpi'] = 210
fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.6)); rng = np.random.default_rng(1)
ax = axes[0]
for i, (c, _) in enumerate(COND):
    for j, (cell, col, mk, name) in enumerate(CELLS):
        v = M[c][cell]['values']; ax.scatter(i + (j - 0.5) * 0.3 + rng.uniform(-0.08, 0.08, len(v)), v, s=14, color=col, marker=mk,
                                             edgecolor='white', linewidth=0.4, label=name if i == 0 else None, zorder=3)
ax.axhline(gate, color=TEXT, lw=1, ls='--'); ax.text(4.45, gate * 1.08, 'gate', ha='right', va='bottom', fontsize=8, color=TEXT)
ax.set_yscale('log'); ax.set_yticks([0.02, 0.05, 0.1, 0.2, 0.5]); ax.set_yticklabels(['0.02', '0.05', '0.1', '0.2', '0.5']); ax.minorticks_off(); ax.set_ylabel('Reading of the low-level check'); ax.set_xticks(range(len(COND))); ax.set_xticklabels([n for _, n in COND], fontsize=7.5)
ax.legend(loc='upper left', fontsize=8); clean(ax)
ax = axes[1]; w = 0.36; x = np.arange(1, len(COND))
for j, (cell, col, mk, name) in enumerate(CELLS):
    v = [C[c][cell]['d_fresh'] for c, _ in COND[1:]]; med = [np.median(a) for a in v]
    q1 = [np.percentile(a, 25) for a in v]; q3 = [np.percentile(a, 75) for a in v]
    ax.bar(x + (j - 0.5) * w, med, w - 0.04, color=col, hatch=None if j == 0 else '///', edgecolor='white', linewidth=0.6, label=name)
    ax.errorbar(x + (j - 0.5) * w, med, yerr=[np.subtract(med, q1), np.subtract(q3, med)], fmt='none', ecolor=TEXT, elinewidth=0.9, capsize=2.5)
ax.set_xticks(x); ax.set_xticklabels([n for _, n in COND[1:]], fontsize=7.5); ax.set_ylabel('Control error lost by starting\nat full level anyway, dB'); ax.set_ylim(0, None); clean(ax)
save(fig, 'fig_reconcile')
