"""Writes Figure 7's tables from the shipped band-average law's first solve
(../data/fig7_band_average_drive.csv, written by shipped_laws/): the response line by line, the
band averages of target and response, and, for comparison, the drive that would match every line.

Run after shipped_laws. Copyright 2026 Kevin Cross. MIT license.
"""
import numpy as np

from make_data import DF, column_of, octave_edges, structure, write

f = np.arange(0.0, 600.0 + DF / 2, DF)
h = structure('band', f=f)[:, 0, 0]
spec = np.where((f >= 40.0) & (f <= 500.0), 1.0, 0.0)
shipped = column_of('fig7_band_average_drive.csv')
drive = np.zeros_like(f)
threshold = np.zeros_like(f)
for r in shipped:
    k = int(round(float(r['frequency_hz']) / DF))
    drive[k] = float(r['drive'])
    threshold[k] = float(r['band_threshold'])
response = np.abs(h) ** 2 * drive
lb, ub = octave_edges(f[1], f[-1], 6)
overlap = lambda fk, l, u: max(min(fk + DF / 2, u) - max(fk - DF / 2, l), 0.0)
bands = []
for b, (l, u) in enumerate(zip(lb, ub)):
    lines = [k for k, fk in enumerate(f) if overlap(fk, l, u) > 0]
    width = u - l
    target_b = sum(overlap(f[k], l, u) * spec[k] for k in lines) / width
    response_b = sum(overlap(f[k], l, u) * response[k] for k in lines) / width
    if target_b > 0 and l >= 40.0 and u <= 500.0:
        inside = [k for k in lines if l <= f[k] < u]
        bands.append([b, l, u, float(np.sqrt(l * u)), target_b, response_b,
                      10 * np.log10(response_b / target_b), float(threshold[inside[0]])])
with np.errstate(divide='ignore', invalid='ignore'):
    line_drive = np.where(spec > 0, spec / np.abs(h) ** 2, 0.0)
keep = (f >= 30) & (f <= 520)
write('fig7_band_average_lines.csv', ['frequency_hz', 'reference', 'band_drive', 'band_response',
                                      'line_by_line_drive'],
      [[f[k], spec[k], drive[k], response[k], line_drive[k]] for k in np.nonzero(keep)[0]])
write('fig7_band_average_bands.csv', ['band', 'lower_hz', 'upper_hz', 'centre_hz', 'reference_band_average',
                                      'response_band_average', 'band_error_db', 'band_threshold'], bands)
