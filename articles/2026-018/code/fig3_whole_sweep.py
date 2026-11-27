"""Figure 3: where each sweep on whole-sweep rungs ended, the level ladder and matrix,
by tier.
data=fig3_whole_sweep_stops.csv. Copyright 2026 Kevin Cross. MIT license."""
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from style import rows, save, ARM_LABEL, TEXT, BLUE, ORANGE, GREEN, MUTED, YELLOW, PURPLE

r = rows('fig3_whole_sweep_stops.csv')
ends = [('-12.0', 'stopped on the -12 dB pass', ORANGE, '...'), ('-9.0', 'on the -9 dB pass', YELLOW, 'xx'),
        ('-6.0', 'on the -6 dB pass', PURPLE, '\\\\'), ('-3.0', 'on the -3 dB pass', MUTED, '--'),
        ('0.0', 'on the full-level pass', TEXT, '++'), ('', 'completed', GREEN, '')]
fig, ax = plt.subplots(figsize=(7.0, 2.9))
bars = []
for tier in ('linear', 'realistic', 'strong'):
    for arm in ('matrix_sw', 'level_ladder_sw'):
        bars.append((arm, tier))
for i, (arm, tier) in enumerate(bars):
    left = 0
    rs = [x for x in r if x['arm'] == arm and x['tier'] == tier]
    for lvl, what, color, hatch in ends:
        n = sum(1 for x in rs if (x['outcome'] == 'completed' if lvl == '' else
                                  (x['outcome'] != 'completed' and x['stopped_at_level_db'] == lvl)))
        if n:
            ax.barh(i, n, left=left, color=color, hatch=hatch, edgecolor='white', height=0.7)
            ax.text(left + n / 2, i, str(n), ha='center', va='center', fontsize=8, color=TEXT,
                    bbox=dict(facecolor='white', edgecolor='none', pad=1.2))
        left += n
handles = [Patch(facecolor=color, hatch=hatch, edgecolor='white', label=what) for lvl, what, color, hatch in ends]
ax.set_yticks(range(len(bars)))
ax.set_yticklabels([f'{ARM_LABEL[a]}, {t}' for a, t in bars], fontsize=8)
ax.invert_yaxis()
ax.set_xlabel('sweeps (T1 and T5, three structures of each of two systems)')
ax.set_xlim(0, 12)
ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.45, -0.22), ncol=3, fontsize=8)
ax.grid(axis='y', visible=False)
save(fig, 'fig3_whole_sweep')
