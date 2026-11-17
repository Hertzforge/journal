"""Draws the article's two result figures (Figure 1 is drawn by fig_setups.py) from the files in ../data into ../figures.

    PYTHONDONTWRITEBYTECODE=1 python figures.py

fig_paired.png        control-gauge error against stress error, structure by structure, as the setup changes
                      (data/fig_paired_setups.csv)
fig_what_tracks.png   stress error against the control-gauge and held-out-gauge errors, run by run
                      (data/fig_what_tracks.csv)

Series are told apart by marker or line style as well as color. Needs NumPy and matplotlib.
Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
FIG = os.path.join(HERE, '..', 'figures')
BLUE, ORANGE, GREEN, YELLOW, PINK = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4'
TEXT, MUTED, GRID = '#10161d', '#566372', '#e2e8ef'
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'], 'font.size': 9,
                     'axes.edgecolor': '#c9d3df', 'axes.labelcolor': TEXT, 'xtick.color': TEXT, 'ytick.color': TEXT,
                     'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8, 'legend.frameon': False, 'savefig.dpi': 200})


def rows(name):
    return list(csv.DictReader(open(os.path.join(DATA, name), newline='')))


def save(fig, name):
    os.makedirs(FIG, exist_ok=True)
    fig.savefig(os.path.join(FIG, name), bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('wrote', name)


def fig_paired():
    t = rows('fig_paired_setups.csv')
    by = defaultdict(dict)
    for r in t:
        by[(r['law'], int(r['seed']))][r['setup']] = (float(r['control_band_rms']), float(r['stress_rms']))
    style = {'3x12': ('v', GREEN, 'none'), '6x12': ('o', BLUE, 'none'), '12x12': ('s', ORANGE, None), '6x6': ('D', PINK, None)}
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 7.6), sharey=True)
    for col, (law, lname) in enumerate((('pinv_closed', 'the default law, which inverts the whole measured response'),
                                         ('band_average', 'the band-average law'))):
        for row, chain in enumerate((('3x12', '6x12', '12x12'), ('6x12', '6x6'))):
            ax = axes[row, col]
            for (lw, seed), d in by.items():
                if lw != law:
                    continue
                xs = [d[s][0] for s in chain]
                ys = [d[s][1] for s in chain]
                ax.plot(xs, ys, color='#b7c1cc', lw=0.8, zorder=1)
            for s in chain:
                m, c, f = style[s]
                pts = np.array([d[s] for (lw, _), d in by.items() if lw == law])
                lab = {'3x12': '3 shakers, 12 control gauges', '6x12': '6 shakers, 12 control gauges',
                       '12x12': '12 shakers, 12 control gauges', '6x6': '6 shakers, 6 control gauges'}[s]
                ax.plot(pts[:, 0], pts[:, 1], m, ls='none', color=c, mfc=f if f else c, mec=c, mew=1.3, ms=6, label=lab, zorder=3)
            ax.set_xlabel('Control-gauge error, per gauge in one-third-octave bands, RMS (dB)')
            if col == 0:
                ax.set_ylabel('Stress error, RMS over elements (dB)')
            head = ('Same 12 control gauges, shakers added' if row == 0 else 'Six shakers on 12 control gauges, then placed anew for 6')
            ax.set_title(f'({"abcd"[2 * row + col]}) {head},\n{lname}', fontsize=8.5, loc='left')
            ax.legend(fontsize=7, loc='upper right')
    fig.tight_layout()
    save(fig, 'fig_paired.png')


def fig_what_tracks():
    t = rows('fig_what_tracks.csv')
    style = {'6x6': ('o', BLUE, None), '12x12': ('^', ORANGE, 'none'), '3x12': ('v', GREEN, 'none'),
             '6x12': ('s', PINK, 'none'), '12x24': ('D', YELLOW, None)}
    names = {'6x6': '6 shakers, 6 control gauges', '12x12': '12 shakers, 12 control gauges', '3x12': '3 shakers, 12 control gauges',
             '6x12': '6 shakers, 12 control gauges', '12x24': '12 shakers, 24 control gauges'}
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 7.6), sharey='row')
    for row, same in enumerate(('1', '0')):
        for col, (key, xl) in enumerate((('control_band_rms', 'Control-gauge error'), ('held_band_rms', 'Held-out-gauge error'))):
            ax = axes[row, col]
            for setup in ([s for s in style if (s in ('6x6', '12x12')) == (same == '1')]):
                R = [r for r in t if r['setup'] == setup]
                m, c, f = style[setup]
                ax.plot([float(r[key]) for r in R], [float(r['stress_rms']) for r in R], m, ls='none', color=c,
                        mfc=f if f else c, mec=c, ms=4.5, mew=1.0, alpha=0.85, label=names[setup])
            ax.set_xlabel(f'{xl}, per gauge in one-third-octave bands, RMS (dB)')
            if col == 0:
                ax.set_ylabel('Stress error, RMS over elements (dB)')
            head = 'As many shakers as control gauges' if same == '1' else 'More control gauges than shakers'
            ax.set_title(f'({"abcd"[2 * row + col]}) {head}: {xl.lower()}', fontsize=8.5, loc='left')
            ax.legend(fontsize=7, loc='upper left')
            if same == '0':
                ax.set_yscale('log')
                ax.set_xscale('log')
                for a in (ax.xaxis, ax.yaxis):
                    a.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'{v:g}'))
                    a.set_minor_formatter(matplotlib.ticker.NullFormatter())
                ax.set_xticks([3, 4, 6, 10, 20, 30])
                ax.set_yticks([2, 3, 4, 6, 10, 20, 30])
    fig.tight_layout()
    save(fig, 'fig_what_tracks.png')


if __name__ == '__main__':
    fig_paired()
    fig_what_tracks()
