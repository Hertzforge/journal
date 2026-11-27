"""Figure 2: the first screen, candidate against its yardstick on every test and tier: (a) sweeps or
dwells completed of six, (b) the paired median of the worst over-test.
data=screen_cells.csv. Copyright 2026 Kevin Cross. MIT license."""
import math
import matplotlib.pyplot as plt
from style import rows, save, ARM_STYLE, ARM_LABEL, BLUE, MUTED, TEXT, panel

r = [x for x in rows('screen_cells.csv') if x['screen'] == 'G' and x['arm'] in ('family_inverse', 'level_ladder', 'level_ladder_sw', 'rls_dither')]
order = {'family_inverse': 0, 'level_ladder': 1, 'level_ladder_sw': 2, 'rls_dither': 3}
tiers = {'linear': 0, 'realistic': 1, 'strong': 2}
r.sort(key=lambda x: (order[x['arm']], x['test'], tiers[x['tier']]))
fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 7.0), sharey=True, gridspec_kw={'width_ratios': [1, 1.2]})
labels, y, prev = [], 0, None
ys = []
for x in r:
    if prev is not None and x['arm'] != prev:
        y += 0.8
    prev = x['arm']
    ys.append(y)
    labels.append(f'{ARM_LABEL[x["arm"]]}, {x["test"]} {x["tier"]}')
    y += 1
for x, yy in zip(r, ys):
    color, marker = ARM_STYLE[x['arm']]
    c, m = int(x['completed']), int(x['completed_yardstick'])
    a.plot([m, c], [yy, yy], color=MUTED, lw=1)
    a.scatter([m], [yy], s=34, facecolors='white', edgecolors=BLUE, marker='o', zorder=3)
    a.scatter([c], [yy], s=40, color=color, marker=marker, zorder=4)
    ov = x['over_test_paired_median_db']
    if ov != '':
        b.scatter([float(ov)], [yy], s=40, color=color, marker=marker, zorder=4)
    else:
        b.text(2.0, yy, 'no pair with both runs scored', va='center', fontsize=7, color=MUTED)
a.set_yticks(ys)
a.set_yticklabels(labels, fontsize=7.5)
a.invert_yaxis()
a.set_xlim(-0.5, 6.5)
a.set_xticks(range(7))
a.set_xlabel('runs completed, of 6')
a.scatter([], [], s=34, facecolors='white', edgecolors=BLUE, marker='o', label='yardstick (matrix)')
a.scatter([], [], s=40, color=MUTED, marker='s', label='candidate')
a.legend(loc='lower center', bbox_to_anchor=(0.5, 1.03), ncol=2, fontsize=8)
panel(a, 'a')
b.axvline(0, color=TEXT, lw=0.8)
b.axvline(1, color=MUTED, lw=1, ls='--')
b.text(2.0, ys[-1] + 0.6, 'the rule allowed +1 dB', fontsize=7.5, color=MUTED, va='center')
b.set_xlabel('worst over-test, candidate less yardstick, paired median (dB)')
panel(b, 'b')
save(fig, 'fig2_first_screen')
