"""Figure 4: the effective-duration correction. SRS targets, runs with a last full-level pulse:
effective duration within 0.8 to 1.2 on every control by the earlier 10 % threshold and by
Annex A. Copyright 2026 Kevin Cross. MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import ORANGE, PURPLE, rows, num, save, percent_axis

te = [r for r in rows('te_definition.csv') if r['set'] == 'study' and r['tier'] != 'strong']
fig, ax = plt.subplots(figsize=(5.0, 3.3))
x = np.arange(len(te))
w = 0.27
ax.bar(x - w / 2, [num(r['te_ok_10pct']) for r in te], w, color=PURPLE, label='10 % of the peak')
ax.bar(x + w / 2, [num(r['te_ok_516']) for r in te], w, color=ORANGE, hatch='...', edgecolor='white',
       label='peak over 3 (Annex A)')
ax.set_xticks(x)
ax.set_xticklabels([f"{'linear' if r['tier'] == 'none' else r['tier']}\n({r['runs_at_full_level']} runs)"
                    for r in te], fontsize=7)
ax.set_ylim(0, 1.05)
ax.set_ylabel('Runs with TE within 0.8 to 1.2 (%)')
percent_axis(ax)
ax.set_title('Effective duration, SRS targets', loc='left', fontsize=9)
ax.legend(fontsize=7, loc='upper right')
fig.tight_layout()
save(fig, 'fig4_effective_duration')
