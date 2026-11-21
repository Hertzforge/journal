"""The claims set beside the held-back structures. Left: every paired claim, the difference the study
gave on the same system (structures 0 to 9) against the difference on the held-back structures (20,
21, 22, 23 and 52), with the marker's shape and color its verdict; a claim on the diagonal carried
over exactly, and the grey band is the 0.2 dB inside which nothing is claimed. Right: every level
claim the same way, with the lines at +1.0 and -1.0 dB. From ../data/audit_verdicts.csv (written by
claims_check.py).

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
from style import BLUE, GRID, MUTED, ORANGE, RED, TEXT, plt, rows, save

LOOK = {'holds': (BLUE, 'o', 'Holds'), 'inside 0.2 dB': (ORANGE, 's', 'Inside 0.2 dB'), 'not borne out': (RED, 'X', 'Not borne out')}
v = [r for r in rows('audit_verdicts.csv') if r['held_back_db'] != '' and r['study_same_system_db'] != '']
fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.4))
for ax, kind in zip(axes, ('pair', 'level')):
    pts = [r for r in v if r['kind'] == kind]
    lim = max([1.0] + [abs(float(r[k])) for r in pts for k in ('study_same_system_db', 'held_back_db')]) * 1.08
    band = 0.2 if kind == 'pair' else 1.0
    ax.axhspan(-band, band, color=GRID, zorder=0)
    ax.plot([-lim, lim], [-lim, lim], color=MUTED, lw=0.8, ls='--', zorder=1)
    ax.axhline(0, color=TEXT, lw=0.6)
    ax.axvline(0, color=TEXT, lw=0.6)
    for verdict, (c, m, name) in LOOK.items():
        p = [r for r in pts if r['verdict'] == verdict]
        if p:
            ax.scatter([float(r['study_same_system_db']) for r in p], [float(r['held_back_db']) for r in p], s=26 if m == 'o' else 40,
                       color=c, marker=m, edgecolor='white', linewidth=0.5, zorder=3, label=f'{name} ({len(p)})')
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect('equal')
    ax.legend(fontsize=7.5, loc='upper left')
    if kind == 'pair':
        ax.set_title('Differences between two laws', fontsize=9)
        ax.set_xlabel('Study structures: median difference, dB')
        ax.set_ylabel('Held-back structures: median difference, dB')
    else:
        ax.set_title('Level of a law at its defaults', fontsize=9)
        ax.set_xlabel('Study structures: median level error, dB')
        ax.set_ylabel('Held-back structures: median level error, dB')
fig.tight_layout()
save(fig, 'fig_held_back.png')
