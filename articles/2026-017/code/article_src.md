---
# Filled in by the editors at publication.
id: "2026-017"
version: 1
date: "2026-11-27"
doi: "10.5281/zenodo.24595042"
doi_latest: "10.5281/zenodo.24595041"
note: First published.

# Filled in by the authors.
title: "Six Control Laws for Multi-Shaker Sine Testing: The Laws, Their Build in Hertzforge, and How Each Scores on the MIMO Sine Suite"
type: Research Article
evidence: simulator
evidence_note: "Closed-loop runs of Hertzforge's five MIMO Sine control laws and one candidate law on the Open Benchmark Set's MIMO Sine suite, draft 0.1: {{s:problems}} generated structures on five systems, five tests and a limit case, {{s:runs_hertzforge}} runs in the Hertzforge version and {{s:runs_python}} in the Python version, one sequence of measurement noise, every finding a claim of a rule fixed before an independent audit on {{f:heldout_problems}} held-back problems. The five shipped laws ran as Hertzforge's Rust law mathematics inside its shipped MIMO Sine engine, on the simulator, driven by a closed-loop runner built for the study. The candidate, followed poles, ran only in the suite's Python harness, beside the Python port of matrix; it has no Rust build."
authors:
  - name: "Kevin Cross"
    orcid: "https://orcid.org/0009-0002-6608-9426"
    roles: ["Conceptualization", "Methodology", "Software", "Validation", "Formal analysis", "Investigation", "Data curation", "Visualization", "Writing: original draft", "Writing: review and editing"]
implemented_in: ""
benchmarks: "Hertzforge Open Benchmark Set: MIMO Sine Suite, draft 0.1 (DOI 10.5281/zenodo.24594791; problem format {{s:problem_format}}, scorer {{s:scorer_version}}): problems frame-12x3, frame-12x6, frame-24x12, frame-6x6 and frame-12x12, linear, realistic and strong, structures 0 to 9, 12 to 15, 17, 19 and 32 to 35; softening only and hardening only, realistic and strong, on frame-12x6 and frame-6x6, structures 0 to 9; the limit case on frame-12x6 and frame-6x6, realistic and strong, structures 0 to 9; held back: structures 90, 91, 93, 94 and 96 to 101 on every cell"
abstract: >
  Hertzforge, an open-source structural dynamics suite, ships five control laws for sine tests
  with several shakers: matrix, its default, which corrects the drive through the inverse of a
  measured model and carries the drive along a sweep; paired, which pairs each control with one
  shaker; ratio, an amplitude-ratio law; and steepest_descent and secant, two published laws for a
  dwell. This article describes each law, its build in Hertzforge's Rust law mathematics, and how
  each scores on the MIMO Sine suite of the Open Benchmark Set, draft 0.1, under the tolerances of
  IEC 60068-2-6 and MIL-STD-810H Method 514.8: {{s:runs_hertzforge}} runs on {{s:problems}}
  structures, each finding a claim of a rule fixed before an audit on held-back structures. A sixth
  law, followed poles, which follows the frequency and damping of the modes near the tone, entered the study
  after a screen that no candidate passed, and runs in the suite's Python version only. At a dwell,
  matrix, steepest_descent and secant complete {{hertzforge_matrix_T4_all_completed_pct}},
  {{hertzforge_steepest_descent_T4_all_completed_pct}} and {{hertzforge_secant_T4_all_completed_pct}}
  percent of their runs, and each is inside the IEC check-point band in the median on
  {{level_hertzforge_matrix_T4_iec_check_point_inside}} of the
  {{level_hertzforge_matrix_T4_iec_check_point_cells}} cells: every square system, and
  {{hertzforge_matrix_T4_iec_check_point_more_controls_inside}} of
  {{hertzforge_matrix_T4_iec_check_point_more_controls_cells}} with more controls than shakers. On
  a sweep or a stepped sine no law's median run is inside that band in any cell; matrix completes
  {{hertzforge_matrix_T1_all_completed_pct}} percent of its sweeps up at one octave a minute and
  {{hertzforge_matrix_T5_all_completed_pct}} percent of its sweeps down. Safety: the study widened
  the engine's control abort band from {{f:protective_abort_default_db}} to
  {{f:protective_abort_widened_db}} dB so that runs would go on far enough to be read, and
  {{hertzforge_sweep_step_over_6db_pct_of_scored}} percent of the scored sweeps and stepped sines
  then put a resonance more than 6 dB over its reference ({{hertzforge_sweep_step_over_6db_pct_of_runs}}
  percent of all of them); at the engine's default protections, {{defaults_hertzforge_sweep_or_step_completed}}
  of {{defaults_hertzforge_sweep_or_step_runs}} sweeps and stepped sines on a sample of
  {{defaults_structures}} structures completed, against {{defaults_hertzforge_sweep_or_step_record_completed}}
  with the band widened. paired completes {{steps_paired_all_completed}} of its
  {{steps_paired_all_runs}} stepped sines and ratio {{steps_ratio_all_completed}}. The followed-poles law completes more
  sweeps than the Python matrix ({{python_followed_poles_T1_all_completed_pct}} against
  {{python_matrix_T1_all_completed_pct}} percent up, {{python_followed_poles_T5_all_completed_pct}} against
  {{python_matrix_T5_all_completed_pct}} percent down), and over-tests less in
  {{python_T1_matrix_followed_poles_worst_over_db_favour_against}} of {{python_T1_matrix_followed_poles_worst_over_db_cells}}
  cells of the slow sweep up and more in one cell of the fast one. On the held-back structures,
  {{a:law_holds}} of the {{a:law_n}} claims about the laws hold, {{a:law_weaker}} hold weaker and
  {{a:law_does_not_hold}} do not hold. Everything here is simulation.
---

## Summary

A sine test with several shakers plays one tone on every shaker at once, reads the amplitude and
phase of every control, and corrects the drive at every update. The rule that makes the correction
is the control law. This article describes Hertzforge's five MIMO Sine laws and one candidate, how
each is built and how the study ran it, and how each scores on the MIMO Sine suite of the Open
Benchmark Set, draft 0.1, proposed in a companion article [@sinesuite2026]. The suite gives every
law the same {{s:problems}} problems on five systems and reads each run under several readings:
completion, the share of the test inside IEC 60068-2-6's tolerance at each control [@iec2007],
the worst over-test on the way through a resonance, and the reference-point and Method 514.8 lines
[@mil810h2019]. No law is graded as a whole. Each statement below that compares laws, or places a
law inside or outside a line, is a claim of the suite's claims rule, cited by its id; anything else
is marked "not a claim of the rule". An audit on held-back structures, which no run of the study
had seen, tested every claim; Section 5.7 gives its verdicts.

- **At a dwell, three laws are inside the IEC check-point band on most cells.** matrix,
  steepest_descent and secant complete {{hertzforge_matrix_T4_all_completed}},
  {{hertzforge_steepest_descent_T4_all_completed}} and {{hertzforge_secant_T4_all_completed}} of
  {{hertzforge_matrix_T4_all_runs}} dwells. Each is inside the band in the median on every square
  system ({{hertzforge_matrix_T4_iec_check_point_square_inside}} of
  {{hertzforge_matrix_T4_iec_check_point_square_cells}} cells; for matrix
  {{hertzforge_matrix_T4_iec_check_point_square_first_inside}} and the rest) and on
  {{hertzforge_matrix_T4_iec_check_point_more_controls_inside}} of
  {{hertzforge_matrix_T4_iec_check_point_more_controls_cells}} cells with more controls than
  shakers. Their differences are small: the rule finds a difference in
  {{hertzforge_T4_matrix_steepest_descent_worst_over_db_favour_law}} cells
  ({{hertzforge_T4_matrix_steepest_descent_worst_over_db_first_id}}) and none between matrix and
  secant. On the held-back structures every one of matrix's inside claims holds or holds weaker, while
  {{a:dwell_check_inside_steepest_descent_does_not_hold}} of steepest_descent's and
  {{a:dwell_check_inside_secant_does_not_hold}} of secant's do not hold, all on the 6 x 6 system
  (Section 5.2).
- **ratio and paired at a dwell.** ratio completes {{hertzforge_ratio_T4_all_completed_pct}}
  percent of its dwells and is inside the band on {{hertzforge_ratio_T4_iec_check_point_square_inside}}
  of {{hertzforge_ratio_T4_iec_check_point_square_cells}} square cells and
  {{hertzforge_ratio_T4_iec_check_point_more_controls_inside}} of
  {{hertzforge_ratio_T4_iec_check_point_more_controls_cells}} others; on the held-back structures
  {{a:dwell_check_inside_ratio_does_not_hold}} of those {{a:dwell_check_inside_ratio_n}} do not hold.
  paired completes
  {{hertzforge_paired_T4_all_completed_pct}} percent and is outside the band on every cell
  ({{hertzforge_paired_T4_iec_check_point_square_first_outside}} and the rest), by a median of
  {{hertzforge_paired_T4_iec_check_point_outside_low_db}} to
  {{hertzforge_paired_T4_iec_check_point_outside_high_db}} dB.
- **On a sweep or a stepped sine no law is inside the check-point band in the median of any cell**
  ({{level_sweeps_steps_all_iec_check_point_inside}} of {{level_sweeps_steps_all_iec_check_point_cells}}
  level claims). matrix completes {{hertzforge_matrix_T1_all_completed_pct}} percent of its sweeps up
  at one octave a minute, {{hertzforge_matrix_T2_all_completed_pct}} percent at four, and
  {{hertzforge_matrix_T5_all_completed_pct}} percent of its sweeps down; the share of a sweep run
  inside the band, counting a run that stopped as covering only what it ran, has a median of
  {{hertzforge_matrix_T1_all_iec_median_pct}} percent up and {{hertzforge_matrix_T5_all_iec_median_pct}}
  percent down.
- **Safety.** For the study the engine's control abort band was widened from
  {{f:protective_abort_default_db}} to {{f:protective_abort_widened_db}} dB and its divergence stop
  from {{f:protective_divergence_default_s}} to {{f:protective_divergence_widened_s}} s, so that runs
  would go on far enough to be read. Under those settings
  {{hertzforge_sweep_step_over_6db_pct_of_scored}} percent of the scored Hertzforge sweeps and stepped
  sines put a resonance more than 6 dB over its reference at a control or a held-out gauge
  ({{hertzforge_sweep_step_over_6db_pct_of_runs}} percent of all of them), and
  {{hertzforge_matrix_dwell_over_6db_pct_of_runs}} percent of matrix's dwells. The largest single
  over-tests are {{hertzforge_ratio_T4_largest_db}} dB (ratio, a dwell) and
  {{hertzforge_matrix_T5_largest_db}} dB (matrix, a sweep down). At the engine's default settings,
  {{defaults_hertzforge_sweep_or_step_completed}} of {{defaults_hertzforge_sweep_or_step_runs}}
  Hertzforge sweeps and stepped sines on a sample of {{defaults_structures}} structures completed,
  and {{defaults_hertzforge_dwell_completed}} of {{defaults_hertzforge_dwell_runs}} dwells: the
  defaults stop the test so that the operator looks at the data.
