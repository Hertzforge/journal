"""Runs the port of Smallwood's Appendix A correction on the Figure 3 case of the article
(two gauges, two shakers, measured frequency response with every mode 3 percent high, exact
measurement, 30 loops, drive A Z Z^H A^H with A the pseudo-inverse truncated at 1e-3), beside the
Hertzforge build's loop (an independent port of factor.rs FactorLoop::iterate, own-coordinates case).

Usage: python run_fig3_case.py   (imports make_data.structure from the article's code/ folder, one up)

Copyright 2026 Kevin Cross. MIT license.
"""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from make_data import structure, FREQ                       # noqa: E402
from smallwood_port import correction, factor_with_zeros    # noqa: E402

TRUE, EST = structure('loop_true'), structure('loop_estimate')
NL = len(FREQ)
C08 = 0.8 * np.exp(1j * np.radians(30.0))
TARGETS = {'independent': np.eye(2, dtype=complex),
           'cross terms (coherence 0.64, 30 deg)': np.array([[1, C08], [np.conj(C08), 1]])}


def pinv_trunc(h, rc=1e-3):
    u, s, vh = np.linalg.svd(h)
    fl = max(h.shape) * np.finfo(float).eps * s[0]
    f = np.where(s > max(rc * s[0], fl), 1 / s, 0.0)
    return (vh.conj().T * f) @ u.conj().T


def build_step(z, a, gt, meas, live, last, e=0.5):
    """factor.rs FactorLoop::iterate at 646c4ca4 (own coordinates): first form with the second form
    swapped in, clamp, hold, update, bound, floor, drive limit by halving."""
    q = z.shape[0]; up, dn = 10 ** (3.5 / 20), 10 ** (-6 / 20)
    gmax = max(gt[k, k].real for k in range(q)); minz = 1e-4 * np.sqrt(gmax)
    err = gt - meas; d = np.zeros((q, q), complex); sec = np.zeros((q, q), bool)
    for j in range(q):
        if not live[j]:
            continue
        div = max(z[j, j].real, minz)
        sjj = err[j, j].real - sum(2 * (d[j, t] * np.conj(z[j, t])).real for t in range(j))
        djj = sjj / (2 * div); d[j, j] = djj
        for k in range(j + 1, q):
            t = err[k, j] - sum(d[k, m] * np.conj(z[j, m]) + z[k, m] * np.conj(d[j, m]) for m in range(j)) - z[k, j] * djj
            dkj = t / div; ekk = err[k, k].real
            if ekk < 0 and abs(z[k, j] + dkj * e) > abs(z[k, j]):
                g = gt[k, k].real
                dkj = -z[k, j] * 0.5 if (g <= 0 or -ekk >= 0.5 * g) else z[k, j] * (ekk / (2 * g)); sec[k, j] = True
            d[k, j] = dkj
    for j in range(q):
        if not live[j]:
            continue
        st = e * d[j, j].real; lo, hi = z[j, j].real * (dn - 1), z[j, j].real * (up - 1)
        if st > hi or st < lo:
            c = hi / st if st > hi else lo / st
            for k in range(j, q):
                if not sec[k, j]:
                    d[k, j] *= c
    for k in range(q):
        com = sum(abs(z[k, t]) ** 2 for t in range(k + 1))
        if com > 0 and meas[k, k].real < 0.03 * com:
            for t in range(k + 1):
                if abs(z[k, t] + d[k, t] * e) > abs(z[k, t]):
                    d[k, t] = 0
    zn = z + d * e
    for k in range(q):
        old = sum(abs(z[k, t]) ** 2 for t in range(k + 1)); new = sum(abs(zn[k, t]) ** 2 for t in range(k + 1))
        lim = max(10 * gt[k, k].real, old)
        if new > lim:
            zn[k, :k + 1] *= np.sqrt(lim / new)
    for j in range(q):
        if live[j] and zn[j, j].real < minz:
            old = z[j, j].real; f = min(max(max(zn[j, j].real, 0) / old, 0), 1) if old > 0 else 0
            for k in range(j + 1, q):
                zn[k, j] = z[k, j] * f
            zn[j, j] = minz
    od = np.diag(last).real; fl = 1e-6 * od.max(); alpha = 1.0
    for _ in range(31):
        tr = z + (zn - z) * alpha
        ratio = np.sum(np.abs(a @ tr) ** 2, axis=1) / np.maximum(od, fl)
        if ratio.max() <= up * up * (1 + 1e-12) and ratio.min() >= dn * dn * (1 - 1e-12):
            return tr
        alpha *= 0.5
    return z


