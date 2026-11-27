"""Figure 8: the candidates' screen against matrix, cell by cell (test and tier, 6 structures each):
(a) completions, candidate against matrix; (b) the paired median worst over-test, candidate less
matrix; (c) the paired median p95 control error, candidate less matrix. Copyright 2026 Kevin Cross.
MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import TIER_STYLE, TIERS, rows, num, save, TEXT

ARMS = [('family_inverse', 'family_inverse'), ('followed_poles', 'followed_poles'),
        ('level_ladder', 'level_ladder, 2 s rungs'), ('level_ladder_sw', 'level_ladder, whole-sweep rungs'),
        ('rls_dither', 'rls_dither')]
data = [r for r in rows('screen_cells.csv') if r['screen'] == 'G' and r['arm'] in dict(ARMS)]
cells = []
for arm, _ in ARMS:
    for r in data:
        if r['arm'] == arm and (arm, r['test'], r['tier']) not in [c[:3] for c in cells]:
            cells.append((arm, r['test'], r['tier'], r))
cells.sort(key=lambda c: ([a for a, _ in ARMS].index(c[0]), c[1], TIERS.index(c[2])))
y = np.arange(len(cells))[::-1]
fig, axes = plt.subplots(1, 3, figsize=(11, 7.2), sharey=True)
colors = [TIER_STYLE[c[2]][0] for c in cells]
comp = np.array([int(c[3]['completed']) for c in cells])
yard = np.array([int(c[3]['completed_yardstick']) for c in cells])
axes[0].barh(y + 0.18, comp, 0.36, color=colors, label='candidate')
axes[0].barh(y - 0.18, yard, 0.36, color='white', edgecolor=colors, hatch='///', label='yardstick')
axes[0].set_xlim(0, 6.3)
axes[0].set_xlabel('Runs completed, of 6')
axes[0].set_title('(a) Completions', fontsize=9, loc='left')
for ax, key, title in ((axes[1], 'over_test_paired_median_db', '(b) Worst over-test, paired median'),
                       (axes[2], 'p95_paired_median_db', '(c) p95 control error, paired median')):
    v = np.array([num(c[3][key]) for c in cells])
    ax.barh(y, v, 0.6, color=colors)
    ax.axvline(0, color=TEXT, lw=0.8)
    ax.set_xlabel('candidate less yardstick (dB)')
    ax.set_title(title, fontsize=9, loc='left')
axes[1].axvline(1, color=TEXT, lw=0.8, ls='--')
axes[0].set_yticks(y)
axes[0].set_yticklabels([f"{dict(ARMS)[c[0]]}, {c[1]}, {c[2]}" for c in cells], fontsize=7)
from matplotlib.patches import Patch
handles = [Patch(color=TIER_STYLE[t][0], label=t) for t in TIERS] + [
    Patch(facecolor='white', edgecolor=TEXT, hatch='///', label='yardstick (matrix), panel a')]
axes[2].legend(handles=handles, fontsize=7.5, loc='lower right')
fig.tight_layout()
save(fig, 'fig8_screen_g')
