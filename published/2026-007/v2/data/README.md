The data behind every figure, published under CC BY 4.0. Each file is plain CSV.

| File | What it holds | Written by |
|---|---|---|
| `toy_structures.csv` | The made-up structures: per mode, frequency (Hz), damping ratio, and its shape at each gauge and shaker | `make_data.py` |
| `fig1_run_sequence.csv` | The stages of a run and their levels at the software's defaults | `make_data.py` |
| `fig2_one_loop.csv` | The steps of one loop and who owns each | `make_data.py` |
| `fig3_closed_loop_lines.csv`, `fig3_closed_loop_rms.csv` | Each gauge's error line by line after 0, 5 and 30 loops, and the RMS error over the band each loop, of the shipped `pinv_closed` and `pinv_open` | `shipped_laws` |
| `fig4_shape_directions.csv` | The system's singular values, the ratio threshold and the directions kept per line | `make_data.py` |
| `fig5_buzz_reference.csv` | The identification's coherence and phase of a pair, and the buzz target's | `make_data.py` |
| `fig6a_min_drive_phase.csv`, `fig6b_min_drive_pareto.csv` | Drive power against a cross term's phase and coherence; the trade-off grid, the point the knee alone picks and the point the automatic rule picks with its largest shortfall | `make_data.py` |
| `fig7_band_average_drive.csv` | The shipped `band_average` law's first drive and each line's band threshold | `shipped_laws` |
| `fig7_band_average_lines.csv`, `fig7_band_average_bands.csv` | The response line by line and band by band to that drive | `make_shipped_figure_data.py` |
| `shipped_check_shape.csv`, `shipped_check_buzz.csv`, `shipped_check_min_drive.csv` | The shipped laws' outputs that `check_against_shipped.py` compares with Figures 4, 5 and 6 | `shipped_laws` |
| `smallwood_port_output.txt` | What `code/smallwood_port/run_fig3_case.py` prints: Smallwood's Appendix A, ported, on the case of Figure 3, beside the build's loop | `smallwood_port/run_fig3_case.py` |
| `zero_term_trace_output.txt` | What `zero_term_trace.py` prints: the loop on the line at 91 Hz, and the experiment of Section 6 | `zero_term_trace.py` |
| `check_against_shipped_output.txt` | What `check_against_shipped.py` prints: each comparison of Section 5, its largest difference and its tolerance | `check_against_shipped.py` |

Every file is an illustration on a made-up structure, or a comparison on one; none is a result
about how a law scores.
