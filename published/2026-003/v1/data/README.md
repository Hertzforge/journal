The data behind each figure and table, published under CC BY 4.0. All of it is computed by
`../code/extract_data.py` from formulas stated in the article; none is measured.

- `fig1_layout.csv`: positions of the parts in the Figure 1 drawing (drawing units, not to scale).
- `fig2_sweep_n.csv`: `N = 60 pi f / (Q^2 s ln 2)` for `Q` = 50 at 0.5, 1, 2 and 4 octaves a
  minute, 5 to 500 Hz.
- `table4_sweep.csv`: Table 4 of the article (seconds inside the bandwidth, `N` at 10, 40 and
  100 Hz, and the frequency below which `N` is under 2).
- `fig3_phase_vs_shift.csv`: `2 atan(delta)` in degrees, `delta` from 0 to 5 half-power
  bandwidths.
- `fig3_one_percent_marks.csv`: where a 1 percent frequency shift falls for `Q` of 25, 50, 100.
- `numbers.csv`: every number the text quotes, its section, and its source: a formula marked
  "ours", or a source and the clause, page or table in it. The article's reference list gives
  each source in full.
