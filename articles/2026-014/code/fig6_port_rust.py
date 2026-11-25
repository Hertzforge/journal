"""Figure 6: the two followed laws as the Python ports ran them and as the Rust law math runs
them, on the same runs: the share ending in tolerance and the share never over +3 dB, on the
study's and the held-back structures. Copyright 2026 Kevin Cross. MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import LAW_STYLE, MUTED, rows, num, save, percent_axis

table = {(r['set'], r['law']): r for r in rows('law_port_rust.csv')}
fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.0))
groups = [('study', 'followed'), ('audit', 'followed'), ('study', 'followed-hold'), ('audit', 'followed-hold')]
x = np.arange(len(groups))
for a, key, title in ((ax[0], 'ends', '(a) Ends in tolerance'), (ax[1], 'exposure', '(b) Never over +3 dB')):
    colors = [LAW_STYLE[law][0] for _, law in groups]
    a.bar(x - 0.18, [num(table[g][f'{key}_port']) for g in groups], 0.34, color=MUTED, alpha=0.5,
          label='Python port')
    a.bar(x + 0.18, [num(table[g][f'{key}_rust']) for g in groups], 0.34, color=colors, label='Rust law math')
    a.set_xticks(x)
    a.set_xticklabels([f"{law}\n{'study' if s == 'study' else 'held back'}" for s, law in groups], fontsize=7)
    a.set_ylim(0, 1.05)
    a.set_title(title, loc='left', fontsize=9)
    a.set_ylabel('Runs (%)')
    percent_axis(a)
ax[0].legend(fontsize=7, loc='upper center', ncol=2)
ax[0].set_ylim(0, 1.15)
fig.tight_layout()
save(fig, 'fig6_port_rust')
