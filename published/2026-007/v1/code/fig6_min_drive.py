"""Figure 6: the minimum-drive target on one line of a two-shaker, two-gauge structure. Left, the
drive power a target needs as its cross term's phase and coherence change, the autospectra held.
Right, the trade-off between drive power and the error in the autospectra, the point the knee
alone would pick, and the point the automatic rule picks with its largest shortfall. An illustration, not a run.

Reads ../data/fig6a_min_drive_phase.csv and fig6b_min_drive_pareto.csv only.
Copyright 2026 Kevin Cross. MIT license.
"""
from style import BLUE, GREEN, ORANGE, TEXT, column, plt, rows, save

a = rows('fig6a_min_drive_phase.csv')
b = rows('fig6b_min_drive_pareto.csv')
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.9))
for coh, c, ls in (('0', TEXT, ':'), ('0.5', GREEN, '--'), ('1', BLUE, '-')):
    sel = [r for r in a if float(r['coherence']) == float(coh)]
    a1.plot(column(sel, 'cross_phase_deg'), column(sel, 'drive_power'), color=c, ls=ls, lw=1.5,
            label=f'Coherence {coh}')
a1.set_xlabel('Phase of the cross term (degrees)')
a1.set_ylabel('Drive power (trace of the drive matrix)')
a1.set_xticks([-180, -90, 0, 90, 180])
a1.legend(fontsize=7.5)
x = column(b, 'residual_relative')
y = column(b, 'drive_power_over_d0')
rel = [r['tradeoff_relative'] for r in b]
chosen = [int(r['chosen']) for r in b]
knee = [int(r['knee_without_shortfall']) for r in b]
a2.plot(x, y, color=BLUE, lw=1.0, ls='-', marker='o', mfc='white', ms=5, label='The trade-off grid, 1e-6 to 1e6')
for xi, yi, ri, ki in zip(x, y, rel, knee):
    if ki:
        a2.plot([xi], [yi], color=TEXT, marker='D', mfc='none', ms=9, ls='none', label=f'The knee alone ({ri})')
for xi, yi, ri, ci in zip(x, y, rel, chosen):
    if ci:
        a2.plot([xi], [yi], color=ORANGE, marker='*', ms=14, ls='none', label=f'Picked with the 3 dB largest shortfall ({ri})')
exact = [g for g, r in enumerate(b) if float(r['residual_relative']) < 1e-3]
none = [g for g, r in enumerate(b) if float(r['drive_power_over_d0']) < 1e-6]
if exact:
    a2.annotate(f"{rel[exact[0]]} to {rel[exact[-1]]}: autospectra met,\nleast drive that meets them", (x[exact[0]], y[exact[0]]),
                xytext=(0.25, 3.0), fontsize=7.5, arrowprops=dict(arrowstyle='->', lw=0.8))
if none:
    a2.annotate(f"{rel[none[0]]} and above: no drive", (x[none[0]], y[none[0]]), xytext=(1.25, 0.02),
                fontsize=7.5, arrowprops=dict(arrowstyle='->', lw=0.8))
a2.set_yscale('symlog', linthresh=1e-2)
a2.set_xlabel('Error in the autospectra (sum of fractions missed)')
a2.set_ylabel('Drive power, relative')
a2.legend(fontsize=7.5)
fig.tight_layout()
save(fig, 'fig6_min_drive.png')
