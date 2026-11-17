"""Figure: the hardening member with its dimensions, and how stiff the strips become with amplitude.

Reads ../data/stage2_member.csv and ../data/fig_member.csv (written by stage2_known.py). Panels (a) and (b) are
a line drawing of the realistic tier's member, to scale, from its design numbers; panel (c) is the strip
pair's own frequency rise against its RMS motion under random drive, for both tiers. Needs NumPy and matplotlib.
Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
mem = {r['tier']: {k: (float(v) if k not in ('tier', 'strip_material', 'mass_material') else v) for k, v in r.items()}
       for r in csv.DictReader(open(os.path.join(DATA, 'stage2_member.csv')))}
bb = list(csv.DictReader(open(os.path.join(DATA, 'fig_member.csv'))))
m = mem['realistic']
L, b, t, s = m['strip_length_mm'], m['strip_width_each_mm'], m['strip_thickness_mm'], m['strip_spacing_mm']
ml, mw, mh = m['mass_along_mm'], m['mass_across_mm'], m['mass_thin_mm']
POST, CLAMP = 16.0, 10.0          # bracket post (16 mm square tube) and the clamp block drawn at each end
T_DRAW = 1.2                      # the strips are drawn 2 times their thickness so they can be seen; the label gives the size


def dim(ax, p0, p1, text, off, side='h'):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    o = np.array([0, off]) if side == 'h' else np.array([off, 0])
    a, c = p0 + o, p1 + o
    ax.annotate('', a, c, arrowprops=dict(arrowstyle='<->', lw=0.8, shrinkA=0, shrinkB=0))
    for p, q in ((p0, a), (p1, c)):
        ax.plot(*np.c_[p, q + np.sign(off) * (o / max(abs(off), 1e-9)) * 1.5], color='black', lw=0.5)
    mid = (a + c) / 2
    ax.text(*(mid + (np.array([0, 1.2 * np.sign(off)]) if side == 'h' else np.array([1.2 * np.sign(off), 0]))), text,
            ha='center' if side == 'h' else ('left' if off > 0 else 'right'), va=('bottom' if off > 0 else 'top') if side == 'h' else 'center',
            fontsize=8)


fig, axes = plt.subplots(1, 3, figsize=(15, 4.9), gridspec_kw=dict(width_ratios=[1.15, 1.0, 1.1]))

# (a) side view: along the strips, the thin direction up
ax = axes[0]
for x0 in (-L / 2 - POST, L / 2):
    ax.add_patch(Rectangle((x0, -30), POST, 30 + CLAMP / 2, fc='0.75', ec='black', lw=0.8, hatch='///'))
ax.add_patch(Rectangle((-L / 2, -T_DRAW / 2), L, T_DRAW, fc='white', ec='black', lw=1.0))
ax.add_patch(Rectangle((-ml / 2, T_DRAW / 2), ml, mh, fc='0.55', ec='black', lw=1.0))
ax.add_patch(Rectangle((-ml / 2, -T_DRAW / 2 - 3), ml, 3, fc='0.55', ec='black', lw=1.0))
ax.plot([-L / 2 - POST - 8, L / 2 + POST + 8], [-30, -30], color='black', lw=1.2)
ax.text(0, -33, 'chassis tube (bracket stem not shown)', ha='center', va='top', fontsize=8)
dim(ax, (-L / 2, 0), (L / 2, 0), f'free length {L:.1f} mm', -22)
dim(ax, (-ml / 2, T_DRAW / 2 + mh), (ml / 2, T_DRAW / 2 + mh), f'{ml:.0f} mm', 5)
dim(ax, (ml / 2, T_DRAW / 2), (ml / 2, T_DRAW / 2 + mh), f'{mh:.1f} mm', 14, side='v')
ax.annotate('', (-ml / 2 - 4, T_DRAW / 2 + mh), (-ml / 2 - 4, T_DRAW / 2 + 4), arrowprops=dict(arrowstyle='<|-|>', lw=1.0))
ax.text(-ml / 2 - 6, T_DRAW / 2 + mh + 2, 'motion of\nthe mass', fontsize=8, va='center', ha='right')
ax.annotate(f'strip {t:.2f} mm thick\n(drawn thicker)', (-L / 2 + 5, 0), (-L / 2 - POST - 25, 30), fontsize=8,
            arrowprops=dict(arrowstyle='-', lw=0.6))
ax.text(-L / 2 - POST / 2, -14, 'clamp\npost', fontsize=8, ha='center', rotation=90, va='center',
        bbox=dict(fc='white', ec='none', pad=0.5))
ax.set_title('(a) Side view, along the strips', fontsize=10)

# (b) plan view: looking down the thin direction
ax = axes[1]
for y in (-s / 2, s / 2):
    ax.add_patch(Rectangle((-L / 2, y - b / 2), L, b, fc='white', ec='black', lw=1.0))
    for x0 in (-L / 2 - POST, L / 2):
        ax.add_patch(Rectangle((x0, y - POST / 2), POST, POST, fc='0.75', ec='black', lw=0.8, hatch='///'))
ax.add_patch(Rectangle((-ml / 2, -mw / 2), ml, mw, fc='0.55', ec='black', lw=1.0, alpha=0.85))
dim(ax, (-L / 2, s / 2 + b / 2), (L / 2, s / 2 + b / 2), f'{L:.1f} mm', 10)
dim(ax, (L / 2 + POST, -s / 2), (L / 2 + POST, s / 2), f'strip spacing\n{s:.1f} mm', 8, side='v')
dim(ax, (-L / 2 - POST, -s / 2 - b / 2), (-L / 2 - POST, -s / 2 + b / 2), f'each strip\n{b:.1f} mm wide', -6, side='v')
dim(ax, (-ml / 2, -mw / 2), (ml / 2, -mw / 2), f'{ml:.0f} mm', -14)
dim(ax, (-ml / 2, -mw / 2), (-ml / 2, mw / 2), f'{mw:.1f} mm', -4, side='v')
ax.text(0, 0, f'mass\n{1e3 * m["mass_kg"]:.0f} g\n{m["mass_material"]}', ha='center', va='center', fontsize=8, color='white')
ax.set_title('(b) Plan view: two strips, one mass', fontsize=10)

for ax in axes[:2]:
    ax.set_aspect('equal')
    ax.autoscale_view()
    ax.set_xlim(-L / 2 - POST - 30, L / 2 + POST + 40)
    ax.axis('off')
axes[0].set_ylim(-45, 40)
axes[1].set_ylim(-s / 2 - 30, s / 2 + 30)

# (c) the strip pair's own stiffening, under random drive (equivalent linearization: the rise at RMS motion A is the
# sine backbone at amplitude 2A)
ax = axes[2]
style = {'realistic': dict(color='#0072B2', marker='o', ls='-'), 'strong': dict(color='#D55E00', marker='s', ls='--')}
for tier in ('realistic', 'strong'):
    rr = [r for r in bb if r['tier'] == tier]
    A = np.array([float(r['amplitude_mm']) for r in rr])
    rnd = np.array([float(r['random_rms_change_pct']) for r in rr])
    mm = mem[tier]
    ax.plot(A, rnd, markevery=10, mfc='white', ms=5, lw=1.4,
            label=f'{tier}: {mm["strip_length_mm"]:.1f} x {mm["strip_width_each_mm"]:.1f} x {mm["strip_thickness_mm"]:.2f} mm strips', **style[tier])
sig = float(next(csv.DictReader(open(os.path.join(DATA, 'stage2_known.csv'))))['tier_member_rms_mm'])
ax.axvline(sig, color='black', lw=0.9, ls='-.')
ax.text(sig + 0.002, 9.6, f'tiers sized at\n{sig:.3f} mm RMS', fontsize=8, va='top')
ax.axhline(1, color='black', lw=0.6, ls=':')
ax.axhline(4, color='black', lw=0.6, ls=':')
ax.text(0.198, 1, '1 %', va='bottom', ha='right', fontsize=8)
ax.text(0.198, 4, '4 %', va='bottom', ha='right', fontsize=8)
ax.set_xlim(0, 0.2)
ax.set_ylim(0, 10)
ax.set_xlabel('RMS motion of the mass relative to the clamps (mm)')
ax.set_ylabel('Frequency rise of the member alone (%)')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=8, loc='upper left')
ax.set_title('(c) How the strips stiffen with motion', fontsize=10)
fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig_member.png')
fig.savefig(out, dpi=150)
print('wrote', out)
