The code that draws each figure from the files in ../data. It is published under the MIT license.

Every figure can be drawn again from this bundle alone:

- `fig2_mode_shapes.py` to `fig4_drive_and_single_axis.py` draw Figures 2 to 4 from the `model_*.csv` files in `../data`.
- `fig5_exact_fit.py` to `fig11_coverage_margin.py` each read their own file in `../data`.
- `cad_frame_model.py` builds the CAD model from the `model_*.csv` files with build123d, writes three STEP files to `../data/cad` and draws Figure 1 from the CAD tessellation.

Each writes a static PNG to `../figures`.

Two scripts are the record of how the data files were made. They need files that are not in this bundle:

- `extract_model.py` wrote the `model_*.csv` files (the test model of Section 4.1, seed 0: geometry, rig, service loads, modes and one example test). It imports the study's own `frame_model.py` and `x1_random_study.py`.
- `extract_data.py` wrote the `fig5` to `fig11` data files from the studies' saved results and checked each against the numbers in the study reports.

Requirements: Python 3 with numpy and matplotlib (the figure scripts); build123d as well for `cad_frame_model.py`; scipy for the two extraction scripts. Tested with numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2, build123d 0.13.0.

Draw the figures again:

    mkdir -p ../figures
    python cad_frame_model.py
    for f in fig*.py; do python "$f"; done
