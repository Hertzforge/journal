"""Figure 1: a multi-shaker random test and its control loop, and one line of a reference matrix.

Reads ../data/fig1_setup.csv only. Writes ../figures/fig1_setup.png. A schematic, not a model of
any particular test. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
BLUE, ORANGE, GREEN, PURPLE, GRAY = '#0072B2', '#D55E00', '#009E73', '#CC79A7', '#6b6b6b'

with open(os.path.join(DATA, 'fig1_setup.csv'), newline='') as f:
    rows = list(csv.DictReader(f))
A = [r for r in rows if r['panel'] == 'a']
B = [r for r in rows if r['panel'] == 'b']


def arrow(ax, p, q, color, ls='-', lw=1.5, ms=13):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=ms, color=color, lw=lw,
                                 ls=ls))


fig = plt.figure(figsize=(12, 5.6))
gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1], wspace=0.08)

# (a) the test and the loop
ax = fig.add_subplot(gs[0, 0])
ax.set_title('(a) A random test with several shakers, and its control loop (schematic)',
             fontsize=9.5, loc='left')
ax.set_xlim(-0.6, 9.2)
ax.set_ylim(-0.6, 7.4)
ax.axis('off')
art = next(r for r in A if r['item'] == 'article')
end = next(r for r in A if r['item'] == 'article_end')
x0, y0, x1, y1 = float(art['x']), float(art['y']), float(end['x']), float(end['y'])
ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor='#d9d9d9', edgecolor='black', lw=1))
ax.text(3.65, y0 - 0.32, 'flexible test article', fontsize=8)
comp = next(r for r in A if r['item'] == 'component')
ax.add_patch(Rectangle((float(comp['x']) - 0.35, y1), 0.7, 0.35, facecolor='#9e9e9e',
                       edgecolor='black', lw=1))
for r in A:
    if r['item'] == 'shaker_v':
        x = float(r['x'])
        ax.add_patch(Rectangle((x - 0.42, 0.45), 0.84, 1.1, facecolor='none', edgecolor=BLUE,
                               lw=1.4, hatch='////'))
        ax.plot([x, x], [1.55, y0], color=BLUE, lw=2.2)
        ax.text(x + 0.5, 1.0, r['label'], ha='left', va='center', fontsize=8, color=BLUE)
    elif r['item'] == 'shaker_h':
        x, y = float(r['x']), float(r['y'])
        ax.add_patch(Rectangle((x, y - 0.4), 1.0, 0.8, facecolor='none', edgecolor=BLUE, lw=1.4,
                               hatch='////'))
        ax.plot([x1, x], [y, y], color=BLUE, lw=2.2)
        ax.text(x + 0.5, y - 0.65, r['label'], ha='center', fontsize=8, color=BLUE)
ctrl_pts = []
for r in A:
    if r['item'] == 'control':
        x, y = float(r['x']), float(r['y'])
        ax.plot(x, y + 0.12, marker='^', color=ORANGE, mfc='white', mew=1.6, ms=9)
        ax.text(x, y + 0.42, r['label'], ha='center', fontsize=7.5, color=ORANGE)
        ctrl_pts.append((x, y + 0.6))
    elif r['item'] == 'held_out':
        x, y = float(r['x']), float(r['y'])
        ax.plot(x, y + 0.08, marker='D', color=GREEN, mfc='white', mew=1.6, ms=7)
        ax.text(x, y + 0.45, r['label'], fontsize=7.5, color=GREEN, ha='center')
# the controller
ax.add_patch(FancyBboxPatch((0.2, 4.6), 7.8, 2.45, boxstyle='round,pad=0.05', facecolor='#f4f4f4',
                            edgecolor='black', lw=1))
ax.text(0.4, 6.75, 'Controller, at every frequency line, once a loop', fontsize=8.5,
        fontweight='bold')
ax.text(0.4, 6.3, 'in:   the reference matrix (target spectra, coherences, phases)', fontsize=8)
ax.text(0.4, 5.95, '       the measured response matrix of the control gauges', fontsize=8)
ax.text(0.4, 5.6, '       the frequency response of the setup, from a low-level identification',
        fontsize=8)
ax.text(0.4, 5.15, 'the control law:  works out the next drive matrix', fontsize=8,
        color=PURPLE, fontweight='bold')
ax.text(0.4, 4.8, 'out:  drive signals, random, with the drive matrix\'s spectra and correlations',
        fontsize=8)
for (x, y) in ctrl_pts:
    arrow(ax, (x, y), (x, 4.55), ORANGE, ls='--', lw=1.2, ms=10)
# drive signals leave the controller and run to each shaker's amplifier
ax.plot([0.15, -0.45, -0.45, 8.85, 8.85], [5.3, 5.3, -0.1, -0.1, 2.4], color=BLUE, lw=1.2)
arrow(ax, (8.86, 2.4), (8.33, 2.4), BLUE, lw=1.2, ms=10)
for r in A:
    if r['item'] == 'shaker_v':
        x = float(r['x'])
        arrow(ax, (x, -0.1), (x, 0.43), BLUE, lw=1.2, ms=10)
ax.text(4.2, -0.38, 'drive signals, to each shaker\'s amplifier', ha='center', fontsize=7.5,
        color=BLUE)
ax.plot([], [], color=BLUE, lw=1.4, label='drive to a shaker')
ax.plot([], [], color=ORANGE, lw=1.4, ls='--', label='response of a control gauge')
ax.plot([], [], '^', color=ORANGE, mfc='white', mew=1.6, ms=8, label='control gauge')
ax.plot([], [], 'D', color=GREEN, mfc='white', mew=1.6, ms=7,
        label='held-out gauge (recorded, not controlled)')
ax.legend(fontsize=7.5, loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)

# (b) one line of a reference matrix
ax = fig.add_subplot(gs[0, 1])
ax.set_title('(b) One frequency line of a reference matrix,\n     three control gauges',
             fontsize=9.5, loc='left')
ax.set_xlim(0.4, 3.6)
ax.set_ylim(3.75, 0.25)
ax.set_aspect('equal')
ax.axis('off')
for i in (1, 2, 3):
    ax.text(i, 0.35, 'gauge %d' % i, ha='center', fontsize=8)
    ax.text(0.42, i, 'gauge %d' % i, ha='left', va='center', fontsize=8, rotation=90)
for r in B:
    i, j = int(float(r['x'])), int(float(r['y']))
    if r['item'] == 'auto':
        ax.add_patch(Rectangle((i - 0.45, i - 0.45), 0.9, 0.9, facecolor='#cfe3f2',
                               edgecolor='black', lw=1))
        ax.text(i, i, r['label'].replace(' spectrum', '\nspectrum\n(g$^2$/Hz)'), ha='center',
                va='center', fontsize=7.5)
    else:
        coh, ph = r['label'].split(' / ')
        ax.add_patch(Rectangle((j - 0.45, i - 0.45), 0.9, 0.9, facecolor='#fbe3d3',
                               edgecolor='black', lw=1))
        ax.text(j, i, coh.replace('coherence ', 'coherence\n') + '\n' + ph.replace('phase ', 'phase '),
                ha='center', va='center', fontsize=7.2)
        ax.add_patch(Rectangle((i - 0.45, j - 0.45), 0.9, 0.9, facecolor='white',
                               edgecolor=GRAY, lw=1, ls='--'))
        ax.text(i, j, 'mirror\n(phase\nreversed)', ha='center', va='center', fontsize=7,
                color=GRAY)
ax.text(2.0, 3.65, 'blue: one spectrum per gauge; orange: one coherence\nand phase per pair; the '
        'lower half follows from the upper', ha='center', fontsize=7.5, va='top')

out = os.path.join(HERE, '..', 'figures', 'fig1_setup.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
