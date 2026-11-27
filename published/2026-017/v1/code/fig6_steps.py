"""Figure 6: the stepped sine (T3). Where the runs of matrix, paired and ratio ended, by tier: completed,
held by the identification, or aborted at each rung of the level ladder. Copyright 2026 Kevin Cross.
MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import TIERS, LAW_LABEL, BLUE, GREEN, YELLOW, ORANGE, RED, PURPLE, MUTED, rows, save

data = {(r['law'], r['tier']): r for r in rows('law_steps.csv')}
PARTS = [('completed', 'completed', GREEN, ''), ('held', 'held by the identification', MUTED, ''),
         ('law_fault', 'law fault', PURPLE, ''),
         ('aborted_at_m12db', 'aborted at -12 dB', RED, '///'),
         ('aborted_at_m9db', 'aborted at -9 dB', ORANGE, '///'),
         ('aborted_at_m6db', 'aborted at -6 dB', YELLOW, '///'),
         ('aborted_at_m3db', 'aborted at -3 dB', '#c9a0dc', '///'),
         ('aborted_at_0db', 'aborted at full level', BLUE, '...')]
bars = [(law, tier) for law in ('matrix', 'paired', 'ratio') for tier in TIERS]
x = np.arange(len(bars)) + np.repeat([0, 0.6, 1.2], 3)
fig, ax = plt.subplots(figsize=(9, 4.2))
bottom = np.zeros(len(bars))
for key, label, color, hatch in PARTS:
    v = np.array([int(data[b][key]) / int(data[b]['runs']) for b in bars])
    ax.bar(x, v, 0.8, bottom=bottom, color=color, hatch=hatch, edgecolor='white', label=label)
    bottom += v
ax.set_xticks(x)
ax.set_xticklabels([f"{LAW_LABEL[law]}\n{tier}\n({data[(law, tier)]['runs']} runs)" for law, tier in bars],
                   fontsize=7.5)
ax.set_ylim(0, 1.0)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
ax.set_yticklabels(['0', '25', '50', '75', '100'])
ax.set_ylabel('Stepped-sine runs (%)')
ax.legend(fontsize=7.5, loc='upper left', bbox_to_anchor=(1.01, 1))
fig.tight_layout()
save(fig, 'fig6_steps')
