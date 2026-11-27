"""Figure 9: the predictive leads' screen against followed_poles, on the six nonlinear cells (T1, T2 and T5;
realistic and strong; 6 structures each): (a) completions of 36, every arm; (b) the paired median
worst over-test, lead less followed_poles, cell by cell; (c) the paired median p95 control error, lead less
followed_poles.
Copyright 2026 Kevin Cross. MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import TIER_STYLE, BLUE, ORANGE, MUTED, rows, num, facts, save, TEXT

f = facts()
ARMS = ['matrix', 'followed_poles', 'pole_trajectory', 'amplitude_indexed', 'placed_poles', 'preview',
        'preview_frozen']
LABEL = {a: a for a in ARMS}
fig, axes = plt.subplots(1, 3, figsize=(11, 3.8), gridspec_kw={'width_ratios': [1, 1.6, 1.6]})
done = [int(f[f'J_{a}_completed_nonlinear']) for a in ARMS]
runs = [int(f[f'J_{a}_runs_nonlinear']) for a in ARMS]
colors = [BLUE if a == 'matrix' else ORANGE if a == 'followed_poles' else MUTED for a in ARMS]
axes[0].bar(range(len(ARMS)), done, color=colors)
for k, (d, n) in enumerate(zip(done, runs)):
    axes[0].text(k, d + 0.4, f'{d}', ha='center', fontsize=7)
axes[0].set_xticks(range(len(ARMS)))
axes[0].set_xticklabels([LABEL[a] for a in ARMS], fontsize=7.5, rotation=40, ha='right',
                        rotation_mode='anchor')
axes[0].set_ylabel(f'Runs completed, of {runs[0]}')
axes[0].set_title('(a) Completions', fontsize=9, loc='left')
data = [r for r in rows('screen_cells.csv') if r['screen'] == 'J' and r['yardstick'] == 'followed_poles'
        and r['tier'] != 'linear']
LEADS = ['pole_trajectory', 'amplitude_indexed', 'placed_poles', 'preview', 'preview_frozen']
cells = [(t, tier) for t in ('T1', 'T2', 'T5') for tier in ('realistic', 'strong')]
for ax, key, title in ((axes[1], 'over_test_paired_median_db', '(b) Worst over-test, lead less followed_poles'),
                       (axes[2], 'p95_paired_median_db', '(c) p95 control error, lead less followed_poles')):
    w = 0.14
    for k, lead in enumerate(LEADS):
        by = {(r['test'], r['tier']): r for r in data if r['arm'] == lead}
        v = [num(by[c][key]) for c in cells]
        ax.bar(np.arange(len(cells)) + (k - 2) * w, v, w,
               color=[TIER_STYLE[c[1]][0] for c in cells], alpha=0.35 + 0.13 * k, edgecolor='white',
               hatch=['', '///', '...', 'xxx', '---'][k], label=lead)
    ax.axhline(0, color=TEXT, lw=0.8)
    ax.set_xticks(range(len(cells)))
    ax.set_xticklabels([f'{t}\n{tier}' for t, tier in cells], fontsize=7.5)
    ax.set_ylabel('dB')
    ax.set_title(title, fontsize=9, loc='left')
axes[1].axhline(1, color=TEXT, lw=0.8, ls='--')
handles, labels = axes[2].get_legend_handles_labels()
fig.legend(handles, labels, fontsize=7, ncol=5, loc='lower center', title='bars left to right; blue realistic, orange strong', title_fontsize=7)
fig.tight_layout(rect=(0, 0.13, 1, 1))
save(fig, 'fig9_screen_j')
