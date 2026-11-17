"""Stage 2 closed-loop figure (Section 7.4): each fitted mode as played, under the reference drive, and in service.

Reads ../data/fig_closed_loop_modes.csv and ../data/closed_loop_summary.csv only. Copyright 2026 Kevin Cross.
MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
modes = list(csv.DictReader(open(os.path.join(DATA, 'fig_closed_loop_modes.csv'))))
s = {r['key']: r['value'] for r in csv.DictReader(open(os.path.join(DATA, 'closed_loop_summary.csv')))}
f = lambda k: float(s[k])

soft = [m for m in modes if m['effect'] == 'softening']
mem = [m for m in modes if m['effect'] == 'hardening']

fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
for ax, col, svc_m, svc_s, ylabel in (
        (axes[0], 'change_pct', 'member_change_service', 'soft_change_service_p50', 'Frequency change (%)'),
        (axes[1], 'zfac', 'member_zfac_service', 'soft_zfac_service_p50', 'Damping over its small-signal value')):
    x = [float(m['f0_hz']) for m in soft]
    ax.plot(x, [float(m[col + '_target']) for m in soft], ls='none', marker='^', ms=5, mfc='white', color='#D55E00',
            label='Article modes, reference drive')
    ax.plot(x, [float(m[col + '_played']) for m in soft], ls='none', marker='o', ms=3.5, color='#0072B2',
            label='Article modes, as tested')
    ax.axhline(f(svc_s), color='#0072B2', ls='--', lw=1.0, label='Article modes in service, median')
    xm = [float(m['f0_hz']) for m in mem]
    ax.plot(xm, [float(m[col + '_target']) for m in mem], ls='none', marker='D', ms=9, mfc='white', color='#D55E00',
            mew=1.5, label="Member's mode, reference drive")
    ax.plot(xm, [float(m[col + '_played']) for m in mem], ls='none', marker='*', ms=13, color='#009E73',
            label="Member's mode, as tested")
    ax.plot(xm, [f(svc_m)], ls='none', marker='s', ms=8, mfc='none', color='black', mew=1.5,
            label="Member's mode in service")
    ax.set_xscale('log')
    ax.set_xlabel('Small-signal frequency of the mode (Hz)')
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3, which='both')
axes[0].axhline(0, color='black', lw=0.8)
axes[0].set_title('(a) Frequency change', fontsize=10)
axes[1].set_title('(b) Damping factor', fontsize=10)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, fontsize=8, frameon=False)
fig.tight_layout(rect=(0, 0.12, 1, 1))
out = os.path.join(HERE, '..', 'figures', 'fig_closed_loop.png')
fig.savefig(out, dpi=150)
print('wrote', out)
