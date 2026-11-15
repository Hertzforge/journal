"""Write the data files behind Figures 2 and 3 and the numbers the text quotes from them.

Everything here is this article's own arithmetic: chi-square quantiles for a one-line autospectrum
estimate made from independent averages of Gaussian noise, a Monte Carlo of the coherence and
phase estimates of a pair of channels, and the smallest eigenvalue of a three-channel coherence
matrix. No measured or simulated test data are used.

Writes ../data/fig2a_autospectrum_interval.csv, fig2b_all_lines.csv, fig2c_phase_coherence.csv,
fig3_realizable.csv and numbers.csv. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import numpy as np
from scipy.stats import chi2

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
os.makedirs(DATA, exist_ok=True)
numbers = []


def write(name, header, rows):
    with open(os.path.join(DATA, name), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def db(x):
    return 10.0 * np.log10(x)


# Figure 2a: the 90 and 99 percent intervals of a one-line autospectrum estimate, in dB about the
# true value, against the number of independent averages n. The estimate of Gaussian noise from n
# independent averages is the true value times a chi-square variable with 2n degrees of freedom,
# divided by 2n.
ns = np.unique(np.round(np.logspace(np.log10(4), np.log10(1024), 80)).astype(int))
rows = []
for n in ns:
    nu = 2 * n
    lo90, hi90 = chi2.ppf(0.05, nu) / nu, chi2.ppf(0.95, nu) / nu
    lo99, hi99 = chi2.ppf(0.005, nu) / nu, chi2.ppf(0.995, nu) / nu
    p1 = chi2.cdf(nu * 10 ** 0.1, nu) - chi2.cdf(nu * 10 ** -0.1, nu)
    p3 = chi2.cdf(nu * 10 ** 0.3, nu) - chi2.cdf(nu * 10 ** -0.3, nu)
    rows.append([n, nu, round(db(lo90), 4), round(db(hi90), 4), round(db(lo99), 4),
                 round(db(hi99), 4), round(p1, 6), round(p3, 6)])
write('fig2a_autospectrum_interval.csv',
      ['averages', 'degrees_of_freedom', 'lo90_db', 'hi90_db', 'lo99_db', 'hi99_db',
       'p_within_1db', 'p_within_3db'], rows)
for n in (30, 60, 64, 120, 200):
    nu = 2 * n
    lo, hi = chi2.ppf(0.05, nu) / nu, chi2.ppf(0.95, nu) / nu
    numbers.append(['interval90_db_at_%d_averages' % n, '%.2f / +%.2f' % (db(lo), db(hi)),
                    'fig2a; chi-square, %d degrees of freedom' % nu])

# Figure 2b: the chance that every one of N independent lines lies within +/-3 dB (and +/-1 dB),
# against the number of averages.
rows = []
for n in ns:
    nu = 2 * n
    p3 = chi2.cdf(nu * 10 ** 0.3, nu) - chi2.cdf(nu * 10 ** -0.3, nu)
    p1 = chi2.cdf(nu * 10 ** 0.1, nu) - chi2.cdf(nu * 10 ** -0.1, nu)
    for lines in (100, 400, 1600):
        rows.append([n, lines, round(p3 ** lines, 6), round(p1 ** lines, 6)])
write('fig2b_all_lines.csv', ['averages', 'lines', 'p_all_within_3db', 'p_all_within_1db'], rows)
for n in (16, 32, 60, 64, 128):
    nu = 2 * n
    p3 = chi2.cdf(nu * 10 ** 0.3, nu) - chi2.cdf(nu * 10 ** -0.3, nu)
    p1 = chi2.cdf(nu * 10 ** 0.1, nu) - chi2.cdf(nu * 10 ** -0.1, nu)
    numbers.append(['p_all_400_lines_within_3db_at_%d_averages' % n, '%.3f' % p3 ** 400, 'fig2b'])
    numbers.append(['p_all_400_lines_within_1db_at_%d_averages' % n, '%.3g' % p1 ** 400, 'fig2b'])
    numbers.append(['p_one_line_within_1db_at_%d_averages' % n, '%.3f' % p1, 'fig2a'])

# Figure 2c: Monte Carlo of a pair of channels with true coherence g2 and true phase 0. One frame
# gives, at one line, X and Y = sqrt(g2) X + sqrt(1 - g2) N with X and N independent unit complex
# Gaussian. The cross spectrum and autospectra are averaged over n frames.
rng = np.random.default_rng(20261115)
TRIALS = 20000
rows = []


def cgauss(shape):
    return (rng.standard_normal(shape) + 1j * rng.standard_normal(shape)) / np.sqrt(2.0)


for n in (16, 32, 64, 128):
    for g2 in np.round(np.arange(0.05, 1.0, 0.05), 2):
        x = cgauss((TRIALS, n))
        y = np.sqrt(g2) * x + np.sqrt(1.0 - g2) * cgauss((TRIALS, n))
        sxy = np.mean(x * np.conj(y), axis=1)
        sxx = np.mean(np.abs(x) ** 2, axis=1)
        syy = np.mean(np.abs(y) ** 2, axis=1)
        ph = np.degrees(np.angle(sxy))
        coh = np.abs(sxy) ** 2 / (sxx * syy)
        rows.append([n, g2, round(float(np.percentile(np.abs(ph), 90)), 3),
                     round(float(np.percentile(coh, 5)), 4), round(float(np.percentile(coh, 95)), 4),
                     round(float(np.mean(coh)), 4)])
write('fig2c_phase_coherence.csv',
      ['averages', 'true_coherence', 'phase_error_deg_90pct', 'coherence_p05', 'coherence_p95',
       'coherence_mean'], rows)
for r in rows:
    if r[1] in (0.5, 0.9) and r[0] in (32, 64):
        numbers.append(['phase_error_90pct_deg_at_coh_%.1f_%d_averages' % (r[1], r[0]),
                        '%.1f' % r[2], 'fig2c; Monte Carlo, %d trials, seed 20261115' % TRIALS])
        numbers.append(['coherence_5_95_at_coh_%.1f_%d_averages' % (r[1], r[0]),
                        '%.2f to %.2f' % (r[3], r[4]), 'fig2c'])

# Figure 3: a three-channel reference with the same coherence g2 on every pair and phases whose
# sum around the loop misses by phi (theta12 + theta23 - theta13 = phi). The smallest eigenvalue of
# its coherence matrix C (unit diagonal, off-diagonal sqrt(g2) times the phase factor) must not be
# negative for the reference to be playable.
rows = []
for g2 in (1.0, 0.9, 0.7, 0.5):
    g = np.sqrt(g2)
    for phi in np.arange(0.0, 180.0 + 1e-9, 1.0):
        c = np.array([[1.0, g, g * np.exp(1j * np.radians(phi))],
                      [g, 1.0, g],
                      [g * np.exp(-1j * np.radians(phi)), g, 1.0]], dtype=complex)
        lam = np.linalg.eigvalsh(c)
        rows.append([g2, phi, round(float(lam[0]), 6)])
write('fig3_realizable.csv', ['pair_coherence', 'loop_phase_miss_deg', 'smallest_eigenvalue'], rows)
for g2 in (0.9, 0.7, 0.5):
    # the same limit in closed form, from the determinant of the coherence matrix (the condition
    # Musella and others 2018 print for three channels): 1 - 3 g2 + 2 g2^1.5 cos(phi) >= 0
    g = np.sqrt(g2)
    phi_max = np.degrees(np.arccos((3.0 * g2 - 1.0) / (2.0 * g ** 3)))
    first_neg = [r for r in rows if r[0] == g2 and r[2] < 0][0][1]
    numbers.append(['loop_phase_miss_limit_deg_at_coh_%.1f' % g2, '%.1f' % phi_max,
                    'fig3; closed form; first negative eigenvalue on the 1 degree grid at %.0f' % first_neg])

# Three more numbers the text quotes.
# (1) the number of averages at which all of 400 independent lines fall within +/-1 dB nine times
# in ten
for n in range(100, 400):
    nu = 2 * n
    p1 = chi2.cdf(nu * 10 ** 0.1, nu) - chi2.cdf(nu * 10 ** -0.1, nu)
    if p1 ** 400 >= 0.9:
        numbers.append(['averages_for_400_lines_within_1db_90pct', '%d' % n, 'chi-square, as fig2b'])
        break
# (2) the swing in variance of overlap-added random frames with a Hann window at 50 % overlap: the
# sum of the squared windows runs between 0.5 and 1
t = np.linspace(0.0, 1.0, 2001)
w2 = np.sin(np.pi * t) ** 4 + np.cos(np.pi * t) ** 4
numbers.append(['hann_50pct_variance_swing_db', '%.2f' % (10 * np.log10(w2.max() / w2.min())),
                'sum of squared Hann windows at 50 % overlap'])
# (3) the time for 64 frames at 1 Hz lines with half overlap: (64 + 1) / 2 frame lengths of 1 s
numbers.append(['seconds_64_frames_1hz_half_overlap', '%.1f' % ((64 + 1) / 2.0),
                '(n + 1) / 2 frames of 1 / (line spacing)'])

write('numbers.csv', ['name', 'value', 'source'], numbers)
print('\n'.join('%s = %s' % (a, b) for a, b, c in numbers))
