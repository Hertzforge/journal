"""Figure 7: how far the two versions agree, law by law, on the agreement sample: the share of
paired runs whose outcome agrees, and whose outcome and every reading agree, for the two
comparisons (a, both versions on one identification and its guards; b, each version on its own).
Copyright 2026 Kevin Cross. MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import LAW_LABEL, BLUE, ORANGE, rows, save, percent_axis

LAWS = ['matrix', 'paired', 'ratio', 'steepest_descent', 'secant']
data = {(r['arm'], r['law'], r['test']): r for r in rows('law_agreement.csv')}
fig, ax = plt.subplots(figsize=(9, 3.6))
w = 0.2
x = np.arange(len(LAWS))
for k, (arm, key, label, color, hatch) in enumerate([
        ('a', 'outcome_agrees', '(a) outcome agrees', BLUE, ''),
        ('a', 'every_reading_agrees', '(a) outcome and every reading agree', BLUE, '///'),
        ('b', 'outcome_agrees', '(b) outcome agrees', ORANGE, ''),
        ('b', 'every_reading_agrees', '(b) outcome and every reading agree', ORANGE, '///')]):
    v = [int(data[(arm, law, 'all')][key]) / int(data[(arm, law, 'all')]['pairs']) for law in LAWS]
    ax.bar(x + (k - 1.5) * w, v, w, color=color, alpha=0.9 if hatch == '' else 0.45, hatch=hatch,
           edgecolor='white', label=label)
ax.set_xticks(x)
ax.set_xticklabels([f"{LAW_LABEL[law]}\n({data[('a', law, 'all')]['pairs']} pairs)" for law in LAWS])
ax.set_ylim(0, 1.05)
ax.set_ylabel('Paired runs (%)')
percent_axis(ax)
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, fontsize=7.5, ncol=2, loc='lower center')
fig.tight_layout(rect=(0, 0.14, 1, 1))
save(fig, 'fig7_agreement')
