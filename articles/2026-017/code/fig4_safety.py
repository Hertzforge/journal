"""Figure 4: safety. (a) Every scored run's worst over-test through a resonance, by law and test,
with the 3 and 6 dB lines and the runner's widened abort band. (b) The same jobs on twelve
structures at the engine's default protective settings: runs completed under each setting.
Copyright 2026 Kevin Cross. MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import JOBS, LAW_STYLE, TEXT, BLUE, ORANGE, job_label, rows, num, facts, save

f = facts()
worst = {}
for r in rows('law_worst_runs.csv'):
    worst.setdefault((r['version'], r['law'], r['test']), []).append(num(r['worst_over_db']))
fig, (ax, bx) = plt.subplots(2, 1, figsize=(11, 7.4), gridspec_kw={'height_ratios': [2.2, 1]})
data = [worst.get(j, []) for j in JOBS]
parts = ax.boxplot(data, positions=range(len(JOBS)), widths=0.55, patch_artist=True, showfliers=True,
                   flierprops={'marker': '.', 'ms': 2, 'alpha': 0.4})
for patch, j in zip(parts['boxes'], JOBS):
    color = LAW_STYLE[j[1]][0]
    patch.set_facecolor(color)
    patch.set_alpha(0.55)
    if j[0] == 'python' and j[1] == 'matrix':
        patch.set_hatch('///')
for m in parts['medians']:
    m.set_color(TEXT)
for level, ls, label in ((3, '--', '3 dB'), (6, ':', '6 dB'),
                         (float(f['protective_abort_widened_db']), '-.', 'widened abort band')):
    ax.axhline(level, color=TEXT, lw=0.8, ls=ls)
    ax.text(len(JOBS) - 0.4, level + 0.8, label, fontsize=7, ha='right')
ax.axvline(11.5, color='#c9d3df', lw=1.2)
ax.set_xticks(range(len(JOBS)))
ax.set_xticklabels([job_label(*j) for j in JOBS], fontsize=7)
ax.set_ylabel('Worst over-test through\na resonance (dB), each run')
ax.set_title('(a) Runs of record (widened protective settings)', fontsize=9, loc='left')

d = rows('law_defaults.csv')
groups = []
for setname, label in (('hertzforge', 'Hertzforge'), ('python', 'Python')):
    for kind, tests in (('sweeps and steps', ('T1', 'T2', 'T3', 'T5', 'L1')), ('dwells', ('T4',))):
        g = [r for r in d if r['set'] == setname and r['job'].split('__')[0] in tests]
        if g:
            groups.append((f'{label},\n{kind}', len(g), sum(r['outcome_of_record'] == 'completed' for r in g),
                           sum(r['outcome'] == 'completed' for r in g)))
x = np.arange(len(groups))
bx.bar(x - 0.18, [g[2] / g[1] for g in groups], 0.36, color=BLUE, label='widened (runs of record)')
bx.bar(x + 0.18, [g[3] / g[1] for g in groups], 0.36, color=ORANGE, hatch='///', edgecolor='white',
       label='engine defaults')
for k, g in enumerate(groups):
    bx.text(k - 0.18, g[2] / g[1] + 0.02, f'{g[2]} of {g[1]}', ha='center', fontsize=7)
    bx.text(k + 0.18, g[3] / g[1] + 0.02, f'{g[3]} of {g[1]}', ha='center', fontsize=7)
bx.set_xticks(x)
bx.set_xticklabels([g[0] for g in groups], fontsize=8)
bx.set_ylim(0, 1.15)
bx.set_yticks([0, 0.5, 1])
bx.set_yticklabels(['0', '50', '100'])
bx.set_ylabel('Runs completed (%)')
bx.legend(fontsize=8, loc='upper left')
bx.set_title('(b) The same jobs on 12 structures, widened and default protective settings',
             fontsize=9, loc='left')
fig.tight_layout()
save(fig, 'fig4_safety')
