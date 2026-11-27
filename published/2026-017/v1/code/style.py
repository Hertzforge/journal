"""Shared look of the figures: the journal's series colors, always paired with a marker or a hatch,
and paths. Copyright 2026 Kevin Cross. MIT license."""
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
KIND_ORDER = ['linear', 'realistic', 'strong', 'realistic_soft', 'realistic_hard', 'strong_soft',
              'strong_hard']
KIND = {'linear': 'linear', 'realistic': 'realistic', 'strong': 'strong',
        'realistic_soft': 'realistic, soft', 'realistic_hard': 'realistic, hard',
        'strong_soft': 'strong, soft', 'strong_hard': 'strong, hard'}
TIERS = ['linear', 'realistic', 'strong']
TIER_STYLE = {'linear': (MUTED, ''), 'realistic': (BLUE, '///'), 'strong': (ORANGE, '...')}
TEST = {'T1': 'T1 sweep up', 'T2': 'T2 fast sweep', 'T3': 'T3 stepped', 'T4': 'T4 dwell',
        'T5': 'T5 sweep down', 'L1': 'L1 limit'}
READING = {'iec_share': 'IEC check-point share', 'worst_over_db': 'worst over-test',
           'completion': 'completion'}

# One color and one marker for each law, the same in every figure. The Python version's `matrix`
# keeps the color of `matrix` with an open marker and a hatch.
LAWS = ['matrix', 'paired', 'ratio', 'steepest_descent', 'secant', 'followed_poles']
LAW_STYLE = {'matrix': (BLUE, 'o'), 'paired': (MUTED, 'v'), 'ratio': (PURPLE, 'D'),
             'steepest_descent': (GREEN, 's'), 'secant': (YELLOW, '^'), 'followed_poles': (ORANGE, 'P')}
LAW_HATCH = {'matrix': '', 'paired': '\\\\', 'ratio': 'xxx', 'steepest_descent': '...',
             'secant': '---', 'followed_poles': '///'}
LAW_LABEL = {'matrix': 'matrix', 'paired': 'paired', 'ratio': 'ratio',
             'steepest_descent': 'steepest_descent', 'secant': 'secant',
             'followed_poles': 'followed_poles'}

# The law and test pairs of the study, in the order the figures show them.
JOBS = [('hertzforge', 'matrix', t) for t in ('T1', 'T2', 'T5', 'L1', 'T3', 'T4')] + [
    ('hertzforge', 'paired', 'T3'), ('hertzforge', 'ratio', 'T3'), ('hertzforge', 'paired', 'T4'),
    ('hertzforge', 'ratio', 'T4'), ('hertzforge', 'steepest_descent', 'T4'),
    ('hertzforge', 'secant', 'T4')] + [
    ('python', law, t) for t in ('T1', 'T2', 'T5', 'L1') for law in ('matrix', 'followed_poles')]


def job_label(version, law, test, short=True):
    name = LAW_LABEL[law]
    if short and law in ('steepest_descent', 'followed_poles'):
        name = name.replace('_', '_\n', 1)
    if version == 'python' and law == 'matrix':
        name += '\n(Python)' if short else ' (Python)'
    return f'{name}\n{test}'


def rows(name):
    with open(os.path.join(DATA, name), newline='') as file:
        return list(csv.DictReader(file))


def facts():
    return {r['key']: r['value'] for r in rows('facts.csv')}


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
