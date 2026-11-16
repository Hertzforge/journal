"""Figure 3: the shared closed loop correcting a wrong estimate of a two-shaker, two-gauge
structure, against the open loop. An illustration from the loop's equations, not a run.

Reads ../data/fig3_closed_loop_lines.csv and fig3_closed_loop_rms.csv only.
Copyright 2026 Kevin Cross. MIT license.
"""
from style import BLUE, GREEN, ORANGE, TEXT, column, frequency_axis, plt, rows, save

lines = rows('fig3_closed_loop_lines.csv')
rms = rows('fig3_closed_loop_rms.csv')
f = column(lines, 'frequency_hz')
fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), gridspec_kw=dict(width_ratios=[3, 3, 2.2]))
for ax, c in zip(axes[:2], (1, 2)):
    ax.plot(f, column(lines, f'control{c}_after_0_loops_db'), color=ORANGE, ls='--', lw=1.4,
            label='Open loop (and the first drive)')
    ax.plot(f, column(lines, f'control{c}_after_5_loops_db'), color=GREEN, ls=':', lw=1.6,
            label='Closed loop, after 5 loops')
    ax.plot(f, column(lines, f'control{c}_after_30_loops_db'), color=BLUE, ls='-', lw=1.4,
            label='Closed loop, after 30 loops')
    ax.axhline(0, color=TEXT, lw=0.6)
    frequency_axis(ax)
    ax.set_title(f'Gauge {c}', fontsize=9)
axes[0].set_ylabel('Error against the target (dB)')
axes[0].legend(fontsize=7.5, loc='lower left')
loop = column(rms, 'loop')
axes[2].plot(loop, column(rms, 'control1_rms_db'), color=BLUE, marker='o', ms=3.5, lw=1.2,
             label='Gauge 1, closed loop')
axes[2].plot(loop, column(rms, 'control2_rms_db'), color=GREEN, marker='s',
             mfc='white', ms=3.5, lw=1.2, ls='--', label='Gauge 2, closed loop')
axes[2].plot(loop, column(rms, 'open_loop_control1_rms_db'), color=ORANGE, ls=':', lw=1.4,
             label='Gauge 1, open loop')
axes[2].plot(loop, column(rms, 'open_loop_control2_rms_db'), color=ORANGE, ls='-.', lw=1.4,
             label='Gauge 2, open loop')
axes[2].set_xlabel('Loop')
axes[2].set_ylabel('RMS error over the band (dB)')
axes[2].set_ylim(bottom=0)
axes[2].legend(fontsize=7.5)
fig.tight_layout()
save(fig, 'fig3_closed_loop.png')
