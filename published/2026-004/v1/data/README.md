The data behind every figure, one file per figure where that is practical. Published under CC BY 4.0.
Levels and errors are in dB; an over-test is positive; "absolute" means against the full-level target.

| File | Figure | One row is |
|---|---|---|
| `fig1_geometry.csv` | 1a to 1c | one item of the held-out panel or frame: a node, a beam (lap-joint beams marked), a component (value: kg), a support with its shaker (value: base block), a control (value: number), the lap-joint line, or the plate's size (x: mass in kg, y: rows, x2: columns, y2: spacing in m) |
| `fig1_development_modes.csv` | 1d | one mode of the seven development structures that share one model: frequency and damping ratio |
| `fig1_development_structures.csv` | 1d | one development structure: shakers, controls, sample rate, record length, mode frequencies, the largest frequency drop of its joint law (or, for the research model, set by the level), the drop's exponent on amplitude, its damping gain, the envelope's decay in cycles, and the springs' stiffness drop (the springs have no envelope law) |
| `fig2_test_sequence.csv` | 2 | one pulse of one run (the followed family with its ceiling, severe development structure, seed 11, no noise): kind, level, over-test against its own level, absolute level |
| `fig3_softening_by_level.csv` | 3 | one structure at one level: the first mode's frequency drop (set `development`) or the largest of nine modes' drops relative to -40 dB (held out), in percent |
| `fig4a_identification_length.csv` | 4a | one predictor and buzz length: the median absolute error predicting the first -12 dB pulse's over-test, and the number of structures |
| `fig4b_hardening_pulses.csv` | 4b | one pulse of one law on the held-out hardening panel, seed 11, no noise |
| `fig5_held_out_runs.csv` | 5 | one run on a held-out four-shaker structure (seed 11): its verdict under the seven criteria and the two looser readings, its worst absolute level, and how it ended |
| `fig6_full_level_pulses.csv` | 6 | one full-level pulse of one run on the 32 % spring at noise 1e-3: law, seed, over-test, and whether a judgment of the first, third and last full-level pulses looks at it |
| `fig7_noise_cures.csv` | 7 | one method at one noise level, eight development structures and twenty seeds: passes under the seven criteria and the looser readings, and on the realistic tier |
| `numbers.csv` | text | one count quoted in the article, with the file it was added from |

Every file here is written by `../code/extract_data.py`.
