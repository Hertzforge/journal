"""Shared look of the figures: the journal's series colors, always paired with a marker or a hatch,
and paths (after the laws paper's, so the series look the same). Copyright 2026 Kevin Cross. MIT
license."""
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
TIERS = ['linear', 'realistic', 'strong']
TIER_STYLE = {'linear': (MUTED, '', 'o'), 'realistic': (BLUE, '///', 'o'), 'strong': (ORANGE, '...', '^')}
TEST = {'T1': 'T1 sweep up', 'T2': 'T2 fast sweep', 'T3': 'T3 stepped', 'T4': 'T4 dwell',
        'T5': 'T5 sweep down'}

# The screens' arms: the two yardsticks, the candidates of the first screen and the leads of the
# second, and the two shipped amplitude laws. Each has its own marker, so no figure needs color.
ARM_STYLE = {
    'matrix': (BLUE, 'o'), 'matrix_sw': (BLUE, 'o'), 'followed_poles': (ORANGE, 'P'),
    'family_inverse': (GREEN, 's'), 'level_ladder': (YELLOW, '^'), 'level_ladder_sw': (YELLOW, 'v'),
    'rls_dither': (PINK, 'X'), 'pole_trajectory': (DKGREEN, 'h'), 'amplitude_indexed': (RED, '*'),
    'placed_poles': (PURPLE, 'd'), 'preview': (PINK, '>'), 'preview_frozen': (MUTED, '<'),
    'paired': (MUTED, 'v'), 'ratio': (PURPLE, 'D')}
ARM_HATCH = {'matrix': '', 'followed_poles': '///', 'pole_trajectory': '\\\\', 'amplitude_indexed': 'xxx',
             'placed_poles': '...', 'preview': '---', 'preview_frozen': '++', 'paired': '\\\\', 'ratio': 'xxx'}
# Figure labels use the laws' ids, as the shipped laws' are.
ARM_LABEL = {'matrix': 'matrix', 'matrix_sw': 'matrix, whole-sweep rungs', 'followed_poles': 'followed_poles',
             'family_inverse': 'family_inverse', 'level_ladder': 'level_ladder, 2 s rungs',
             'level_ladder_sw': 'level_ladder, whole-sweep rungs', 'rls_dither': 'rls_dither',
             'pole_trajectory': 'pole_trajectory', 'amplitude_indexed': 'amplitude_indexed',
             'placed_poles': 'placed_poles', 'preview': 'preview', 'preview_frozen': 'preview_frozen',
             'paired': 'paired', 'ratio': 'ratio'}

def rows(name):
    with open(os.path.join(DATA, name), newline='') as file:
        return list(csv.DictReader(file))


def numbers():
    """The article's numbers, as dnw_data.py wrote them."""
    return {r['key']: r['value'] for r in rows('numbers.csv')}


def num(value):
    return float(value) if value not in ('', None) else float('nan')


def percent_axis(ax, axis='y'):
    """Show a share axis, drawn from 0 to 1, in percent (ticks 0 to 100)."""
    from matplotlib.ticker import FuncFormatter
    target = ax.yaxis if axis == 'y' else ax.xaxis
    target.set_major_formatter(FuncFormatter(lambda v, _: f'{v * 100:.0f}'))


def panel(ax, letter):
    ax.set_title(f'({letter})', loc='left', fontsize=9, color=TEXT)


def save(fig, name):
    """Write the figure as PNG and PDF."""
    os.makedirs(FIGURES, exist_ok=True)
    for ext in ('png', 'pdf'):
        out = os.path.join(FIGURES, f'{name}.{ext}')
        fig.savefig(out, bbox_inches='tight', facecolor='white')
        print('wrote', out)
