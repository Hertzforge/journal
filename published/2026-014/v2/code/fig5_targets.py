"""Figure 5: by kind of target. (a) The share ending in tolerance on each kind of target. (b) SRS
targets: ending in tolerance, and ending in tolerance with the effective duration within 0.8 to
1.2 on every control. (c) Classical targets on the square systems, runs with a last full-level
pulse: every control inside Method 516.8's time-domain tolerance. Study's structures; diamonds
are the held-back structures. Copyright 2026 Kevin Cross. MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import LAW_STYLE, LAW_HATCH, TEXT, rows, num, save, percent_axis

LAWS = ['followed', 'followed-hold', 'inverse', 'shape']
tg = {(r['set'], r['law'], r['kind']): r for r in rows('law_targets.csv')}
te = {(r['set'], r['law']): r for r in rows('law_te_srs.csv')}
ct = {(r['set'], r['law'], r['kind']): r for r in rows('law_classical_time.csv') if r['systems'] == 'square'}
fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.3))
w = 0.2
for k, law in enumerate(LAWS):
    color, _ = LAW_STYLE[law]
    for a, groups, get in (
            (ax[0], ['half_sine', 'sawtooth', 'srs'], lambda s, g: tg[(s, law, g)]['ends']),
            (ax[1], ['ends', 'ends_and_te'], lambda s, g: te[(s, law)][g]),
            (ax[2], ['half_sine', 'sawtooth'], lambda s, g: ct[(s, law, g)]['all'])):
        x = np.arange(len(groups)) + (k - 1.5) * w
        a.bar(x, [num(get('study', g)) for g in groups], w, color=color, alpha=0.85,
              hatch=LAW_HATCH[law], edgecolor='white', label=law if a is ax[0] else None)
        a.plot(x, [num(get('audit', g)) for g in groups], marker='D', ms=3, color=TEXT, ls='none',
               label='held-back structures' if (a is ax[0] and k == 0) else None)
ax[0].set_xticks(range(3))
ax[0].set_xticklabels(['half-sine', 'sawtooth', 'SRS'])
ax[0].set_ylabel('Runs (%)')
ax[0].set_title('(a) Ends in tolerance, by target', loc='left', fontsize=9)
ax[1].set_xticks(range(2))
ax[1].set_xticklabels(['ends in\ntolerance', 'and TE within\n0.8 to 1.2'])
ax[1].set_title('(b) SRS targets', loc='left', fontsize=9)
ax[2].set_xticks(range(2))
ax[2].set_xticklabels(['half-sine', 'sawtooth'])
ax[2].set_ylabel('Full-level runs (%)')
ax[2].set_title('(c) Time-domain tolerance, square systems', loc='left', fontsize=9)
for a in ax:
    a.set_ylim(0, 1.05)
    percent_axis(a)
fig.legend(loc='lower center', ncol=5, fontsize=8, bbox_to_anchor=(0.5, -0.04))
fig.tight_layout(rect=(0, 0.06, 1, 1))
save(fig, 'fig5_targets')
