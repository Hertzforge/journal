"""Shared look of the figures, the names of the ten ways of running the test, and the data readers."""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
FIGURES = os.path.join(HERE, '..', 'figures')
BLUE, ORANGE, GREEN, YELLOW, PINK, DKGREEN, PURPLE, RED = (
    '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948')
TEXT, MUTED, GRID = '#10161d', '#566372', '#e2e8ef'
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
                     'font.size': 9, 'axes.edgecolor': '#c9d3df', 'axes.labelcolor': TEXT, 'xtick.color': TEXT,
                     'ytick.color': TEXT, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8,
                     'axes.axisbelow': True, 'legend.frameon': False, 'savefig.dpi': 200, 'hatch.linewidth': 0.6})

# The labels in the data files and the plain names used in the article.
NAME = {
    'A1': 'Band control',
    'A2': 'Band control, stored model',
    'N1': 'Pseudo-inverse, dB-fit reference',
    'N2': 'Pseudo-inverse, dB-fit reference, model updated',
    'N3': 'Pseudo-inverse, first-solve reference',
    'N4': 'Pseudo-inverse, first-solve reference, model updated',
    'N5': 'Pseudo-inverse, stored-model reference',
    'N6': 'Pseudo-inverse, stored-model reference, model updated',
    'S1': 'Shape-constrained, dB-fit reference',
    'B1': 'Broyden, dB-fit reference',
}
SYSTEMS = ('6 x 12', '6 x 6')
SIZES = ('realistic', 'strong')
SYSTEM_WORDS = {'6 x 12': '6 shakers, 12 control gauges', '6 x 6': '6 shakers, 6 control gauges'}


def clean(ax, grid_axis='y'):
    ax.grid(axis='x' if grid_axis == 'y' else 'y', visible=False)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)


def save(fig, name):
    fig.tight_layout()
    out = os.path.join(FIGURES, name)
    fig.savefig(out + '.png', bbox_inches='tight')
    print(out + '.png')


def rows(name):
    with open(os.path.join(DATA, name), newline='') as f:
        return list(csv.DictReader(f))


def stress():
    """{(system, size, run): {structure: stress error RMS, dB}}."""
    out = {}
    for r in rows('stress_by_structure.csv'):
        out.setdefault((r['system'], r['size'], r['run']), {})[int(r['structure'])] = float(r['stress_error_rms_db'])
    return out


def paired(st, system, size, first, second):
    """d = first minus second on each structure both have, as an array in structure order."""
    a, b = st.get((system, size, first)), st.get((system, size, second))
    if not a or not b:
        return np.array([])
    return np.array([a[s] - b[s] for s in sorted(set(a) & set(b))])


def claims():
    """{(system, size, first, second): [claim rows]} from claims.csv."""
    out = {}
    for r in rows('claims.csv'):
        out.setdefault((r['system'], r['size'], r['first'], r['second']), []).append(r)
    return out


def claim_for(cl, system, size, x, y):
    """The claims on the pair (x, y) in either order, and the sign that turns its d into x minus y."""
    if (system, size, x, y) in cl:
        return cl[(system, size, x, y)], 1.0
    if (system, size, y, x) in cl:
        return cl[(system, size, y, x)], -1.0
    return [], 1.0


def quart(d):
    q1, med, q3 = np.percentile(d, [25, 50, 75])
    return med, q1, q3
