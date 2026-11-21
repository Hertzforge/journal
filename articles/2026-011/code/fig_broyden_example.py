"""The Broyden congruence law on the two worked examples of its author's description: the RMS error
over the three control gauges, cycle by cycle, with the learning on and off (left), and with phase
steering on and off (right). The numbers are the description's own, which the law as built
reproduces (its tests); nothing here runs a law. From ../data/law_broyden_example.csv.

    PYTHONDONTWRITEBYTECODE=1 python3 fig_broyden_example.py

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
from style import BLUE, ORANGE, TEXT, plt, rows, save

SERIES = {
    'learning on': dict(color=BLUE, ls='-', marker='o', mfc=BLUE),
    'learning off': dict(color=ORANGE, ls='--', marker='s', mfc='white'),
    'phase steering on': dict(color=BLUE, ls='-', marker='o', mfc=BLUE),
    'phase steering off': dict(color=ORANGE, ls='--', marker='s', mfc='white'),
}


def panel(ax, table, example, settings, title):
    for setting in settings:
        pts = sorted((int(r['cycle']), float(r['rms_error_db'])) for r in table
                     if r['example'] == example and r['setting'] == setting)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], label=setting, lw=1.4, ms=5, **SERIES[setting])
    ax.set_title(title, fontsize=9, color=TEXT)
    ax.set_xlabel('Cycle')
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=7.5)


def figure():
    table = rows('law_broyden_example.csv')
    fig, (left, right) = plt.subplots(1, 2, figsize=(9, 3.4))
    panel(left, table, 'two shakers three gauges', ('learning on', 'learning off'),
          'Real example, the system differs from its model')
    left.set_ylabel('RMS error over the control gauges, dB\n(lower is closer to the target)')
    panel(right, table, 'complex two shakers three gauges', ('phase steering on', 'phase steering off'),
          'Complex example, the system is its model')
    fig.tight_layout()
    return fig


if __name__ == '__main__':
    save(figure(), 'fig_broyden_example.png')
