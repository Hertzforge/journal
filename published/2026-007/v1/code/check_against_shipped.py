"""Section 5: compares the laws as the article writes them (paper_laws.py, make_data.py) with the
shipped laws' outputs on the same made-up structures (written by shipped_laws/ into ../data) and
prints the largest differences. Run after make_data.py and shipped_laws.

Copyright 2026 Kevin Cross. MIT license.
"""
import numpy as np

from make_data import DF, FREQ, column_of, structure
import paper_laws as P

rows = []


def report(what, compared, value, unit, tol):
    ok = value <= tol
    rows.append((what, compared, value, unit, tol, ok))
    print(f'{what}: {compared}; largest difference {value:.2e} {unit} (tolerance {tol:g}) {"agrees" if ok else "DIFFERS"}')


true, estimate = structure('loop_true'), structure('loop_estimate')
target = np.eye(2, dtype=complex)

# 2.3 pseudo-inverse, open loop: the RMS error over the band at each gauge, every loop.
mine = P.open_loop(true, estimate, target)
mine_rms = np.sqrt(np.mean(mine ** 2, axis=0))
rms = column_of('fig3_closed_loop_rms.csv')
d = max(abs(float(r[f'open_loop_control{c + 1}_rms_db']) - mine_rms[c]) for r in rms for c in (0, 1))
report('pinv_open', f'RMS error over 1,161 lines at 2 gauges, loops 0 to 30 ({2 * len(rms)} values)', d, 'dB', 1e-6)

# 2.1 and 2.2 the shared closed loop (pinv_closed): every line's error after 0, 5 and 30 loops,
# and the RMS over the band at every loop.
err = P.closed_loop(true, estimate, target, loops=30)
lines = column_of('fig3_closed_loop_lines.csv')
worst = max(abs(err[k, i, c] - float(r[f'control{c + 1}_after_{k}_loops_db']))
            for i, r in enumerate(lines) for c in (0, 1) for k in (0, 5))
report('pinv_closed', f'error on each of 1,161 lines at 2 gauges after 0 and 5 loops ({4 * len(lines)} values)',
       worst, 'dB', 1e-6)
mine_rms = np.sqrt(np.mean(err ** 2, axis=1))
shipped_rms = np.array([[float(r[f'control{c + 1}_rms_db']) for c in (0, 1)] for r in rms])
by_loop = np.abs(shipped_rms - mine_rms).max(axis=1)
report('pinv_closed', 'RMS error over the band at 2 gauges, loops 0 to 22 (46 values)', by_loop[:23].max(), 'dB', 1e-6)
# From about loop 22 on, a few lines near three resonances are sensitive to rounding: the same
# implementation with the estimate changed by one part in 10^15 moves them. The shipped law's
# difference from this implementation is compared with that spread, not with a fixed tolerance.
spread_rms, spread_line = 0.0, 0.0
for eps in (1e-15, -1e-15, 2e-15):
    other = P.closed_loop(true, estimate * (1 + eps), target, loops=30)
    spread_rms = max(spread_rms, np.abs(np.sqrt(np.mean(other ** 2, axis=1)) - mine_rms)[23:].max())
    spread_line = max(spread_line, np.abs(other[30] - err[30]).max())
line30 = max(abs(err[30, i, c] - float(r[f'control{c + 1}_after_30_loops_db'])) for i, r in enumerate(lines) for c in (0, 1))
print(f'pinv_closed, loops 23 to 30: shipped against this implementation, RMS {by_loop[23:].max():.2e} dB, '
      f'one line after 30 loops {line30:.2f} dB; this implementation against itself with the estimate changed '
      f'by 1 to 2 parts in 10^15, RMS {spread_rms:.2e} dB, one line {spread_line:.2f} dB')
rows.append(('pinv_closed late', '', by_loop[23:].max(), 'dB (rounding-sensitive)', 2 * spread_rms, by_loop[23:].max() <= 2 * spread_rms))