- **paired and ratio on a stepped sine.** paired completes {{steps_paired_all_completed}} of
  {{steps_paired_all_runs}} stepped sines and ratio {{steps_ratio_all_completed}}; matrix is ahead of
  paired on completion in {{hertzforge_T3_matrix_paired_completion_favour_law}} of
  {{s:cells_T3}} cells ({{hertzforge_T3_matrix_paired_completion_first_id}});
  {{vg:hertzforge_T3_matrix_paired_completion_first_id}}. Both are amplitude
  laws with no model of the coupling between shakers or none along frequency, on coupled
  structures; Section 6.1 gives where they stop.
- **Followed poles** tracks the poles of the modes near the tone on a modal fit of the identification. It ran
  in the Python version only, beside the Python port of matrix on the same exact identification. It
  completes {{python_followed_poles_T1_all_completed_pct}}, {{python_followed_poles_T2_all_completed_pct}} and
  {{python_followed_poles_T5_all_completed_pct}} percent of the three sweeps against
  {{python_matrix_T1_all_completed_pct}}, {{python_matrix_T2_all_completed_pct}} and
  {{python_matrix_T5_all_completed_pct}} percent. The rule finds it over-testing less in
  {{python_T1_matrix_followed_poles_worst_over_db_favour_against}} of {{python_T1_matrix_followed_poles_worst_over_db_cells}}
  cells of the slow sweep up ({{python_T1_matrix_followed_poles_worst_over_db_first_id}}), inside the band for
  more of the fast sweep in {{python_T2_matrix_followed_poles_iec_share_favour_against}} of
  {{python_T2_matrix_followed_poles_iec_share_cells}} cells ({{python_T2_matrix_followed_poles_iec_share_first_id}}), and
  over-testing more in one cell ({{followed_poles_matrix_favoured_T2_worst_over_db_id}});
  {{vg:python_T1_matrix_followed_poles_worst_over_db_first_id+python_T2_matrix_followed_poles_iec_share_first_id+followed_poles_matrix_favoured_T2_worst_over_db_id}}. It was admitted after
  the screen, post hoc, and its Rust build waits on the audit.
- **What did not work.** Three more candidates (the family inverse, the level ladder and the dither
  identification) and four predictive leads built on followed poles were screened and left out. Section 6 gives
  each one's idea, readings and the reason as far as it is known.
