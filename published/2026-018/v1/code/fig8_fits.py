"""Figure 8: the modal fit. (a) Modes found and modes within 10 percent on the four frame sets, by fit
method, against the bar; (b) the in-band model error of the fit on two structures with four ways of
treating the identification's delay. data=fig8_fits.csv and numbers.csv (the bar). Copyright 2026 Kevin Cross. MIT license."""
import matplotlib.pyplot as plt
from style import rows, save, numbers, BLUE, ORANGE, MUTED, TEXT, percent_axis, panel

r = rows('fig8_fits.csv')
n = numbers()
fig, (a, b) = plt.subplots(1, 2, figsize=(7.6, 3.5), gridspec_kw={'width_ratios': [1.5, 1]})
fits = ['m0', 'm3', 'm5', 'm7', 'm7c', 'm7d', 'm9d']
names = {'m0': 'M0', 'm3': 'M3', 'm5': 'M5', 'm7': 'M7', 'm7c': 'M7c', 'm7d': 'M7d', 'm9d': 'M9d'}
sets = ['frame-6x6', 'frame-6x6-realistic', 'frame-12x6', 'frame-12x6-realistic']
markers = {'frame-6x6': 'o', 'frame-6x6-realistic': 's', 'frame-12x6': '^', 'frame-12x6-realistic': 'D'}
label = {'frame-6x6': '6 x 6 linear', 'frame-6x6-realistic': '6 x 6 realistic',
         'frame-12x6': '6 x 12 linear', 'frame-12x6-realistic': '6 x 12 realistic'}
for i, fit in enumerate(fits):
    for k, s in enumerate(sets):
        v = [x for x in r if x['part'] == 'fit' and x['case'] == fit and x['structures'] == s]
        if not v:
            continue
        x = i + (k - 1.5) * 0.12
        a.scatter(x, float(v[0]['found_share']), color=BLUE, marker=markers[s], s=26, zorder=3,
                  label=label[s] if i == 0 else None)
        a.scatter(x, float(v[0]['model_error_or_within_10pct']), facecolors='white', edgecolors=ORANGE,
                  marker=markers[s], s=26, zorder=3)
a.axhline(float(n['bar1_found']), color=BLUE, ls='--', lw=1)
a.axhline(float(n['bar1_within']), color=ORANGE, ls=':', lw=1.2)
a.text(1.6, float(n['bar1_found']) + 0.015, 'bar: found', fontsize=7.5, color=BLUE)
a.text(1.6, float(n['bar1_within']) - 0.055, 'bar: within 10 %', fontsize=7.5, color=ORANGE)
a.scatter([], [], color=BLUE, marker='o', s=26, label='filled: modes found')
a.scatter([], [], facecolors='white', edgecolors=ORANGE, marker='o', s=26, label='open: within 10 %')
a.set_xticks(range(len(fits)))
a.set_xticklabels([names[f] for f in fits])
a.set_ylim(-0.03, 1.03)
percent_axis(a)
a.set_ylabel('share of the true modes (%)')
a.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3)
a.grid(axis='x', visible=False)
panel(a, 'a')
cases = [('block', 'the\nblock\'s\ndelay'), ('C estimate', 'estimated\nfrom the\ndata'),
         ('no delay', 'none\nremoved'), ('lag less pipeline', 'engine lag\nless the\npipeline')]
for k, (s, m, c) in enumerate((('frame-6x6-realistic_s00', 'o', BLUE), ('frame-12x6_s00', '^', TEXT))):
    for i, (case, _) in enumerate(cases):
        v = next(x for x in r if x['part'] == 'delay' and x['structures'] == s and x['case'].startswith(case))
        b.bar(i + (k - 0.5) * 0.36, float(v['model_error_or_within_10pct']), width=0.36,
              color=c if k == 0 else 'white', edgecolor=c, hatch='' if k == 0 else '///',
              label=('6 x 6 realistic, structure 0' if k == 0 else '6 x 12 linear, structure 0') if i == 0 else None)
b.set_xticks(range(len(cases)))
b.set_xticklabels([c[1] for c in cases], fontsize=7.5)
b.set_ylabel('in-band model error (relative)')
b.legend(fontsize=7, loc='upper left')
b.grid(axis='x', visible=False)
panel(b, 'b')
fig.subplots_adjust(wspace=0.3)
save(fig, 'fig8_fits')
