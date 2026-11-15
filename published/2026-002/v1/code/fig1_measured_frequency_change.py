"""Figure 1: measured change of a resonance frequency with level, by joint condition and excitation.

Reads ../data/fig1_measured_frequency_change.csv only. Writes ../figures/fig1_measured_frequency_change.png.
Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, '..', 'data', 'fig1_measured_frequency_change.csv'), newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Groups keep the file's order. Color marks the group, and each group also has its own header line,
# so color is never the only cue.
GROUP_COLOR = {
    'Well-tightened bolted joints': '#0072B2',
    'Lightly torqued or friction joints': '#D55E00',
    'Bolted joint in macroslip': '#CC79A7',
    'Measured at shock level': '#009E73',
    'Bolted joint hardening, cause not identified': '#56B4E9',
    'Geometry (stretching or curvature)': '#000000',
}
# The marker says how the structure was excited.
MARKER = {
    'hammer': ('o', 'hammer'),
    'shaker': ('s', 'shaker (sine, random or force appropriation)'),
    'shaker shock': ('^', 'shaker shock pulses'),
    'hammer and projectile shock': ('D', 'hammer test against projectile shock'),
    'hammer and shaker': ('P', 'hammer test against shaker'),
}

groups = []
for r in rows:
    if r['group'] not in groups:
        groups.append(r['group'])

y = 0.0
ticks, labels, heads = [], [], []
placed = []
for g in groups:
    heads.append((y, g))
    y -= 1.0
    for r in [r for r in rows if r['group'] == g]:
        placed.append((y, r))
        ticks.append(y)
        labels.append(f"{r['case']}\n{r['source']}")
        y -= 1.0
    y -= 0.4

fig, ax = plt.subplots(figsize=(8.4, 12.0))
ax.axvspan(-4.0, -0.1, color='#e3e3e3', zorder=0)
ax.axvline(0, color='#555555', lw=0.9, zorder=1)
for yy, r in placed:
    lo, hi = float(r['change_low_percent']), float(r['change_high_percent'])
    color = GROUP_COLOR[r['group']]
    marker = MARKER[r['excitation']][0]
    filled = r['read_from'] == 'text'
    face = color if filled else 'white'
    if hi > lo:
        ax.plot([lo, hi], [yy, yy], color=color, lw=2.2, solid_capstyle='butt', zorder=2)
        ax.plot([lo, hi], [yy, yy], ls='none', marker=marker, ms=7, mfc=face, mec=color, mew=1.5, zorder=3)
    else:
        ax.plot([lo], [yy], ls='none', marker=marker, ms=7.5, mfc=face, mec=color, mew=1.5, zorder=3)
for yy, g in heads:
    ax.text(-30.6, yy, g, fontsize=9.2, fontweight='bold', color=GROUP_COLOR[g], va='center')
ax.text(-2.0, 0.55, 'shaded: about 0.1 to 4 %', fontsize=8.0, ha='center', va='bottom', color='#3b3b3b')
ax.set_yticks(ticks)
ax.set_yticklabels(labels, fontsize=8.0, linespacing=1.15)
ax.set_ylim(y - 0.2, 1.5)
ax.set_xlim(-31, 35)
ax.set_xlabel('Change of the resonance frequency,\nfrom low level to the highest level tested (%)', fontsize=9.0)
ax.tick_params(axis='x', labelsize=8.5)
ax.grid(True, axis='x', alpha=0.3)

handles = [Line2D([], [], ls='none', marker=m, ms=7, mfc='#7a7a7a', mec='#333333', label=lab)
           for m, lab in MARKER.values()]
handles += [Line2D([], [], ls='none', marker='o', ms=7, mfc='#333333', mec='#333333',
                   label='filled: number stated in the text'),
            Line2D([], [], ls='none', marker='o', ms=7, mfc='white', mec='#333333',
                   label='open: read off a figure axis (approximate)'),
            Line2D([], [], color='#333333', lw=2.2, label='bar: a range of modes, assemblies or tests')]
ax.legend(handles=handles, fontsize=7.8, loc='upper right', frameon=True, framealpha=0.95)
out = os.path.join(HERE, '..', 'figures', 'fig1_measured_frequency_change.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
