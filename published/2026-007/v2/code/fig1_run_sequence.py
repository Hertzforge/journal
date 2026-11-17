"""Figure 1: the order of a multiple-shaker random run, at the shipped defaults.

Reads ../data/fig1_run_sequence.csv only. Copyright 2026 Kevin Cross. MIT license.
"""
from style import BLUE, MUTED, ORANGE, TEXT, plt, rows, save

t = rows('fig1_run_sequence.csv')
fig, ax = plt.subplots(figsize=(9.5, 4.0))
for r in t:
    a, b = float(r['start']), float(r['end'])
    if r['level_db_start'] == '':
        ax.axvspan(a, b, color='#f2f4f7', lw=0)
        ax.text((a + b) / 2, -29.5, r['label'], rotation=90, ha='center', va='bottom', fontsize=7.5,
                color=MUTED)
        continue
    l0, l1 = float(r['level_db_start']), float(r['level_db_end'])
    dashed = r['stage'] in ('identification', 'soft start')
    ax.plot([a, b], [l0, l1], color=ORANGE if dashed else BLUE, lw=2.3, ls='--' if dashed else '-')
    if r['stage'] == 'identification':
        ax.text((a + b) / 2, l0 - 1.4, 'Identification:\nuncorrelated random on\nevery shaker, about\n20 dB under the target',
                ha='center', va='top', fontsize=7.5, color=TEXT)
    elif r['stage'] == 'soft start':
        ax.text(b - 0.05, l0 + 1.0, 'Soft start: 9 dB under\nthe first step, climbing', ha='left', va='bottom',
                fontsize=7.5, color=TEXT)
    else:
        ax.text((a + b) / 2, l0 + 0.6, r['label'], ha='center', fontsize=8, color=TEXT)
ax.plot([], [], color=ORANGE, lw=2.3, ls='--', label='Identification and soft start')
ax.plot([], [], color=BLUE, lw=2.3, label='Closed loop: the level steps and full level')
ax.set_ylim(-30, 3)
ax.set_xlim(0, 12)
ax.set_xticks([])
ax.set_xlabel('Order of events (not to time scale)')
ax.set_ylabel('Level (dB re full level)')
ax.legend(loc='upper left', fontsize=8)
save(fig, 'fig1_run_sequence.png')
