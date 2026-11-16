"""Figure 5: the buzz-test reference of a pair of gauges: the coherence and phase it takes from
the identification, and the floor below which the pair is left independent. An illustration.

Reads ../data/fig5_buzz_reference.csv only. Copyright 2026 Kevin Cross. MIT license.
"""
from style import BLUE, ORANGE, TEXT, column, frequency_axis, plt, rows, save

t = rows('fig5_buzz_reference.csv')
f = column(t, 'frequency_hz')
fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 5.0), sharex=True)
a1.plot(f, column(t, 'identification_coherence'), color=BLUE, lw=1.4, label='Identification: the structure on its own')
a1.plot(f[::6], column(t, 'reference_coherence')[::6], color=ORANGE, ls='none', marker='^', ms=3.5,
        label='Buzz reference')
a1.plot(f, column(t, 'floor'), color=TEXT, lw=1.0, ls=':', label='Coherence floor, 0.1')
a1.set_ylabel('Coherence of the pair')
a1.set_ylim(-0.03, 1.03)
a1.legend(fontsize=7.5, loc='lower left')
a2.plot(f, column(t, 'identification_phase_deg'), color=BLUE, lw=1.4, label='Identification')
a2.plot(f[::6], column(t, 'reference_phase_deg')[::6], color=ORANGE, ls='none', marker='^', ms=3.5,
        label='Buzz reference (where the pair is kept)')
a2.set_ylabel('Phase of the pair (degrees)')
a2.set_ylim(-190, 190)
a2.set_yticks([-180, -90, 0, 90, 180])
frequency_axis(a2)
a2.legend(fontsize=7.5, loc='lower left')
fig.tight_layout()
save(fig, 'fig5_buzz_reference.png')
