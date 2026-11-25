"""Shared look of the figures."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, '..', 'data'); FIGURES = os.path.join(HERE, '..', 'figures')
BLUE, ORANGE, GREEN, YELLOW, PURPLE = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#6250d6'
TEXT, MUTED, GRID = '#10161d', '#566372', '#e2e8ef'
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'], 'font.size': 9,
                     'axes.edgecolor': '#c9d3df', 'axes.labelcolor': TEXT, 'xtick.color': TEXT, 'ytick.color': TEXT,
                     'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8, 'axes.axisbelow': True,
                     'legend.frameon': False, 'savefig.dpi': 200, 'hatch.linewidth': 0.6})
def clean(ax):
    ax.grid(axis='x', visible=False)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
def save(fig, name):
    fig.tight_layout(); out = os.path.join(FIGURES, name); fig.savefig(out + '.png', bbox_inches='tight'); fig.savefig(out + '.pdf', bbox_inches='tight'); print(out)
