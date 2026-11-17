"""Figure 7: the shipped band-average law's first solve, at its defaults, on one gauge and one
shaker: one flat drive per one-sixth-octave band, so the band averages match and the lines inside
a band do not. An illustration on a made-up structure, not a run.

Reads ../data/fig7_band_average_lines.csv and fig7_band_average_bands.csv only.
Copyright 2026 Kevin Cross. MIT license.
"""
import math

from style import BLUE, GREEN, ORANGE, TEXT, column, frequency_axis, plt, rows, save

lines = rows('fig7_band_average_lines.csv')
bands = rows('fig7_band_average_bands.csv')
f = column(lines, 'frequency_hz')
db = lambda v: [10 * math.log10(x) if x > 0 else float('nan') for x in v]
fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 5.6), sharex=True)
a1.plot(f, db(column(lines, 'reference')), color=TEXT, lw=1.0, label='Target, line by line')
a1.plot(f, db(column(lines, 'band_response')), color=BLUE, lw=1.0, ls='--', label='Response, line by line')
c = column(bands, 'centre_hz')
a1.plot(c, db(column(bands, 'reference_band_average')), ls='none', marker='o', mfc='white', mec=TEXT, ms=7,
        label='Target, band average')
a1.plot(c, db(column(bands, 'response_band_average')), ls='none', marker='^', color=ORANGE, ms=5,
        label='Response, band average')
low = min(bands, key=lambda r: float(r['band_error_db']))
a1.annotate(f"{float(low['band_error_db']):.1f} dB: the band where\nthe drive costs most", (float(low['centre_hz']),
            float(low['band_error_db'])), xytext=(130, 8.5), fontsize=7.5, arrowprops=dict(arrowstyle='->', lw=0.8))
a1.set_ylabel('Gauge response (dB re target)')
a1.set_ylim(-25, 15)
a1.legend(fontsize=7.5, ncol=2, loc='lower center')
a2.plot(f, db(column(lines, 'band_drive')), color=GREEN, lw=1.6, label='Band-average drive: flat in each band')
a2.plot(f, db(column(lines, 'line_by_line_drive')), color=ORANGE, lw=1.0, ls=':',
        label='Drive that would match every line')
a2.set_ylabel('Drive (dB, arbitrary reference)')
frequency_axis(a2, 30, 520, (30, 50, 100, 200, 500))
a2.legend(fontsize=7.5, loc='upper right')
fig.tight_layout()
save(fig, 'fig7_band_average.png')
