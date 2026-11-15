The code that draws each figure from the files in ../data. It is published under the MIT license.

Every figure can be drawn again from this bundle alone. Each script reads only its own files in
`../data` and writes a static PNG to `../figures`:

- `fig1_setup.py`: Figure 1, a sine test with several shakers and its loop (`fig1_layout.csv`).
- `fig2_sweep_time_constants.py`: Figure 2, the mode's time constants inside its bandwidth
  against frequency (`fig2_sweep_n.csv`).
- `fig3_phase_vs_shift.py`: Figure 3, the largest phase difference against the resonance's move
  (`fig3_phase_vs_shift.csv`, `fig3_one_percent_marks.csv`).

`extract_data.py` writes every file in `../data`. The article's own numbers are arithmetic on one
mode, so it computes them from their formulas; it needs nothing outside this bundle. It also
writes `../data/numbers.csv`, every number the text quotes with where it comes from.

Requirements: Python 3 with matplotlib (the figure scripts). Tested with matplotlib 3.11.2.

    python extract_data.py
    mkdir -p ../figures
    for f in fig*.py; do python "$f"; done
