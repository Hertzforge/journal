"""Writes the data behind every figure of the article into ../data.

These are illustrations, not results. Each one runs a law on a small made-up structure: a
few modes, two to six gauges, two to four shakers, an exact measurement and no noise. None of it
is a run of the control service, and none of it is from the study the article reports.

The made-up structures are written to data/toy_structures.csv first. Figures 3 and 7 come from
the shipped laws themselves, run on those structures by the Rust program in shipped_laws/ (see
README.md). The others are computed here from the law's equations as the code states them, and
check_against_shipped.py compares each with the shipped code. The code is
`crates/hertzforge-mimo-laws/src/` and `crates/hertzforge-law-band-average-math/src/` at
Hertzforge main commit acfcb970.

Run: python make_data.py (NumPy and SciPy). Copyright 2026 Kevin Cross. MIT
license.
"""
import csv
import os

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
DF = 0.5
FREQ = np.arange(20.0, 600.0 + DF / 2, DF)


def write(name, header, rows):
    with open(os.path.join(DATA, name), 'w', newline='') as file:
        out = csv.writer(file)
        out.writerow(header)
        for row in rows:
            out.writerow([f'{v:.6g}' if isinstance(v, float) else v for v in row])
    print('wrote', name)


# The made-up structures: gauges, shakers, modes (Hz), damping ratio, and the seed their mode
# shapes are drawn from. The estimate in Figure 3 is the true structure with every mode 3 % high.
SPECS = {
    'loop_true': (2, 2, [90.0, 160.0, 260.0, 410.0], 0.02, 1),
    'loop_estimate': (2, 2, [90.0 * 1.03, 160.0 * 1.03, 260.0 * 1.03, 410.0 * 1.03], 0.02, 1),
    'shape': (6, 4, [70.0, 110.0, 180.0, 240.0, 330.0, 470.0], 0.02, 4),
    'buzz': (2, 3, [85.0, 150.0, 240.0, 380.0], 0.02, 7),
    'min_drive': (2, 2, [90.0, 160.0, 260.0, 410.0], 0.02, 3),
    'band': (1, 1, [120.0, 310.0], 0.02, 11),
}


def shapes(name):
    nc, nd, modes_hz, zeta, seed = SPECS[name]
    rng = np.random.default_rng(seed)
    return modes_hz, zeta, rng.normal(size=(len(modes_hz), nc)), rng.normal(size=(len(modes_hz), nd))


def write_structures():
    rows = []
    for name in SPECS:
        modes_hz, zeta, out_shape, in_shape = shapes(name)
        for r, fr in enumerate(modes_hz):
            for side, table in (('gauge', out_shape), ('shaker', in_shape)):
                for i, v in enumerate(table[r]):
                    rows.append([name, r, repr(float(fr)), repr(zeta), side, i, repr(float(v))])
    write('toy_structures.csv', ['structure', 'mode', 'f_hz', 'zeta', 'side', 'index', 'shape'], rows)


def structure(name, f=FREQ):
    """Acceleration per unit force of a made-up modal structure, gauges by shakers per line:
    sum over modes of (f/fr)^2 / (1 - (f/fr)^2 + 2 i zeta f/fr) times the outer product of the
    mode's gauge and shaker shapes."""
    modes_hz, zeta, out_shape, in_shape = shapes(name)
    nc, nd = out_shape.shape[1], in_shape.shape[1]
    h = np.zeros((len(f), nc, nd), complex)
    for r, fr in enumerate(modes_hz):
        ratio = f / fr
        h += ((ratio ** 2) / (1 - ratio ** 2 + 2j * zeta * ratio))[:, None, None] \
            * np.outer(out_shape[r], in_shape[r])[None]
    return h


def column_of(name):
    with open(os.path.join(DATA, name), newline='') as file:
        return list(csv.DictReader(file))


def db(x):
    return 10 * np.log10(x)