def run(target, mode, e=0.5, loops=30, col1='printed', switch=(), lines=None):
    """Returns err[loop, line, gauge] (dB) and drive power tr(G_uu)[loop, line]."""
    lines = range(NL) if lines is None else lines
    lines = list(lines)
    err = np.zeros((loops + 1, len(lines), 2)); pw = np.zeros((loops + 1, len(lines)))
    for ii, i in enumerate(lines):
        a = pinv_trunc(EST[i])
        z = factor_with_zeros(target)
        live = [abs(z[j, j]) > 0 for j in range(2)]
        drv = (a @ z) @ (a @ z).conj().T
        for k in range(loops + 1):
            y = TRUE[i] @ drv @ TRUE[i].conj().T
            err[k, ii] = 10 * np.log10(np.diag(y).real / np.diag(target).real)
            pw[k, ii] = np.trace(drv).real
            if k == loops:
                break
            if mode == 'build':
                z = build_step(z, a, target, y, live, drv, e=e)
            else:
                z = correction(target, y, z, e, col1=col1, switch=switch)[0]
            drv = (a @ z) @ (a @ z).conj().T
    return err, pw


def band_rms(err, lo, hi, k=30, g=1):
    m = (FREQ >= lo) & (FREQ < hi)
    return float(np.sqrt(np.mean(err[k][m, g] ** 2)))


if __name__ == '__main__':
    i91, i161 = int(np.argmin(abs(FREQ - 91))), int(np.argmin(abs(FREQ - 161)))
    variants = [('build (factor.rs)', 'build', 0.5, 'printed', ()),
                ('Smallwood, as printed, e=0.5', 'sw', 0.5, 'printed', ()),
                ('Smallwood, column-1 read as columns 2:N, e=0.5', 'sw', 0.5, 'columns', ()),
                ('Smallwood, as printed, e=1 (his example)', 'sw', 1.0, 'printed', ()),
                ('Smallwood, as printed, e=0.25', 'sw', 0.25, 'printed', ())]
    for tname, tg in TARGETS.items():
        print(f'=== target: {tname}')
        for label, mode, e, col1, sw in variants:
            err, pw = run(tg, mode, e=e, col1=col1, switch=sw)
            print(f'--- {label}')
            print('  loop | g2 91 Hz | g2 161 Hz | worst line (dB, Hz, gauge) | drive power 91 Hz | drive power summed over band')
            for k in list(range(0, 11)) + [15, 20, 25, 30]:
                w = np.unravel_index(np.argmax(np.abs(err[k])), err[k].shape)
                print(f'  {k:3d} | {err[k, i91, 1]:+7.2f} | {err[k, i161, 1]:+7.2f} | {err[k][w]:+7.2f} at {FREQ[w[0]]:.1f} g{w[1] + 1} | '
                      f'{pw[k, i91]:9.4f} | {pw[k].sum():10.3f}')
            print(f'  loop 30 gauge 2 RMS: band {band_rms(err, 0, 1e9):.3f}, 85-96 Hz {band_rms(err, 85, 96):.2f}, '
                  f'150-172 Hz {band_rms(err, 150, 172):.2f}; lines over 0.5 dB (both gauges) {int(np.sum(abs(err[30]) > 0.5))}')
            m = (FREQ >= 89) & (FREQ < 94.5)
            print('  loop 30 gauge 2, 89 to 94 Hz: ' + ' '.join(f'{f:.1f}:{v:+.2f}' for f, v in zip(FREQ[m], err[30][m, 1])))
    # One at a time: each build feature switched into the faithful port (as printed, e=0.5).
    print('=== one at a time (independent target; port as printed, e = 0.5, one feature replaced by the build\'s)')
    sel = [i for i in range(NL) if 85 <= FREQ[i] < 96 or 150 <= FREQ[i] < 172]
    fsel = FREQ[sel]
    for sw in [(), ('step',), ('zero',), ('divisor',), ('limit',), ('order',), ('step', 'zero'),
               ('step', 'zero', 'order'), ('step', 'zero', 'divisor', 'limit', 'order')]:
        for tname in TARGETS:
            err, _ = run(TARGETS[tname], 'sw', 0.5, col1='printed', switch=sw, lines=sel)
            a = np.sqrt(np.mean(err[30][(fsel < 96), 1] ** 2)); b = np.sqrt(np.mean(err[30][(fsel >= 150), 1] ** 2))
            j91 = int(np.argmin(abs(fsel - 91)))
            print(f'  {"+".join(sw) or "none":32s} {tname[:11]:11s}: g2 RMS 85-96 {a:.2f}, 150-172 {b:.2f}; 91 Hz {err[30][j91, 1]:+.2f}')
