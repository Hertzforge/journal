The data behind every figure goes here, one file per figure where that is practical. Published under CC BY 4.0.

| File | Figure | One row is |
|---|---|---|
| `model_nodes.csv` | 1, 2 | one node of the article or the host frame, seed 0: position (m), role, lumped mass (kg) |
| `model_elements.csv` | 1, 2 | one beam element: its two nodes, group (chassis, stalk = component, host), tube width and wall (m) |
| `model_rig.csv` | 1 | one channel: shaker (per rig, `<shakers>x<controls>`), control (per control set), held-out or component tip; node and axis |
| `model_service_forces.csv` | 1 | one random service force input (node and axis), with its RMS relative to the others |
| `model_service_force_spectra.csv` | (Section 4.1) | one force point and frequency: the force PSD, summed over axes, in relative units |
| `model_modes.csv` | 2, table in 4.1 | one mode of unit B in one configuration (free in the lab, mounted in service, rigid base): frequency, damping ratio, share of modal mass in the article, share of kinetic energy in the components |
| `model_mode_shapes.csv` | 2 | one node of one lab mode: translations scaled to a largest value of 1 |
| `model_example_spectra.csv` | 3 | one line of the example test: target and achieved acceleration PSD at one gauge (line law, seed 0, one step of difference) |
| `model_example_drive.csv` | 4a | one line of one shaker's drive force PSD in that test, relative units (every second line) |
| `model_single_axis_z.csv` | 4b | one point of a mount spectrum, the mean of the mounts, or the single-axis vertical specification |
| `model_summary.csv` | (Section 4.1) | one number quoted in Section 4.1 for seed 0 |
| `cad/frame_model_seed0_*.step` | 1 | the CAD model of seed 0 as STEP files: the article alone, the article on its host frame, and the article on its suspension with six shakers (written by `../code/cad_frame_model.py`) |
| `fig5_exact_fit.csv` | 5 | one test case (random: line law, MM-X1; shock: waveform control, MM-X2) |
| `fig6_rank_correlation.csv` | 6 | one metric, gauge set and case set (random, MM-X1) |
| `fig7_floor.csv` | 7 | one quantity for one seed and control set (MM-X1 and MM-X2, the floor) |
| `fig8_single_axis_decomposition.csv` | 8 | one base input for one seed (MM-A1, finding A1) |
| `fig9a_line_vs_band_paired.csv` | 9a | one seed and rig, band law fitted in dB against the line law (MM-X1c) |
| `fig9b_first_shot.csv` | 9b, 9c | one law, model and rig class, summarized over cases (MM-X1c) |
| `fig10_shock_same_spectrum_spread.csv` | 10 | one case of twenty synthesized shots (MM-X2) |
| `fig11_coverage_margin.csv` | 11 | one test case, rule P against the truth margin (MM-X1c) |

The `model_*` files are in SI units, or relative units where the column says so; the `fig5` to `fig11` files are in dB unless the column name says otherwise. Stress errors are lab against service, positive meaning over-test. The `model_*` files are rebuilt by `../code/extract_model.py`, the others by `../code/extract_data.py`.