# ----------------------------------------------------------------------------------------------
# Figure 1: the order of a run (the shipped defaults of crates/hertzforge-mimo-random/src/config.rs
# and the level schedule of crates/hertzforge-random/src/service/config.rs).
# ----------------------------------------------------------------------------------------------
def run_sequence():
    rows = [
        ('noise floor', 0, 1, None, None, 'Drives off: the noise floor'),
        ('identification', 1, 3, -20.0, -20.0, 'Uncorrelated random on every shaker, about 20 dB under the target'),
        ('gate', 3, 3.6, None, None, 'Coherence and condition gates'),
        ('prediction', 3.6, 4.2, None, None, "The law's first drive, predicted"),
        ('soft start', 4.2, 5.2, -21.0, -12.0, 'Soft start: 9 dB under the first step, climbing to it'),
        ('step', 5.2, 6.2, -12.0, -12.0, '-12 dB'),
        ('step', 6.2, 7.2, -9.0, -9.0, '-9 dB'),
        ('step', 7.2, 8.2, -6.0, -6.0, '-6 dB'),
        ('step', 8.2, 9.2, -3.0, -3.0, '-3 dB'),
        ('full level', 9.2, 12.0, 0.0, 0.0, 'Full level: the record'),
    ]
    write('fig1_run_sequence.csv', ['stage', 'start', 'end', 'level_db_start', 'level_db_end', 'label'],
          [(s, a, b, '' if l0 is None else l0, '' if l1 is None else l1, t) for s, a, b, l0, l1, t in rows])


# ----------------------------------------------------------------------------------------------
# Figure 2: one loop, in the order of crates/hertzforge-mimo-random/src/service.rs (module comment)
# and guards.rs.
# ----------------------------------------------------------------------------------------------
def loop_steps():
    rows = [
        (1, 'core', 'Play the drive in force at the present level'),
        (2, 'core', 'Estimate the response matrix; refer it to full level'),
        (3, 'core', 'Judge it: abort lines, a growing error'),
        (4, 'law', 'The law: target, measured response and frequency response in; next drive out'),
        (5, 'core', 'Check the drive: size, numbers, Hermitian, zero out of band; repair a small negative eigenvalue, refuse a large one'),
        (6, 'core', 'Cap each drive\'s change: +3.5 dB, -6 dB a loop'),
        (7, 'core', "Hold each drive's ceiling; limit the limit channels"),
        (8, 'core', 'Keep it as the drive in force'),
    ]
    write('fig2_one_loop.csv', ['order', 'owner', 'step'], rows)


# Figure 3 is drawn from the shipped default law's run (shipped_laws/); the loop as the article
# writes it is paper_laws.py, and check_against_shipped.py compares the two.


# ----------------------------------------------------------------------------------------------
# Figure 4: the shape constraint's choice of directions per line (support.rs, filter, the ratio
# selection: singular values at or above tau times the largest, at most the maximum).
# ----------------------------------------------------------------------------------------------
def shape_directions():
    h = structure('shape')
    s = np.linalg.svd(h, compute_uv=False)
    tau = 0.2
    kept = np.sum(s >= tau * s[:, :1], axis=1)
    write('fig4_shape_directions.csv',
          ['frequency_hz', 's1', 's2', 's3', 's4', 'threshold', 'directions_kept'],
          [[f, *s[i], tau * s[i, 0], int(kept[i])] for i, f in enumerate(FREQ)])


# ----------------------------------------------------------------------------------------------
# Figure 5: the buzz-test reference (buzz.rs, buzz_reference) on a pair of controls.
# ----------------------------------------------------------------------------------------------
def buzz_reference():
    h = structure('buzz')
    b = h @ h.conj().transpose(0, 2, 1)          # the response to uncorrelated unit drives
    coh = np.abs(b[:, 0, 1]) ** 2 / (b[:, 0, 0].real * b[:, 1, 1].real)
    phase = np.degrees(np.angle(b[:, 0, 1]))
    floor = 0.1
    kept = coh >= floor
    write('fig5_buzz_reference.csv',
          ['frequency_hz', 'identification_coherence', 'identification_phase_deg', 'floor',
           'reference_coherence', 'reference_phase_deg'],
          [[f, coh[i], phase[i], floor, coh[i] if kept[i] else 0.0, phase[i] if kept[i] else '']
           for i, f in enumerate(FREQ)])


# ----------------------------------------------------------------------------------------------
# Figure 6: the minimum-drive target on one line of a two-shaker, two-control structure
# (pareto.rs: the problem, the relative trade-off, and choose_tradeoff's rule).
# ----------------------------------------------------------------------------------------------
GRID = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6]
SHORTFALL_DB = 3.0                                # min_drive's default largest shortfall