- **The audit.** On the held-back structures, {{a:law_holds}} of the {{a:law_n}} claims about the
  laws hold, {{a:law_weaker}} hold weaker (the direction held and the size fell outside the study's quartiles) and {{a:law_does_not_hold}}
  do not hold; of the {{a:followed_poles_n}} claims of followed poles, {{a:followed_poles_holds}} hold,
  {{a:followed_poles_weaker}} hold weaker and {{a:followed_poles_does_not_hold}} do not hold.
  {{a:all_not_tested_text}}
- **Implemented.** The five laws' mathematics is on Hertzforge's main branch and each is a
  selectable law. The study's runner is on a research branch, and followed poles is in the suite's Python code.

## 1. The Test and the Laws' Common Frame

A sine test holds one tone at a time. At the tone's frequency $f$ every shaker plays a sine of the
same frequency, so the drives are one complex vector $D$ (an amplitude and a phase per shaker), and
the controls, once settled, are $C = H(f)\,D$, with $H(f)$ the structure's response from drives to
controls at that frequency. The test gives a reference $R$, an amplitude (and, for most laws, a
phase) at every control. A sweep moves the tone through the band at a set rate; a stepped sine
holds it at a grid of frequencies in turn; a dwell holds it at one frequency, here the first
resonance in the band.

Hertzforge's MIMO Sine engine runs the loop and the law makes one decision. The engine measures
$H$ before the test, at its own low level and with measurement noise, and hands the law that
identification. At every update it
reads each control with a tracking filter (four one-pole sections on the heterodyned signal), asks
the law for the next drive, and plays it. Around the law it keeps the same guards for every law: a
cap on how far a drive may change in one update, a drive ceiling, an alarm band and an abort band
on the control error, a divergence stop when the caps bind for too long, settle windows at every
level move and every step in which nothing is judged, and a ladder that brings the test up
through rungs at {{f:ladder_levels}} dB of full level, each held {{f:ladder_rung_s}} s. So a
law decides only the drive, and the suite's readings say how well that decision served the test.

The laws differ in what model they use and how they move along frequency. Some use the measured
$H$ throughout; one learns its own; one uses no model of the coupling at all. In a sweep the tone
never rests, so a law that waits to read each correction settled falls behind; at a dwell every law
has time.

## 2. The Six Laws

Notation: $H$ is the identification at the tone, $Z$ its regularized inverse (least squares where
there are more controls than drives, least norm where there are more drives, regularized at
{{f:matrix_regularization}} of its largest singular value), $C$ the controls as the tracking
filters read them, $R$ the reference, $D_f$ the drive in force as played (after every guard), and
$g$ the gain of the engine's loop-speed rule, set every update from the tracking filter's delay and
the identification's group delay near the tone. The five shipped laws and their keys are in
Hertzforge's guide [@hertzforge2026], section "The built-in MIMO Sine laws"; the numbers below are
the guide's defaults.

### 2.1 `matrix`

matrix is the default law and the only shipped law that takes every test: sweeps, stepped sines and
dwells, with a reference that gives phases or amplitudes only. Each update it gives

$$
D^{+} = D_f + w\,\big(Z(f') - Z(f)\big)\,H(f)\,D_f + Z(f')\,(R - R_{-}) + P + g\,Z(f)\,(\tilde{R} - C)
$$ {#eq-matrix}

with $f'$ the frequency of the next interval, $R_{-}$ the reference told the update before, $\tilde{R}$
the reference passed through the loop's own delay, and $P$ the part of the last carry that a change
cap cut. The last term is the published correction through a fixed inverse, $D_{k+1} = D_k + g\,Z\,(R - C_k)$
[@qiu2019; @zhang2017; @sinesurvey2026], with the published gain of about one half
({{f:matrix_fixed_gain}}, a parameter) replaced by the loop-speed rule. The other terms are
Hertzforge's own. The carry, weighted by $w$ (default {{f:matrix_carry_default}}), moves the drive by
the model's own change between this frequency and the next, so that in a sweep the drive is already
near where the next frequency needs it; a model error common to $Z$ and $H$ cancels in it. The
reference's change is carried through the model at full weight, so a profile's breakpoint is
followed the update it is told. The correction is aimed at $\tilde{R}$, the reference as the trackers
read it, so that while the reference moves the filter's trail is not taken for a control error.
With more drives than controls, the part of the drive the controls cannot see is removed every
update. The model is the identification with its resonances fitted and the rest smoothed over
{{f:matrix_smoothing_lines}} lines.

The guide states the law's limit: it assumes the structure responds at test level as it did at the
identification's level. Where a resonance moves by less than a quarter of its half-power bandwidth,
expect the same control as on a linear structure; between a quarter and one bandwidth, errors over
3 dB at that resonance; past about one bandwidth the loop can be lost. On the testbed's linear
four-by-four structure it completed {{testbed_matrix_1}} of {{testbed_matrix_2}} dwells,
{{testbed_matrix_3}} of {{testbed_matrix_4}} stepped sines and {{testbed_matrix_5}} of
{{testbed_matrix_6}} sweeps at one octave a minute.

### 2.2 `paired`

paired pairs control $i$ with drive $i$ and uses nothing of the coupling. Every update each drive's
amplitude moves toward its control's ratio of wanted to measured amplitude, and its phase is left to
the pair:

$$
\lvert d_i \rvert^{+} = \lvert d_i \rvert \left( \frac{\lvert r_i \rvert}{\lvert c_i \rvert} \right)^{g}
$$ {#eq-paired}

Its first drive is the one this rule settles to on the identification at the tone (the rule run on
$C = H D$ until every control is within {{f:paired_settle_db}} dB, at most {{f:paired_settle_rounds}}
rounds). It takes dwells and stepped sines. It is Hertzforge's simplest law, the template a
contributor copies, and not a published multi-shaker law; the guide says it is for structures whose
pairs are weakly coupled, each control dominated by its own shaker. The suite's frames are coupled,
so its results here say how such a loop behaves where that condition does not hold.

### 2.3 `ratio`

ratio is the published amplitude-ratio law of Zhang, Chen and He [@zhang2015; @sinesurvey2026],
moved onto the inverse of the model. It plays $D = Z(f)\,\mathrm{diag}(\sigma)\,R$ with one factor
$\sigma_i$ per control, updated once the reading has settled from $E_i = \lvert C_i \rvert / \lvert R_i \rvert$:

$$
\sigma_i \leftarrow \sigma_i \,\frac{K + 1/E_i}{K + E_i} \;\; (E_i \le 1), \qquad
\sigma_i \leftarrow \sigma_i \,\frac{K + 1}{K + E_i} \;\; (E_i > 1)
$$ {#eq-ratio}

with $K$ the compression (default {{f:ratio_compression}}; larger is gentler). The source applies the
factor to each drive on a square setup; the default here applies it to each control's reference,
which needs no pairing of controls with shakers. The law has no gain; its pace is how often it
updates. It takes dwells and stepped sines, with amplitude-only references.

### 2.4 `steepest_descent`

steepest_descent is the published steepest-descent correction of Musella and co-authors
[@musella2019; @musella2020; @sinesurvey2026]:

$$
D^{+} = D_f + \frac{g}{s_{\max}^{2}}\, H^{H} (R - C)
$$ {#eq-steepest}

with $s_{\max}$ the largest singular value of $H$. Its first drive is the inverse drive $Z R$. It is
slow in the directions of $H$ with small singular values. It takes dwells only. On the testbed's
four-by-four structure it completed {{testbed_steepest_descent_1}} of {{testbed_steepest_descent_2}}
dwells, {{testbed_steepest_descent_3}} of {{testbed_steepest_descent_4}} stepped sines and none of
{{testbed_steepest_descent_5}} sweeps.

### 2.5 `secant`

secant is the adaptive law of Underwood's patent [@underwood1994; @sinesurvey2026]: a two-step cycle
that probes, measures the complex gain the probe produced, steps by it, and updates its inverse
model by a rank-one secant formula. With $E_k = R - C_k$ and $\langle x, v \rangle = v^{H} x$,

$$
\beta = \frac{(\hat{C}_k - C_k)^{\mathrm{H}} E_k}{\lVert \hat{C}_k - C_k \rVert^{2}}, \qquad
D_{k+1} = D_k + \beta P_k, \qquad
Z \leftarrow (I + u S^{H}) Z
$$ {#eq-secant}

where the probe $P_k = c\,Z_k E_k$ was played and read as $\hat{C}_k$, and $u$ and $S$ make the
model map the last change of control onto the last change of drive. Each step waits for the
response to settle ({{f:secant_settle_factor}} times the filter's and the structure's delays), so
its pace is the settle wait; the probe's weight starts at {{f:secant_first_probe}}. At a level move
the readings the cycle holds are scaled with the level, so the probe is read against the drive in
force. The survey found no published test of the patent's printed equations [@sinesurvey2026].
It takes dwells only.

### 2.6 Followed Poles

A structure whose joints soften or stiffen with level moves the frequency and damping of its modes
at test level and leaves their shapes nearly alone. matrix's inverse is the low-level one, so near a
mode that has moved by a bandwidth or more its correction points the wrong way. Followed poles keeps the
identification as a modal model plus a smooth remainder,

$$
\hat{H}(f;\theta) = B_{\mathrm{rem}}(f) + \sum_{r} \psi_r \lambda_r^{T}\, q(f; f_r, \zeta_r), \qquad
q = \frac{u^{2}}{1 - u^{2} + 2 j \zeta_r u}, \quad u = f / f_r
$$ {#eq-followed-poles-model}

with $\psi_r$ the shape at the controls, $\lambda_r$ the participation at the drives, and the
remainder $B_{\mathrm{rem}}$ chosen so the model equals the identification at low level. During the
test it refits the frequency $f_r$ and damping $\zeta_r$ of the modes within
{{f:followed_poles_near_bw}} bandwidths of the tone from the operating drives and responses of the last
{{f:followed_poles_window}} updates, with a prior that anchors each to its last value:

$$
\min_{f_r, \zeta_r} \sum_{j} w_j \lVert C_j - \hat{H}(f_j;\theta)\,D_j \rVert^{2}
+ \rho_f \frac{(f_r - f_{r,\mathrm{prev}})^{2}}{f_r^{2}} + \rho_\zeta (\ln \zeta_r - \ln \zeta_{r,\mathrm{prev}})^{2}
$$ {#eq-followed-poles-fit}

A mode is moved only where the data can tell a shift from none, by at most {{f:followed_poles_step_bw}} of a
bandwidth a fit. The drive comes from the carried loop of Section 2.1 in its research form (gain
{{f:carried_g}} with the loop-speed rule) through the inverse of $\hat{H}$. A prediction gate compares
the followed model's residual with the frozen model's over the window, and uses the frozen inverse
while the followed one is worse by a ratio of {{f:followed_poles_gate_ratio}}; both predict the same
measurements, so the noise cancels from the comparison.

The modal fit under followed poles is the suite's M7d: poly-reference least-squares complex-frequency fits
(pLSCF) over half-octave ranges, orders {{f:m7d_orders}}, poles clustered over the orders
({{f:m7d_cluster_freq_pct}} percent in frequency, {{f:m7d_cluster_damp_pct}} percent in damping,
participation MAC {{f:m7d_mac}}), then real rank-one residues by least squares in the frequency
domain [@peeters2004; @guillaume2003; @steffensen2025; @cauberghe2005]. Before the fit a pure delay
is taken out of the identification and put back on the residues: the delay of the simulator's
block, read from the structure file ({{f:block_delay_linear}} samples on the linear tier,
{{f:block_delay_jointed}} on the jointed tiers), the delay a loopback measures on a real station.
Section 6.6 gives why it is not the engine's measured lag.

The idea that frequency and damping move while the shapes stay is the one Hertzforge's followed
laws for shock use [@shocklaws2026]. The anchored, gated, pooled estimator is this work's own; its
derivation and the research runs that shaped it are in the benchmark's record [@sineresults2026].

### 2.7 The Screen, and How Followed Poles Entered

Before the study, four candidates were screened on the study's own structures
{{f:screen_structure_numbers}} of the 6 x 6 and 6 x 12 systems, realistic and strong
({{f:screen_structures_nonlinear}} structures, {{f:screen_cell_structures}} a cell), with the linear
tier on the same structures as a control ({{f:screen_structures_all}} in all, {{f:g_runs}} runs).
The candidates were the family inverse, followed poles, the level ladder and the dither
identification (recursive least squares on a dither at the dwell); each is described in Section 6. The rule, written before the runs: a candidate enters if, on at
least one test and tier, it ends in tolerance (completed, and inside the IEC check-point band at
every judged update) on more structures than matrix, with its median worst over-test not worse
than matrix's by more than {{f:g_rule_over_db}} dB.

No candidate passed, and on the sweeps and stepped sines, the tests the candidates were built for,
the rule could not have passed one: on every realistic and strong sweep and stepped sine of the
screen no run of any law ended in tolerance, matrix included
({{f:G_matrix_T1_realistic_ends}} of {{f:screen_cell_structures}} in every such cell); only the dwells
and matrix's linear stepped sine ({{f:G_matrix_T3_linear_ends}} of {{f:screen_cell_structures}}) did.
On the graded readings followed poles was the strongest candidate: it completed
{{screen_G_followed_poles_vs_matrix_nonlinear_completed}} of {{f:G_followed_poles_runs_nonlinear}} nonlinear sweeps against
matrix's {{screen_G_followed_poles_vs_matrix_nonlinear_completed_yardstick}}, its p95 control error was lower on
{{screen_G_followed_poles_vs_matrix_nonlinear_p95_lower_on}} of {{screen_G_followed_poles_vs_matrix_nonlinear_p95_n}} paired
structures and its IEC share higher on {{screen_G_followed_poles_vs_matrix_nonlinear_iec_higher_on}}, but on the
strong tier it over-tested more (paired medians {{screen_G_followed_poles_vs_matrix_T5_strong_over_db}} to
{{screen_G_followed_poles_vs_matrix_T2_strong_over_db}} dB). Read with "completed" in place of "ended in
tolerance", a reading added after the runs, the rule would have passed it on
{{f:G_post_hoc_followed_poles_cells}} cells. Kevin Cross admitted it on that record ("{{f:followed_poles_quote}}"). The
admission is post hoc and is recorded as such: each of its {{s:claims_followed_poles}} claims carries the mark
`admitted_after_screen`, the screen ran on study structures, and the held-back structures are the
test of whether its claims stand. The family inverse, the level ladder and the dither identification
were left out.

## 3. Their Build in Hertzforge, and How the Study Ran Them

### 3.1 What Is on Hertzforge's Main Branch

The five laws' mathematics is the crate `hertzforge-mimo-sine-law-math`: `matrix.rs`, `paired.rs`,
`ratio.rs`, `steepest.rs` and `secant.rs`, with the shared parts in `modal.rs` (the modal model),
`speed.rs` (the loop-speed rule), `setup.rs`, `linalg.rs`, `law.rs` and `readings.rs`, and the
crate's parity vectors in its test data. The crate `hertzforge-mimo-sine-laws` makes them selectable
(`choice.rs`, `facts.rs`, `check.rs`, and `wasm.rs` for law files), and `hertzforge-mimo-sine` is the
engine that runs them. Each law also builds as a law file (`laws/mimo-sine-matrix` and the others)
from the same mathematics; over whole recorded runs the law file gives the native law's drives
within rounding (matrix within about {{f:law_file_rounding_matrix}}, because its modal fit is an
iterative search that the platforms' rounding moves) [@hertzforge2026].

Followed poles is not in Hertzforge. Its Rust build, about {{f:followed_poles_rust_lines}} lines with its tests, plus a
declared block delay in the engine so the modal fit can take the right delay out, waits on the
audit.

### 3.2 How the Study Ran Them

The suite has two versions that run the same cases and write the same run file, read by the same
scorer [@sinesuite2026].

- **The Hertzforge version** is a closed-loop runner on Hertzforge's own MIMO Sine engine: the
  engine as shipped, its identification measured at its own low level with noise, its tracking
  filters, guards, ladder and pipeline, and the five laws as Rust law mathematics, on the simulator
  station. The runner is an example program on a research branch; the three MIMO Sine crates are
  the same at the commit the study ran and on main (a diff between the two lists
  {{f:law_crate_files_changed}} files in them). Every Hertzforge
  run's card names the same runner (one SHA-256 over {{s:runs_hertzforge}} runs).
- **The Python version** is the suite's own harness, which restates the engine's loop in Python and
  runs Python ports of the laws. It hands the law the structure's exact small-signal response as the
  identification, with no noise and every line trusted. It is the only version that runs followed
  poles, and it ran matrix beside it, so every comparison of followed poles is with the Python matrix on the same structures and
  the same identification. Neither of the Python version's laws is compared with a Hertzforge run.

Every run of record used the engine's widened protective settings: the control abort band
{{f:protective_abort_widened_db}} dB in place of {{f:protective_abort_default_db}}, the abort count
{{f:protective_ticks_widened}} updates in place of {{f:protective_ticks_default}}, the divergence stop
{{f:protective_divergence_widened_s}} s in place of {{f:protective_divergence_default_s}}, the alarm
band {{f:protective_alarm_widened_db}} dB as by default. At the defaults most runs stop early on a
structure that changes with level, and the readings would say only that they stopped. The default
settings were run on a sample (Section 5.4). Every law ran at its defaults; none was tuned on the
suite.

### 3.3 Parity of the Two Versions

Parity was shown in two places, and they show different things.

**Against Hertzforge's parity vectors.** The Python ports are held to the shipped laws' parity
vectors, copied from the Hertzforge repository: {{f:parity_runs}} runs (each law and schedule), on
the vectors' own small structure, not on suite problems. The largest relative difference of drive
and controls is {{f:parity_largest}}, and a different law is shown to miss them by more than
{{f:parity_other_law}}. The vectors have a flat reference, no guards and the quasi-steady loop, so
they cannot see matrix's carry of the reference's change, its aimed reference or its carry of what
a cap cut; the Python matrix restates those from `matrix.rs` and a separate test shows the vectors'
form and the restated form part on a sloped reference. They also cannot see the modal fit: the
Python matrix fits every group of modes jointly and carries everywhere, where the shipped fit
limits its groups and carries nothing in the windows it leaves out.

**Between the two versions on suite problems.** The agreement sample is
{{f:agree_a_structures}} suite structures (the 6 x 6, 6 x 12 and 3 x 12 systems, linear and
realistic, the first two structures of each), every test each law takes: {{f:agree_a_pairs}} pairs
of runs. A pair agrees on its outcome when both runs end the same way at the same place, and on its
readings when every reading of the two cards is within a tolerance set against its use in the
study. Two comparisons were made: (a) both versions' laws on the exact response, and (b) each
version on its own identification, the Python version handed the Hertzforge run's measured one. On
(a), {{f:agree_a_outcome}} of {{f:agree_a_pairs}} pairs agree on their outcome and {{f:agree_a_every}}
on every reading; on (b), {{f:agree_b_outcome}} and {{f:agree_b_every}} (@fig-agreement). ratio's and
paired's stepped sines aborted in both versions in all {{f:agree_a_ratio_T3_runs}} pairs of each, in
both comparisons. On (a) every outcome that differs is one of ratio's stepped sines
({{agree_a_ratio_T3_outcome_differs}} pairs), aborted in both versions at different places. On (b)
{{agree_b_ratio_T3_outcome_differs}} of ratio's stepped sines differ, and one pair each of ratio's
dwell, secant's dwell, matrix's sweep down and paired's stepped sine. Where a diverging loop ends is
not reproducible between versions.
The readings that most often part are the worst-point readings of a sweep (the worst excursion, the
worst over-test), which rest on one update; the shares and medians agree more often. This is not a
claim of the rule.

![How far the two versions agree, law by law, on the agreement sample of {{f:agree_a_structures}} suite structures: the share of paired runs whose outcome agrees (solid) and whose outcome and every reading agree (hatched), for comparison (a), both versions' laws on the exact response (blue), and comparison (b), each version on its own identification (orange). Pairs per law under each group.](figures/fig7_agreement.png){#fig-agreement fig-alt="Grouped bars for five laws (matrix, paired, ratio, steepest_descent, secant), four bars each, share of paired runs from 0 to 100 percent. Outcome agreement is near 100 percent for every law but ratio, where it is lower in both comparisons. Agreement on every reading is lower for every law, lowest for ratio and matrix, and highest for steepest_descent." data="data/law_agreement.csv"}

So the two versions are two implementations of the same loop that agree on how most runs end and
less often on every reading. The claims rule never pairs a reading of one version with one of the
other: matrix's Hertzforge claims are among Hertzforge runs, and those of followed poles against the Python matrix.

## 4. The Study

The suite's {{s:problems}} structures are the Random suite's, on five systems written here as
shakers by controls: 3 x 12, 6 x 12, 12 x 24, 6 x 6 and 12 x 12. Each system has a linear, a
realistic and a strong tier, whose joints soften or stiffen with level by a realistic amount and by
more; on the 6 x 12 and 6 x 6 systems four more kinds hold softening only or hardening only at each
of the two sizes. A cell is one system and structure kind on one test; there are {{s:cells_T1}}
cells on each of T1 to T4, {{s:cells_T5}} on T5 and {{s:cells_L1}} on L1 [@sinesuite2026].

The tests, each run up a ladder before its judged level:

- **T1**, a log sweep up from {{f:band_low_hz}} to {{f:band_high_hz}} Hz at one octave a minute
  ({{f:t1_seconds}} s); **T2**, the same at four octaves a minute ({{f:t2_seconds}} s);
- **T3**, a stepped sine at {{f:t3_steps_per_octave}} steps an octave ({{f:t3_steps}} steps), each
  held {{f:t3_step_time_constants}} time constants of the slowest mode in band;
- **T4**, a dwell at the first resonance in band, held {{f:t4_time_constants}} time constants of its
  mode and at least {{f:t4_least_s}} s, the first {{f:t4_not_judged}} not judged;
- **T5**, a log sweep down at one octave a minute, on {{s:structures_T5}} structures;
- **L1**, T1 with one limit channel, on {{s:structures_L1}} structures.

The Hertzforge version ran matrix on every test, paired and ratio on T3 and T4, and steepest_descent
and secant on T4: {{s:runs_hertzforge}} runs. The Python version ran matrix and followed poles on T1, T2, T5 and
L1: {{s:runs_python}} runs. One sequence of measurement noise was used, the same for every law on a
problem and test. {{s:runs_hertzforge_held_by_identification}} Hertzforge runs never started,
because the engine's coherence gate held their identification; they count as covering nothing.

**The readings.** Each run has three primary readings, taken from the scorer's card:

- the **IEC share**, the share of the test, from where full level began, run inside the IEC
  60068-2-6 check-point band (each control within {{f:check_point_low_pct}} percent up to
  {{f:check_point_corner_hz}} Hz and {{f:check_point_high_pct}} percent above), times the share of
  the test covered: so a run that stopped halfway reads at most one half, and an unscored run reads
  0;
- the **worst over-test**, the largest error over the reference at the controls and held-out gauges
  on the way through each mode's half-power band, in dB; missing for an unscored run;
- the **completion**, 1 for a completed run and otherwise the share of the test covered at full
  level.

The scorer also reads each line of the standards: the IEC check point, the IEC reference point (the
average of the controls within {{f:reference_point_pct}} percent), Method 514.8's composite
({{f:composite_pct}} percent) and its average and maxi individual-control lines [@mil810h2019]. Phase
is reported, not judged.

**The claims rule.** The claims were made by a rule fixed before the audit and frozen with the
readings [@sinesuite2026]. For every two laws that ran the same test in a cell, the rule pairs the
structures and makes a claim where the median difference of a reading is beyond its threshold
({{s:threshold_iec_share}} in a share, {{s:threshold_worst_over_db}} dB) and most of the pairs agree
in sign: at least {{f:claims_rule_side_in_10}} in 10 beyond the threshold on the median's side and at most {{f:claims_rule_other_in_10}} in 10 on the other.
For every law in every cell and every line it makes a level claim, inside or outside, from the
median worst excursion over the line, an unscored run counting as outside. Of the rule's
{{s:claims}} claims, {{s:claims_law}} are about laws ({{s:claims_level}} levels and {{s:claims_pair}}
paired differences); the other {{s:claims_effect}} are effects of the structure, for the suite
paper. No claim was added after the freeze ({{s:claims_late}}).

**The audit.** The audit runs every job on {{f:heldout_problems}} held-back problems (structures
{{f:heldout_structures}} of every cell) and judges each claim: a level claim holds if the audit's
median is on its side of the line and inside the study's quartiles, is weaker if it is on its side
but outside them, and does not hold otherwise; a paired difference holds if the audit's median has
its sign, is beyond the threshold and is inside the study's quartiles, is weaker if it has the sign
and is beyond the threshold but lies outside them, and does not hold otherwise. Of the
{{a:law_n}} law claims, {{a:law_holds}} hold, {{a:law_weaker}} are weaker and
{{a:law_does_not_hold}} do not hold. {{a:all_not_tested_text}} Section 5.7 gives them by law.

**Two more sets.** The engine's default protective settings were run on
{{defaults_structures}} structures, the first two of each tier of the 6 x 6 and 6 x 12 systems, for
every job: {{defaults_hertzforge_runs}} Hertzforge and {{defaults_python_runs}} Python runs. And
{{repeats_sets_each}} repeats of every job on {{repeats_structures}} structures read how far one run
moves when it is run again: {{repeats_hertzforge_repeat_runs}} Hertzforge and
{{repeats_python_repeat_runs}} Python runs.

## 5. Results

### 5.1 How Often Each Law Completes, and How Close It Holds

@fig-readings gives each job's completions and median readings, tier by tier.

![Each law and test, tier by tier: (a) the share of runs completed, (b) the median IEC share (the share of the test inside the check-point band, a stopped run counting only what it covered), (c) the median worst over-test in dB. The Hertzforge version is left of the dashed line; the Python version, with followed poles, right of it. Grey is the linear tier, blue with hatching the realistic tier, orange with dots the strong tier; the outline is all tiers.](figures/fig1_readings.png){#fig-readings fig-alt="Three panels of grouped bars, one group per law and test: twelve Hertzforge jobs (matrix on T1, T2, T3, T4, T5 and L1; paired and ratio on T3 and T4; steepest_descent and secant on T4) and eight Python jobs (matrix and followed_poles on T1, T2, T5 and L1). The dwell jobs of matrix, steepest_descent and secant complete nearly every run on every tier with a median IEC share near 100 percent and a median over-test from about {{r0:hertzforge_matrix_T4_linear_worst_median_db}} dB on the linear tier to about {{r0:hertzforge_matrix_T4_strong_worst_median_db}} dB on the strong. The sweeps and steps complete far less on the realistic and strong tiers than on the linear, and their median over-tests run from about {{r0:python_followed_poles_T5_linear_worst_median_db}} dB (followed_poles on the linear tier) to about {{r0:hertzforge_ratio_T3_linear_worst_median_db}} dB (ratio's stepped sine). paired's stepped sine completes nothing." data="data/law_readings.csv"}

**The dwell.** matrix, steepest_descent and secant complete
{{hertzforge_matrix_T4_all_completed_pct}}, {{hertzforge_steepest_descent_T4_all_completed_pct}}
and {{hertzforge_secant_T4_all_completed_pct}} percent of their dwells, and the median dwell of each
is inside the IEC band for its whole length. Counted run by run, matrix's dwell is inside the band at
every judged update in {{hertzforge_matrix_T4_all_inside_cp}} of {{hertzforge_matrix_T4_all_runs}}
runs ({{hertzforge_matrix_T4_all_inside_cp_pct}} percent; of its completed runs,
{{pct:hertzforge_matrix_T4_all_inside_cp:hertzforge_matrix_T4_all_completed}} percent),
steepest_descent's in {{hertzforge_steepest_descent_T4_all_inside_cp}}
({{hertzforge_steepest_descent_T4_all_inside_cp_pct}} percent) and secant's in
{{hertzforge_secant_T4_all_inside_cp}} ({{hertzforge_secant_T4_all_inside_cp_pct}} percent). On the
linear tier matrix's dwell is inside in {{hertzforge_matrix_T4_linear_inside_cp}} of
{{hertzforge_matrix_T4_linear_runs}} runs, on the strong tier in {{hertzforge_matrix_T4_strong_inside_cp}}
of {{hertzforge_matrix_T4_strong_runs}}. ratio completes {{hertzforge_ratio_T4_all_completed_pct}}
percent of its dwells and is inside at every update in {{hertzforge_ratio_T4_all_inside_cp_pct}}
percent of them; paired completes {{hertzforge_paired_T4_all_completed_pct}} percent, none inside at every update
({{hertzforge_paired_T4_all_inside_cp}} runs); its median IEC share is
{{hertzforge_paired_T4_all_iec_median_pct}} percent and its median worst over-test
{{hertzforge_paired_T4_all_worst_median_db}} dB: the widened abort band lets a dwell go on with its
controls far off the reference (Section 5.4). These
run counts are not claims of the rule; the cell-level statements in Section 5.2 are.

**The sweeps and the stepped sine.** matrix completes {{hertzforge_matrix_T1_linear_completed_pct}}
percent of its slow sweeps up on the linear tier, {{hertzforge_matrix_T1_realistic_completed_pct}} on
the realistic and {{hertzforge_matrix_T1_strong_completed_pct}} on the strong; over all tiers
{{hertzforge_matrix_T1_all_completed_pct}} percent of T1, {{hertzforge_matrix_T2_all_completed_pct}} of
T2, {{hertzforge_matrix_T3_all_completed_pct}} of T3 and {{hertzforge_matrix_T5_all_completed_pct}} of
T5. Even a completed sweep has stretches outside the band: of matrix's
{{hertzforge_matrix_T1_all_runs}} slow sweeps up, none is inside at every judged update, and of all
the study's sweeps and stepped sines only {{hertzforge_matrix_T3_all_inside_cp}} of matrix's stepped
sines, {{python_followed_poles_T1_all_inside_cp}} of the slow sweeps up of followed poles and {{python_followed_poles_T5_all_inside_cp}} of its
sweeps down are. The
median IEC share, which counts a stopped run as covering only what it ran, is
{{hertzforge_matrix_T1_all_iec_median_pct}} percent on T1 and {{hertzforge_matrix_T5_all_iec_median_pct}}
percent on T5. The median worst over-test on a sweep is {{hertzforge_matrix_T1_all_worst_median_db}} dB
on T1 and {{hertzforge_matrix_T1_linear_worst_median_db}} dB on the linear tier alone, where nothing
moves with level: on these lightly damped frames the over-test at the worst resonance of a sweep,
at a control or a held-out gauge, is large even when the controls are held well on most of the
band. matrix completes fewer sweeps down than up in both versions
({{hertzforge_matrix_T5_all_completed_pct}} against {{hertzforge_matrix_T1_all_completed_pct}} percent
in the Hertzforge version, {{python_matrix_T5_all_completed_pct}} against
{{python_matrix_T1_all_completed_pct}} in the Python), most of all on the realistic tier
({{hertzforge_matrix_T5_realistic_completed}} of {{hertzforge_matrix_T5_realistic_runs}} down); the
followed-poles law completes about as many down as up ({{python_followed_poles_T5_all_completed_pct}} and
{{python_followed_poles_T1_all_completed_pct}} percent). The sweep down runs on fewer structures than the sweeps
up (no softening-only or hardening-only kinds), so these shares are not of the same structures, and
none of this is a claim of the rule, which compares laws, not tests. On the held-back structures
matrix completes {{a:heldout_hertzforge_matrix_T1_all_completed_pct}} percent of its slow sweeps up and
{{a:heldout_hertzforge_matrix_T5_all_completed_pct}} percent of its sweeps down in the Hertzforge
version, and {{a:heldout_python_matrix_T1_all_completed_pct}} and
{{a:heldout_python_matrix_T5_all_completed_pct}} percent in the Python version; these are run counts,
not claims of the rule.

### 5.2 Cell by Cell: The Level Claims

@fig-levels counts, for each job and each tolerance line, the cells whose median run is inside the
line.

![Level claims: for each job (rows) and each line the scorer reads (columns: IEC check point, IEC reference point, MIL-STD-810H composite, MIL average individual, MIL maxi individual), the number of cells whose median run is inside the line, of the cells the job ran. Darker is more cells inside.](figures/fig2_levels.png){#fig-levels fig-alt="A heat map with twenty rows (the jobs) and five columns (the lines). The dwell rows of matrix, steepest_descent and secant are dark: {{level_hertzforge_matrix_T4_iec_check_point_inside}} of {{level_hertzforge_matrix_T4_iec_check_point_cells}} cells inside the check point, all {{level_hertzforge_matrix_T4_iec_reference_point_cells}} inside the reference point and composite. ratio's dwell has {{level_hertzforge_ratio_T4_mil_maxi_individual_inside}} or {{level_hertzforge_ratio_T4_iec_check_point_inside}}. paired's dwell has none. Every sweep and step row is empty under the check point and the individual-control lines, with a few cells inside the reference point and composite, more for followed_poles than for matrix." data="data/law_level_counts.csv"}

**At a dwell** matrix, steepest_descent and secant are each inside the check-point band on
{{level_hertzforge_matrix_T4_iec_check_point_inside}} of {{level_hertzforge_matrix_T4_iec_check_point_cells}}
cells ({{level_hertzforge_matrix_T4_iec_check_point_first_inside}},
{{level_hertzforge_steepest_descent_T4_iec_check_point_first_inside}} and
{{level_hertzforge_secant_T4_iec_check_point_first_inside}} and the rest), and inside the reference
point and the composite on all {{level_hertzforge_matrix_T4_iec_reference_point_cells}}
({{level_hertzforge_matrix_T4_iec_reference_point_first_inside}}). Each of the three is inside on {{hertzforge_matrix_T4_iec_check_point_square_inside}}
of {{hertzforge_matrix_T4_iec_check_point_square_cells}} square cells and on
{{hertzforge_matrix_T4_iec_check_point_more_controls_inside}} of
{{hertzforge_matrix_T4_iec_check_point_more_controls_cells}} with more controls than shakers, and the
cells outside are the same seven for all three ({{hertzforge_matrix_T4_iec_check_point_more_controls_first_outside}}
for matrix), with median excursions of {{hertzforge_matrix_T4_iec_check_point_outside_low_db}} to
{{hertzforge_matrix_T4_iec_check_point_outside_high_db}} dB for matrix. They are the cells of the
3 x 12, 6 x 12 and 12 x 24 systems whose joints soften (realistic, strong and softening only), all
but the realistic 12 x 24; the linear and hardening-only cells of those systems are inside. With more
controls than shakers the controls cannot all be held at once, and where the joints soften the
low-level model is further off at test level; which of the two puts these cells outside was not
separated. This reading of where the cells lie is not a claim of the rule. Under the maxi individual line matrix and secant are inside on {{level_hertzforge_matrix_T4_mil_maxi_individual_inside}}
cells and steepest_descent on {{level_hertzforge_steepest_descent_T4_mil_maxi_individual_inside}}
({{level_hertzforge_steepest_descent_T4_mil_maxi_individual_first_inside}} and the rest). ratio is
inside the check point on {{hertzforge_ratio_T4_iec_check_point_square_inside}} of
{{hertzforge_ratio_T4_iec_check_point_square_cells}} square cells
({{hertzforge_ratio_T4_iec_check_point_square_first_inside}}) and
{{hertzforge_ratio_T4_iec_check_point_more_controls_inside}} of
{{hertzforge_ratio_T4_iec_check_point_more_controls_cells}} others
({{hertzforge_ratio_T4_iec_check_point_more_controls_first_inside}}), its cells outside by
{{hertzforge_ratio_T4_iec_check_point_outside_low_db}} to {{hertzforge_ratio_T4_iec_check_point_outside_high_db}}
dB. paired is outside every line on every cell ({{hertzforge_paired_T4_iec_check_point_more_controls_first_outside}}).
On the held-back structures, of the {{level_hertzforge_matrix_T4_iec_check_point_inside}} check-point
inside claims of each, {{a:dwell_check_inside_matrix_holds}} of matrix's hold and
{{a:dwell_check_inside_matrix_weaker}} hold weaker; {{a:dwell_check_inside_steepest_descent_holds}} of
steepest_descent's hold, {{a:dwell_check_inside_steepest_descent_weaker}} hold weaker and
{{a:dwell_check_inside_steepest_descent_does_not_hold}} do not hold
({{a:dwell_check_inside_steepest_descent_does_not_hold_ids}}); {{a:dwell_check_inside_secant_holds}} of
secant's hold, {{a:dwell_check_inside_secant_weaker}} holds weaker and
{{a:dwell_check_inside_secant_does_not_hold}} do not hold ({{a:dwell_check_inside_secant_does_not_hold_ids}});
and of ratio's {{a:dwell_check_inside_ratio_n}}, {{a:dwell_check_inside_ratio_holds}} hold and
{{a:dwell_check_inside_ratio_does_not_hold}} do not ({{a:dwell_check_inside_ratio_does_not_hold_ids}}).
On the other four lines, {{a:dwell_other_lines_does_not_hold}} of the {{a:dwell_other_lines_n}} dwell
level claims do not hold ({{a:dwell_other_lines_does_not_hold_ids}}), every one of them a claim of
ratio, steepest_descent or secant.

**On a sweep or a stepped sine** no job is inside the check-point band in any cell:
{{level_sweeps_steps_hertzforge_iec_check_point_inside}} of
{{level_sweeps_steps_hertzforge_iec_check_point_cells}} Hertzforge level claims and
{{level_sweeps_steps_python_iec_check_point_inside}} of {{level_sweeps_steps_python_iec_check_point_cells}}
Python ones (for matrix's slow sweep up, {{hertzforge_matrix_T1_iec_check_point_more_controls_first_outside}}
and the rest). The looser lines separate them a little. Inside the reference point, which judges the
average of the controls, are {{level_hertzforge_matrix_T1_iec_reference_point_inside}} of matrix's
Hertzforge slow-sweep cells ({{level_hertzforge_matrix_T1_iec_reference_point_first_inside}}),
{{level_python_matrix_T1_iec_reference_point_inside}} of the Python matrix's
({{level_python_matrix_T1_iec_reference_point_first_inside}}) and
{{level_python_followed_poles_T1_iec_reference_point_inside}} of those of followed poles
({{level_python_followed_poles_T1_iec_reference_point_first_inside}}); inside the composite,
{{level_hertzforge_matrix_T1_mil_composite_inside}}, {{level_python_matrix_T1_mil_composite_inside}}
and {{level_python_followed_poles_T1_mil_composite_inside}}. Under the individual-control lines of Method 514.8
no sweep or stepped sine of any law is inside in any cell. On the held-back structures every one of
the sweep and stepped check-point claims stays outside: of the Hertzforge version's
{{a:sweep_step_check_hertzforge_n}}, {{a:sweep_step_check_hertzforge_holds}} hold and
{{a:sweep_step_check_hertzforge_weaker}} hold weaker, and of the Python version's
{{a:sweep_step_check_python_n}}, {{a:sweep_step_check_python_holds}} and
{{a:sweep_step_check_python_weaker}}. Over all five lines, {{a:sweep_step_python_does_not_hold}} of the
Python version's {{a:sweep_step_python_n}} sweep level claims do not hold:
{{a:job_python_matrix_sweep_step_does_not_hold}} of the Python matrix's
({{a:job_python_matrix_sweep_step_does_not_hold_ids}}) and {{a:job_python_followed_poles_sweep_step_does_not_hold}}
of those of followed poles (Section 5.5).

### 5.3 Law Against Law

@fig-pairs gives the paired claims among the Hertzforge laws, where two laws ran the same test.

![Paired claims among the Hertzforge laws on the stepped sine (T3) and the dwell (T4): for each pair of laws and each reading, the number of cells (of {{s:cells_T3}}) where the rule favours the first law (to the right) and the second (to the left). Cells with no claim are not drawn.](figures/fig3_pairs.png){#fig-pairs fig-alt="Diverging horizontal bars, one row per pair of laws and reading. On T3 matrix is favoured over paired and over ratio in most cells on completion and IEC share, and ratio over paired in every cell on completion and IEC share. On T4 matrix, steepest_descent and secant are favoured over paired in every cell on IEC share and in about half on completion; over ratio on IEC share and over-test in about half the cells; among the three, only two cells each favour matrix and secant over steepest_descent on over-test." data="data/law_pair_counts.csv"}

**Stepped sine.** matrix is favoured over paired on completion in
{{hertzforge_T3_matrix_paired_completion_favour_law}} of {{s:cells_T3}} cells
({{hertzforge_T3_matrix_paired_completion_first_id}}) and on IEC share in
{{hertzforge_T3_matrix_paired_iec_share_favour_law}} ({{hertzforge_T3_matrix_paired_iec_share_first_id}});
over ratio on completion in {{hertzforge_T3_matrix_ratio_completion_favour_law}}
({{hertzforge_T3_matrix_ratio_completion_first_id}}), on IEC share in
{{hertzforge_T3_matrix_ratio_iec_share_favour_law}} ({{hertzforge_T3_matrix_ratio_iec_share_first_id}})
and on over-test in {{hertzforge_T3_matrix_ratio_worst_over_db_favour_law}}
({{hertzforge_T3_matrix_ratio_worst_over_db_first_id}});
{{vg:hertzforge_T3_matrix_paired_completion_first_id+hertzforge_T3_matrix_paired_iec_share_first_id+hertzforge_T3_matrix_ratio_completion_first_id+hertzforge_T3_matrix_ratio_iec_share_first_id+hertzforge_T3_matrix_ratio_worst_over_db_first_id}}.
ratio is favoured over paired on completion and IEC share in every cell
({{hertzforge_T3_paired_ratio_completion_first_id}}, {{hertzforge_T3_paired_ratio_iec_share_first_id}}):
ratio covers more of the test before it stops;
{{vg:hertzforge_T3_paired_ratio_completion_first_id+hertzforge_T3_paired_ratio_iec_share_first_id}}.

**Dwell.** The three laws with a model of the coupling are favoured over paired on IEC share in
every cell ({{hertzforge_T4_matrix_paired_iec_share_first_id}},
{{hertzforge_T4_paired_steepest_descent_iec_share_first_id}},
{{hertzforge_T4_paired_secant_iec_share_first_id}}) and on completion in
{{hertzforge_T4_matrix_paired_completion_favour_law}} to
{{hertzforge_T4_paired_steepest_descent_completion_favour_against}}
({{hertzforge_T4_matrix_paired_completion_first_id}}); over ratio on IEC share in
{{hertzforge_T4_ratio_steepest_descent_iec_share_favour_against}} to
{{hertzforge_T4_matrix_ratio_iec_share_favour_law}} cells
({{hertzforge_T4_matrix_ratio_iec_share_first_id}}) and on over-test in
{{hertzforge_T4_ratio_secant_worst_over_db_favour_against}} to
{{hertzforge_T4_matrix_ratio_worst_over_db_favour_law}} ({{hertzforge_T4_matrix_ratio_worst_over_db_first_id}}),
and never on completion against ratio;
{{vg:hertzforge_T4_matrix_paired_iec_share_first_id+hertzforge_T4_paired_steepest_descent_iec_share_first_id+hertzforge_T4_paired_secant_iec_share_first_id+hertzforge_T4_matrix_paired_completion_first_id+hertzforge_T4_matrix_ratio_iec_share_first_id+hertzforge_T4_matrix_ratio_worst_over_db_first_id}}.
Among matrix, steepest_descent and secant the rule makes four
claims, all on over-test and all against steepest_descent: matrix in
{{hertzforge_T4_matrix_steepest_descent_worst_over_db_favour_law}} cells
({{hertzforge_T4_matrix_steepest_descent_worst_over_db_first_id}}) and secant in
{{hertzforge_T4_steepest_descent_secant_worst_over_db_favour_against}}
({{hertzforge_T4_steepest_descent_secant_worst_over_db_first_id}});
{{vg:pair_ids_hertzforge_T4_matrix_steepest_descent_worst_over_db+pair_ids_hertzforge_T4_steepest_descent_secant_worst_over_db}}.
On every other reading and
cell the three differ by less than the rule can tell on these structures. So at a dwell the choice
among them is not settled by these readings; matrix is the one that also sweeps.
On the held-back structures, of the {{a:pair_hertzforge_n}} paired claims among the Hertzforge laws,
{{a:pair_hertzforge_holds}} hold, {{a:pair_hertzforge_weaker}} hold weaker and
{{a:pair_hertzforge_does_not_hold}} do not hold ({{a:pair_hertzforge_does_not_hold_ids}}).

### 5.4 Safety

@fig-safety gives the worst over-test of every scored run and what the default protections do.

![Safety. (a) The worst over-test of every scored run, by job: boxes are the quartiles, whiskers the 5th and 95th percentiles, and points the runs beyond; the lines are at 3 dB, 6 dB and the widened abort band of {{f:protective_abort_widened_db}} dB. (b) Runs completed on the sample of {{defaults_structures}} structures at the engine's default protective settings (solid) and at the widened settings of record (hatched), by job.](figures/fig4_safety.png){#fig-safety fig-alt="Panel a: box plots of worst over-test in dB, one per job. The dwells of matrix, steepest_descent and secant sit low, with a tail to about {{r0:hertzforge_matrix_T4_largest_db}} dB; ratio's and paired's dwells sit higher. Every sweep and step box lies mostly above 6 dB, with points up to about {{r0:hertzforge_ratio_T4_largest_db}} dB. Panel b: paired bars per job; at the default settings the sweeps and steps complete nothing (the Python ones {{defaults_python_sweep_or_step_completed}} run), the dwells fewer than half of what they complete widened." data="data/law_worst_runs.csv data/law_defaults.csv data/facts.csv"}

With the abort band widened to {{f:protective_abort_widened_db}} dB, a run goes on while its controls
are far off. Of the Hertzforge sweeps and stepped sines,
{{hertzforge_sweep_step_over_6db_pct_of_scored}} percent of those scored put some resonance more than
6 dB over its reference ({{hertzforge_sweep_step_over_6db}} runs,
{{hertzforge_sweep_step_over_6db_pct_of_runs}} percent of all {{hertzforge_sweep_step_runs}}); of the
Python ones, {{python_sweep_step_over_6db_pct_of_scored}} percent of those scored
({{python_sweep_step_over_6db_pct_of_runs}} percent of all): of followed poles,
{{python_followed_poles_sweep_step_over_6db_pct_of_scored}} percent, and of the Python matrix,

{{python_matrix_sweep_step_over_6db_pct_of_scored}} percent. At a dwell, matrix put a resonance more than
6 dB over in {{hertzforge_matrix_T4_over_6db}} of {{hertzforge_matrix_T4_all_runs}} runs
({{hertzforge_matrix_T4_over_6db_pct_of_runs}} percent), steepest_descent in
{{hertzforge_steepest_descent_T4_over_6db}} and secant in {{hertzforge_secant_T4_over_6db}}, ratio in
{{hertzforge_ratio_T4_over_6db}} ({{hertzforge_ratio_T4_over_6db_pct_of_runs}} percent) and paired
in {{hertzforge_paired_T4_over_6db}} ({{hertzforge_paired_T4_over_6db_pct_of_runs}} percent of all
its dwells, {{hertzforge_paired_T4_over_6db_pct_of_scored}} percent of those scored). The largest
single over-tests are {{hertzforge_ratio_T4_largest_db}} dB (ratio, a dwell),
{{hertzforge_ratio_T3_largest_db}} dB (ratio, a stepped sine) and {{hertzforge_matrix_T5_largest_db}} dB
(matrix, a sweep down); the dwells of matrix, steepest_descent and secant reach
{{hertzforge_matrix_T4_largest_db}}, {{hertzforge_steepest_descent_T4_largest_db}} and
{{hertzforge_secant_T4_largest_db}} dB. In a test these would be stopped long before by the default
settings, by the operator or by the article's own limits; they are what the law does when nothing
stops it.

The defaults stop them. On the {{defaults_structures}} structures run both ways, at the engine's
defaults {{defaults_hertzforge_sweep_or_step_completed}} of {{defaults_hertzforge_sweep_or_step_runs}}
Hertzforge sweeps and stepped sines completed, against {{defaults_hertzforge_sweep_or_step_record_completed}}
in the runs of record; {{defaults_hertzforge_dwell_completed}} of {{defaults_hertzforge_dwell_runs}}
dwells, against {{defaults_hertzforge_dwell_record_completed}}; and {{defaults_python_sweep_or_step_completed}}
of {{defaults_python_sweep_or_step_runs}} Python sweeps, against
{{defaults_python_sweep_or_step_record_completed}}. The defaults are conservative by design: the
controller stops when a control is {{f:protective_abort_default_db}} dB off for
{{f:protective_ticks_default}} updates, and the operator looks at the data before going on. On a
structure that changes with level, these laws at these settings will stop a sweep more often than
they finish it, and an operator who widens the settings to finish it should expect the over-tests
above. None of these counts is a claim of the rule. On the held-back structures,
{{a:heldout_hertzforge_sweep_step_over_6db_pct_of_scored}} percent of the scored Hertzforge sweeps and
stepped sines put a resonance more than 6 dB over its reference
({{a:heldout_hertzforge_sweep_step_over_6db_pct_of_runs}} percent of all of them), and
{{a:heldout_hertzforge_matrix_dwell_over_6db_pct_of_runs}} percent of matrix's dwells; these too are run
counts, not claims of the rule.

### 5.5 Followed Poles Against the Python `matrix`

@fig-followed-poles gives followed poles against the Python matrix cell by cell.

![Followed poles against the Python version's matrix, cell by cell: each point is one cell (system and structure kind) on one test, the median over its structures of the reading of followed poles less matrix's; (a) completion, (b) IEC share, both in points of the test, (c) worst over-test in dB. Grey is the linear tier, blue the realistic, orange the strong. A cross marks a cell where the rule makes a claim for followed poles, a filled circle with a black edge one for matrix, an open circle no claim.](figures/fig5_followed_poles.png){#fig-followed-poles fig-alt="Three panels of points over four tests (T1, T2, T5, L1). Panel a: completion differences from {{followed_poles_cells_completion_low}} to {{followed_poles_cells_completion_high}} points, highest on T5 realistic cells. Panel b: IEC share differences mostly above zero, highest on T5 realistic. Panel c: over-test differences mostly below zero, from {{followed_poles_cells_worst_over_db_low}} to {{followed_poles_cells_worst_over_db_high}} dB, with one strong cell of T2 above zero marked as a claim for matrix and two strong cells of T1 further above zero with no claim." data="data/law_followed_poles_cells.csv"}

The followed-poles law completes {{python_followed_poles_T1_all_completed}} of {{python_followed_poles_T1_all_runs}} slow sweeps up against the
Python matrix's {{python_matrix_T1_all_completed}}, {{python_followed_poles_T2_all_completed}} fast sweeps
against {{python_matrix_T2_all_completed}}, and {{python_followed_poles_T5_all_completed}} of
{{python_followed_poles_T5_all_runs}} sweeps down against {{python_matrix_T5_all_completed}}; the median IEC share
of its sweeps down is {{python_followed_poles_T5_all_iec_median_pct}} percent against
{{python_matrix_T5_all_iec_median_pct}} percent. On the realistic tier sweeping down it completes
{{python_followed_poles_T5_realistic_completed}} of {{python_followed_poles_T5_realistic_runs}} against
{{python_matrix_T5_realistic_completed}}; on the strong tier, {{python_followed_poles_T5_strong_completed}} against
{{python_matrix_T5_strong_completed}}. Cell by cell, the rule favours followed poles in the cells
listed below; of the claims the list cites, {{vg:python_T1_matrix_followed_poles_worst_over_db_first_id+python_T1_matrix_followed_poles_completion_first_id+python_T1_matrix_followed_poles_iec_share_first_id+python_T2_matrix_followed_poles_iec_share_first_id+python_T2_matrix_followed_poles_worst_over_db_first_id_against+python_T5_matrix_followed_poles_completion_first_id+python_T5_matrix_followed_poles_iec_share_first_id+python_T5_matrix_followed_poles_worst_over_db_first_id+python_L1_matrix_followed_poles_iec_share_first_id+python_L1_matrix_followed_poles_worst_over_db_first_id}}. The cells:

- on the slow sweep up, on over-test in {{python_T1_matrix_followed_poles_worst_over_db_favour_against}} of
  {{python_T1_matrix_followed_poles_worst_over_db_cells}} cells, by medians of {{followed_poles_T1_worst_over_db_favoured_low}}
  to {{followed_poles_T1_worst_over_db_favoured_high}} dB ({{python_T1_matrix_followed_poles_worst_over_db_first_id}}), and on
  completion and IEC share in one cell each ({{python_T1_matrix_followed_poles_completion_first_id}},
  {{python_T1_matrix_followed_poles_iec_share_first_id}});
- on the fast sweep up, on IEC share in {{python_T2_matrix_followed_poles_iec_share_favour_against}} of
  {{python_T2_matrix_followed_poles_iec_share_cells}} cells, by {{followed_poles_T2_iec_share_favoured_low}} to
  {{followed_poles_T2_iec_share_favoured_high}} points ({{python_T2_matrix_followed_poles_iec_share_first_id}}), and on
  over-test in {{python_T2_matrix_followed_poles_worst_over_db_favour_against}}
  ({{python_T2_matrix_followed_poles_worst_over_db_first_id_against}});
- on the sweep down, on completion in {{python_T5_matrix_followed_poles_completion_favour_against}} of
  {{python_T5_matrix_followed_poles_completion_cells}} cells, by {{followed_poles_T5_completion_favoured_low}} to
  {{followed_poles_T5_completion_favoured_high}} points ({{python_T5_matrix_followed_poles_completion_first_id}}), on IEC
  share in {{python_T5_matrix_followed_poles_iec_share_favour_against}} ({{python_T5_matrix_followed_poles_iec_share_first_id}})
  and on over-test in {{python_T5_matrix_followed_poles_worst_over_db_favour_against}}
  ({{python_T5_matrix_followed_poles_worst_over_db_first_id}});
- on the limit case, on IEC share and over-test in one cell each of {{python_L1_matrix_followed_poles_iec_share_cells}}
  ({{python_L1_matrix_followed_poles_iec_share_first_id}}, {{python_L1_matrix_followed_poles_worst_over_db_first_id}}).

The rule favours matrix once: on the fast sweep up of the strong softening structures of the
6 x 12 system, where the median over-test of followed poles is {{followed_poles_matrix_favoured_T2_worst_over_db_followed_poles_less_matrix_db}}
dB higher ({{followed_poles_matrix_favoured_T2_worst_over_db_id}});
{{vg:followed_poles_matrix_favoured_T2_worst_over_db_id}}. The screen had seen followed poles over-test most on
the same test and tier. The largest cell median against followed poles is on the slow sweep up, on the strong
softening structures of the 6 x 6 system: {{followed_poles_cells_worst_over_db_high}} dB higher than matrix, where the rule
makes no claim. Of the {{followed_poles_favoured_claims_all}} claims that favour followed poles,
{{followed_poles_favoured_claims_linear}} are on the linear tier, where nothing moves: the modal model itself, before anything is followed, holds the controls closer than matrix's
smoothed identification (the median slow-sweep over-test of followed poles on the linear tier is
{{python_followed_poles_T1_linear_worst_median_db}} dB against matrix's {{python_matrix_T1_linear_worst_median_db}}).
This is a reading of @fig-followed-poles, not a claim of the rule.

Two limits bound these results. Followed poles ran on the exact identification, which a test does not have, and
in the Python version only; and it was admitted on the study's structures after a screen on some of
them. On the held-back structures, of the {{a:followed_poles_n}} claims of followed poles,
{{a:followed_poles_holds}} hold, {{a:followed_poles_weaker}} hold weaker and
{{a:followed_poles_does_not_hold}} do not hold: {{a:followed_poles_pair_does_not_hold}} of its
{{a:followed_poles_pair_n}} claims against matrix ({{a:followed_poles_pair_does_not_hold_ids}}) and
{{a:followed_poles_level_does_not_hold}} of its {{a:followed_poles_level_n}} level claims
({{a:followed_poles_level_does_not_hold_ids}}). Of the
{{a:followed_poles_favoured_T1_worst_over_db_n}} claims that favour it on the slow sweep's over-test,
the verdicts are holds for {{a:followed_poles_favoured_T1_worst_over_db_holds}} and weaker for
{{a:followed_poles_favoured_T1_worst_over_db_weaker}}; of the {{a:followed_poles_favoured_T5_completion_n}}
that favour it on the sweep down's completion, holds for {{a:followed_poles_favoured_T5_completion_holds}}
and weaker for {{a:followed_poles_favoured_T5_completion_weaker}}.

### 5.6 Run Again: How Far One Run Moves

The repeats read how much of a difference one run can carry. In the Hertzforge version
{{repeats_hertzforge_outcome_changed}} of {{repeats_hertzforge_repeat_runs}} repeat runs ended
differently from the run of record, and the worst over-test moved by more than the rule's
{{s:threshold_worst_over_db}} dB in {{repeats_hertzforge_worst_over_db_beyond_threshold}} of
{{repeats_hertzforge_worst_over_db_n}} (a median move of {{r2:repeats_hertzforge_worst_over_db_median_abs_change}}
dB, the largest {{r1:repeats_hertzforge_worst_over_db_largest_abs_change}} dB): the engine's own
measured identification and its timing are not the same twice. In the Python version
{{repeats_python_outcome_changed}} of {{repeats_python_repeat_runs}} ended differently and
{{repeats_python_worst_over_db_beyond_threshold}} of {{repeats_python_worst_over_db_n}} moved beyond
the threshold. So a single Hertzforge run's worst over-test moves by more than the threshold about
half the time; the rule's claims stand on the agreement of most paired structures in a cell, not on
any one run. This is not a claim of the rule.

### 5.7 The Audit

The audit ran every job on the {{f:heldout_problems}} held-back problems:
{{a:heldout_runs_hertzforge}} runs in the Hertzforge version and {{a:heldout_runs_python}} in the
Python version. Of the {{a:law_n}} claims about the laws, {{a:law_holds}} hold,
{{a:law_weaker}} hold weaker (the direction held and the size fell outside the study's quartiles) and {{a:law_does_not_hold}} do not hold.
{{a:all_not_tested_text}} By law, the level claims that hold are, in the Hertzforge version,
{{a:job_hertzforge_matrix_holds}} of matrix's {{a:job_hertzforge_matrix_n}} and
{{a:job_hertzforge_paired_holds}} of paired's {{a:job_hertzforge_paired_n}}, neither having a level
claim that does not hold; {{a:job_hertzforge_ratio_holds}} of ratio's {{a:job_hertzforge_ratio_n}},
with {{a:job_hertzforge_ratio_does_not_hold}} that do not hold; {{a:job_hertzforge_steepest_descent_holds}}
of steepest_descent's {{a:job_hertzforge_steepest_descent_n}}, with
{{a:job_hertzforge_steepest_descent_does_not_hold}}; {{a:job_hertzforge_secant_holds}} of secant's
{{a:job_hertzforge_secant_n}}, with {{a:job_hertzforge_secant_does_not_hold}}; and in the Python version
{{a:job_python_matrix_holds}} of matrix's {{a:job_python_matrix_n}}, with
{{a:job_python_matrix_does_not_hold}}, and {{a:job_python_followed_poles_holds}} of the
{{a:job_python_followed_poles_n}} of followed poles, with {{a:job_python_followed_poles_does_not_hold}}.
The rest hold weaker. Every Hertzforge level claim that does not hold is at the dwell; none of the
{{a:sweep_step_hertzforge_n}} on sweeps and stepped sines fails to hold. Of the paired claims, {{a:pair_hertzforge_does_not_hold}} among the Hertzforge laws
and {{a:followed_poles_pair_does_not_hold}} between followed poles and matrix do not hold (Sections
5.3 and 5.5). Where a claim cited above does not hold, or holds weaker, the sentence that cites it says
so. The verdicts are those of the frozen code; Section 7 gives {{a:rounding_n}} that turn on how the
claims file rounds the study's quartiles.

## 6. What Did Not Work

What was tried and set aside is the subject of the companion negative-result article
[@sinedidnotwork2026], which gives each idea's source, what it was told and could measure, its
readings against matrix and followed poles, and why it did not work as built. This section gives the outline.
Except in 6.1, the readings are the screens' (Section 2.7), screen evidence on {{f:screen_structures_nonlinear}}
structures that move, not claims of the rule.

### 6.1 `paired` and `ratio` on the Stepped Sine

paired completes {{steps_paired_all_completed}} of {{steps_paired_all_runs}} stepped sines, and
{{steps_paired_all_aborted_at_m12db}} of them abort on the ladder's first rung; ratio completes
{{steps_ratio_all_completed}}, and {{steps_ratio_all_aborted_at_0db}} of its runs abort at full
level. matrix completes {{steps_matrix_all_completed}}, most of its aborts at full level on the
jointed tiers. At the dwell the same two laws complete more
({{hertzforge_paired_T4_all_completed_pct}} and {{hertzforge_ratio_T4_all_completed_pct}} percent).
As far as is known, paired has no model of the coupling, and on these frames each control is moved
by every shaker, so each pair's correction moves the others; ratio carries the factors learned at
one step to the next, on a structure that has moved between steps. These causes are read from the
agreement runs (Section 3.3) and the laws' design, not tested apart.

### 6.2 The Family Inverse

The inverse on several copies of the model, the moving resonances spread across an expected drop,
as in the MIMO Shock work's protection for square systems [@negative2026]. On its linear control it
completed {{screen_G_family_inverse_vs_matrix_linear_completed}} of {{screen_G_family_inverse_vs_matrix_linear_runs}} runs
where matrix completed {{screen_G_family_inverse_vs_matrix_linear_completed_yardstick}}: a family that expects
every mode to drop is a wrong model where nothing moves.

### 6.3 The Level Ladder, With Followed Poles

Low-level passes before the full-level one, as in the ECSS notching process [@ecss2022], used to
predict each mode at the next level: where the suite's ladder only brings the test up, the level
ladder learns from each pass.
 On rungs of one whole sweep each it completed
{{screen_G_level_ladder_sw_vs_matrix_sw_nonlinear_completed}} of {{f:G_level_ladder_sw_runs_nonlinear}} nonlinear runs,
every one stopping on a pass below full level, where matrix on the same rungs completed
{{screen_G_level_ladder_sw_vs_matrix_sw_nonlinear_completed_yardstick}}. On the suite's short rungs it is the
carried loop on its low-level model, and was worse than matrix sweeping down.

### 6.4 The Dither Identification at the Dwell

Recursive least squares on a dither at the dwell, after helicopter higher-harmonic control [@johnson1982;
@chandrasekar2004]. It tied matrix on completions, ended in tolerance on
{{screen_G_rls_dither_vs_matrix_nonlinear_ends}} nonlinear structures against matrix's
{{screen_G_rls_dither_vs_matrix_nonlinear_ends_yardstick}}, and its worst over-test was higher on
{{screen_G_rls_dither_vs_matrix_nonlinear_over_test_higher_on}} of
{{screen_G_rls_dither_vs_matrix_nonlinear_over_test_n}} paired dwells. matrix already holds these dwells.

### 6.5 The Predictive Leads

Four leads built on followed poles to predict the structure rather than react to it: pole
trajectory, which extrapolates each pole along its rate [@kalman1960; @chatzi2009];
amplitude-indexed poles, a curve in each mode's amplitude [@krack2013; @deaner2015; @roettgen2017;
@lacayo2019; @londono2015]; placed poles, which places modes not yet met before arrival
[@karaagacli2021; @rugh2000]; and preview control, over a horizon [@mayne2000; @tomizuka1987;
@markert2001; @gloth2004]. Against followed poles they met the rule on {{f:J_pole_trajectory_cells_vs_followed_poles}},
{{f:J_amplitude_indexed_cells_vs_followed_poles}}, {{f:J_placed_poles_cells_vs_followed_poles}} and {{f:J_preview_cells_vs_followed_poles}} cells, where it asks
{{f:j_rule_cells}}; placed poles completed the most, {{screen_J_placed_poles_vs_followed_poles_nonlinear_completed}} against
{{screen_J_placed_poles_vs_followed_poles_nonlinear_completed_yardstick}} for followed poles. None was better than followed poles, and Kevin Cross left
all four out ("{{f:leads_quote}}").

### 6.6 Smaller Things That Did Not Work

The engine's measured lag less its pipeline ({{f:lag_less_pipeline_a}} and
{{f:lag_less_pipeline_b}} samples on two structures) is a cross-correlation's peak, not the
identification's pure delay, and a fit with it is worse than one with no delay taken out. The
simulator block's own delay (Section 2.6) gave the fit the screen used; it is the declared delay
the Rust build of followed poles needs. A refined fit, M9d, took {{f:G_m9d_clock_ratio_low}} to
{{f:G_m9d_clock_ratio_high}} times as long to run as followed poles on M7d and was not carried into the study.
The research round's own modal fit misses most of the frames' modes; M7d replaced it.

## 7. What Was Not Tested

- **Followed poles in Hertzforge.** Followed poles has no Rust build; its results are the Python
  version's, on the exact identification. The engine's measured identification, with noise and
  untrusted lines, was not given to it.
- **Hertzforge's control service.** The laws ran in the study's runner on the engine, not in the
  application with its operator settings.
- **Noise.** One sequence of measurement noise at one level.
- **Settings.** Every law ran at its defaults; no law was tuned on the suite. The protective settings
  of record are widened; the defaults were run on {{defaults_structures}} structures only.
- **Hardware.** Simulation only: no converters, amplifiers or shakers.
- **The limit case's notch.** The Python version's notch is a simplification of the engine's, so L1
  is the one test whose two versions were not compared (Section 3.3).
- **Phase.** Read and reported, never judged.
- **Rounding in the audit's test.** The claims file stores the study's quartiles rounded to
  {{a:rounding_places}} decimals, and the frozen code tests the audit's median against those. On
  {{a:rounding_n}} paired claims among the Hertzforge laws at the dwell ({{a:rounding_ids}}) the
  audit's median equals the unrounded study quartile and lies just outside the rounded one, so the
  code reads them as weaker where the rule's words, which name the unrounded quartiles, give holds.
  The counts here are the code's; under the words, {{a:rounding_law_words_holds}} of the law claims
  would hold and {{a:rounding_law_words_weaker}} would be weaker.
- **The predictive leads' variants.** Placement on plain followed poles and the reasons for the start
  error of preview control were not run.

## Data Availability

The problems are the MIMO Sine suite, draft 0.1 [@sinesuite2026], and the study's run records, the
claims and the screens' records are the benchmark's results record [@sineresults2026]; both are
published as data sets, the suite with DOI 10.5281/zenodo.24594791 and the results record with DOI
10.5281/zenodo.24594793. The data behind every figure and every number in
this article, and the code that computes and draws them, are with the article in `data/` and `code/`:
the code under the MIT license and the data under CC BY 4.0. `data/number_sources.csv` names the file
each number in the text was read from.

## Contribution Statement

Kevin Cross is the sole author. He chose the laws and the candidates, directed their design and
implementation, the screens, the study and its audit, and their analysis, and made the decisions to
admit followed poles and to leave the other candidates out.

## How This Was Made

The text, the figures, the code that draws them, the laws' Rust and Python code, the candidates, and
the study's runner and analysis scripts were written with Claude Code, an AI coding assistant running
Anthropic's Claude Opus models, under Kevin Cross's direction. The author is responsible for every
word, number and line of code.

## Acknowledgments

The laws rest on the published work of others, credited by name. The correction through a fixed
inverse is published by H. Qiu, Y. Feng, S. Fan, X. Du and W. Zhang, and by Zhang, Wang and Zeng;
the amplitude-ratio law by Zhang, Chen and He; the steepest-descent law by U. Musella, S. Waimer,
B. Peeters, F. Marulo, P. Guillaume and co-authors; the adaptive secant law with a complex gain by
M. A. Underwood in US Patent 5,299,459. The modal fit under followed poles uses the PolyMAX and pLSCF work of
B. Peeters, H. Van der Auweraer, P. Guillaume, J. Leuridan and co-authors, the formulation of
M. T. Steffensen, M. Döhler, D. Tcherniak and J. J. Thomsen, and the study of the parameter constraint
by B. Cauberghe and co-authors. The dither identification follows the higher-harmonic control of W. Johnson of NASA and of
J. Chandrasekar, L. Liu, D. Patt, P. P. Friedmann and D. S. Bernstein. The predictive leads draw on
the work cited in Section 6.5. The tolerances are those of IEC 60068-2-6 and of MIL-STD-810H Method
514.8, a standard of the U.S. Department of Defense, and the level ladder follows the ladder of
passes of the ECSS testing handbook.
 The computations use NumPy [@harris2020] and the figures
Matplotlib [@hunter2007].

## References

## Implemented In

The five laws' mathematics is in Hertzforge, https://github.com/Hertzforge/Hertzforge, crate
`crates/hertzforge-mimo-sine-law-math` (`src/matrix.rs`, `paired.rs`, `ratio.rs`, `steepest.rs`,
`secant.rs`), made selectable by `crates/hertzforge-mimo-sine-laws` and run by the engine
`crates/hertzforge-mimo-sine`, on the main branch at `{{f:main_commit}}`. The study ran commit
`{{f:run_commit}}` on a research branch that leaves main at `{{f:run_base}}`; the three crates are
the same at the study's commit and on main ({{f:law_crate_files_changed}} files differ). The study's runner,
`crates/sds-control/examples/msnb_run` on that branch, is not on main. Every Hertzforge run file names
the runner by its SHA-256, `{{f:runner_sha256_hertzforge}}`. The Python version, the Python ports, followed
poles (`FollowedPoles`) and the M7d fit
 are in the suite's code (`sine/pyloop/`) [@sinesuite2026]; every
Python run file names its harness by SHA-256, `{{f:runner_sha256_python}}`.
