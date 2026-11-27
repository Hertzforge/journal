"""Figure 7: (a) the same cases at the engine's default protections and 9 V ceiling against the
runs of record; (b) the runs of the repeat sets, each with its own noise sequence, against the run
of record. Reads data/defaults.csv and data/repeats.csv. Copyright 2026 Kevin Cross. MIT license."""
from collections import defaultdict

import matplotlib.pyplot as plt

from style import BLUE, MUTED, ORANGE, TEXT, num, percent_axis, rows, save

defaults = rows('defaults.csv')
repeats = rows('repeats.csv')
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), gridspec_kw={'width_ratios': [1, 1.7]})
ax = axes[0]
for version, color, marker in (('hertzforge', BLUE, 'o'), ('python', ORANGE, 's')):
    g = [r for r in defaults if r['version'] == version]
    ax.scatter([num(r['iec_study']) for r in g], [num(r['iec_defaults']) for r in g], s=12,
               color=color, marker=marker, alpha=0.7, lw=0,
               label='Hertzforge version' if version == 'hertzforge' else 'Python version')
ax.plot([0, 1], [0, 1], color=MUTED, ls='--', lw=0.8)
ax.set_xlabel('IEC share, run of record (widened)')
ax.set_ylabel('IEC share, engine defaults')
percent_axis(ax, 'x')
percent_axis(ax, 'y')
ax.set_title('(a) the default protections', loc='left', color=TEXT)
ax.legend(fontsize=7, loc='upper left')

ax = axes[1]
units = defaultdict(list)
for r in repeats:
    units[(r['version'], r['unit'])].append(r)
keys = sorted(units, key=lambda k: (k[0], k[1]))
for i, k in enumerate(keys):
    g = units[k]
    color, marker = (BLUE, 'o') if k[0] == 'hertzforge' else (ORANGE, 's')
    if g[0]['iec_study'] != '':
        ax.scatter(i, num(g[0]['iec_study']), color='black', marker='_', s=90, lw=1.5, zorder=3)
    ax.scatter([i] * len(g), [num(r['iec_share']) for r in g], color=color, marker=marker, s=12,
               alpha=0.8, lw=0)
n_hf = sum(k[0] == 'hertzforge' for k in keys)
ax.axvline(n_hf - 0.5, color=MUTED, lw=0.8)
ax.text(n_hf / 2, 1.04, 'Hertzforge version', ha='center', fontsize=7, color=BLUE)
ax.text(n_hf + (len(keys) - n_hf) / 2, 1.04, 'Python version', ha='center', fontsize=7, color=ORANGE)
ax.set_xticks([])
ax.set_xlabel('one run of a problem, test and law (black bar: run of record; markers: repeats)')
ax.set_ylabel('IEC share')
ax.set_ylim(-0.03, 1.1)
percent_axis(ax)
ax.set_title('(b) another noise sequence', loc='left', color=TEXT)
fig.tight_layout()
save(fig, 'fig7_defaults_repeats')