# 2.4 shape_svd: the directions kept on each line.
h = structure('shape')
s = np.linalg.svd(h, compute_uv=False)
kept = np.sum(s >= 0.2 * s[:, :1], axis=1)
b = column_of('shipped_check_shape.csv')
n_diff = sum(int(kept[i]) != int(float(r['directions_kept'])) for i, r in enumerate(b))
report('shape_svd', f'directions kept on each of {len(b)} lines', n_diff, 'lines', 0)

# 2.5 buzz_match: the modified target of one pair, from uncorrelated unit drives.
h = structure('buzz')
ident = h @ h.conj().transpose(0, 2, 1)
b = column_of('shipped_check_buzz.csv')
dc = dp = 0.0
for i, r in enumerate(b):
    g = P.buzz_pair(ident[i], 1.0, 1.0)
    coh = abs(g[0, 1]) ** 2
    dc = max(dc, abs(coh - float(r['reference_coherence'])))
    if coh > 0:
        dp = max(dp, abs((np.degrees(np.angle(g[0, 1])) - float(r['reference_phase_deg']) + 180) % 360 - 180))
report('buzz_match', f'target coherence on {len(b)} lines', dc, '', 1e-6)
report('buzz_match', f'target phase on the lines kept', dp, 'degrees', 1e-3)

# 2.6 min_drive: one line at 200 Hz, every point of the trade-off grid, and the automatic choice.
hl = structure('min_drive', f=np.array([200.0]))[0]
y = np.array([1.0, 0.5])
w = 1 / y
r0, d0 = float(np.sum(w * y)), float(np.sum(y / np.sum(np.abs(hl) ** 2, axis=1)))
pts = [P.min_drive_line(hl, y, rel * r0 / d0) for rel in P.GRID]
b = column_of('shipped_check_min_drive.csv')
fixed = [r for r in b if not r['tradeoff_relative'].startswith('auto')]
auto = [r for r in b if r['tradeoff_relative'].startswith('auto')][0]
top = max(float(r['drive_power']) for r in fixed)
dpow = max(abs(p[0] - float(r['drive_power'])) / top for p, r in zip(pts, fixed))
drat = max(abs(p[2][k] / y[k] - float(r[f'target{k + 1}_over_spec'])) for p, r in zip(pts, fixed) for k in (0, 1))
report('min_drive', 'drive power at 13 trade-offs, relative to the largest', dpow, '', 1e-5)
report('min_drive', 'target over specification at 13 trade-offs and 2 gauges', drat, '', 1e-5)
mine_choice = P.GRID[P.min_drive_choice(pts, y)]
shipped_choice = float(auto['tradeoff_relative'].split()[1])
report('min_drive', f'automatic choice (here {mine_choice:g}, shipped {shipped_choice:g})',
       abs(np.log10(mine_choice / shipped_choice)), 'decades', 0)

# 2.7 band_average: the first solve, drive and threshold on every line of the band.
f = np.arange(0.0, 600.0 + DF / 2, DF)
hb = structure('band', f=f)[:, 0, 0]
spec = np.where((f >= 40.0) & (f <= 500.0), 1.0, 0.0)
drive, thr = P.band_average_first_solve(hb, f, spec, DF)
b = column_of('fig7_band_average_drive.csv')
k = [int(round(float(r['frequency_hz']) / DF)) for r in b]
dd = max(abs(drive[i] - float(r['drive'])) / max(float(r['drive']), 1e-300) for i, r in zip(k, b) if float(r['drive']) > 0)
dt = sum(abs(thr[i] - float(r['band_threshold'])) > 1e-6 * float(r['band_threshold']) for i, r in zip(k, b) if float(r['drive']) > 0)
nz = sum(float(r['drive']) > 0 for r in b)
report('band_average', f'drive on {nz} lines, relative', dd, '', 1e-9)
report('band_average', f'threshold of the band on {nz} lines', dt, 'lines', 0)

print()
print('largest difference in dB over the comparisons held to a fixed tolerance:',
      f"{max(v for _, _, v, u, _, _ in rows if u == 'dB'):.2e} dB")
print('all agree' if all(r[5] for r in rows) else 'NOT ALL AGREE')
