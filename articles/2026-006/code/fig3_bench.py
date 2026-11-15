"""Figure 3: the loopback bench that the hardware evidence in this article comes from.

Draws from crates/hertzforge-hal-ni/src/clock.rs at commit b587d5a1 and the article's Section 5;
reads no data file. Writes ../figures/fig3_bench.png. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
from matplotlib.patches import Rectangle

from diagram import BLUE, GRAY, GREEN, ORANGE, arrow, box, canvas, save

fig, ax = canvas(9.0, 4.4, 100, 60)

box(ax, 1, 18, 24, 32, 'Computer',
    ['Runs the control', 'service and the shell.', 'No shaker, no', 'amplifier.'],
    edge=GRAY)

# Chassis with two modules.
box(ax, 34, 6, 36, 48, 'cDAQ-9178 chassis', [], edge=BLUE)
ax.add_patch(Rectangle((37, 10), 13, 34, facecolor='white', edgecolor=BLUE, lw=1.1, zorder=3))
ax.text(43.5, 41.5, 'NI 9263', fontsize=8, ha='center', va='top', fontweight='bold', zorder=4)
ax.text(43.5, 37.5, 'voltage\noutput\n(the drive)', fontsize=7, ha='center', va='top', zorder=4)
ax.text(43.5, 14, 'AO0', fontsize=7.5, ha='center', zorder=4, color=ORANGE)
ax.add_patch(Rectangle((54, 10), 13, 34, facecolor='white', edgecolor=BLUE, lw=1.1, zorder=3))
ax.text(60.5, 41.5, 'NI 9234', fontsize=8, ha='center', va='top', fontweight='bold', zorder=4)
ax.text(60.5, 37.5, 'delta-sigma\ninput\n(the "response")', fontsize=7, ha='center', va='top',
        zorder=4)
ax.text(60.5, 14, 'AI0', fontsize=7.5, ha='center', zorder=4, color=ORANGE)

arrow(ax, 25.6, 34, 33.4, 34, color=GRAY, both=True, label='USB', label_xy=(29.5, 38))

# Jumper and tee.
ax.plot([43.5, 43.5, 60.5, 60.5], [11.5, 3.0, 3.0, 11.5], color=ORANGE, lw=1.6, zorder=2)
ax.text(52, 1.0, 'jumper: the drive is fed back as the measured signal', fontsize=7.2,
        ha='center', va='center', color=ORANGE)
ax.plot([52, 87.5, 87.5], [3.0, 3.0, 5.4], color=ORANGE, lw=1.6, ls=(0, (4, 2)), zorder=2)
ax.text(70, 4.6, 'tee', fontsize=7.2, ha='center', color=ORANGE)

box(ax, 76, 6, 23, 26, 'Bench multimeter',
    ['Digitizes the drive', 'at the tee, outside', 'Hertzforge, to time', 'an abort.'], edge=GREEN)

ax.text(52, 57.5, 'clock: AO sample clock taken from /<chassis>/ai/SampleClock (the proven '
        'configuration); the same run with the route removed is the negative control',
        fontsize=7.2, ha='center', va='center', color=BLUE, style='italic')

save(fig, 'fig3_bench.png')
