The code that draws each figure from the files in `../data`, and the code that writes those files.
It is published under the MIT license.

Every figure is an illustration on a small made-up structure, not a result about how a law scores. In order:

1. `make_data.py` (NumPy, SciPy) writes `data/toy_structures.csv`, the made-up structures (each
   mode's frequency, damping and shapes at the gauges and shakers), and the data of Figures 1, 2,
   4, 5 and 6, computed from each law's equations as Hertzforge's code states them.
2. `shipped_laws/` (Rust) runs Hertzforge's shipped laws, unchanged, on those structures and writes
   the data of Figures 3 and 7 and three check files. Build it against a checkout of Hertzforge
   (github.com/Hertzforge/Hertzforge) at main commit b587d5a1 (the law code this article describes; the laws are identical at 646c4ca4), placed at `code/hertzforge`:
   `cd shipped_laws && cargo run --release -- ../../data`.
3. `make_shipped_figure_data.py` writes Figure 7's tables from the shipped law's drive.
4. `check_against_shipped.py` compares the laws as the article writes them (`paper_laws.py`) with
   the shipped laws of step 2 and prints the largest differences (Section 5).
5. `fig1_run_sequence.py` to `fig7_band_average.py` (Matplotlib) draw the figures into
   `../figures`. `style.py` holds their shared colors and axes.
6. `paper_laws.py` (NumPy, SciPy) is the six laws and the shared closed loop written from the
   article's own equations, without Hertzforge. `check_against_shipped.py` uses it (Section 5) and
   `worked_example.py` carries one line of a made-up structure through each law (Appendix B):
   `python worked_example.py`.
7. `zero_term_trace.py` (NumPy) follows the shared loop on the line at 91 Hz of the structure of
   Figure 3 (Appendix B.8), and runs the experiment of Section 6: the loop of `paper_laws.py` with and
   without the two rules of Smallwood's appendix against a term of the factor at zero, on an
   independent, a banded and a cross-term target: `python zero_term_trace.py`. The rules are an
   option of this article's code; they are not in Hertzforge's loop.
8. `smallwood_port/` (NumPy): a line-by-line port of the correction in Appendix A of Smallwood's 1999
   paper, with his factorization with zeros, run on the case of Figure 3 beside the shipped loop's
   arithmetic (Sections 2.1 and 6, Appendix B.8). Its `README.md` says how each ambiguity of the scanned
   listing was read. `cd smallwood_port && python run_fig3_case.py > ../../data/smallwood_port_output.txt`.
