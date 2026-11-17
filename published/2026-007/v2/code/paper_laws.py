"""The six laws and the shared closed loop, written from the article's own equations (Sections 2.1
to 2.7 and Appendix A), for the numerical check against the shipped laws (Section 5) and for the
worked example (Appendix B). Nothing here imports or calls Hertzforge.

Copyright 2026 Kevin Cross. MIT license.
"""
import numpy as np
from scipy.optimize import minimize

from make_data import FREQ, structure

# ---------------------------------------------------------------------------------------------
# Section 1.4 and 2.2: the regularized pseudo-inverse, H+ = V diag(f) U^H (W).
# ---------------------------------------------------------------------------------------------


def pinv(h, rule='truncated', amount=1e-3, target_diag=None):
    """Equation (pinv-filter): truncation keeps 1/s for s above amount times the largest; Tikhonov
    uses s / (s^2 + (amount s1)^2); with target_diag the gauges are weighted by 1/sqrt(G_ref,kk)."""
    w = np.ones(h.shape[0]) if target_diag is None else 1 / np.sqrt(np.maximum(target_diag, 1e-12 * max(target_diag)))
    u, s, vh = np.linalg.svd(w[:, None] * h)
    floor = max(h.shape) * np.finfo(float).eps * s[0]
    if rule == 'truncated':
        f = np.where(s > max(amount * s[0], floor), 1 / np.where(s > 0, s, 1), 0.0)
    elif rule == 'tikhonov':
        f = np.where(s > floor, s / (s ** 2 + (amount * s[0]) ** 2), 0.0)
    else:
        f = np.where(s > floor, 1 / np.where(s > 0, s, 1), 0.0)
    k = len(s)
    return (vh.conj().T[:, :k] * f) @ u[:, :k].conj().T * w[None, :]


# ---------------------------------------------------------------------------------------------
# Section 2.1: the shared closed loop on one line (as many sources as gauges, so the loop runs in
# the gauges' own coordinates and A = H+).
# ---------------------------------------------------------------------------------------------


def factor_with_zeros(g):
    """G = R R^H with R lower triangular; a pivot at or below 1e-10 of its autospectrum is zero."""
    n = g.shape[0]
    r = np.zeros_like(g, dtype=complex)
    live = np.zeros(n, bool)
    for j in range(n):
        d = g[j, j].real - np.sum(np.abs(r[j, :j]) ** 2)
        if g[j, j].real > 0 and d > 1e-10 * g[j, j].real:
            live[j] = True
            r[j, j] = np.sqrt(d)
            for k in range(j + 1, n):
                r[k, j] = (g[k, j] - np.sum(r[k, :j] * np.conj(r[j, :j]))) / r[j, j]
    return r, live


