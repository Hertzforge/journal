"""Figure 3: what full level is on the study's problems: the peak of the target at the control
gauges, and how far the full-level pulse moves the structure (the median fall of the softening
modes and the member's rise, at the peak of each mode's envelope). Copyright 2026 Kevin Cross.
MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import BLUE, ORANGE, GREEN, MUTED, SYSTEM, SYSTEM_ORDER, rows, num, save

table = [r for r in rows('problems.csv') if r['set'] == 'study']
TARGETS = [('srs', 'SRS', BLUE, 'o'), ('half_sine', 'half-sine', ORANGE, 's'),
           ('sawtooth', 'sawtooth', GREEN, '^')]
fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.2))
for k, (key, label, color, marker) in enumerate(TARGETS):
    for i, cls in enumerate(SYSTEM_ORDER):
        y = [num(r[f'{key}_peak_g']) for r in table if r['cls'] == cls]
        x = i + (k - 1) * 0.22 + np.zeros(len(y))
        ax[0].scatter(x, y, s=7, color=color, marker=marker, alpha=0.6,
                      label=label if i == 0 else None)
ax[0].set_yscale('log')
ax[0].set_xticks(range(5))
ax[0].set_xticklabels([SYSTEM[c] for c in SYSTEM_ORDER])
ax[0].set_xlabel('System (shakers x control gauges)')
ax[0].set_ylabel('Peak at full level (g)')
ax[0].set_title('(a) Full-level peak, every problem', loc='left', fontsize=9)
ax[0].legend(fontsize=7, loc='upper left')

groups = [('realistic', 'realistic'), ('strong', 'strong'), ('realistic_soft', 'realistic,\nsoft only'),
          ('strong_soft', 'strong,\nsoft only'), ('realistic_hard', 'realistic,\nhard only'),
          ('strong_hard', 'strong,\nhard only')]
for panel, column, title, scale in ((1, 'soft_p50', '(b) Median fall of the softening modes', -100),
                                    (2, 'largest_rise', '(c) Largest rise of any mode', 100)):
    keep = [g for g in groups if (column == 'soft_p50' and not g[0].endswith('hard'))
            or (column == 'largest_rise' and not g[0].endswith('soft'))]
    for k, (key, label, color, marker) in enumerate(TARGETS):
        for i, (tier, _) in enumerate(keep):
            y = np.array([num(r[f'{key}_{column}']) for r in table if r['tier'] == tier]) * scale
            q = np.nanpercentile(y, [25, 50, 75])
            x = i + (k - 1) * 0.22
            ax[panel].plot([x, x], [q[0], q[2]], color=color, lw=1.2)
            ax[panel].plot(x, q[1], marker=marker, color=color, ms=5, ls='none',
                           label=label if i == 0 else None)
    ax[panel].set_xticks(range(len(keep)))
    ax[panel].set_xticklabels([g[1] for g in keep], fontsize=7)
    ax[panel].set_ylabel('Frequency change at full level (%)')
    ax[panel].set_title(title, loc='left', fontsize=9)
    ax[panel].set_ylim(bottom=0)
ax[1].text(0.5, 0.62, 'median over the problems;\nbars span the quartiles', transform=ax[1].transAxes, ha='center',
           va='top', fontsize=7, color=MUTED)
fig.tight_layout()
save(fig, 'fig3_full_level')
