The code that writes the data of Section 3 and draws its two figures. It is published under the MIT
license. The illustrations of what each law does, and the code that runs the shipped laws on made-up
structures, are in the companion article that describes the laws.

1. `study_results.py` (NumPy) reads the study's scorecards and writes the `study_*` files of
   `../data`, the numbers of Section 3. It runs nothing and imports no study or scorer code:
   `python study_results.py RESULTS/cards/main`, where RESULTS is the unpacked results record of the
   study and its audit, version 0.2 (DOI 10.5281/zenodo.24310746). Given the audit's two batches
   (`cards/audit` and `cards/audit2`) and `--audit`, it writes the same tables as `audit_*` files.
2. `fig1_stress_by_law.py` and `fig2_effects_by_law.py` (Matplotlib) draw Figures 1 and 2 from those
   files into `../figures`. `style.py` holds their shared colors and axes.
