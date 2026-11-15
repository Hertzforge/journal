"""Figure 2: four mode shapes of the test article, free on its lab suspension (seed 0, unit B).

Reads ../data/model_nodes.csv, model_elements.csv and model_mode_shapes.csv only.
Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'data')
nodes = [r for r in csv.DictReader(open(os.path.join(D, 'model_nodes.csv'))) if r['structure'] == 'article']
X = np.array([[float(r['x_m']), float(r['y_m']), float(r['z_m'])] for r in nodes])
els = [r for r in csv.DictReader(open(os.path.join(D, 'model_elements.csv'))) if r['structure'] == 'article']
shapes = list(csv.DictReader(open(os.path.join(D, 'model_mode_shapes.csv'))))
modes = []
for r in shapes:
    if r['mode'] not in [m[0] for m in modes]:
        modes.append((r['mode'], float(r['f_hz']), float(r['component_energy_share'])))
SCALE = 0.08  # m of drawn deflection for the largest translation

fig = plt.figure(figsize=(12, 4.0))
for i, (mode, f, share) in enumerate(modes):
    U = np.array([[float(r['ux']), float(r['uy']), float(r['uz'])] for r in shapes if r['mode'] == mode])
    Y = X + SCALE * U
    ax = fig.add_subplot(1, 4, i + 1, projection='3d')
    for e in els:
        a, b = int(e['node_i']), int(e['node_j'])
        ax.plot(*X[[a, b]].T, color='0.6', lw=1.0, ls=':')
        stalk = e['group'] == 'stalk'
        ax.plot(*Y[[a, b]].T, color='#D55E00' if stalk else '#0072B2', lw=2.4 if stalk else 1.6,
                ls='--' if stalk else '-')
    lo, hi = X.min(0) - 0.08, X.max(0) + 0.08; c = (lo + hi) / 2; r = (hi - lo).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1)); ax.set_axis_off(); ax.view_init(22, -58)
    kind = 'component' if share > 0.5 else 'chassis'
    ax.set_title(f'Mode {mode}, {f:.0f} Hz\n{kind} mode\n({share * 100:.0f} % of energy in components)', fontsize=9)
ax = fig.axes[0]
ax.plot([], [], color='0.6', ls=':', label='Undeformed')
ax.plot([], [], color='#0072B2', ls='-', label='Chassis, deformed')
ax.plot([], [], color='#D55E00', ls='--', lw=2.4, label='Component, deformed')
fig.legend(*ax.get_legend_handles_labels(), loc='lower center', ncol=3, fontsize=8, frameon=False)
fig.tight_layout(rect=(0, 0.06, 1, 1))
out = os.path.join(HERE, '..', 'figures', 'fig2_mode_shapes.png')
fig.savefig(out, dpi=150)
print('wrote', out)
