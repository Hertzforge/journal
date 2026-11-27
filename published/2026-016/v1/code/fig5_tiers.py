"""Figure 5: how much harder the realistic and strong structures are, pooled over the laws and
the systems: the share of runs that complete (bars) and the median share of the test inside the
IEC check-point band (markers, with quartile bars), by test and version. Reads data/pooled.csv.
Copyright 2026 Kevin Cross. MIT license."""
import matplotlib.pyplot as plt

from style import BLUE, ORANGE, TEXT, TEST, TEST_ORDER, num, percent_axis, rows, save

pooled = {(r['version'], r['system'], r['kind'], r['test']): r for r in rows('pooled.csv')}
tiers = ['linear', 'realistic', 'strong']
fig, axes = plt.subplots(1, 6, figsize=(12, 3.4), sharey=True)
for ax, test in zip(axes, TEST_ORDER):
    for k, (version, color, marker, hatch) in enumerate(
            [('hertzforge', BLUE, 'o', None), ('python', ORANGE, 's', '///')]):
        for i, tier in enumerate(tiers):
            r = pooled.get((version, 'all', tier, test))
            if not r:
                continue
            x = i + (k - 0.5) * 0.38
            ax.bar(x, num(r['completed_share']), 0.36, color=color, alpha=0.35, hatch=hatch,
                   edgecolor=color, lw=0.6)
            y, lo, hi = num(r['iec_share_median']), num(r['iec_share_q1']), num(r['iec_share_q3'])
            ax.errorbar(x, y, yerr=[[y - lo], [hi - y]], fmt=marker, color=color, ms=5, capsize=2,
                        lw=1, label=None)
    ax.set_xticks(range(3), ['lin.', 'real.', 'strong'])
    ax.set_title(TEST[test].replace('\n', ' '), fontsize=8, color=TEXT)
    ax.set_ylim(0, 1.05)
    percent_axis(ax)
axes[0].set_ylabel('percent')
handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE, alpha=0.35),
           plt.Rectangle((0, 0), 1, 1, color=ORANGE, alpha=0.35, hatch='///'),
           plt.Line2D([], [], color=BLUE, marker='o', ls=''),
           plt.Line2D([], [], color=ORANGE, marker='s', ls='')]
fig.legend(handles, ['completed, Hertzforge version', 'completed, Python version',
                     'IEC share, Hertzforge (median, quartiles)', 'IEC share, Python (median, quartiles)'],
           loc='lower center', ncol=4, fontsize=7, bbox_to_anchor=(0.5, -0.04))
fig.tight_layout(rect=(0, 0.06, 1, 1))
save(fig, 'fig5_tiers')
