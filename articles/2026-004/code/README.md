The code that draws each figure from the files in ../data. It is published under the MIT license.

Every figure can be drawn again from this bundle alone. Each script reads only its own files in
`../data` and writes a static PNG to `../figures`:

- `fig1_setup.py`: Figure 1, the structures (`fig1_*.csv`).
- `fig2_test_sequence.py`: Figure 2, one run's test sequence.
- `fig3_softening_by_level.py`: Figure 3, frequency drop against test level.
- `fig4_networks.py`: Figure 4, identification length and the network law on the hardening panel.
- `fig5_held_out.py`: Figure 5, runs that pass on the held-out structures, by reading.
- `fig6_unjudged_pulses.py`: Figure 6, every full-level pulse on the 32 % spring at noise 1e-3.
- `fig7_noise_cures.py`: Figure 7, the two attempted cures for heavy-noise failures.

`extract_data.py` is the record of how the data files were made, and it adds every count the
article quotes (written to `../data/numbers.csv` with its source). It needs the study's run files,
printed outputs and simulator code, which are not in this bundle:

    python extract_data.py --runs <folder of run files> --outputs <folder of printed outputs>

Requirements: Python 3 with numpy and matplotlib (the figure scripts). Tested with numpy 2.5.4 and
matplotlib 3.11.2.

Draw the figures again:

    mkdir -p ../figures
    for f in fig*.py; do python "$f"; done
