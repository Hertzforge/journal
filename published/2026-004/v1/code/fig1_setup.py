"""Figure 1: the simulated structures and their setups.

Reads ../data/fig1_geometry.csv, fig1_development_modes.csv and fig1_development_structures.csv only.
Writes ../figures/fig1_setup.png. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
BLUE, ORANGE, GREEN, PURPLE, GRAY = '#0072B2', '#D55E00', '#009E73', '#CC79A7', '#6b6b6b'


def rows(name):
    with open(os.path.join(DATA, name), newline='') as f:
        return list(csv.DictReader(f))


geo = rows('fig1_geometry.csv')


def plan(ax, structure, title, shaker_size):
    g = [r for r in geo if r['structure'] == structure]
    for r in g:
        if r['item'] in ('beam', 'lap_beam'):
            x, y, x2, y2 = (float(r[k]) for k in ('x_m', 'y_m', 'x2_m', 'y2_m'))
            ax.plot([x, x2], [y, y2], color=GRAY, lw=2.2 if r['item'] == 'beam' else 1.0,
                    ls='-' if r['item'] == 'beam' else (0, (2, 1.5)), zorder=1)
    for r in g:
        if r['item'] == 'lap_joint_line':
            x, y, x2, y2 = (float(r[k]) for k in ('x_m', 'y_m', 'x2_m', 'y2_m'))
            ax.plot([x, x2], [y, y2], color=PURPLE, lw=1.6, ls=(0, (5, 3)), zorder=2)
            ax.annotate('bolted lap joint', (x, y2), xytext=(x + 0.012, y2 + 0.02), fontsize=7.5,
                        color=PURPLE)
    s = shaker_size
    for r in g:
        x, y = float(r['x_m']), float(r['y_m'])
        if r['item'] == 'support_and_shaker':
            ax.add_patch(Rectangle((x - s / 2, y - s / 2), s, s, facecolor='none', edgecolor=BLUE,
                                   lw=1.4, hatch='////', zorder=0))
        elif r['item'] == 'node':
            ax.plot(x, y, 'o', color=GRAY, ms=3, zorder=3)
        elif r['item'] == 'component':
            kg = float(r['value'])
            ax.plot(x, y, 's', color='#3b3b3b', ms=6 + 10 * kg, zorder=4)
            ax.annotate('%.2g kg' % kg, (x, y), xytext=(x + 0.014, y + 0.016), fontsize=7.5)
        elif r['item'] == 'control':
            ax.plot(x, y, marker='^', ls='none', color=ORANGE, mfc='white', mew=1.6, ms=8, zorder=5)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=9.5, loc='left')
    ax.set_xlabel('x (m)', fontsize=8)
    ax.set_ylabel('y (m)', fontsize=8)
    ax.tick_params(labelsize=7.5)
    ax.margins(0.12)


fig = plt.figure(figsize=(11, 8.2))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.05], hspace=0.38, wspace=0.18)

ax = fig.add_subplot(gs[0, 0])
plan(ax, 'panel', '(a) Held-out panel, from above: 4 shakers, 4 controls', 0.05)
ax.plot([], [], 's', color=BLUE, mfc='none', mew=1.4, ms=10, label='base block with its shaker below')
ax.plot([], [], '^', color=ORANGE, mfc='white', mew=1.6, ms=8, label='control accelerometer')
ax.plot([], [], 's', color='#3b3b3b', ms=8, label='component (lumped mass)')
ax.plot([], [], color=GRAY, lw=2.2, label='panel beams (grillage)')
ax.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)

# (b) side view: schematic, not to scale
ax = fig.add_subplot(gs[0, 1])
ax.set_title('(b) The panel, side view (schematic, not to scale)', fontsize=9.5, loc='left')
xs = [0.0, 1.0, 2.0, 3.0]
ax.add_patch(Rectangle((-0.25, 2.0), 3.5, 0.18, facecolor='#d9d9d9', edgecolor='black', lw=1))
ax.text(1.5, 2.33, 'panel, 1.87 kg, two components', ha='center', fontsize=7.5)
ax.plot([1.5, 1.5], [1.95, 2.23], color=PURPLE, lw=2.0, ls=(0, (3, 2)))
for k, x in enumerate([0.0, 3.0]):
    # bracket spring and joint between panel corner and base block
    ax.plot([x - 0.08, x - 0.08], [1.45, 2.0], color='black', lw=1)
    ax.plot([x + 0.08, x + 0.08], [1.45, 2.0], color=PURPLE, lw=2.2)
    ax.add_patch(Rectangle((x - 0.25, 1.1), 0.5, 0.35, facecolor='none', edgecolor=BLUE, lw=1.4,
                           hatch='////'))
    for dx in (-0.12, 0.12):
        zz = [1.1, 1.0, 0.92, 0.84, 0.76, 0.68, 0.6]
        xx = [x + dx + (0.05 if i % 2 else -0.05) * (0 < i < len(zz) - 1) for i in range(len(zz))]
        ax.plot(xx, zz, color='black', lw=0.9)
    ax.add_patch(FancyArrowPatch((x, 0.15), (x, 0.55), arrowstyle='-|>', mutation_scale=14,
                                 color=BLUE, lw=1.6))
    ax.plot(x, 2.2, marker='^', color=ORANGE, mfc='white', mew=1.6, ms=8)
ax.plot([0.25, 2.75], [1.27, 1.27], color='black', lw=0.8, ls=(0, (1, 2)))
ax.text(1.5, 0.98, 'fixture springs join the blocks in a ring', ha='center', fontsize=7)
ax.text(1.5, 1.78, 'bolted lap joint in the panel', ha='center', fontsize=7, color=PURPLE)
ax.text(-0.25, 0.85, 'soft\nsuspension', fontsize=7, ha='right')
ax.text(3.35, 1.62, 'bracket spring (thin)\nand joint (thick)', fontsize=7, color=PURPLE, va='center')
ax.text(3.35, 1.27, 'base block', fontsize=7, color=BLUE, va='center')
ax.text(3.35, 0.33, 'shaker force', fontsize=7, color=BLUE, va='center')
ax.text(3.35, 2.2, 'control', fontsize=7, color=ORANGE, va='center')
ax.plot([-0.5, 3.5], [0.6, 0.6], color='black', lw=1.5)
ax.set_xlim(-0.9, 4.5)
ax.set_ylim(0.0, 2.6)
ax.axis('off')

ax = fig.add_subplot(gs[1, 0])
plan(ax, 'frame', '(c) Held-out frame, from above: 8 shakers, 12 controls', 0.05)

# (d) the development set: modal models only
ax = fig.add_subplot(gs[1, 1])
ax.set_title('(d) The development set: modal models only, 4 shakers, 4 controls', fontsize=9.5, loc='left')
modes = rows('fig1_development_modes.csv')
recs = {r['structure']: r for r in rows('fig1_development_structures.csv')}
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
for k in range(4):
    y = 8.6 - 1.25 * k
    ax.add_patch(FancyArrowPatch((0.2, y), (2.2, y), arrowstyle='-|>', mutation_scale=12,
                                 color=BLUE, lw=1.4))
    ax.text(0.2, y + 0.2, 'shaker %d' % (k + 1), fontsize=7, color=BLUE)
    ax.add_patch(FancyArrowPatch((7.6, y), (9.6, y), arrowstyle='-|>', mutation_scale=12,
                                 color=ORANGE, lw=1.4, ls='--'))
    ax.text(7.7, y + 0.2, 'control %d' % (k + 1), fontsize=7, color=ORANGE)
ax.add_patch(Rectangle((2.3, 4.2), 5.2, 5.0, facecolor='#f2f2f2', edgecolor='black', lw=1))
txt = ['seven share these 8 modes:',
       '   ' + ', '.join('%g' % float(m['frequency_hz']) for m in modes[:4]) + ',',
       '   ' + ', '.join('%g' % float(m['frequency_hz']) for m in modes[4:]) + ' Hz,',
       '   damping %g to %g %%' % (100 * min(float(m['damping_ratio']) for m in modes),
                                   100 * max(float(m['damping_ratio']) for m in modes)),
       'in four, each mode\'s frequency falls',
       '   with its own recent amplitude']
for i, t in enumerate(txt):
    ax.text(2.5, 8.75 - 0.72 * i, t, fontsize=7.5)
lines = [('linear', 'no change'),
         ('moderate', '%.0f %% drop, damping doubles' % (100 * float(recs['moderate']['mode_drop']))),
         ('severe', '%.0f %% drop, stops growing at -21 dB' % (100 * float(recs['severe']['mode_drop']))),
         ('non-saturating', '%.0f %% drop, still growing at full level' % (100 * float(recs['nonsat']['mode_drop']))),
         ('late', '%.0f %% drop, grows as amplitude squared' % (100 * float(recs['late']['mode_drop']))),
         ('springs', 'stiffness falls %.0f %% and %.0f %% inside each cycle'
          % (100 * float(recs['spring16']['spring_stiffness_drop']), 100 * float(recs['spring32']['spring_stiffness_drop']))),
         ('research', 'a separate model: %d modes, %s Hz, %.0f Hz sampling,'
          % (len(recs['research']['modes_hz'].split()), recs['research']['modes_hz'].replace(' ', ', '),
             float(recs['research']['sample_rate_hz']))),
         ('', 'its own target; %.0f %% drop set by the level' % (100 * float(recs['research']['mode_drop'])))]
for i, (a, b) in enumerate(lines):
    ax.text(0.3, 3.5 - 0.5 * i, a + (':' if a else ''), fontsize=7.5, fontweight='bold')
    ax.text(3.0, 3.5 - 0.5 * i, b, fontsize=7.5)

out = os.path.join(HERE, '..', 'figures', 'fig1_setup.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
