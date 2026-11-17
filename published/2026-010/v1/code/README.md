The code behind every number and figure in the article. MIT license. Python with NumPy, SciPy and
matplotlib. Run from this folder, in order:

1. `collect_runs.py` reads the study's scorecards (and, for the signed mean errors at the control and
   held-out gauges, the kept run files and problem folders) and writes `../data/runs_of_record.csv`,
   one row per case: the run with the controller's checks widened if it completed, else the run at
   the default checks if it completed.
2. `setup_analysis.py` reads that table and prints every result in the article
   (`> ../data/setup_analysis.txt`); it also writes the tables behind the figures.
3. `setup_geometry.py` reads the five linear problem folders of structure 0 and writes the frame and
   setup tables for the setup figure, and prints what the setups share.
4. `fig_setups.py` draws Figure 1, `../figures/fig_setups.png`: the article rendered as solids and the five
   systems on their shakers (needs build123d, tested 0.13.0).
5. `figures.py` draws `../figures/fig_paired.png` and `fig_what_tracks.png`.

The first and third steps need the study's run files and the problem folders, which are not in this
bundle (paths are arguments; the defaults are the author's). The second and fourth need only
`../data/`.
