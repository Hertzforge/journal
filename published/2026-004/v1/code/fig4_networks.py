"""Figure 4: (a) how long an identification the predictors need; (b) the network law on the
hardening structure.

Reads ../data/fig4a_identification_length.csv and ../data/fig4b_hardening_pulses.csv only.
Writes ../figures/fig4_networks.png. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')


def rows(name):
    with open(os.path.join(DATA, name), newline='') as f:
        return list(csv.DictReader(f))


fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw=dict(wspace=0.28))

ident = rows('fig4a_identification_length.csv')
SER = [('held-out (nine)', 'frozen', '#0072B2', '-', 'o', 'held out: frozen linear model'),
       ('held-out (nine)', 'setnet', '#0072B2', '--', 's', 'held out: network, buzz and 4 low pulses'),
       ('population, stress', 'frozen', '#D55E00', '-', '^', 'unseen simulated, stress tier: frozen'),
       ('population, stress', 'setnet', '#D55E00', '--', 'D', 'unseen simulated, stress tier: network, 4 low pulses')]
for plants, pred, c, ls, m, lab in SER:
    pts = sorted((float(r['buzz_s']), float(r['median_abs_error_db'])) for r in ident
                 if r['plants'] == plants and r['predictor'] == pred
                 and (pred == 'frozen' or r['low_pulses'] == '4'))
    a.plot([p[0] for p in pts], [p[1] for p in pts], color=c, ls=ls, marker=m, mfc='white', mew=1.4,
           ms=6, lw=1.6, label=lab)
a.axvline(102.4, color='#6b6b6b', lw=0.8, ls=(0, (1, 2)))
a.text(97, 15, 'identification used\neverywhere else\n(102 s, 40 averages)', fontsize=7, ha='right', va='top')
a.set_xscale('log')
a.set_yscale('log')
a.set_xticks([5.12, 10.24, 20.48, 40.96, 79.36, 102.4])
a.set_xticklabels(['5 s\n(2)', '10 s\n(4)', '20 s\n(8)', '41 s\n(16)', '79 s\n(31)', '102 s\n(40)'])
a.minorticks_off()
a.set_xlabel('Length of the identification buzz (number of averages)', fontsize=8.5)
a.set_ylabel('Median error predicting the first -12 dB pulse\'s over-test (dB)', fontsize=8)
a.set_title('(a) How long an identification', fontsize=9.5, loc='left')
a.set_ylim(0.05, 40)
a.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False)
a.grid(True, which='major', alpha=0.3)
a.tick_params(labelsize=7.5)

hard = rows('fig4b_hardening_pulses.csv')
LAW = [('network as the law\'s model', '#D55E00', '-', 'o'),
       ('followed family, 12 % ceiling', '#0072B2', '--', 's'),
       ('frozen law', '#009E73', ':', '^')]
for law, c, ls, m in LAW:
    pts = [(int(r['pulse']), float(r['absolute_db']), r['kind']) for r in hard if r['law'] == law]
    b.plot([p[0] for p in pts], [p[1] for p in pts], color=c, ls=ls, marker=m, mfc='white', mew=1.4,
           ms=5.5, lw=1.4, label=law)
b.axhline(3, color='black', lw=1, ls='--')
b.text(0.5, 3.3, '3 dB over the full-level target', fontsize=7.5, ha='left')
b.axhline(0, color='#6b6b6b', lw=0.6)
b.set_ylim(-14, 7)
b.set_xlabel('Pulse number (low pulses below -14 dB are off the axis)', fontsize=8.5)
b.set_ylabel('Worst point against the full-level target (dB)', fontsize=8.5)
b.set_title('(b) The hardening structure (held out), no added noise', fontsize=9.5, loc='left')
b.legend(fontsize=7.5, loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=3, frameon=False)
b.grid(True, alpha=0.3)
b.tick_params(labelsize=7.5)
out = os.path.join(HERE, '..', 'figures', 'fig4_networks.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
