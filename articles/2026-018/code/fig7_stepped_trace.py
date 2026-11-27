"""Figure 7: one stepped sine, three laws: at each step at full level, the largest control error over
the step's judged updates (frame 6 x 6, structure 0, linear tier, Hertzforge version).
data=fig7_stepped_trace.csv. Copyright 2026 Kevin Cross. MIT license."""
import matplotlib.pyplot as plt
from style import rows, save, ARM_STYLE, MUTED

r = rows('fig7_stepped_trace.csv')
fig, ax = plt.subplots(figsize=(7.2, 3.2))
for law in ('matrix', 'ratio', 'paired'):
    color, marker = ARM_STYLE[law]
    step = {}
    for v in r:
        if v['law'] == law and v['judged'] == '1':
            f = float(v['frequency_hz'])
            step[f] = max(step.get(f, 0.0), float(v['worst_control_error_db']))
    x = sorted(step)
    ax.plot(x, [step[f] for f in x], color=color, marker=marker, ms=4, lw=0.8, label=law)
    ax.plot(x[-1:], [step[x[-1]]], color=color, marker=marker, ms=10, ls='', markeredgecolor='white')
ax.set_xscale('log')
ax.set_ylim(bottom=0)
ax.set_xlabel('step frequency (Hz)')
ax.set_ylabel('largest control error over\nthe step\'s judged updates (dB)')
ax.legend(loc='upper right', fontsize=8, title='large marker: the last step', title_fontsize=7.5)
save(fig, 'fig7_stepped_trace')