def loop_step(z, a, target, measured, live, last_drive, e=0.5, up_db=3.5, down_db=6.0, safeguards=False):
    """One correction of the factor: equations (first-form), (second-form), the diagonal limit,
    the hold on a source that does not answer, the bound on what a source commands, the floor and
    the halving of the step (Section 2.1, steps 3 to 10).

    With safeguards=True, two rules of Smallwood's appendix that the shipped loop does not have are
    added, as Section 6 describes: the second form acts only on a cross term that is not zero, and
    a cross term that is exactly zero after the update is set to the floor (rows the hold holds
    excepted). This is an experiment of this article, not Hertzforge's loop."""
    q = z.shape[0]
    err = target - measured
    gmax = max(target[k, k].real for k in range(q))
    zmin = 1e-4 * np.sqrt(gmax)
    d = np.zeros_like(z)
    second = np.zeros((q, q), bool)
    for j in range(q):
        if not live[j]:
            continue
        div = max(z[j, j].real, zmin)
        d[j, j] = (err[j, j].real - sum(2 * (d[j, t] * np.conj(z[j, t])).real for t in range(j))) / (2 * div)
        for k in range(j + 1, q):
            t = err[k, j] - sum(d[k, m] * np.conj(z[j, m]) + z[k, m] * np.conj(d[j, m]) for m in range(j))
            dkj = (t - z[k, j] * d[j, j].real) / div
            if err[k, k].real < 0 and abs(z[k, j] + e * dkj) > abs(z[k, j]) and not (safeguards and z[k, j] == 0):
                g = target[k, k].real
                dkj = -0.5 * z[k, j] if (g <= 0 or -err[k, k].real >= 0.5 * g) else z[k, j] * err[k, k].real / (2 * g)
                second[k, j] = True
            d[k, j] = dkj
    up, down = 10 ** (up_db / 20), 10 ** (-down_db / 20)
    for j in range(q):
        if live[j]:
            step, lo, hi = e * d[j, j].real, z[j, j].real * (down - 1), z[j, j].real * (up - 1)
            if step > hi or step < lo:
                c = (hi if step > hi else lo) / step
                d[j:, j] = np.where(second[j:, j], d[j:, j], d[j:, j] * c)
    held = np.zeros(q, bool)
    for k in range(q):                                     # the hold
        commanded = np.sum(np.abs(z[k, :k + 1]) ** 2)
        if commanded > 0 and measured[k, k].real < 0.03 * commanded:
            held[k] = True
            grows = np.abs(z[k, :k + 1] + e * d[k, :k + 1]) > np.abs(z[k, :k + 1])
            d[k, :k + 1] = np.where(grows, 0, d[k, :k + 1])
    znew = z + e * d
    for k in range(q):                                     # the bound
        old, new = np.sum(np.abs(z[k, :k + 1]) ** 2), np.sum(np.abs(znew[k, :k + 1]) ** 2)
        limit = max(10 * target[k, k].real, old)
        if new > limit:
            znew[k, :k + 1] *= np.sqrt(limit / new)
    if safeguards:                                         # the experiment's minimum
        for j in range(q):
            for k in range(j + 1, q):
                if live[j] and not held[k] and znew[k, j] == 0:
                    znew[k, j] = zmin
    for j in range(q):                                     # the floor
        if live[j] and znew[j, j].real < zmin:
            old = z[j, j].real
            frac = np.clip(max(znew[j, j].real, 0) / old, 0, 1) if old > 0 else 0.0
            znew[j + 1:, j] = z[j + 1:, j] * frac
            znew[j, j] = zmin
    old = np.diag(last_drive).real                        # the halving
    floor = 1e-6 * old.max()
    alpha = 1.0
    for _ in range(31):
        trial = z + alpha * (znew - z)
        ratio = np.sum(np.abs(a @ trial) ** 2, axis=1) / np.maximum(old, floor)
        if np.all(ratio <= up * up * (1 + 1e-12)) and np.all(ratio >= down * down * (1 - 1e-12)):
            return trial
        alpha *= 0.5
    return z


def closed_loop(true, estimate, target, loops=30, a_of=None, safeguards=False, trace=None):
    """The default law on every line of a stack: the seed Z = R, then `loops` corrections, the
    response measured exactly on the true structure. Returns each gauge's error, dB, per loop."""
    a_of = a_of or (lambda h: pinv(h))
    n = true.shape[0]
    err = np.zeros((loops + 1, n, true.shape[1]))
    for i in range(n):
        a = a_of(estimate[i])
        tg = target[i] if target.ndim == 3 else target
        r, live = factor_with_zeros(tg)
        z = r.copy()
        drive = (a @ z) @ (a @ z).conj().T
        for k in range(loops + 1):
            y = true[i] @ drive @ true[i].conj().T
            err[k, i] = 10 * np.log10(np.diag(y).real / np.diag(tg).real)
            if trace is not None and i == trace[0]:
                trace[1].append((k, z.copy(), y.copy()))
            if k == loops:
                break
            z = loop_step(z, a, tg, y, live, drive, safeguards=safeguards)
            drive = (a @ z) @ (a @ z).conj().T
    return err


