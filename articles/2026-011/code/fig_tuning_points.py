"""Every setting tried in the tuning runs of the three laws: the mean error at the held-out gauges
over the four tuning cases of a system (structures 30 and 31, the linear stage and the strong size of
the level-dependent one). One row of panels a law, one column a system. The law's defaults are the
hatched orange bar and the setting the tuning rule chose is the crossed green one; where the rule
chose the defaults the bar is orange. From ../data/tuning_points.csv (written by tuning_results.py).

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
from matplotlib.patches import Patch

from style import BLUE, GREEN, NEW, ORANGE, TEXT, plt, rows, save

t = rows('tuning_points.csv')
laws = [law for law in NEW if any(r['law'] == law for r in t)]
counts = [sum(1 for r in t if r['law'] == law and r['system'] == '6 x 12') for law in laws]
fig, axes = plt.subplots(len(laws), 2, figsize=(9.6, 0.27 * sum(counts) + 2.2), sharex='row',
                         gridspec_kw={'height_ratios': counts}, squeeze=False)
for row, law in zip(axes, laws):
    for ax, system in zip(row, ('6 x 12', '6 x 6')):
        r = [x for x in t if x['law'] == law and x['system'] == system]
        for i, x in enumerate(r):
            default, chosen = x['setting'] == 'defaults', x['chosen'] == 'yes'
            c, h = (ORANGE, '///') if default else ((GREEN, 'xxx') if chosen else (BLUE, None))
            v = float(x['held_out_db'])
            ax.barh(i, v, height=0.68, color=c, hatch=h, edgecolor='white', linewidth=0.5)
            ax.text(v + 0.05, i, x['held_out_db'], va='center', fontsize=7, color=TEXT)
        ax.set_yticks(range(len(r)))
        ax.set_yticklabels([x['setting'] for x in r] if system == '6 x 12' else [], fontsize=7.5)
        ax.invert_yaxis()
        ax.grid(axis='y', visible=False)
        ax.set_xlim(0, max(float(x['held_out_db']) for x in t if x['law'] == law) * 1.12)
        ax.set_title(f'{law}, {system} system', fontsize=8.5)
for ax in axes[-1]:
    ax.set_xlabel('Mean error at the held-out gauges, dB (lower is better)')
fig.tight_layout()
fig.legend(handles=[Patch(facecolor=ORANGE, hatch='///', edgecolor='white', label='Defaults'),
                    Patch(facecolor=GREEN, hatch='xxx', edgecolor='white', label='Chosen by the tuning rule'),
                    Patch(facecolor=BLUE, edgecolor='white', label='Other settings tried')], fontsize=8, ncol=3,
           loc='lower center', bbox_to_anchor=(0.5, 1.0))
save(fig, 'fig_tuning_points.png')
