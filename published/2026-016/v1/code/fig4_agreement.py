"""Figure 4: how far the two versions agree, by test, on the comparison sample. Reads
data/agreement.csv. Copyright 2026 Kevin Cross. MIT license."""
import matplotlib.pyplot as plt

from style import BLUE, ORANGE, TEXT, num, percent_axis, rows, save

agree = rows('agreement.csv')
tests = ['T1', 'T2', 'T3', 'T4', 'T5', 'all']
labels = ['T1\nup 1', 'T2\nup 4', 'T3\nstepped', 'T4\ndwell', 'T5\ndown 1', 'all']
fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.7), sharey=True)
for ax, s, title in zip(axes, ['a', 'b'], ['(a) the same model', '(b) the same measured identification']):
    by = {r['test']: r for r in agree if r['set'] == s}
    x = range(len(tests))
    out = [num(by[t]['outcome_agrees']) / num(by[t]['pairs']) for t in tests]
    both = [num(by[t]['both_agree']) / num(by[t]['pairs']) for t in tests]
    ax.bar([i - 0.2 for i in x], out, 0.38, color=BLUE, label='outcome agrees')
    ax.bar([i + 0.2 for i in x], both, 0.38, color=ORANGE, hatch='///', edgecolor='white',
           label='outcome and every reading agree')
    for i, t in enumerate(tests):
        ax.text(i, 1.03, by[t]['pairs'], ha='center', fontsize=7, color=TEXT)
    ax.set_xticks(list(x), labels)
    ax.set_ylim(0, 1.12)
    percent_axis(ax)
    ax.set_title(title, loc='left', color=TEXT)
axes[0].set_ylabel('share of pairs, percent (pairs above each test)')
axes[0].legend(fontsize=7, loc='upper center', bbox_to_anchor=(1.05, -0.2), ncol=2)
fig.tight_layout()
save(fig, 'fig4_agreement')
