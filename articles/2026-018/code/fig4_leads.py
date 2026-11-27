"""Figure 4: the second screen. (a) Nonlinear sweeps completed, of 36; (b) tests and tiers that met the rule
against matrix and against followed poles; (c) for each lead and each nonlinear test and tier, the
paired median p95 control error against followed poles. data=fig4_leads.csv. Copyright 2026 Kevin Cross. MIT license."""
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from style import rows, save, ARM_STYLE, ARM_LABEL, ARM_HATCH, TEXT, MUTED, panel

r = rows('fig4_leads.csv')
leads = ['pole_trajectory', 'amplitude_indexed', 'placed_poles', 'preview', 'preview_frozen']
cells = [(t, tier) for tier in ('realistic', 'strong') for t in ('T1', 'T2', 'T5')]
fig = plt.figure(figsize=(7.4, 6.4))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.1], hspace=0.75, wspace=0.35)
a = fig.add_subplot(gs[0, 0])
c = fig.add_subplot(gs[0, 1])
b = fig.add_subplot(gs[1, :])


def get(arm, yard, t, tier):
    return next(x for x in r if (x['arm'], x['yardstick'], x['test'], x['tier']) == (arm, yard, t, tier))


arms = ['matrix', 'followed_poles'] + leads
done = {}
for arm in leads:
    done[arm] = sum(int(get(arm, 'followed_poles', t, tier)['completed']) for t, tier in cells)
done['followed_poles'] = sum(int(get('pole_trajectory', 'followed_poles', t, tier)['completed_yardstick']) for t, tier in cells)
done['matrix'] = sum(int(get('pole_trajectory', 'matrix', t, tier)['completed_yardstick']) for t, tier in cells)
for i, arm in enumerate(arms):
    color, _ = ARM_STYLE[arm]
    a.bar(i, done[arm], color=color, hatch=ARM_HATCH[arm], edgecolor='white', width=0.7)
    a.text(i, done[arm] + 0.6, str(done[arm]), ha='center', fontsize=8)
a.set_xticks(range(len(arms)))
a.set_xticklabels([ARM_LABEL[x] for x in arms], fontsize=8, rotation=40, ha='right', rotation_mode='anchor')
a.set_ylim(0, 36)
a.set_ylabel('sweeps completed, of 36')
a.grid(axis='x', visible=False)
panel(a, 'a')
w = 0.36
for i, arm in enumerate(leads):
    color, _ = ARM_STYLE[arm]
    for k, (yard, hatch) in enumerate((('matrix', ''), ('followed_poles', '///'))):
        n = sum(int(get(arm, yard, t, tier)['passes']) for t, tier in cells)
        c.bar(i + (k - 0.5) * w, n, width=w, color=color if yard == 'matrix' else 'white',
              edgecolor=color, hatch=hatch, lw=1.2)
c.set_xticks(range(len(leads)))
c.set_xticklabels(leads, fontsize=8, rotation=40, ha='right', rotation_mode='anchor')
c.set_ylim(0, 6)
c.set_ylabel('tests and tiers meeting the rule, of 6')
c.legend(handles=[Patch(facecolor=MUTED, label='against matrix'),
                  Patch(facecolor='white', edgecolor=MUTED, hatch='///', label='against followed_poles')],
         fontsize=8, loc='upper right')
c.grid(axis='x', visible=False)
panel(c, 'b')
for j, (t, tier) in enumerate(cells):
    for i, arm in enumerate(leads):
        color, marker = ARM_STYLE[arm]
        v = get(arm, 'followed_poles', t, tier)['p95_paired_median_db']
        if v != '':
            b.scatter(j + (i - 2) * 0.13, float(v), color=color, marker=marker, s=46, zorder=3,
                      label=arm if j == 0 else None)
b.axhline(0, color=TEXT, lw=0.8, label='followed_poles (zero)')
for j in range(1, len(cells)):
    b.axvline(j - 0.5, color='#c9d3df', lw=0.8)
b.set_xticks(range(len(cells)))
b.set_xticklabels([f'{t} {tier}' for t, tier in cells], fontsize=8)
b.set_ylabel('p95 control error, lead less\nfollowed_poles, paired median (dB)')
b.grid(axis='x', visible=False)
b.legend(ncol=3, fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.12))
panel(b, 'c')
save(fig, 'fig4_leads')
