"""Section 2.1, Section 6 and Appendix B.8: why gauge 2 stays high near 90 Hz in Figure 3, and the
experiment with the two safeguards of Smallwood's appendix that the shipped loop does not have.
Uses only paper_laws.py and make_data.py. Run: python zero_term_trace.py

Copyright 2026 Kevin Cross. MIT license.
"""
import numpy as np

from make_data import FREQ, structure
import paper_laws as P

true, est = structure('loop_true'), structure('loop_estimate')
n = len(FREQ)
LINE = int(np.argmin(np.abs(FREQ - 91.0)))


def targets():
    ind = np.zeros((n, 2, 2), complex)
    ind[:, 0, 0] = ind[:, 1, 1] = 1.0
    band = np.zeros((n, 2, 2), complex)
    lv = [[1.0, 0.5], [2.0, 1.0], [0.5, 2.0]]
    for i, f in enumerate(FREQ):
        a, b = lv[0 if f < 150 else 1 if f < 300 else 2]
        band[i, 0, 0], band[i, 1, 1] = a, b
    coh = ind.copy()
    c = 0.8 * np.exp(1j * np.radians(30.0))
    coh[:, 0, 1], coh[:, 1, 0] = c, np.conj(c)
    return {'independent': ind, 'banded': band, 'cross terms (coherence 0.64, 30 deg)': coh}


def rms(err, lo=None, hi=None):
    sel = np.ones(n, bool) if lo is None else (FREQ >= lo) & (FREQ < hi)
    return np.sqrt(np.mean(err[:, sel, :] ** 2, axis=1))


if __name__ == '__main__':
    # The trace on one line.
    a = P.pinv(est[LINE])
    m = true[LINE] @ a                       # the loop's gain: measured response per commanded one
    ev = np.linalg.eigvals(m)
    lag = max(abs(np.degrees(np.angle(x))) for x in ev)
    print(f'Line {FREQ[LINE]:g} Hz. Loop gain H a: eigenvalues {ev[0]:.3f}, {ev[1]:.3f}; largest phase {lag:.0f} degrees; '
          f'|gain 2,1|^2 = {abs(m[1, 0]) ** 2:.2f}; condition of the measured frequency response '
          f'{np.linalg.cond(est[LINE]):.1f}')
    tr = []
    P.closed_loop(true[LINE:LINE + 1], est[LINE:LINE + 1], targets()['independent'][LINE:LINE + 1], loops=30, trace=(0, tr))
    print('loop | Z11 | |Z21| | Z22 | gauge 2 (dB)')
    for k, z, y in tr:
        if k in (0, 1, 2, 3, 5, 10, 15, 20, 25, 30):
            print(f'{k} | {z[0, 0].real:.3f} | {abs(z[1, 0]):.3g} | {z[1, 1].real:.3g} | {10 * np.log10(y[1, 1].real):+.2f}')
    k, z, y = tr[-1]
    need = abs(m[1, 0] * z[0, 0] / m[1, 1])
    print(f'cross term that would cancel the leak: |Z21| = {need:.2f}; gauge 2 from source 1 alone '
          f'|gain 2,1|^2 Z11^2 = {abs(m[1, 0]) ** 2 * z[0, 0].real ** 2:.2f}')
    tr2 = []
    P.closed_loop(true[LINE:LINE + 1], est[LINE:LINE + 1], targets()['cross terms (coherence 0.64, 30 deg)'][LINE:LINE + 1], loops=30, trace=(0, tr2))
    print(f'the same line, cross terms (coherence 0.64, 30 deg), gauge 2 at loop 30: {10 * np.log10(tr2[-1][2][1, 1].real):+.2f} dB')

    # The experiment.
    print()
    print('target | safeguards | gauge 2 RMS over the band, loop 30 (dB) | 85 to 96 Hz | 150 to 172 Hz | '
          'lines over 0.5 dB at loop 30 | worst line at loop 5 (dB) | worst line at loop 30 (dB)')
    for name, tg in targets().items():
        for sg in (False, True):
            err = P.closed_loop(true, est, tg, loops=30, safeguards=sg)
            print(f'{name} | {"with" if sg else "without"} | {rms(err)[30, 1]:.3f} | {rms(err, 85, 96)[30, 1]:.2f} | '
                  f'{rms(err, 150, 172)[30, 1]:.2f} | {int(np.sum(np.abs(err[30]) > 0.5))} | '
                  f'{err[5][np.unravel_index(np.argmax(np.abs(err[5])), err[5].shape)]:+.1f} | '
                  f'{err[30][np.unravel_index(np.argmax(np.abs(err[30])), err[30].shape)]:+.1f}')