def open_loop(true, estimate, target):
    """Section 2.3: equation (pinv) every loop; the error at the true structure, dB."""
    out = np.zeros((true.shape[0], true.shape[1]))
    for i in range(true.shape[0]):
        a = pinv(estimate[i])
        y = true[i] @ (a @ target @ a.conj().T) @ true[i].conj().T
        out[i] = 10 * np.log10(np.diag(y).real / np.diag(target).real)
    return out


# ---------------------------------------------------------------------------------------------
# Section 2.6: the minimum-drive problem on one line of a square, invertible structure, solved in
# the coordinates of the target (Appendix A.5): with F = H^-H H^-1 and the target's autospectra
# d held, the least drive is F11 d1 + F22 d2 - 2 |F12| sqrt(d1 d2), at full coherence.
# ---------------------------------------------------------------------------------------------


def min_drive_line(h, y, lam, w=None):
    w = 1 / y if w is None else w
    hinv = np.linalg.inv(h)
    f = hinv.conj().T @ hinv

    def least_power(d):
        return f[0, 0].real * d[0] + f[1, 1].real * d[1] - 2 * abs(f[0, 1]) * np.sqrt(d[0] * d[1])

    def objective(p):
        d = p ** 2
        return float(np.sum(w * np.abs(y - d)) + lam * least_power(d))

    best = None
    for s0 in [np.sqrt(y), 0.5 * np.sqrt(y), 0.1 * np.sqrt(y), np.array([np.sqrt(y[0]), 0.1]),
               np.array([0.1, np.sqrt(y[1])]), np.array([1e-3, 1e-3])]:
        res = minimize(objective, s0, method='Nelder-Mead',
                       options={'xatol': 1e-13, 'fatol': 1e-16, 'maxiter': 20000, 'maxfev': 20000})
        if best is None or res.fun < best.fun:
            best = res
    d = best.x ** 2
    # Exact control of either autospectrum is a kink of the objective; try it directly.
    for cand in ([y[0], None], [None, y[1]], [y[0], y[1]]):
        def obj1(t, cand=cand):
            dd = np.array([cand[0] if cand[0] is not None else t[0] ** 2,
                           cand[1] if cand[1] is not None else t[-1] ** 2])
            return objective(np.sqrt(dd))
        free = [c is None for c in cand]
        if any(free):
            r = minimize(obj1, [np.sqrt(y[free.index(True)])], method='Nelder-Mead',
                         options={'xatol': 1e-13, 'fatol': 1e-16})
            dd = np.array([cand[0] if cand[0] is not None else r.x[0] ** 2,
                           cand[1] if cand[1] is not None else r.x[0] ** 2])
        else:
            dd = np.array(cand, float)
        if objective(np.sqrt(dd)) < objective(np.sqrt(d)):
            d = dd
    power = least_power(d)
    return power, float(np.sum(w * np.abs(y - d))), d


GRID = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6]


def min_drive_choice(points, y, shortfall_db=3.0):
    """The automatic choice of equation (knee): leave out the points in the top tenth of drive
    power or of error, and those keeping less than the largest shortfall; take the least product."""
    inp = np.array([p[0] for p in points])
    res = np.array([p[1] for p in points])
    floor = 1e-12 * (inp.max() + res.max())
    keep = 10 ** (-shortfall_db / 10)
    best, score = 0, np.inf
    for g, (power, residual, d) in enumerate(points):
        if power > 0.9 * inp.max() or residual > 0.9 * res.max():
            continue
        if any(min(d[k] / y[k], 1) < keep for k in range(len(y))):
            continue
        s = (power + floor) * (residual + floor)
        if s < score:
            best, score = g, s
    return best


# ---------------------------------------------------------------------------------------------
# Section 2.7: the band-average law's first solve, one gauge and one shaker, with the threshold
# sweep and the common price ("front").
# ---------------------------------------------------------------------------------------------


