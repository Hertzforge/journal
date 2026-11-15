"""Figure 2: published work on shock testing with several shakers, by year and kind.

Reads ../data/fig2_timeline.csv only. Writes ../figures/fig2_timeline.png.
Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, '..', 'data', 'fig2_timeline.csv'), newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Each kind has its own band, its own marker and its own color, so color is never the only cue.
LANES = [
    ('Waveform replication with several drives', 'o', '#0072B2'),
    ('One shaker, SRS at several points', 's', '#E69F00'),
    ('SRS with several drives', 'D', '#D55E00'),
    ('Shock on random vibration', '^', '#009E73'),
    ('Six-degree-of-freedom tables and resonant plates', 'v', '#CC79A7'),
    ('Learning-based', 'P', '#56B4E9'),
    ("Controller makers' descriptions", 'X', '#000000'),
]
READ = {'read in full', 'read in part'}
BREAK = 1990                      # the axis is broken between the 1970s and 2001
YEARS_PER_CHAR = {0: 0.24, 1: 0.23}  # label width in years per character, for each panel
SUB = 0.8                         # spacing of the sub-rows that keep labels apart
TITLE = 0.95                      # height of the row that carries a band's title


def place(items):
    """Put each label in the first sub-row where it does not run into the previous label."""
    ends, out = [], []
    for r in items:
        yr = int(r['year'])
        panel = 0 if yr < BREAK else 1
        start = yr - 0.3
        width = 0.5 + YEARS_PER_CHAR[panel] * len(r['label'])
        sub = next((i for i, e in enumerate(ends) if e[panel] < start), None)
        if sub is None:
            ends.append({0: -1e9, 1: -1e9})
            sub = len(ends) - 1
        ends[sub][panel] = start + width + 1.0
        out.append((r, panel, sub))
    return out, max(1, len(ends))


fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(11.5, 8.4), sharey=True,
                               gridspec_kw=dict(width_ratios=[1.7, 5.8], wspace=0.03))
axes = (ax0, ax1)
ax1.patch.set_visible(False)
ax0.set_zorder(2)
top = 0.0
for lane, marker, color in LANES:
    items = sorted([r for r in rows if r['lane'] == lane], key=lambda r: (int(r['year']), r['label']))
    placed, nsub = place(items)
    ax0.text(1974.7, top - 0.15, lane, fontsize=8.3, fontweight='bold', color=color, va='top', ha='left',
             zorder=5, clip_on=False)
    first = top - TITLE
    for r, panel, sub in placed:
        ax = axes[panel]
        yr = int(r['year'])
        yy = first - SUB * sub
        filled = r['access'] in READ
        ax.plot([yr], [yy], ls='none', marker=marker, ms=7.5, mec=color, mew=1.6,
                mfc=color if filled else 'white', zorder=3)
        ax.text(yr + 0.42, yy, r['label'], fontsize=6.9, va='center', color='#222222', zorder=4)
    bottom = first - SUB * (nsub - 1) - 0.55
    for ax in axes:
        ax.axhline(bottom, color='#c8c8c8', lw=0.7)
    top = bottom

ax0.set_xlim(1974.5, 1986.0)
ax1.set_xlim(2001.0, 2032.8)
ax0.set_xticks([1975, 1980])
ax1.set_xticks(list(range(2002, 2028, 2)))
for ax in axes:
    ax.tick_params(axis='x', labelsize=7.6)
    ax.set_yticks([])
    ax.grid(True, axis='x', alpha=0.25)
ax0.set_ylim(top - 0.1, 0.25)
ax0.spines['right'].set_visible(False)
ax1.spines['left'].set_visible(False)
# Break marks on the bottom axis.
for ax, x in ((ax0, 1.0), (ax1, 0.0)):
    ax.plot([x - 0.012 if ax is ax0 else x - 0.004, x + 0.012 if ax is ax0 else x + 0.004],
            [-0.012, 0.012], transform=ax.transAxes, color='#333333', lw=1.0, clip_on=False)
fig.supxlabel('Year the work first appeared (online, presented or filed); the axis is broken between 1986 and 2001',
              fontsize=8.5, y=0.045)
handles = [Line2D([], [], ls='none', marker='o', ms=7.5, mfc='#555555', mec='#555555',
                  label='filled: read in full or in part'),
           Line2D([], [], ls='none', marker='o', ms=7.5, mfc='white', mec='#555555',
                  label='open: abstract or record only')]
fig.legend(handles=handles, fontsize=7.8, loc='lower center', ncol=2, frameon=False,
           bbox_to_anchor=(0.5, -0.005))
out = os.path.join(HERE, '..', 'figures', 'fig2_timeline.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
