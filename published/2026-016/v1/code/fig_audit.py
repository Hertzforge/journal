"""Figure 8, drawn once the audit reports: the audit's verdict on every claim, by kind of claim,
and each effect of the structure on the held-back structures against the study. Reads
data/audit_verdicts.csv (written by audit_fill.py) and data/effects.csv. Copyright 2026 Kevin
Cross. MIT license.

    python3 fig_audit.py [--data DIR] [--figures DIR]
"""
import argparse
import csv
import os

import matplotlib.pyplot as plt

import style
from style import BLUE, GREEN, MUTED, ORANGE, RED, TEXT

ap = argparse.ArgumentParser()
ap.add_argument('--data', default=style.DATA)
ap.add_argument('--figures', default=style.FIGURES)
a = ap.parse_args()
style.FIGURES = a.figures
verdicts = list(csv.DictReader(open(os.path.join(a.data, 'audit_verdicts.csv'))))
effects = {r['id']: r for r in csv.DictReader(open(os.path.join(a.data, 'effects.csv')))}
kinds = ['effect', 'level', 'pair']
names = ['holds', 'weaker', 'does not hold', 'not tested']
look = [(BLUE, None), (GREEN, '..'), (RED, '///'), (MUTED, 'xx')]

fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), gridspec_kw={'width_ratios': [1, 1.3]})
ax = axes[0]
for i, kind in enumerate(kinds):
    g = [v for v in verdicts if v['kind'] == kind]
    left = 0.0
    for name, (color, hatch) in zip(names, look):
        share = sum(v['verdict'] == name for v in g) / len(g) if g else 0
        shown = any(v['verdict'] == name for v in verdicts)  # no legend entry for an empty verdict
        ax.barh(i, share, left=left, color=color, hatch=hatch, edgecolor='white',
                label=name if i == 0 and shown else None)
        left += share
    ax.text(1.02, i, f'{len(g):,}', va='center', fontsize=7, color=TEXT)
ax.set_yticks(range(len(kinds)), ['effects of\nthe structure', 'levels', 'law\ndifferences'])
ax.set_xlim(0, 1.12)
style.percent_axis(ax, 'x')
ax.set_xlabel('share of the claims, percent (number at right)')
ax.set_title('(a) the verdicts', loc='left', color=TEXT)
ax.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=4)

ax = axes[1]
for v in verdicts:
    if v['kind'] != 'effect' or v['audit_median'] == '':
        continue
    e = effects[v['id']]
    color, marker = {'iec_share': (BLUE, 'o'), 'completion': (ORANGE, 's'),
                     'worst_over_db': (GREEN, '^')}[e['reading']]
    scale = 1.0 if e['reading'] == 'worst_over_db' else 100.0
    x, y = float(v['study_median']) * scale, float(v['audit_median']) * scale
    lo, hi = float(v['study_q1']) * scale, float(v['study_q3']) * scale
    ax.plot([lo, hi], [y, y], color=color, lw=0.5, alpha=0.5)
    ax.scatter(x, y, color=color, marker=marker, s=12, lw=0)
ax.plot([-100, 50], [-100, 50], color=MUTED, ls='--', lw=0.8)
ax.set_xlim(-100, 50)
ax.set_ylim(-100, 50)
ax.axhline(0, color=TEXT, lw=0.6)
ax.axvline(0, color=TEXT, lw=0.6)
ax.set_xlabel('study: median difference (bar: quartiles)')
ax.set_ylabel('held-back structures: median difference')
handles = [plt.Line2D([], [], color=BLUE, marker='o', ls='', label='IEC share, points'),
           plt.Line2D([], [], color=ORANGE, marker='s', ls='', label='completion, points'),
           plt.Line2D([], [], color=GREEN, marker='^', ls='', label='worst over-test, dB')]
ax.legend(handles=handles, fontsize=7, loc='upper left')
ax.set_title('(b) the effects of the structure', loc='left', color=TEXT)
fig.tight_layout()
style.save(fig, 'fig8_audit')
