"""Figure 2: the three targets at the first control gauge of one problem, and the SRS target with
Method 516.8's tolerance. Copyright 2026 Kevin Cross. MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import BLUE, ORANGE, GREEN, MUTED, rows, num, save

wave = rows('example_waveforms.csv')
t = np.array([num(r['time_s']) for r in wave])
srs_wave = np.array([num(r['srs_g']) for r in wave])
half = np.array([num(r['half_sine_g']) for r in wave])
saw = np.array([num(r['sawtooth_g']) for r in wave])
target = rows('example_srs_target.csv')
f = np.array([num(r['natural_hz']) for r in target])
a = np.array([num(r['target_g']) for r in target])

fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.0))
m = (t >= 0.58) & (t <= 0.70)
ax[0].plot((t[m] - 0.6) * 1e3, srs_wave[m], color=BLUE, lw=0.8)
ax[0].set_xlabel('Time from the start of the pulse (ms)')
ax[0].set_ylabel('Acceleration (g)')
ax[0].set_title('(a) SRS target: the waveform', loc='left', fontsize=9)
m = (t >= 0.82) & (t <= 0.98)
ax[1].plot((t[m] - 0.9) * 1e3, half[m], color=ORANGE, lw=1.0, label='half-sine')
ax[1].plot((t[m] - 0.9) * 1e3, saw[m], color=GREEN, lw=1.0, ls='--', label='terminal-peak sawtooth')
ax[1].set_xlabel('Time from the centre of the pulse (ms)')
ax[1].set_ylabel('Acceleration (g)')
ax[1].set_title('(b) Classical targets, 11 ms', loc='left', fontsize=9)
ax[1].legend(loc='upper left', fontsize=8)
ax[2].fill_between(f, a * 10 ** (-3 / 20), a * 10 ** (6 / 20), color=MUTED, alpha=0.15,
                   label='-3 / +6 dB')
ax[2].fill_between(f, a * 10 ** (-1.5 / 20), a * 10 ** (3 / 20), color=BLUE, alpha=0.25,
                   label='-1.5 / +3 dB (90 % of points)')
ax[2].plot(f, a, color=BLUE, lw=1.2, marker='o', ms=2, label='target')
ax[2].set_xscale('log')
ax[2].set_yscale('log')
ax[2].set_xlabel('Natural frequency (Hz), twelfth-octave points')
ax[2].set_ylabel('Maximax SRS, Q = 10 (g)')
ax[2].set_title('(c) SRS target and tolerance', loc='left', fontsize=9)
ax[2].legend(loc='lower right', fontsize=7)
fig.tight_layout()
save(fig, 'fig2_targets')
