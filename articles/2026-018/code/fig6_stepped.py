"""Figure 6: the stepped sine in the study. (a) How each of the 380 stepped sines of matrix, paired
and ratio ended (Hertzforge version). (b) For each structure, the share of steps and control-shaker
pairs at which a control's paired shaker is its largest path, against one over the number of
shakers. data=fig6_stepped_runs.csv, fig6_coupling.csv. Copyright 2026 Kevin Cross. MIT license."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from style import rows, save, SYSTEM, SYSTEM_ORDER, TIER_STYLE, TEXT, MUTED, GREEN, ORANGE, YELLOW, PURPLE, panel

runs = [x for x in rows('fig6_stepped_runs.csv') if x['test'] == 'T3']
coup = rows('fig6_coupling.csv')
fig, (a, b) = plt.subplots(1, 2, figsize=(7.6, 3.4), gridspec_kw={'width_ratios': [1.15, 1]})
classes = [('completed', GREEN, '', lambda x: x['outcome'] == 'completed'),
           ('stopped at -12 dB', ORANGE, '...', lambda x: x['outcome'] != 'completed' and x['ended_at_level_db'] == '-12.0'),
           ('stopped at -9 to -3 dB', YELLOW, 'xx', lambda x: x['outcome'] != 'completed' and x['ended_at_level_db'] in ('-9.0', '-6.0', '-3.0')),
           ('stopped at full level (aborted or a law fault)', TEXT, '++', lambda x: x['outcome'] != 'completed' and x['ended_at_level_db'] == '0.0'),
           ('held by the identification', MUTED, '//', lambda x: x['outcome'] == 'held_by_identification')]
laws = ['matrix', 'paired', 'ratio']
for i, law in enumerate(laws):
    left = 0
    rs = [x for x in runs if x['law'] == law]
    for name, color, hatch, test in classes:
        n = sum(1 for x in rs if test(x))
        if n:
            a.barh(i, n, left=left, color=color, hatch=hatch, edgecolor='white', height=0.65)
            if n >= 15:
                a.text(left + n / 2, i, str(n), ha='center', va='center', fontsize=7.5, color=TEXT,
                       bbox=dict(facecolor='white', edgecolor='none', pad=1))
        left += n
a.set_yticks(range(len(laws)))
a.set_yticklabels(laws)
a.invert_yaxis()
a.set_xlim(0, len([x for x in runs if x['law'] == 'matrix']))
a.set_xlabel('stepped sines (T3), of 380 structures')
a.legend(handles=[Patch(facecolor=c, hatch=h, edgecolor='white', label=n) for n, c, h, _ in classes],
         loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=7.5)
a.grid(axis='y', visible=False)
panel(a, 'a')
rng = np.random.default_rng(2)
for i, system in enumerate(SYSTEM_ORDER):
    for tier in ('linear', 'realistic', 'strong'):
        y = [float(x['share_own_shaker_largest']) for x in coup if x['system'] == system and x['kind'] == tier]
        if y:
            color, _, marker = TIER_STYLE[tier]
            b.scatter(i + rng.uniform(-0.25, 0.25, len(y)), y, s=8, color=color, marker=marker, alpha=0.6,
                      linewidths=0, label=tier if i == 0 else None)
    chance = float(next(x['one_over_drives'] for x in coup if x['system'] == system))
    b.plot([i - 0.38, i + 0.38], [chance, chance], color=TEXT, lw=2,
           label='one over the number of shakers' if i == 0 else None)
b.set_xticks(range(len(SYSTEM_ORDER)))
b.set_xticklabels([SYSTEM[s] for s in SYSTEM_ORDER], fontsize=8)
b.set_xlabel('system (shakers x controls)')
b.set_ylabel('paired shaker is the largest path (%)')
from style import percent_axis
percent_axis(b)
b.set_ylim(0, 1)
b.legend(fontsize=7.5, loc='upper center', ncol=2, bbox_to_anchor=(0.5, 1.0))
b.grid(axis='x', visible=False)
panel(b, 'b')
fig.subplots_adjust(wspace=0.38)
save(fig, 'fig6_stepped')
