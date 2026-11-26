# Data

Copied from the study's own output files by `../code/make_data.py`; nothing here is computed anew.
Stress is the element stress error, root mean square over the elements, in dB. Systems: `6 x 12` is the
benchmark problem `frame-12x6` (6 shakers, 12 control gauges); `6 x 6` is `frame-6x6`.

| File | Rows | What it holds |
|:---|:---|:---|
| `stress_by_structure.csv` | 560 | Stress error of every study run, by system, size, structure and way of running the test |
| `scores_by_run.csv` | 342 | Median and quartiles of each score, by system, size and way of running the test |
| `claims.csv` | 136 | The claims written by rule, with the held-back medians and the audit's verdicts |
| `line_yardstick.csv` | 4 | The line yardstick at the strong size, with the stress against band control |
| `default_checks.csv` | 76 | The runs with the controller's checks at their defaults, as the audit printed them |

In `claims.csv`, d is the first run minus the second; `study_low_db` and `study_high_db` are the quartiles
for a difference and the 90 percent interval of the median for "same test".

The run labels:

| Label | Way of running the test |
|:---|:---|
| A1 | Band control (`band_average`) |
| A2 | Band control, stored model |
| N1 | Pseudo-inverse (`pinv_closed`), dB-fit reference, model kept |
| N2 | Pseudo-inverse, dB-fit reference, model updated |
| N3 | Pseudo-inverse, first-solve reference, model kept |
| N4 | Pseudo-inverse, first-solve reference, model updated |
| N5 | Pseudo-inverse, stored-model reference, model kept |
| N6 | Pseudo-inverse, stored-model reference, model updated |
| S1 | Shape-constrained (`shape_svd`), dB-fit reference |
| B1 | Broyden congruence (`broyden_congruence`), dB-fit reference |
