The data behind every figure, one file per figure panel where that is practical. Published under
CC BY 4.0. Every file except `fig1_setup.csv` is written by `../code/make_data.py`.

| File | Figure | One row is |
|---|---|---|
| `fig1_setup.csv` | 1 | one item of the schematic: the article, a shaker, a control or held-out gauge (panel a), or one cell of the example reference matrix (panel b, with its coherence and phase) |
| `fig2a_autospectrum_interval.csv` | 2a | one number of independent averages: the 90 and 99 percent intervals of a one-line autospectrum estimate in dB about the truth, and the chance one line is within 1 dB and 3 dB |
| `fig2b_all_lines.csv` | 2b | one number of averages and one count of lines: the chance every line is within 3 dB and within 1 dB |
| `fig2c_phase_coherence.csv` | 2c | one number of averages and one true coherence: the phase error not exceeded by 90 percent of estimates, and the 5th and 95th percentiles and mean of the coherence estimate (20,000 trials, seed 20261115) |
| `fig3_realizable.csv` | 3 | one pair coherence and one phase miss: the smallest eigenvalue of the three-gauge coherence matrix |
| `numbers.csv` | text | one number quoted in the article, with where it comes from |
