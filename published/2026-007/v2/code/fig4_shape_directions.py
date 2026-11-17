"""Figure 4: which directions the shape-constrained law keeps on each line, at its default ratio
of 0.2. Six gauges and four shakers on a made-up structure; an illustration, not a run.

Reads ../data/fig4_shape_directions.csv only. Copyright 2026 Kevin Cross. MIT license.
"""
from style import BLUE, GREEN, ORANGE, PINK, TEXT, YELLOW, column, frequency_axis, plt, rows, save

t = rows('fig4_shape_directions.csv')
f = column(t, 'frequency_hz')
fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 5.2), sharex=True, gridspec_kw=dict(height_ratios=[3, 1.3]))
styles = [(BLUE, '-'), (ORANGE, '--'), (GREEN, '-.'), (PINK, ':')]
for k, (c, ls) in enumerate(styles, start=1):
    a1.plot(f, column(t, f's{k}'), color=c, ls=ls, lw=1.4, label=f'Singular value {k}')
a1.plot(f, column(t, 'threshold'), color=TEXT, lw=1.0, ls=(0, (1, 1)), label='0.2 times the largest')
a1.set_yscale('log')
a1.set_ylabel('Singular value of the system')
a1.legend(fontsize=7.5, ncol=3, loc='lower right')
a2.step(f, column(t, 'directions_kept'), where='mid', color=YELLOW, lw=1.6)
a2.set_ylabel('Directions kept')
a2.set_yticks([1, 2, 3, 4])
frequency_axis(a2)
fig.tight_layout()
save(fig, 'fig4_shape_directions.png')