def octave_edges(f_min, f_max, order):
    ratio = 10 ** 0.3
    lb, ub = [], []
    for b in range(-200, 201):
        power = (2 * b + 1) / (2 * order) if order % 2 == 0 else b / order
        centre = 1000 * ratio ** power
        lower, upper = round(centre * ratio ** (-1 / (2 * order)), 12), round(centre * ratio ** (1 / (2 * order)), 12)
        if max(f_min, 10.0) < upper and f_max > lower:
            lb.append(lower)
            ub.append(upper)
    return np.array(lb), np.array(ub)


def band_average_first_solve(h, f, spec, df, order=6):
    """Equation (band): band targets and sensitivities; the Tikhonov filter s/(s^2 + (s1/kappa)^2);
    81 thresholds from 1 to 1e5; one common price swept over 241 values; of the prices within
    0.1 dB of the best mean error, the least drive energy. Returns the drive per line and each
    line's threshold."""
    lb, ub = octave_edges(f[1], f[-1], order)
    ov = lambda fk, l, u: max(min(fk + df / 2, u) - max(fk - df / 2, l), 0.0)
    bands = []
    for l, u in zip(lb, ub):
        width = u - l
        t = sum(ov(fk, l, u) / width * spec[k] for k, fk in enumerate(f))
        sel = [k for k, fk in enumerate(f) if l <= fk < u and spec[k] > 0]
        if not sel:
            continue
        wk = np.array([ov(f[k], l, u) for k in sel])
        a = float(np.sum(wk * np.abs(h[sel]) ** 2) / width)   # the band sensitivity, 1 x 1
        bands.append((sel, wk, a, t))
    kappas = 10 ** np.linspace(0, 5, 81)
    err = np.full((len(kappas), len(bands)), np.nan)
    energy = np.zeros((len(kappas), len(bands)))
    drive = np.zeros((len(kappas), len(bands)))
    for i, kap in enumerate(kappas):
        for b, (sel, wk, a, t) in enumerate(bands):
            p = max(a / (a * a + (a / kap) ** 2) * t, 0.0)
            drive[i, b] = p
            r = a * p
            if t > 0:
                err[i, b] = abs(10 * np.log10(max(r / t, 1e-6)))
            energy[i, b] = p * wk.sum()
    scored = [b for b in range(len(bands)) if not np.all(np.isnan(err[:, b]))]
    weighted = np.where(np.isnan(err[:, scored]), np.inf, err[:, scored])
    mu_ref = np.sum(weighted[0][np.isfinite(weighted[0])]) / max(energy[-1, scored].sum(), 1e-300)
    picks, errs, energies = [], [], []
    for scale in 10 ** np.linspace(-6, 6, 241):
        pick = [int(np.argmin(weighted[:, j] + mu_ref * scale * energy[:, b])) for j, b in enumerate(scored)]
        picks.append(pick)
        errs.append(np.mean([weighted[pick[j], j] for j in range(len(scored))]))
        energies.append(sum(energy[pick[j], b] for j, b in enumerate(scored)))
    best = min(errs)
    near = [i for i in range(len(errs)) if errs[i] <= best + 0.1]
    sel_i = near[int(np.argmin([energies[i] for i in near]))]
    out, thr = np.zeros(len(f)), np.zeros(len(f))
    for j, b in enumerate(scored):
        k = picks[sel_i][j]
        out[bands[b][0]] = drive[k, b]
        thr[bands[b][0]] = kappas[k]
    return out, thr


# ---------------------------------------------------------------------------------------------
# Section 2.5: the buzz-test target of one pair.
# ---------------------------------------------------------------------------------------------


def buzz_pair(b, g11, g22, floor=0.1):
    c = b[0, 1] / np.sqrt(b[0, 0].real * b[1, 1].real)
    cross = np.sqrt(g11 * g22) * c if abs(c) ** 2 >= floor else 0.0
    return np.array([[g11, cross], [np.conj(cross), g22]])


if __name__ == '__main__':
    print(len(FREQ), structure('loop_true').shape)
