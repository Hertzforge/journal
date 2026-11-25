The data behind every figure and number, published under CC BY 4.0. Each file is plain CSV.

| File | What it holds | Written by |
|---|---|---|
| `problems.csv` | One row a problem, study (380) and held back (230): system, size, structure number, modes, highest reachable frequency, and per target the full-level peak, the median peak ratio and change of the structure at full level, the declared deviation of the projected target, the ideal drive's SRS error and the finiteness check (Sections 2.3, 2.4, 2.6; Figure 3) | `suite_results.py` |
| `example_waveforms.csv` | The three full-level targets at control gauge 1 of `frame-6x6-realistic_s00`, 0.55 to 1.0 s (Figure 2) | `suite_results.py` |
| `example_srs_target.csv` | The same problem's SRS target at control gauge 1 (Figure 2) | `suite_results.py` |
| `pooled_cells.csv` | Per cell and per target, pooled over the five laws: runs, the share under each reading, the best and worst single law's share ending in tolerance and never over 3 dB, the median run time (Sections 5 and 6; Figures 5 and 6) | `suite_results.py` |
| `te_definition.csv` | SRS runs with a last full-level pulse: effective duration within 0.8 to 1.2 by the earlier 10 % threshold and by Method 516.8 Annex A (Section 3.3; Figure 4) | `suite_results.py` |
| `classical_time.csv` | Classical runs with a last full-level pulse: every control gauge inside Method 516.8's time-domain tolerance, square systems and systems with more gauges than shakers (Section 5.3) | `suite_results.py` |
| `pooled_safety.csv` | Runs more than 3 dB and more than 6 dB over the full-level target, all and on a pulse at -3 dB or above, summed over the five laws (Section 5.1) | `suite_results.py` |
| `audit_sign.csv` | How many comparisons of two laws per cell kept their sign on the held-back structures (Section 6) | `suite_results.py` |
| `target_self_check.csv` | Each classical target read as a pulse: largest compensation-pulse and sawtooth post-slope departure over the control gauges (Section 5.3) | `target_self_check.py` |
| `fig_article_parts.csv`, `fig_article_rig.csv` | Copied unchanged from 2026-008, for Figure 1 | 2026-008 |

The run files they are computed from are in the results record of the study and its audit (DOI to be
assigned); the problems are the MIMO Shock suite, draft 0.2 (DOI to be assigned).
