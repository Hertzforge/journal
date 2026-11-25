The code that writes the data of Sections 2 to 6 and draws Figures 2 to 6. It is published under the
MIT license. Every number it writes is pooled over the five laws of the companion article; no law is
named. Figure 1 is reproduced from 2026-008, whose code draws it.

1. `suite_results.py` (NumPy) reads the results record and the problem folders and writes
   `problems.csv`, `example_waveforms.csv`, `example_srs_target.csv`, `pooled_cells.csv`,
   `te_definition.csv`, `classical_time.csv`, `pooled_safety.csv` and `audit_sign.csv` in
   `../data`.
   It runs nothing and imports no study or scorer code:
   `python suite_results.py RECORD PROBLEMS AUDIT_PROBLEMS`, where RECORD is the `experiments` folder
   of the unpacked results record of the study and its audit (DOI to be assigned), and PROBLEMS and
   AUDIT_PROBLEMS are the suite's draft 0.2 problem folders and the held-back problem folders.
2. `target_self_check.py` (NumPy) reads each classical target, as the pulse itself, against Method
   516.8's time-domain tolerance, with the suite's own reading of a pulse, and writes
   `target_self_check.csv`: `python target_self_check.py SUITE_CODE PROBLEMS AUDIT_PROBLEMS`, where
   SUITE_CODE is the suite's `shock` folder (draft 0.2). It imports the suite's `classical_band` and
   nothing else.
3. `fig2_targets.py`, `fig3_full_level.py`, `fig4_effective_duration.py`, `fig5_cells.py` and
   `fig6_audit.py` (Matplotlib) draw Figures 2 to 6 from those files into `../figures`, as PNG and PDF.
   `style.py` holds their shared colors and axes.
