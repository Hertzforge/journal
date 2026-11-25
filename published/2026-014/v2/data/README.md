The data behind every figure and number, published under CC BY 4.0. Each file is plain CSV, one row a
law (and set, study or held back) unless said.

| File | What it holds | Written by |
|---|---|---|
| `law_readings.csv` | Runs and the share under each reading: strict, ends, ends with TE on SRS, ends within -3/+3 dB, Level, exposure (Section 5.1; Figure 1) | `law_results.py` |
| `law_cells.csv` | Per law and cell: runs, share ending in tolerance, share never over 3 dB, runs over 6 dB at or near full level (Section 5.2; Figure 2) | `law_results.py` |
| `law_safety.csv` | Runs over 3 dB and over 6 dB, all and at or near full level; median and largest worst exposure of the runs over 3 dB (Section 5.3; Figure 3) | `law_results.py` |
| `law_misses.csv` | Runs ending in tolerance, and the misses: stopped below full level, stopped at a probe, missed at full level and by how much; median highest level reached (Section 5.4; Figure 4) | `law_results.py` |
| `law_targets.csv` | Per law and target: share ending in tolerance and never over 3 dB (Section 5.5; Figure 5a) | `law_results.py` |
| `law_te_srs.csv` | SRS runs: share ending in tolerance with and without the effective duration, TE within tolerance at full level, ratio to the target's TE (Section 5.5; Figure 5b) | `law_results.py` |
| `law_classical_time.csv` | Classical runs with a last full-level pulse, per law, target and systems: share inside each time-domain criterion and all of them, of the runs with a last full-level pulse; and `all_of_runs`, the share of every run, a run without a full-level pulse counted outside (Section 5.5 and the Abstract; Figure 5c) | `law_results.py` |
| `law_port_rust.csv` | followed and followed-hold, port against Rust law math: shares, runs that changed end, change of largest exposure (Section 5.7; Figure 6) | `law_results.py` |
| `screen.csv` | The screen, six laws on 12 problems: shares and median run time (Section 2.6) | `law_results.py` |

They are computed from the results record of the study and its audit (DOI 10.5281/zenodo.24526370); the
problems are the MIMO Shock suite, draft 0.2 (DOI 10.5281/zenodo.24526368).