def min_drive():
    f_line = 200.0
    h = structure('min_drive', f=np.array([f_line]))[0]
    y = np.array([1.0, 0.5])                      # the specified autospectra on this line
    w = 1 / y                                     # relative residual weights
    zinv = np.linalg.inv(h)
    fmat = zinv.conj().T @ zinv                   # drive power is tr(F Y) for a target Y

    rows = []
    for coherence in (0.0, 0.5, 1.0):
        for phase in np.linspace(-180, 180, 361):
            cross = np.sqrt(coherence * y[0] * y[1]) * np.exp(1j * np.radians(phase))
            target = np.array([[y[0], cross], [np.conj(cross), y[1]]])
            rows.append([coherence, phase, float(np.trace(fmat @ target).real)])
    write('fig6a_min_drive_phase.csv', ['coherence', 'cross_phase_deg', 'drive_power'], rows)

    r0 = float(np.sum(w * y))
    d0 = float(np.sum(y / np.sum(np.abs(h) ** 2, axis=1)))

    def solve(lam):
        def objective(p):
            l = np.array([[p[0], 0], [p[2] + 1j * p[3], p[1]]])
            x = l @ l.conj().T
            pred = np.diag(h @ x @ h.conj().T).real
            return float(np.sum(w * np.abs(y - pred)) + lam * np.trace(x).real)
        lmin = np.linalg.cholesky(zinv @ np.diag(y) @ zinv.conj().T)
        starts = [np.array([lmin[0, 0].real, lmin[1, 1].real, lmin[1, 0].real, lmin[1, 0].imag]) * s
                  for s in (1.0, 0.3, 0.05, 1e-3)]
        rng = np.random.default_rng(0)
        starts += [rng.normal(size=4) * np.sqrt(d0) for _ in range(8)]
        best = None
        for p0 in starts:
            res = minimize(objective, p0, method='Nelder-Mead',
                           options={'xatol': 1e-12, 'fatol': 1e-14, 'maxiter': 40000, 'maxfev': 40000})
            if best is None or res.fun < best.fun:
                best = res
        p = best.x
        l = np.array([[p[0], 0], [p[2] + 1j * p[3], p[1]]])
        x = l @ l.conj().T
        pred = np.diag(h @ x @ h.conj().T).real
        return float(np.trace(x).real), float(np.sum(w * np.abs(y - pred))), pred

    pts = []
    for rel in GRID:
        trace, residual, pred = solve(rel * r0 / d0)
        pts.append((rel, trace, residual, pred))
    inp = np.array([p[1] for p in pts])
    res = np.array([p[2] for p in pts])
    floor = 1e-12 * (inp.max() + res.max())
    knee = [(inp[g] + floor) * (res[g] + floor) if (inp[g] <= 0.9 * inp.max() and res[g] <= 0.9 * res.max())
            else np.inf for g in range(len(GRID))]
    # The largest shortfall (shortfall_db, 3 dB by default): a point whose target keeps less than
    # 10^(-0.3) of any control's specified autospectrum (each line counted at most at 1) is left out.
    retained = 10 ** (-SHORTFALL_DB / 10)
    keeps = [all(min(p[3][k] / y[k], 1.0) >= retained for k in range(len(y))) for p in pts]
    score = [knee[g] if keeps[g] else np.inf for g in range(len(GRID))]
    chosen = int(np.argmin(score)) if np.isfinite(min(score)) else 0
    knee_only = int(np.argmin(knee))
    write('fig6b_min_drive_pareto.csv',
          ['tradeoff_relative', 'drive_power_over_d0', 'residual_relative', 'target1_over_spec',
           'target2_over_spec', 'chosen', 'knee_without_shortfall'],
          [[rel, trace / d0, residual, pred[0] / y[0], pred[1] / y[1], int(g == chosen), int(g == knee_only)]
           for g, (rel, trace, residual, pred) in enumerate(pts)])


# ----------------------------------------------------------------------------------------------
# Figure 7: the band-average law's first solve on one control and one shaker (lib.rs: the band
# targets of initialize, the band sensitivity, one flat drive per band, bands.rs for the edges).
# ----------------------------------------------------------------------------------------------
def octave_edges(f_min, f_max, order):
    ratio = 10 ** 0.3
    lb, ub = [], []
    for b in range(-200, 201):
        power = (2 * b + 1) / (2 * order) if order % 2 == 0 else b / order
        centre = 1000 * ratio ** power
        lower = round(centre * ratio ** (-1 / (2 * order)), 12)
        upper = round(centre * ratio ** (1 / (2 * order)), 12)
        if max(f_min, 10.0) < upper and f_max > lower:
            lb.append(lower)
            ub.append(upper)
    return np.array(lb), np.array(ub)


if __name__ == '__main__':
    os.makedirs(DATA, exist_ok=True)
    write_structures()
    run_sequence()
    loop_steps()
    shape_directions()
    buzz_reference()
    min_drive()
