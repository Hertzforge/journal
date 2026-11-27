"""Figure 1: how far each mode of the twelve nonlinear screen structures moves at full level, in its
own half-power bandwidths. data=fig1_mode_shift.csv. Copyright 2026 Kevin Cross. MIT license."""
import numpy as np
import matplotlib.pyplot as plt
from style import rows, save, TIER_STYLE, SYSTEM, MUTED, TEXT

r = rows('fig1_mode_shift.csv')
problems = []
for tier in ('realistic', 'strong'):
    for system in ('frame-6x6', 'frame-12x6'):
        for s in ('0', '1', '2'):
            problems.append((system, tier, s))
fig, ax = plt.subplots(figsize=(7.2, 3.4))
rng = np.random.default_rng(1)
for i, (system, tier, s) in enumerate(problems):
    y = np.array([float(x['shift_in_bandwidths']) for x in r
                  if x['system'] == system and x['tier'] == tier and x['structure'] == s])
    color, _, marker = TIER_STYLE[tier]
    ax.scatter(i + rng.uniform(-0.28, 0.28, len(y)), y, s=7, color=color, marker=marker, alpha=0.45,
               linewidths=0, label=tier if (system, s) == ('frame-6x6', '0') else None)
    ax.plot([i - 0.35, i + 0.35], [np.median(y)] * 2, color=TEXT, lw=2)
for v, what in ((0.25, 'a quarter bandwidth'), (1.0, 'one bandwidth')):
    ax.axhline(v, color=MUTED, ls='--', lw=1)
    ax.text(-0.45, v * 1.06, what, ha='left', va='bottom', fontsize=8, color=MUTED,
            bbox=dict(facecolor='white', edgecolor='none', pad=0.5), zorder=5)
ax.set_yscale('log')
ax.set_ylim(0.01, 12)
ax.set_xticks(range(len(problems)))
ax.set_xticklabels([f'{SYSTEM[sy.split("-")[1]]}\n{s}' for sy, t, s in problems], fontsize=7.5)
ax.set_xlabel('system (shakers x controls) and structure, realistic tier left, strong tier right')
ax.set_ylabel('shift at full level (half-power bandwidths)')
ax.plot([], [], color=TEXT, lw=2, label='median of the structure')
ax.legend(loc='lower right', ncol=3, fontsize=8)
ax.grid(axis='x', visible=False)
save(fig, 'fig1_mode_shift')
