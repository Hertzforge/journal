"""Shared drawing helpers for the three block diagrams in this article.

Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
FIGURES = os.path.join(HERE, '..', 'figures')

BLUE, ORANGE, GREEN, PURPLE, GRAY = '#0072B2', '#D55E00', '#009E73', '#CC79A7', '#6b6b6b'
INK = '#222222'


def canvas(width_in, height_in, xmax=100, ymax=100):
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.axis('off')
    return fig, ax


def box(ax, x, y, w, h, title, lines=(), edge=GRAY, fill='white', lw=1.2, ls='-',
        title_size=9.5, text_size=7.6, title_color=INK):
    """A rounded box with a bold title and plain lines below it, top-left aligned."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.4,rounding_size=1.2',
                                facecolor=fill, edgecolor=edge, lw=lw, ls=ls, zorder=2))
    ax.text(x + 1.2, y + h - 1.4, title, fontsize=title_size, fontweight='bold', va='top',
            ha='left', color=title_color, zorder=3)
    for i, line in enumerate(lines):
        ax.text(x + 1.2, y + h - 5.0 - i * 3.3, line, fontsize=text_size, va='top', ha='left',
                color=INK, zorder=3)


def arrow(ax, x1, y1, x2, y2, color=GRAY, lw=1.3, style='-|>', ls='-', both=False,
          label=None, label_xy=None, label_size=7.4, label_color=None, rad=0.0):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='<|-|>' if both else style,
                        mutation_scale=11, color=color, lw=lw, ls=ls, zorder=1,
                        connectionstyle=f'arc3,rad={rad}')
    ax.add_patch(a)
    if label:
        lx, ly = label_xy if label_xy else ((x1 + x2) / 2, (y1 + y2) / 2)
        ax.text(lx, ly, label, fontsize=label_size, color=label_color or color, ha='center',
                va='center', zorder=4,
                bbox=dict(facecolor='white', edgecolor='none', pad=0.6))


def save(fig, name):
    os.makedirs(FIGURES, exist_ok=True)
    path = os.path.join(FIGURES, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path
