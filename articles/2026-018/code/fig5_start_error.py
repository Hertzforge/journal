"""Figure 5: the largest control error along one sweep at full level (frame 6 x 6, structure 0, linear
tier, T1): followed poles, preview control, its control run preview on a frozen model, and matrix. data=fig5_start_error.csv.
Copyright 2026 Kevin Cross. MIT license."""
import matplotlib.pyplot as plt
from style import rows, save, ARM_STYLE, ARM_LABEL, MUTED, panel

r = rows('fig5_start_error.csv')
fig, (a, b) = plt.subplots(2, 1, figsize=(7.2, 5.4), sharex=True)
for ax, arms in ((a, ('followed_poles', 'preview', 'preview_frozen')), (b, ('followed_poles', 'matrix'))):
    for arm in arms:
        color, marker = ARM_STYLE[arm]
        x = [float(v['frequency_hz']) for v in r if v['arm'] == arm]
        y = [float(v['worst_control_error_db']) for v in r if v['arm'] == arm]
        ax.plot(x, y, color=color, lw=0.9, marker=marker, markevery=max(1, len(x) // 25), ms=5,
                label=ARM_LABEL[arm], alpha=0.9)
    ax.set_xscale('log')
    ax.set_ylabel('largest control error (dB)')
    ax.axvspan(30, 50, color=MUTED, alpha=0.08, lw=0)
    ax.legend(loc='upper right', fontsize=8, ncol=3)
a.text(38.7, a.get_ylim()[1] * 0.92, '30 to 50 Hz', ha='center', fontsize=8, color=MUTED)
b.set_xlabel('frequency (Hz)')
panel(a, 'a')
panel(b, 'b')
save(fig, 'fig5_start_error')
