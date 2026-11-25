"""Figure: measured frequency of each tracked mode through the pretest's levels, as a change from the low-level
identification, for one structure (6 x 6, realistic size, structure 2), with the true change at full level at the
right. Colour and line style give the call made by the rule fixed beforehand.
Data: ../data/e32_map_figure.json (e32_figure_data.py, from e32_score.py)."""
import json, os
from matplotlib.lines import Line2D
from style import *
J = json.load(open(os.path.join(DATA, 'e32_map_figure.json'))); x = J['levels_db']; xt = 3.0
LOOK = {'softening': (BLUE, '-', 1.1, 0.75), 'hardening': (ORANGE, '-', 2.6, 1.0), 'level-independent': (MUTED, '--', 0.9, 0.55)}
fig, ax = plt.subplots(figsize=(7.4, 4.4))
for m in J['modes']:
    c, ls, lw, al = LOOK[m['call']]; y = m['change_pct']
    ax.plot(x, y, ls, color=c, lw=lw, alpha=al, zorder=3 if m['call'] == 'hardening' else 2)
    rise = m['true_pct'] > 0
    ax.plot([xt], [m['true_pct']], 'D' if rise else 'o', ms=7 if rise else 4, mfc='none', mec=ORANGE if rise else BLUE, mew=1.2, zorder=4)
ax.axhline(0, color=TEXT, lw=0.7); ax.axvline(1.5, color=GRID, lw=1)
ax.set_xticks(list(x) + [xt]); ax.set_xticklabels(['Identification\n(%.0f dB)' % x[0]] + ['%g' % v for v in x[1:]] + ['True change\nat full level'])
ax.set_xlabel('Level of the pretest loop, dB relative to full level'); ax.set_ylabel('Change in mode frequency\nfrom the identification, %')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.legend(handles=[Line2D([], [], color=BLUE, lw=1.1, label='Measured, called softening'), Line2D([], [], color=ORANGE, lw=2.6, label='Measured, called hardening'),
                   Line2D([], [], color=MUTED, lw=0.9, ls='--', label='Measured, called level-independent'),
                   Line2D([], [], ls='none', marker='o', mfc='none', mec=BLUE, label='True change, a drop'),
                   Line2D([], [], ls='none', marker='D', mfc='none', mec=ORANGE, label='True change, a rise')], loc='lower left', fontsize=8)
save(fig, 'fig_map')
