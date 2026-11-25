"""Figure: eight control laws on the level ladder and started at full level on the stored model (timing corrected).
20 structures (6 x 6 system, realistic and strong sizes, 10 each), banded target. Bars: median; whiskers: quartiles.
Top: control error. Bottom: typical element stress error. Data: ../data/e28_laws.json (e28_analyze.py)."""
import json, os
import numpy as np
from style import *
J = json.load(open(os.path.join(DATA, 'e28_laws.json')))
LAWS = [('band_average', 'Band\naverage'), ('pinv_closed', 'Per-line\npseudo-inverse'), ('min_drive', 'Minimum\ndrive'), ('shape_svd', 'Shape-\nconstrained'),
        ('buzz_match', 'Buzz-test\nmatched'), ('independent', 'Independent'), ('nearly_independent', 'Nearly\nindependent'), ('broyden_congruence', 'Broyden\ncongruence')]
fig, axes = plt.subplots(2, 1, figsize=(7.4, 5.6), sharex=True); x = np.arange(len(LAWS)); w = 0.38
for ax, (kl, kn, lab) in zip(axes, (('b3_l', 'b3_n', 'Control error, dB'), ('st_l', 'st_n', 'Typical element stress error, dB'))):
    for off, key, col, hatch, name in ((-w / 2, kl, BLUE, None, 'Level ladder (no pretest)'), (w / 2, kn, ORANGE, '///', 'Started at full level on the stored model')):
        v = [J[l][key] for l, _ in LAWS]; med = [np.median(a) for a in v]; q1 = [np.percentile(a, 25) for a in v]; q3 = [np.percentile(a, 75) for a in v]
        ax.bar(x + off, med, w - 0.04, color=col, hatch=hatch, edgecolor='white', linewidth=0.6, label=name)
        ax.errorbar(x + off, med, yerr=[np.subtract(med, q1), np.subtract(q3, med)], fmt='none', ecolor=TEXT, elinewidth=0.9, capsize=2.5)
    ax.set_ylabel(lab); ax.set_ylim(0, None); clean(ax)
axes[1].set_xticks(x); axes[1].set_xticklabels([n for _, n in LAWS], fontsize=8); axes[0].legend(loc='upper left', bbox_to_anchor=(0, 1.2), ncol=2)
save(fig, 'fig_laws')
