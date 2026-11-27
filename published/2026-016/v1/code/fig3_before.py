"""Figure 3: what the study's problems show before any law runs. Reads data/problems.csv.
Copyright 2026 Kevin Cross. MIT license."""
import random

import matplotlib.pyplot as plt

from style import BLUE, GREEN, MUTED, ORANGE, RED, SYSTEM, SYSTEM_ORDER, TEXT, num, rows, save

study = [r for r in rows('problems.csv') if r['set'] == 'study']
rng = random.Random(0)
TIERS = [('linear', BLUE, 'o'), ('realistic', ORANGE, 's'), ('strong', GREEN, '^')]


def strip(ax, groups, key, log=False):
    for i, g in enumerate(groups):
        for j, (tier, color, marker) in enumerate(TIERS):
            ys = [num(r[key]) for r in study if r['system'] == g and r['kind'] == tier]
            xs = [i + (j - 1) * 0.24 + rng.uniform(-0.07, 0.07) for _ in ys]
            ax.scatter(xs, ys, s=9, color=color, marker=marker, alpha=0.75,
                       label=tier if i == 0 else None, lw=0)
    ax.set_xticks(range(len(groups)), [SYSTEM[g] for g in groups])
    if log:
        ax.set_yscale('log')


fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4))
ax = axes[0]
strip(ax, SYSTEM_ORDER, 'declared_rms_db')
ax.set_ylabel('declared deviation, dB RMS')
ax.set_xlabel('system (shakers x controls)')
ax.set_title('(a) what the shakers cannot reach', loc='left', color=TEXT)
ax.legend(fontsize=7, loc='upper right')

ax = axes[1]
strip(ax, SYSTEM_ORDER, 'ideal_drive_peak_v', log=True)
ax.axhline(10, color=RED, lw=0.9, ls='--', label="10 V: the engine's converter range")
ax.set_ylabel('ideal full-level drive peak, V, before the gain')
ax.set_xlabel('system (shakers x controls)')
ax.set_title('(b) the ideal drive', loc='left', color=TEXT)
ax.legend(fontsize=7, loc='upper left')

ax = axes[2]
for j, (tier, color, marker) in enumerate(TIERS[1:]):
    ys = [abs(num(r['t4_offset_bandwidths'])) for r in study
          if r['kind'] == tier and r['t4_offset_bandwidths'] != '']
    xs = [j + rng.uniform(-0.18, 0.18) for _ in ys]
    ax.scatter(xs, ys, s=9, color=color, marker=marker, alpha=0.75, lw=0)
ax.axhline(1, color=MUTED, lw=0.9, ls='--', label='one half-power half-bandwidth')
ax.set_xticks([0, 1], ['realistic', 'strong'])
ax.set_xlim(-0.6, 1.6)
ax.set_yscale('log')
ax.set_ylim(0.02, 30)
ax.set_ylabel('dwell resonance at full level from the tone,\nhalf-power half-bandwidths')
ax.set_title('(c) where the dwell mode moves', loc='left', color=TEXT)
ax.legend(fontsize=7, loc='upper center')
fig.tight_layout()
save(fig, 'fig3_before')
