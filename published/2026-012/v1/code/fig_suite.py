"""Figure: what a suite of tests puts on the article outside the scored dwell, by the number of tests in the suite, for
three routes: a ladder for every test; one pretest and every test started at full level; the first test on a ladder
and stored, the rest started at full level. Left: clock time. Right: equivalent full-level seconds (a second at a lower
level counts by its power). Counted from saved runs of the 6 x 6 system. Data: ../data/e31a_suite.json
(e31a_suite_exposure.py)."""
import json, os
from style import *
J = json.load(open(os.path.join(DATA, 'e31a_suite.json')))
N = [1, 2, 3, 5, 10, 20]
ROUTES = [(0, BLUE, 'o', '-', 'A ladder for every test'), (1, ORANGE, 's', '--', 'One pretest, then every test at full level'),
          (2, GREEN, '^', ':', 'First test on a ladder and stored, the rest at full level')]
fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.3))
for ax, (key, lab) in zip(axes, (('time outside the dwell, s', 'Time outside the dwell, s'),
                                 ('equivalent full-level seconds outside the dwell', 'Equivalent full-level seconds\noutside the dwell'))):
    for i, col, mk, ls, name in ROUTES:
        ax.plot(N, [J[f'{key}|{n}'][i] for n in N], color=col, marker=mk, ms=5, lw=2, ls=ls, label=name)
    ax.set_xlabel('Tests in the series'); ax.set_ylabel(lab); ax.set_xticks(N); ax.set_ylim(0, None)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
fig.legend(*axes[0].get_legend_handles_labels(), loc='upper center', ncol=1, fontsize=8, bbox_to_anchor=(0.5, 1.16))
save(fig, 'fig_suite')
