The code that writes the data of Sections 2.6 and 5 and draws Figures 1 to 6. It is published under
the MIT license. The laws themselves, their Python ports and the bridge to the Rust law mathematics
are in the suite's code, not here.

1. `law_results.py` (NumPy) reads the results record and writes the `law_*` files and `screen.csv` of
   `../data`. It runs nothing and imports no study or scorer code:
   `python law_results.py RECORD STUDY_RUNS AUDIT_RUNS`, where RECORD is the `experiments` folder of
   the unpacked results record of the study and its audit (DOI 10.5281/zenodo.24526370), and STUDY_RUNS and
   AUDIT_RUNS are the record's folders of run files (one JSON a run), read only for the classical
   pulses' time-domain criteria one by one.
2. `fig1_readings.py`, `fig2_cells.py`, `fig3_safety.py`, `fig4_misses.py`, `fig5_targets.py` and
   `fig6_port_rust.py` (Matplotlib) draw Figures 1 to 6 from those files into `../figures`, as PNG and
   PDF. `style.py` holds the laws' shared colors and hatches, so the figures read in grey.
