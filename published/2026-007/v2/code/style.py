"""Shared look of the figures: the journal's series colors, always paired with a line style or a
marker, and paths. Copyright 2026 Kevin Cross. MIT license."""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
FIGURES = os.path.join(HERE, '..', 'figures')
BLUE, ORANGE, GREEN, YELLOW, PINK, DKGREEN, PURPLE, RED = (
    '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948')
TEXT, MUTED, GRID = '#10161d', '#566372', '#e2e8ef'

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 9, 'axes.edgecolor': '#c9d3df', 'axes.labelcolor': TEXT, 'xtick.color': TEXT,
    'ytick.color': TEXT, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8,
    'legend.frameon': False, 'savefig.dpi': 200, 'figure.dpi': 100,
})


def rows(name):
    with open(os.path.join(DATA, name), newline='') as file:
        return list(csv.DictReader(file))


def column(table, key):
    return [float(r[key]) if r[key] != '' else float('nan') for r in table]


def save(fig, name):
    os.makedirs(FIGURES, exist_ok=True)
    out = os.path.join(FIGURES, name)
    fig.savefig(out, bbox_inches='tight', facecolor='white')
    print('wrote', out)


def frequency_axis(ax, lo=20, hi=600, ticks=(20, 50, 100, 200, 500)):
    """A log frequency axis with plain tick labels."""
    from matplotlib.ticker import FixedLocator, NullFormatter, NullLocator
    ax.set_xscale('log')
    ax.set_xlim(lo, hi)
    ax.xaxis.set_major_locator(FixedLocator(ticks))
    ax.set_xticklabels([str(t) for t in ticks])
    ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel('Frequency (Hz)')
