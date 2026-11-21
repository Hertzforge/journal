"""The independent drive law on the eight tuning cases, three ways of solving for the drive levels:
the published rule (a negative level set to zero), the non-negative solve with the weighting by the
target, and the non-negative solve without it (the law's defaults). Top: the mean error at the
held-out gauges over the four cases of a system. Bottom: the level error, the mean over the four
cases with a line from the smallest to the largest. From ../data/tuning_points.csv (written by
tuning_results.py).

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
from style import BLUE, ORANGE, TEXT, YELLOW, plt, rows, save

WAYS = [('solve = set_to_zero', 'Published rule\n(negative set to zero)', YELLOW, '...'),
        ('solve_weighting = target', 'Non-negative solve,\ntarget weighting on', BLUE, '\\\\\\'),
        ('defaults', 'Non-negative solve,\nno weighting (defaults)', ORANGE, '///')]
t = [r for r in rows('tuning_points.csv') if r['law'] == 'independent']
fig, axes = plt.subplots(2, 2, figsize=(8.6, 5.6), sharex=True, sharey='row')
for col, system in enumerate(('6 x 12', '6 x 6')):
    for i, (setting, name, c, h) in enumerate(WAYS):
        r = [x for x in t if x['system'] == system and x['setting'] == setting][0]
        axes[0][col].bar(i, float(r['held_out_db']), width=0.62, color=c, hatch=h, edgecolor='white', linewidth=0.5)
        axes[0][col].text(i, float(r['held_out_db']) + 0.15, r['held_out_db'], ha='center', fontsize=8, color=TEXT)
        lo, hi = float(r['level_min_db']), float(r['level_max_db'])
        axes[1][col].bar(i, float(r['level_mean_db']), width=0.62, color=c, hatch=h, edgecolor='white', linewidth=0.5)
        axes[1][col].plot([i, i], [lo, hi], color=TEXT, lw=1.2)
    axes[0][col].set_title(system + ' system', fontsize=9)
    axes[1][col].axhline(0, color=TEXT, lw=0.8)
    axes[1][col].set_xticks(range(len(WAYS)))
    axes[1][col].set_xticklabels([w[1] for w in WAYS], fontsize=7.5)
    for ax in (axes[0][col], axes[1][col]):
        ax.grid(axis='x', visible=False)
axes[0][0].set_ylabel('Error at the held-out gauges, dB\n(lower is better)')
axes[1][0].set_ylabel('Level error, dB\n(zero is on level; below zero is low)')
axes[0][0].set_ylim(0, 10.5)
fig.tight_layout()
save(fig, 'fig_tuning_independent.png')
