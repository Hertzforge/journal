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

# Systems are written shakers x control gauges in the text; the problem names put the gauges first.
SYSTEM = {'12x3': '3 x 12', '12x6': '6 x 12', '24x12': '12 x 24', '6x6': '6 x 6', '12x12': '12 x 12'}
SYSTEM_ORDER = ['12x3', '12x6', '24x12', '6x6', '12x12']
TIER = {'none': 'linear', 'realistic': 'realistic', 'strong': 'strong',
        'realistic_soft': 'realistic,\nsoft only', 'realistic_hard': 'realistic,\nhard only',
        'strong_soft': 'strong,\nsoft only', 'strong_hard': 'strong,\nhard only'}
TIER_ORDER = ['none', 'realistic', 'strong', 'realistic_soft', 'realistic_hard', 'strong_soft',
              'strong_hard']


def rows(name):
    with open(os.path.join(DATA, name), newline='') as file:
        return list(csv.DictReader(file))


def num(value):
    return float(value) if value not in ('', None) else float('nan')


def percent_axis(ax, axis='y'):
    """Show a share axis, drawn from 0 to 1, in percent (ticks 0 to 100)."""
    from matplotlib.ticker import FuncFormatter
    target = ax.yaxis if axis == 'y' else ax.xaxis
    target.set_major_formatter(FuncFormatter(lambda v, _: f'{v * 100:.0f}'))


def save(fig, name):
    """Write the figure as PNG and PDF."""
    os.makedirs(FIGURES, exist_ok=True)
    for ext in ('png', 'pdf'):
        out = os.path.join(FIGURES, f'{name}.{ext}')
        fig.savefig(out, bbox_inches='tight', facecolor='white')
        print('wrote', out)


# One color and one marker for each law, the same in every figure.
LAWS = ['followed', 'followed-hold', 'inverse', 'shape', 'paired']
LAW_STYLE = {'followed': (BLUE, 'o'), 'followed-hold': (GREEN, 's'), 'inverse': (ORANGE, '^'),
             'shape': (PURPLE, 'D'), 'paired': (MUTED, 'v')}
# A bar's fill pattern for each law, so that a bar is told apart by more than its color.
LAW_HATCH = {'followed': '', 'followed-hold': '///', 'inverse': '...', 'shape': 'xxx', 'paired': '\\\\'}
