"""Figure 2: how far an estimate made from a finite number of averages scatters.

Reads ../data/fig2a_autospectrum_interval.csv, fig2b_all_lines.csv and fig2c_phase_coherence.csv
only. Writes ../figures/fig2_statistics.png. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
BLUE, ORANGE, GREEN, PURPLE, GRAY = '#0072B2', '#D55E00', '#009E73', '#CC79A7', '#6b6b6b'


def rows(name):
    with open(os.path.join(DATA, name), newline='') as f:
        return list(csv.DictReader(f))


fig, axs = plt.subplots(1, 3, figsize=(13.5, 4.3))
fig.subplots_adjust(wspace=0.3)

# (a) one line
a = rows('fig2a_autospectrum_interval.csv')
n = [float(r['averages']) for r in a]
ax = axs[0]
ax.fill_between(n, [float(r['lo99_db']) for r in a], [float(r['hi99_db']) for r in a],
                color=BLUE, alpha=0.15, lw=0, label='99 % of estimates')
ax.plot(n, [float(r['lo90_db']) for r in a], color=BLUE, lw=1.6, label='90 % of estimates')
ax.plot(n, [float(r['hi90_db']) for r in a], color=BLUE, lw=1.6)
for v, ls in ((1, ':'), (3, '--')):
    ax.axhline(v, color=GRAY, lw=1, ls=ls)
    ax.axhline(-v, color=GRAY, lw=1, ls=ls)
    ax.text(1000, v + 0.12, '+/-%d dB' % v, ha='right', fontsize=7.5, color=GRAY)
ax.set_xscale('log')
ax.set_xlim(4, 1024)
ax.set_ylim(-5, 4)
ax.set_xlabel('independent averages behind the estimate', fontsize=8.5)
ax.set_ylabel('estimate against the true spectrum (dB)', fontsize=8.5)
ax.set_title('(a) One line of one gauge\'s spectrum', fontsize=9.5, loc='left')
ax.legend(fontsize=7.5, loc='lower right', frameon=False)
ax.tick_params(labelsize=7.5)

# (b) every line at once
b = rows('fig2b_all_lines.csv')
ax = axs[1]
for lines, ls, mk in ((100, '-', 'o'), (400, '--', 's'), (1600, ':', '^')):
    rr = [r for r in b if int(r['lines']) == lines]
    x = [float(r['averages']) for r in rr]
    ax.plot(x, [float(r['p_all_within_3db']) for r in rr], color=ORANGE, ls=ls, lw=1.6,
            marker=mk, markevery=8, ms=4, label='%d lines, +/-3 dB' % lines)
    ax.plot(x, [float(r['p_all_within_1db']) for r in rr], color=PURPLE, ls=ls, lw=1.6,
            marker=mk, markevery=8, ms=4, label='%d lines, +/-1 dB' % lines)
ax.set_xscale('log')
ax.set_xlim(4, 1024)
ax.set_ylim(-0.02, 1.02)
ax.set_xlabel('independent averages behind each line', fontsize=8.5)
ax.set_ylabel('chance every line is inside the band', fontsize=8.5)
ax.set_title('(b) Every line inside a band, a perfect controller', fontsize=9.5, loc='left')
ax.legend(fontsize=6.8, loc='upper left', bbox_to_anchor=(0.0, 0.97), frameon=False)
ax.tick_params(labelsize=7.5)

# (c) phase and coherence of a pair
c = rows('fig2c_phase_coherence.csv')
ax = axs[2]
for navg, color, ls, mk in ((16, GRAY, ':', 'v'), (32, BLUE, '--', 's'), (64, ORANGE, '-', 'o'),
                            (128, GREEN, '-.', '^')):
    rr = [r for r in c if int(r['averages']) == navg]
    ax.plot([float(r['true_coherence']) for r in rr],
            [float(r['phase_error_deg_90pct']) for r in rr], color=color, ls=ls, marker=mk, ms=4,
            lw=1.5, label='%d averages' % navg)
ax.axvspan(0.0, 0.5, color='#eeeeee', lw=0)
ax.text(0.02, 1.0, 'MIL-STD-810H Annex E:\nany phase where the\ncoherence is under 0.5',
        fontsize=7, va='bottom')
ax.axhline(10, color=GRAY, lw=1, ls='--', label='+/-10 degrees (Annex E)')
ax.set_xlim(0, 1)
ax.set_ylim(0, 45)
ax.set_xlabel('true coherence of the pair', fontsize=8.5)
ax.set_ylabel('phase error not exceeded by 90 % of estimates (deg)', fontsize=8.5)
ax.set_title('(c) The phase of a pair', fontsize=9.5, loc='left')
ax.legend(fontsize=7.5, loc='upper right', frameon=False)
ax.tick_params(labelsize=7.5)

out = os.path.join(HERE, '..', 'figures', 'fig2_statistics.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
