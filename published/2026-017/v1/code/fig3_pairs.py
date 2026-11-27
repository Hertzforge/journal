"""Figure 3: the pair claims between the shipped laws on the stepped sine (T3) and the dwell (T4).
For each pair of laws and each reading, the cells where the rule favours the first law (left), the
second (right) and neither (grey), of the 23 cells both ran. Copyright 2026 Kevin Cross. MIT
license."""
import numpy as np
import matplotlib.pyplot as plt

from style import LAW_LABEL, READING, BLUE, ORANGE, GRID, rows, save

data = [r for r in rows('law_pair_counts.csv') if r['version'] == 'hertzforge']
READS = ['completion', 'iec_share', 'worst_over_db']
fig, axes = plt.subplots(1, 3, figsize=(11, 4.6), sharey=True)
pairs = []
for r in data:
    key = (r['test'], r['law'], r['against'])
    if key not in pairs:
        pairs.append(key)
y = np.arange(len(pairs))[::-1]
for ax, reading in zip(axes, READS):
    by = {(r['test'], r['law'], r['against']): r for r in data if r['reading'] == reading}
    first = np.array([int(by[p]['cells_favour_law']) for p in pairs])
    second = np.array([int(by[p]['cells_favour_against']) for p in pairs])
    none = np.array([int(by[p]['cells_no_claim']) for p in pairs])
    ax.barh(y, -first, color=BLUE, label='first law favoured', edgecolor='white')
    ax.barh(y, second, color=ORANGE, hatch='///', label='second law favoured', edgecolor='white')
    ax.barh(y, none / 2, left=second, color=GRID, label='no claim (half each side)')
    ax.barh(y, -none / 2, left=-first, color=GRID)
    ax.axvline(0, color='#10161d', lw=0.8)
    ax.set_xlim(-24, 24)
    ax.set_xticks([-23, -12, 0, 12, 23])
    ax.set_xticklabels(['23', '12', '0', '12', '23'])
    ax.set_title(READING[reading], fontsize=9)
    ax.set_xlabel('cells (of 23)')
axes[0].set_yticks(y)
axes[0].set_yticklabels([f'{t}: {LAW_LABEL[a]} | {LAW_LABEL[b]}' for t, a, b in pairs], fontsize=7.5)
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, fontsize=7.5, loc='lower center', ncol=3)
fig.tight_layout(rect=(0, 0.07, 1, 1))
save(fig, 'fig3_pairs')
