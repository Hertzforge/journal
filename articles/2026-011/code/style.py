"""Shared look of the figures: the journal's series colors, always paired with a hatch, a line style
or a marker, the laws' order and names, and paths. Copyright 2026 Kevin Cross and Norman Hunter. MIT license."""
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
SIX = ['pinv_closed', 'pinv_open', 'shape_svd', 'buzz_match', 'min_drive', 'band_average']
NEW = ['independent', 'nearly_independent', 'broyden_congruence']
LAWS = SIX + NEW
GROUPS = (('more_controls', 'More control gauges than shakers'), ('equal', 'As many shakers as control gauges'))

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 9, 'axes.edgecolor': '#c9d3df', 'axes.labelcolor': TEXT, 'xtick.color': TEXT,
    'ytick.color': TEXT, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8, 'axes.axisbelow': True,
    'legend.frameon': False, 'savefig.dpi': 200, 'figure.dpi': 100, 'hatch.linewidth': 0.6,
})


def rows(name):
    with open(os.path.join(DATA, name), newline='') as file:
        return list(csv.DictReader(file))


def one(table, **want):
    """The single row of a table with the given values, or None."""
    hit = [r for r in table if all(r[k] == v for k, v in want.items())]
    return hit[0] if hit else None


def law_bars(ax, table, key, laws=LAWS, **want):
    """One bar per law at the row's median, with a line from the first to the third quartile. The
    six laws of the earlier study are plain blue; the three laws of this article are hatched orange."""
    for i, law in enumerate(laws):
        r = one(table, law=law, **want)
        if r is None:
            continue
        new = law in NEW
        ax.bar(i, float(r[key + '_db']), width=0.68, color=ORANGE if new else BLUE, hatch='///' if new else None,
               edgecolor='white', linewidth=0.5)
        ax.plot([i, i], [float(r[key + '_q1']), float(r[key + '_q3'])], color=TEXT, lw=1.1)
    ax.set_xticks(range(len(laws)))
    ax.set_xticklabels(laws, rotation=35, ha='right', fontsize=7.5)
    ax.grid(axis='x', visible=False)


def legend_laws(ax, **kw):
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=BLUE, edgecolor='white', label='The six laws of the earlier study'),
                       Patch(facecolor=ORANGE, edgecolor='white', hatch='///', label='The three laws of this article')],
              fontsize=7.5, **kw)


def save(fig, name):
    os.makedirs(FIGURES, exist_ok=True)
    out = os.path.join(FIGURES, name)
    fig.savefig(out, bbox_inches='tight', facecolor='white')
    print('wrote', out)
