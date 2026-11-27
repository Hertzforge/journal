"""Figure 2: the five tests' schedules on one problem, its reference against the specification,
and the ideal drive in engine volts after the drive gain. Reads data/schedules.csv and
data/example_reference.csv. Copyright 2026 Kevin Cross. MIT license."""
import matplotlib.pyplot as plt

from style import BLUE, GREEN, MUTED, ORANGE, PURPLE, RED, TEXT, num, rows, save

sched = rows('schedules.csv')
ref = rows('example_reference.csv')

fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.9))
ax = axes[0]
look = {'T1': (BLUE, '-', 'T1 up sweep, 1 oct/min'), 'T2': (ORANGE, '--', 'T2 up sweep, 4 oct/min'),
        'T5': (GREEN, '-.', 'T5 down sweep, 1 oct/min'), 'T3': (PURPLE, ':', 'T3 stepped, 12 steps an octave'),
        'T4': (RED, '-', 'T4 dwell')}
for test, (color, ls, label) in look.items():
    xs = [num(r['seconds']) for r in sched if r['test'] == test]
    ys = [num(r['hz']) for r in sched if r['test'] == test]
    ax.plot(xs, ys, color=color, ls=ls, lw=2.2 if test == 'T4' else 1.4, label=label)
ax.set_yscale('log')
ax.set_xlabel('time at full level, s')
ax.set_ylabel('tone frequency, Hz')
ax.set_title('(a) the tests', loc='left', color=TEXT)
ax.legend(fontsize=6.5, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)

hz = [num(r['hz']) for r in ref]
ax = axes[1]
ax.fill_between(hz, [num(r['ref_over_spec_db_min']) for r in ref],
                [num(r['ref_over_spec_db_max']) for r in ref], color=BLUE, alpha=0.18, lw=0,
                label='range over the 12 controls')
ax.plot(hz, [num(r['ref_over_spec_db_median']) for r in ref], color=BLUE, lw=1.3,
        label='median control')
ax.plot(hz, [num(r['ref_over_spec_db_min']) for r in ref], color=BLUE, lw=0.7, ls=':',
        label='lowest control')
ax.axhline(0, color=MUTED, lw=0.8)
ax.set_xscale('log')
ax.set_xlabel('frequency, Hz')
ax.set_ylabel('reference over specification, dB')
ax.set_title('(b) the reference', loc='left', color=TEXT)
ax.legend(fontsize=7, loc='lower left')

ax = axes[2]
ax.plot(hz, [num(r['ideal_drive_max_engine_v']) for r in ref], color=ORANGE, lw=1.3,
        label='largest drive of the ideal drive')
ax.axhline(1.0, color=TEXT, lw=0.9, ls='--', label='1 V: its peak')
ax.axhline(10 ** (6 / 20), color=RED, lw=0.9, ls='-.', label='ceiling, 6 dB over')
ax.set_xscale('log')
ax.set_ylim(0, 2.3)
ax.set_xlabel('frequency, Hz')
ax.set_ylabel('engine volts, peak')
ax.set_title('(c) the ideal drive after the gain', loc='left', color=TEXT)
ax.legend(fontsize=7, loc='upper left')
fig.tight_layout()
save(fig, 'fig2_tests')
