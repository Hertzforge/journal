"""What two parts of the Broyden congruence law are worth on the eight tuning cases: the law at its
defaults, with the learning switched off (broyden_gain 0) and with phase steering switched off. The
mean over the four cases of a system of the error at the control gauges and at the held-out gauges.
From ../data/tuning_points.csv (written by tuning_results.py).

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
from style import BLUE, ORANGE, PURPLE, TEXT, plt, rows, save

WAYS = [('defaults', 'As built\n(defaults)', ORANGE, '///'), ('broyden_gain = 0.0', 'Learning off', BLUE, '\\\\\\'),
        ('phase_steering = off', 'Phase steering off', PURPLE, '+++')]
t = [r for r in rows('tuning_points.csv') if r['law'] == 'broyden_congruence']
fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.3), sharey=True)
for ax, system in zip(axes, ('6 x 12', '6 x 6')):
    for g, (key, name) in enumerate((('control_db', 'Control gauges'), ('held_out_db', 'Held-out gauges'))):
        for i, (setting, label, c, h) in enumerate(WAYS):
            r = [x for x in t if x['system'] == system and x['setting'] == setting][0]
            x = g * (len(WAYS) + 0.8) + i
            ax.bar(x, float(r[key]), width=0.8, color=c, hatch=h, edgecolor='white', linewidth=0.5, label=label.replace('\n', ' ') if g == 0 else None)
            ax.text(x, float(r[key]) + 0.08, r[key], ha='center', fontsize=7.5, color=TEXT)
    ax.set_xticks([1, len(WAYS) + 0.8 + 1])
    ax.set_xticklabels(['Control gauges', 'Held-out gauges'])
    ax.set_title(system + ' system', fontsize=9)
    ax.grid(axis='x', visible=False)
axes[0].set_ylabel('Mean error, dB (lower is better)')
axes[0].set_ylim(0, 6.2)
axes[1].legend(fontsize=7.5, loc='upper left')
fig.tight_layout()
save(fig, 'fig_tuning_broyden_parts.png')
