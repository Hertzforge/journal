"""Appendix B: one line (150 Hz) of the made-up two-gauge, two-shaker structure of Figure 3,
carried through the shared closed loop and each law, from the article's own equations
(paper_laws.py). Prints every number Appendix B quotes. Run: python worked_example.py

Copyright 2026 Kevin Cross. MIT license.
"""
import numpy as np

from make_data import DF, structure
import paper_laws as P

np.set_printoptions(precision=4, suppress=False)
F = 150.0
f = np.array([F])
h = structure('loop_true', f=f)[0]          # the structure as it is
he = structure('loop_estimate', f=f)[0]     # as the identification measured it: every mode 3 % high
g = np.diag([1.0, 0.5]).astype(complex)     # the target: autospectra 1 and 0.5, independent


def c(x):
    return f'{x.real:+.4f}{x.imag:+.4f}i'


def db(x):
    return 10 * np.log10(x)


print(f'B.1 The line, {F:g} Hz')
for name, m in (('H (the structure)', h), ('H estimate (identification)', he)):
    s = np.linalg.svd(m, compute_uv=False)
    print(f'  {name}: [[{c(m[0,0])}, {c(m[0,1])}], [{c(m[1,0])}, {c(m[1,1])}]]; singular values {s[0]:.4f}, {s[1]:.4f}; condition {s[0]/s[1]:.2f}')

print('B.2 Pseudo-inverse, open loop (pinv_open)')
a = P.pinv(he)
guu = a @ g @ a.conj().T
y = h @ guu @ h.conj().T
print(f'  drive autospectra {guu[0,0].real:.4f}, {guu[1,1].real:.4f}; drive coherence {abs(guu[0,1])**2/(guu[0,0].real*guu[1,1].real):.4f}')
print(f'  response autospectra {y[0,0].real:.4f}, {y[1,1].real:.4f} (error {db(y[0,0].real/1):+.2f}, {db(y[1,1].real/0.5):+.2f} dB); response coherence {abs(y[0,1])**2/(y[0,0].real*y[1,1].real):.4f}')
print(f'  the same drive on the estimate: {np.diag(he @ guu @ he.conj().T).real.round(6)}')

print('B.3 Pseudo-inverse, closed loop (pinv_closed), loops 0 to 8')
r, live = P.factor_with_zeros(g)
z = r.copy()
drive = (a @ z) @ (a @ z).conj().T
for k in range(9):
    y = h @ drive @ h.conj().T
    print(f'  loop {k}: error {db(y[0,0].real):+.3f}, {db(y[1,1].real/0.5):+.3f} dB; Z11 {z[0,0].real:.4f}, Z21 {c(z[1,0])}, Z22 {z[1,1].real:.4f}; '
          f'drive power {np.trace(drive).real:.4f}')
    z = P.loop_step(z, a, g, y, live, drive)
    drive = (a @ z) @ (a @ z).conj().T

print('B.4 Shape-constrained (shape_svd), ratio 0.2')
u, s, vh = np.linalg.svd(he)
m = int(np.sum(s >= 0.2 * s[0]))
print(f'  s2/s1 = {s[1]/s[0]:.4f}; directions kept m = {m}')
v1 = vh.conj().T[:, :m]
hc = he @ v1
gc = np.linalg.pinv(hc) @ g @ np.linalg.pinv(hc).conj().T
guu_s = v1 @ gc @ v1.conj().T
ys = h @ guu_s @ h.conj().T
print(f'  drive power {np.trace(guu_s).real:.4f} against {np.trace(guu).real:.4f} for the full inverse; '
      f'response {ys[0,0].real:.4f}, {ys[1,1].real:.4f} ({db(ys[0,0].real):+.2f}, {db(ys[1,1].real/0.5):+.2f} dB)')

print('B.5 Buzz-test matched (buzz_match)')
b = he @ he.conj().T
coh = abs(b[0, 1]) ** 2 / (b[0, 0].real * b[1, 1].real)
gb = P.buzz_pair(b, 1.0, 0.5)
print(f'  identification coherence {coh:.4f}, phase {np.degrees(np.angle(b[0,1])):.2f} degrees; target cross term {c(gb[0,1])}')
ab = P.pinv(he)
db_ = ab @ gb @ ab.conj().T
print(f'  first drive power {np.trace(db_).real:.4f}; drive coherence {abs(db_[0,1])**2/(db_[0,0].real*db_[1,1].real):.4f}')

print('B.6 Minimum drive (min_drive), this line alone')
yv = np.array([1.0, 0.5])
r0, d0 = float(np.sum(yv / yv)), float(np.sum(yv / np.sum(np.abs(he) ** 2, axis=1)))
print(f'  r0 = {r0:.4f}, d0 = {d0:.4f}')
pts = [P.min_drive_line(he, yv, rel * r0 / d0) for rel in P.GRID]
for rel, (pw, res, d) in zip(P.GRID, pts):
    print(f'  trade-off {rel:g}: drive power {pw:.5f}, weighted error {res:.4f}, target over specification {d[0]:.4f}, {d[1]/0.5:.4f}')
choice = P.min_drive_choice(pts, yv)
print(f'  automatic choice: {P.GRID[choice]:g}; drive power {pts[choice][0]:.5f} against {np.trace(guu).real:.5f} for the independent target')

print('B.7 Band average (band_average): the band of Figure 7 that holds 150 Hz')
fb = np.arange(0.0, 600.0 + DF / 2, DF)
hb = structure('band', f=fb)[:, 0, 0]
spec = np.where((fb >= 40.0) & (fb <= 500.0), 1.0, 0.0)
drive_b, thr = P.band_average_first_solve(hb, fb, spec, DF)
lb, ub = P.octave_edges(fb[1], fb[-1], 6)
i = int(np.where((lb <= F) & (F < ub))[0][0])
l, u = lb[i], ub[i]
sel = [k for k, x in enumerate(fb) if l <= x < u and spec[k] > 0]
wk = np.array([max(min(fb[k] + DF / 2, u) - max(fb[k] - DF / 2, l), 0.0) for k in sel])
sens = float(np.sum(wk * np.abs(hb[sel]) ** 2) / (u - l))
print(f'  band {l:.3f} to {u:.3f} Hz, {len(sel)} lines; band target 1; band sensitivity {sens:.5g}; threshold {thr[sel[0]]:g}')
print(f'  flat drive {drive_b[sel[0]]:.5g}; band response {sens*drive_b[sel[0]]:.5f} ({db(sens*drive_b[sel[0]]):+.3f} dB)')
line = sel[int(np.argmin(np.abs(fb[sel] - F)))]
print(f'  at {fb[line]:g} Hz itself: response {abs(hb[line])**2*drive_b[line]:.4f} ({db(abs(hb[line])**2*drive_b[line]):+.2f} dB)')
