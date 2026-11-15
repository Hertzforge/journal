The code that makes the data files and draws each figure. It is published under the MIT license.

Every figure can be drawn again from this bundle alone. `make_data.py` writes every file in
`../data` from arithmetic only (chi-square quantiles, a seeded Monte Carlo and an eigenvalue sweep;
no measured or simulated test data), and writes `../data/numbers.csv` with every number the text
quotes from them. Each figure script reads only its own files in `../data` and writes a static PNG
to `../figures`:

- `fig1_setup.py`: Figure 1, the schematic of a test and one line of a reference matrix.
- `fig2_statistics.py`: Figure 2, how far estimates from a finite number of averages scatter.
- `fig3_realizable.py`: Figure 3, when a three-gauge reference can be played.

Requirements: Python 3 with numpy, scipy and matplotlib. Tested with numpy 2.5.4, scipy 1.18.1 and
matplotlib 3.11.2.

    python make_data.py
    mkdir -p ../figures
    for f in fig*.py; do python "$f"; done
