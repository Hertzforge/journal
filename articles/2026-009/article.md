---
# Filled in by the editors at publication.
id: "2026-009"
version: 1
date: 2026-11-17
doi: "10.5281/zenodo.24311107"
doi_latest: "10.5281/zenodo.24311106"
note: First published.

# Filled in by the authors.
title: "Six Control Laws for Multi-Shaker Random Vibration: How Each Scores on the Open Benchmark Set"
type: Research Article
evidence: simulator
evidence_note: "Closed-loop runs of the six laws through Hertzforge's control service on its simulator, on the Open Benchmark Set's MIMO Random suite (version 0.2): 20 generated structures, five systems, stage 1 and stage 2 at two sizes, one run per case, each finding tested again on ten held-back structures by an independent audit. The laws themselves are described in a companion article."
authors:
  - name: "Kevin Cross"
    orcid: "https://orcid.org/0009-0002-6608-9426"
    roles: ["Conceptualization", "Methodology", "Software", "Validation", "Formal analysis", "Investigation", "Writing: original draft", "Writing: review and editing"]
implemented_in: ""
benchmarks: "Hertzforge Open Benchmark Set: MIMO Random Suite, version 0.2 (DOI 10.5281/zenodo.24310742), Frames tier: problems frame-12x3, frame-12x6, frame-24x12, frame-6x6 and frame-12x12, line and banded targets, linear, realistic and strong, seeds 0 to 9, 12 to 15, 17, 19 and 32 to 35"
abstract: >
  Hertzforge, an open-source structural dynamics suite, ships six control laws for multi-shaker
  random vibration tests, described in a companion article. This article reports how each one
  scores on the Open Benchmark Set, closed loop through the real control service on its simulator,
  at its defaults and at one tuned setting, on structures that do not change with level (stage 1)
  and on the same structures with modes that soften and modes that harden with level (stage 2), on
  five systems and 20 generated structures, with each finding tested again by an independent audit
  on ten held-back structures. At the controller's default checks, which are conservative on
  purpose, about nine runs in ten stopped early and completed once the checks were widened; the
  scores are of the widened runs. With as many shakers as control gauges, the two pseudo-inverse
  laws and the buzz-test law held their control gauges closely and over-tested the article's stress
  by about 8 to 11 dB more than the band-average law, on every structure of both sets, and a
  stronger regularization chosen on structures not scored lowered the pseudo-inverse laws' stress
  error there on every structure. At the strong size of stage 2 the stress error rose for five of
  the six laws on both sets of structures; the rise came with the softening joints, while the
  hardening member alone moved no law's median by more than 0.2 dB with more control gauges than
  shakers. Everything here is simulation.
---

## Summary

A random vibration test on one shaker has one control signal, which may be one accelerometer or a
combination of several, and one target. With several shakers on one article, each shaker's drive
affects every accelerometer, and the target says not only how strong the vibration is at each
accelerometer but how the motion at one point is related to the motion at another. The rule that
decides the drives is the control law. Hertzforge ships six; a companion article describes each
one, its equations, settings and sources [@primer2026].

This article reports how each law scores on the Open Benchmark Set: simulated test problems with a
target, the limits of a fair run and a fixed scorecard [@obs2026]. Each law runs closed loop through
Hertzforge's real control service on its simulator, at its defaults and at one tuned setting, on
structures that do not change with level and on the same structures with modes that soften and
modes that harden as the level rises. Each result is stated against the lines of the scorecard; no
law is graded as a whole. The study ran 2,880 cases on 20 generated structures and five systems,
and an independent audit tested each finding on ten structures held back until the findings were
written. What both found, law by law, is in Section 3.

- **The controller's default checks are conservative on purpose.** At those defaults 901 of 990 runs
  on the study's structures stopped, and 811 of 870 on the held-back ones, most at the seventh loop,
  the first at full level. Once the checks were widened, all 901 completed, and 810 of the 811. That
  is a fact about the defaults, which the test engineer may widen for their own system, not about the
  laws.
- **With as many shakers as control gauges, holding the control gauges is not holding the stress.**
  The two pseudo-inverse laws and the buzz-test law met their control gauges within about 4 dB and
  over-tested the article's stress by a median 9 to 11 dB more than the band-average law on all 20
  study structures, and by 7.7 to 9.1 dB on all ten held-back ones. The band-average law runs on a
  banded target and the others on the full line target, so each comparison is of a law with its own
  target.
- **Tuning.** A regularization amount of 0.1, chosen on two structures that were not scored, lowered
  the stress error of the two pseudo-inverse laws on those systems on every structure of both sets,
  by a median 6.4 and 11.6 dB on the study's linear structures and 6.3 and 9.1 dB on the held-back
  ones. Elsewhere tuning changed little; one change seen on the study's structures was not borne out
  on the held-back ones.
- **Structures that change with level.** At the realistic size the stress errors barely moved. At the
  strong size they rose for five of the six laws, by a median 0.8 to 1.9 dB on the study's structures
  (0.8 to 1.6 dB on the held-back ones) with more control gauges than shakers, and by up to 5.8 dB
  (4.4 dB) with as many shakers as control gauges. The rise came with the softening joints; the
  hardening member alone, though it hardened as designed, moved no law's median by more than 0.2 dB
  with more control gauges than shakers, and its larger moves on the system with six shakers and six
  control gauges did not repeat from one set of structures to the other.

## 1. The Six Laws

The terms are those of the first article in this journal [@cross2026]. The accelerometers the
controller reads and brings to their targets are the **control gauges**. A **held-out gauge** is
recorded but never shown to the controller; it is used only to judge the test. A **system** is the
article on its shakers with its gauges, as the controller sees it; the first article calls it the
rig. A system is written shakers by control gauges: a 6 x 12 system has six shakers and twelve
control gauges, and a **square system** has as many shakers as control gauges. The controller works
line by line on a grid of narrow frequency slices, and what it knows of the system is the
**measured frequency response**: on each line, the acceleration at each control gauge per volt of
drive at each shaker, measured at the start of the run, about 20 dB under the target, and by default
kept for the whole run. The target at the control gauges is a spectrum for each gauge and, for each
pair, a cross spectrum that carries their coherence and phase. @tbl-laws lists the six laws; the
companion article gives each one in full [@primer2026].

```{=typst}
#block(breakable: false, width: 100%)[
```

| Law | Code name | What it does | Source | Primer |
|:---|:---|:---|:---|:---|
| Pseudo-inverse, closed loop (the default) | `pinv_closed` | Inverts the measured frequency response, regularized, and corrects the drive every loop from the measured response | Smallwood [@smallwood1999]; regularization after Schultz [@schultz2018] | 2.2 |
| Pseudo-inverse, open loop | `pinv_open` | Plays the same inverse every loop with no correction | The same | 2.3 |
| Shape-constrained | `shape_svd` | Drives, on each line, only the patterns of shaker drive the system responds to most | Schultz and Avitabile [@schultz2019; @schultz2020] | 2.4 |
| Buzz-test matched | `buzz_match` | Keeps the target's spectra and takes the coherence and phase between gauges from the article's own response to uncorrelated drive | Daborn [@daborn2014], as stated by Schultz [@schultz2018] | 2.5 |
| Minimum drive | `min_drive` | Chooses the coherence and phase between gauges that need the least drive to meet the spectra | Coletti, Davis and Schultz [@coletti2026]; Smallwood [@smallwood2007; @smallwood2013] | 2.6 |
| Band average | `band_average` | Fits one drive matrix per one-sixth-octave band so that band averages, not single lines, match the target | Brandon Zwink | 2.7 |

: The six control laws Hertzforge ships for multi-shaker random vibration, the published source of each as the companion article credits it, and the section of the companion article that describes each ("Primer") [@primer2026]. {#tbl-laws tbl-colwidths="[16,19,37,22,6]"}

```{=typst}
]
```

**The closed loop four of them share.** `pinv_closed`, `shape_svd`, `buzz_match` and `min_drive`
run the same correction and differ in the target and the directions they feed it. Following
Smallwood [@smallwood1999], the loop never corrects the drive matrix directly, which could ask for
negative power: it splits the target into a triangular factor, keeps a running copy of that factor,
corrects the copy from the error each loop with a convergence factor of 0.5, and forms the drive from
the copy in a way that cannot ask for negative power. Where the system has fewer independent
directions than control gauges, the loop settles at the response closest to the target that the
system can produce. Its safeguards and its known limits are in the companion article's Sections 2.1
and 6 [@primer2026].

**The controller's protective checks.** Whatever law runs, the controller checks every drive the law
returns, holds each drive's change to +3.5 dB and -6 dB a loop (the change cap), holds each drive
under its voltage ceiling, and can end a run (Section 3 of the companion article [@primer2026]).
Three checks matter here. The **growing-error check**, on which most runs at the defaults ended, is
given in full in Section 3.1. The **drive-change check** aborts a run when the change cap has held a
drive back on 10 or more lines in 5 of the last 10 drives the law produced and the controller
accepted. The **drive-voltage abort** is the drive ceiling plus 1 dB: with the problems' ceiling of
5.0 V RMS, 5.61 V RMS. It is a rule of the controller applied to the problem's ceiling, not a
separate setting. A run climbs to full level in steps: by default a soft start, then -12, -9, -6 and
-3 dB, one loop each, then full level; in the study's runs the first loop at full level is loop 7.

## 2. The Study

**The runs.** Each law runs closed loop through Hertzforge's real multiple-shaker random control
service, the same code that runs a test, on the software's simulator. Nothing in the loop is
re-implemented for the study: identification, the estimates, the level steps, the law calls, the
checks, the caps and the protections are the service's own. A tap on the simulator records the
response at every gauge, held-out gauges included, as the simulator played it. Where an
identification gate fails, the run goes on and the failure is recorded, because the gate is a property
of the system and not of the law. The laws and the simulator are those of Hertzforge's main branch at
commit `b587d5a1`. The runs were made by two programs written for the study, a runner that runs one
case through the control service and a player that plays a structure's response on the simulator,
built on top of that commit at commit `646c4ca4`; nothing in the laws or the simulator differs
between the two. The same programs are the examples `x4_runner` and `obs_play` of the crate
`sds-control` in the Hertzforge repository, main branch at commit 268c3bfd, where six
cases rerun gave scorecards equal in every number to the study's. The band-average law was run as shipped at
commit `b587d5a1`, and its author took no part in designing, running or analyzing the study.

**The problems.** The problems are the MIMO Random suite of the Open Benchmark Set, version 0.2,
Frames tier, in problem format 0.2-draft, under the fair-run limits `frames-fair-run/0.1-draft`
[@obsdata2026]; the scorecards record the set's version by its draft name, 0.2-draft. The benchmark
article describes the problems in full [@obs2026].
In short: one frame article with jointed parts whose modes soften as the level rises and one member,
a mass on two thin strips clamped at both ends, whose mode hardens. Stage 1 is the article with both
effects switched off, so it does not change with level. Stage 2 is the same article with both effects
on, at a realistic and at a strong size of change. The article on the shakers is a second unit of the
same design as the one measured in service, and the target is the service response of the first unit
at the control gauges.

The study uses five systems: three with more control gauges than shakers (3 x 12, 6 x 12 and
12 x 24) and two square systems (6 x 6 and 12 x 12). The benchmark's problem identifiers write control
gauges first, so the 6 x 12 system is problem `frame-12x6`. The two classes are never pooled. No
system with fewer control gauges than shakers is in this version of the suite.

**The structures.** Each structure is generated from a whole number, its seed, which is its label in
the data set; structure 4 is the one generated from seed 4. A seed is not a level. The study uses 20
structures: 0 to 9, 12 to 15, 17, 19, and 32 to 35, which replace 10, 11, 16 and 18, on which the
hardening member cannot be placed (the benchmark's rule). Structures 30 and 31 are used only to
choose the tuned settings and are never scored.

**The cases.** Every case is one law on one structure, system and stage, run once (@tbl-cases).

```{=typst}
#block(breakable: false, width: 100%)[
```

| Runs | Structures | Systems | Stages | Cases |
|:---|:---|:---|:---|---:|
| Each law at its defaults, the frequency response measured once and kept | 20 | all five | linear, realistic, strong | 1,800 |
| The same, with only the softening joints or only the hardening member active | first 10 | 6 x 12, 6 x 6 | both sizes | 480 |
| Each law with the frequency response measured again during the run | first 10 | 6 x 12, 6 x 6 | realistic, strong | 240 |
| Each law at its one tuned setting | first 10 | 6 x 12, 6 x 6 | linear, realistic, strong | 360 |
| All | | | | 2,880 |

: The study's cases. "First 10" is structures 0 to 9. Each case is run once, with one sequence of simulator noise fixed by its name, so the run at default checks and the run with the checks widened play the same simulator noise. {#tbl-cases tbl-colwidths="[44,11,16,19,10]"}

```{=typst}
]
```

With the frequency response measured again, the update is blended half and half with the
identification's every loop; `band_average` also has its own update (`use_tf_update`) switched on.
Each law keeps its own target, as a test would: `band_average` runs on the banded specification
(one-third-octave values at each control gauge, with no cross terms), which is its native form, and
the five line-by-line laws run on the full line target, a full spectral matrix with its cross
spectra. A comparison of `band_average` with another law is therefore a comparison of two laws each
with its own target.

**The checks.** On structures 0 to 4, every case is first run with the controller's checks at their
defaults (Section 1) and no alarm or abort lines, since the target cannot be reached exactly and the
benchmark scores tolerance on the scorecard, not at run time. Where that run stops, the case is run
again with the checks widened so the run completes, with the same noise. On the other structures
only the widened run is made. Widened means: the growing-error floor raised to 1,000 dB, so that check
never acts; no limit on the lines outside the abort lines or on the lines the change cap holds back;
and the overload indicator at the full input range. The drive-voltage abort, the drive ceiling of
5.0 V RMS and the change cap itself stay at their defaults. The result of a case is its widened run
where it completed, else its completed run at default checks. A stopped run is not a result.

**The tuned settings.** Each law has one tuned setting for each class of system, chosen before any
study structure was scored, on structures 30 and 31 only, systems 6 x 12 and 6 x 6, the linear and
strong stages, from a grid of points per law with the defaults among them (336 runs, checks widened).
The rule was fixed in code before those runs: the lowest mean error at the held-out gauges over the
four tuning cases, and among the points within 0.10 dB of it, the one with the smallest mean level
error. The stress, which a laboratory cannot measure, is never read. @tbl-tuned gives the choice; the
tuning runs themselves are not part of the published records. The tuned settings
were chosen on a build whose control-law, simulator and controller code is identical to the study's.

```{=typst}
#block(breakable: false, width: 100%)[
```

| Law | More control gauges | Square |
|:---|:---|:---|
| `pinv_closed` | truncated, amount 0.1 | Tikhonov, amount 0.1 |
| `pinv_open` | Tikhonov, amount 0.01 | truncated, amount 0.1 |
| `shape_svd` | ratio 0.1 | ratio 0.1 |
| `buzz_match` | coherence floor 0.2 | coherence floor 0 |
| `min_drive` | fixed trade-off 10⁻⁴ | fixed trade-off 0.1 |
| `band_average` | its defaults | its defaults |

: The tuned setting of each law, by class of system: the systems with more control gauges than shakers, and the square systems. Every other setting is the law's default. The rule picked the defaults for `band_average` on both classes. {#tbl-tuned tbl-colwidths="[22,39,39]"}

```{=typst}
]
```

**Scores.** Each run is scored by the benchmark's scorer, version 0.2.1-draft (SHA-256
`a06e6beb...`), which reads the problem and the run's records and writes a fixed scorecard
[@obs2026]. This article uses six of its lines, each in decibels:

- **Control gauges:** the RMS, over the control gauges and the one-third-octave bands, of the error
  of each gauge's band against the target's. Every law is scored against the same target.
- **Held-out gauges:** the same at the held-out gauges, against their response in service.
- **Level:** the mean of those band errors over the control and held-out gauges; positive is a test
  too strong.
- **Worst over-test:** the largest of them.
- **Stress error:** for every element of the article, its RMS stress on the shakers against its RMS
  stress in service, in decibels; the stress error is the RMS of those errors over the elements.
  0 dB is a perfect match, and lower is closer.
- **Stress bias:** the mean of the same errors; positive is stress too high.

**How results are given.** A structure's value is the mean over the systems of the class; the median
and quartiles are over structures; counts are of structures on which a difference passes 0.2 dB
either way. A difference under 0.2 dB is not claimed: the simulator's equalized step alone leaves
about 0.13 dB at the 95th percentile. A change from the linear structure to stage 2 is taken on the
same structure, system and law. Each table and figure of Section 3 is written by
`code/study_results.py` from the scorecards, which are published with the audit's record as the
results of the study and its audit [@results2026].

**The audit.** The study's findings were tested on ten structures held back from everyone until the
findings were written down: 20 to 23 and 26 to 28, with 50 and 51 replacing 25 and 29 (the hardening
member could not be placed) and 52 replacing 24. At the strong size one mode of structure 24 could
rise past the simulator's highest frequency, so the simulator refused it; its completed runs count
in no verdict. A separate agent, which built none of the study, generated and checked those
structures with the set's own code and ran them through the study's own runner, build and scorer:
each law at its defaults and at its tuned setting, and the runs with one effect only; it did not run
the frequency response measured again or the same case at both check settings. For each finding it
fixed its test before the held-back structures were run. A finding **holds** where the held-back
median has the same sign and lies inside the study's quartiles; where it has the same sign and lies
outside, this article says whether it came out larger or smaller. The audit's record, its held-back
problems and its scorecards are part of the results record [@results2026]. The held-back numbers
below are the audit's, from the same scorecard lines.

## 3. Results

Every number in this section is from the study's 20 structures, or the first ten where the runs
were made on ten, with the checks widened unless it says otherwise; the held-back structures' numbers
are given beside them.

### 3.1 Default Checks

The controller's checks are protective, and their defaults are conservative on purpose: they protect
the shakers, the amplifiers and the article. Widening them for a real test is the test engineer's
decision for that test's hardware. The study widened them because a simulator has no hardware to
protect. A run that a default check stopped is a fact about the default, not a failure of the law,
and this article recommends no new default.

The check that stopped most runs is the growing-error check (`check_divergence` in the control
service, commit `646c4ca4`). It ends a run when one control gauge's error, against what the system
can reach, stays at or above 3 dB without improving on its best by 0.1 dB for five judged loops. It
counts the loops of the level steps as well as the loops at full level. The error at the low steps of
these problems is above 3 dB, so the count reaches five at the first loop at full level, loop 7, where
the error was near 4 dB.

On structures 0 to 4, 990 runs were made at default checks and 901 stopped: 840 on the growing-error
check and 61 on the drive-change check. Every stop came at full level: most at the seventh loop (719),
864 by loop 12, a few as late as the 34th. All 901 cases completed once the checks were widened. The
12 cases that completed at default checks and were also run widened gave identical scorecards; the
audit did not run such pairs. On the held-back structures the same held: 811 of 870 runs stopped
(792 on the growing-error check, 19 on the drive-change check), 654 at the seventh loop, 785 by loop
12, a few as late as the 35th, and 810 of the 811 completed once widened. @tbl-outcomes gives the
study's counts by law.

```{=typst}
#block(breakable: false, width: 100%)[
```

| Law | Settings | Runs | Completed | Growing error | Drive change |
|:---|:---|---:|---:|---:|---:|
| `pinv_closed` | defaults | 115 | 28 | 87 | 0 |
| `pinv_open` | defaults | 115 | 37 | 78 | 0 |
| `shape_svd` | defaults | 115 | 0 | 115 | 0 |
| `buzz_match` | defaults | 115 | 6 | 109 | 0 |
| `min_drive` | defaults | 115 | 8 | 95 | 12 |
| `band_average` | defaults | 115 | 0 | 110 | 5 |
| All six | tuned | 180 | 9 | 171 | 0 |
| All six | measured again | 120 | 1 | 75 | 44 |

: Runs at the controller's default checks, the study's structures 0 to 4: the runs, those completed, those stopped for a growing error and those stopped for a drive change. "Measured again" is the frequency response measured again during the run. Data: `data/study_outcomes.csv`; the held-back structures' counts are in `data/audit_outcomes.csv`. {#tbl-outcomes tbl-colwidths="[22,20,11,15,16,16]"}

```{=typst}
]
```

With the checks widened, 2,800 of 2,803 runs completed. The other three, and one of the 1,681
widened runs on the held-back structures (structure 23, linear), reached the drive-voltage abort of
5.61 V RMS, which the study did not widen. All four are `min_drive` at its defaults on the 3 x 12
system: the study's structures 7 (linear and realistic) and 35 (linear). These cases have no result.
They are the extreme of what `min_drive` does on that system at its default settings: on the linear
structure its control gauges read low (level -11.00 dB on the study's structures, -13.32 on the
held-back ones) while the stress reads high (stress bias +19.27 and +17.49 dB), because it puts its
drive into narrow lines that over-stress the article while the band averages at the gauges stay
under the target, as the audit's record describes [@results2026].

### 3.2 Scores by Stage

@tbl-stage1 and @tbl-stage1-stress give each law's scorecard on the linear structure, and @fig-stress each law's stress
error at every stage. The values at stage 2 on every line are in `data/study_scores.csv`, and the
held-back structures' in `data/audit_scores.csv`.

```{=typst}
#block(breakable: false, width: 100%)[
```

| Law | Systems | Control | Held-out | Level | Over-test |
|:---|:---|---:|---:|---:|---:|
| `pinv_closed` | more control gauges | 6.58 | 6.44 | -0.25 | 22.9 |
| `pinv_open` | more control gauges | 5.93 | 5.99 | -0.95 | 21.8 |
| `shape_svd` | more control gauges | 7.13 | 6.87 | -2.07 | 20.9 |
| `buzz_match` | more control gauges | 6.04 | 6.28 | +0.35 | 23.0 |
| `min_drive` | more control gauges | 10.43 | 11.46 | -3.60 | 28.2 |
| `band_average` | more control gauges | 4.69 | 5.35 | -0.64 | 19.4 |
| `pinv_closed` | square | 3.92 | 10.73 | +4.24 | 37.0 |
| `pinv_open` | square | 4.53 | 11.55 | +5.42 | 38.8 |
| `shape_svd` | square | 6.03 | 6.47 | -0.73 | 23.1 |
| `buzz_match` | square | 3.96 | 10.77 | +4.25 | 37.3 |
| `min_drive` | square | 3.37 | 7.76 | +1.86 | 29.2 |
| `band_average` | square | 2.12 | 5.53 | +0.52 | 22.5 |

: Each law at its defaults on the linear structure (stage 1), the study's 20 structures: the gauge lines of the scorecard, medians over structures, in dB. The columns are the error at the control gauges and at the held-out gauges, the level, and the worst over-test. "More control gauges" is the 3 x 12, 6 x 12 and 12 x 24 systems; "square" is the 6 x 6 and 12 x 12 systems. Every law is scored against the same target; `band_average` runs on its banded form, the others on the line target. Data: `data/study_scores.csv`. {#tbl-stage1 tbl-colwidths="[19,25,14,14,14,14]"}

```{=typst}
]
```

```{=typst}
#block(breakable: false, width: 100%)[
```

| Law | Error, more | Bias, more | Error, square | Bias, square |
|:---|---:|---:|---:|---:|
| `pinv_closed` | 3.69 [3.25, 4.41] | -0.34 | 11.68 [11.02, 12.99] | +11.08 |
| `pinv_open` | 3.39 [3.08, 3.90] | -0.64 | 14.29 [12.55, 15.90] | +13.15 |
| `shape_svd` | 4.45 [3.74, 5.03] | -2.92 | 3.55 [2.94, 4.13] | -1.84 |
| `buzz_match` | 3.15 [2.99, 3.69] | -0.02 | 11.71 [10.79, 13.44] | +10.94 |
| `min_drive` | 8.44 [7.13, 9.63] | +5.99 | 6.01 [5.10, 7.84] | +4.37 |
| `band_average` | 3.29 [2.93, 3.60] | -1.94 | 2.87 [2.65, 3.58] | -0.12 |

: The stress of the same runs as @tbl-stage1: the stress error, median over structures with its quartiles in brackets, and the stress bias, in dB, on the systems with more control gauges than shakers ("more") and on the square systems. Data: `data/study_scores.csv`. {#tbl-stage1-stress tbl-colwidths="[19,25,16,24,16]"}

```{=typst}
]
```

![Each law's stress error at its defaults on the linear structure (filled circles, solid bars) and at stage 2 at the realistic size (open squares, dashed bars) and the strong size (open triangles, dotted bars), by class of system. Median over the study's 20 structures; the bars span the quartiles. Lower is closer to the stress in service.](figures/fig1_stress_by_law.png){#fig-stress fig-alt="Two panels, one per class of system, each with the six laws along the horizontal axis and the stress error in dB from 2 to 16 on the vertical axis. Each law has three markers: a filled blue circle with a solid bar for the linear structure, an open green square with a dashed bar for the realistic size, an open orange triangle with a dotted bar for the strong size. Left, more control gauges than shakers: pinv_closed, pinv_open, shape_svd, buzz_match and band_average lie between about 3 and 5.3 dB at every stage; min_drive sits near 8.4, 8.5 and 10 dB. The strong-size triangles of pinv_closed, pinv_open, buzz_match and band_average are above their circles; shape_svd's is below. Right, square systems: pinv_closed, pinv_open and buzz_match lie between about 10 and 15 dB; min_drive at 6, 7.7 and 12 dB; shape_svd and band_average between about 2.9 and 5.8 dB, band_average's strong-size triangle at 5.8 the highest of its three." data="data/study_scores.csv"}

**On the square systems,** the two pseudo-inverse laws and `buzz_match` hold their control gauges
closely (3.9 to 4.5 dB) and over-test the article's stress. Against `band_average`, structure by
structure, their stress error is higher by a median 9.25 dB (`pinv_closed`), 11.21 dB (`pinv_open`)
and 9.23 dB (`buzz_match`) on all 20 study structures each, with stress bias +10.9 to +13.2 dB; the
same holds on the 6 x 6 and the 12 x 12 system alone, and without the flagged structures. On the ten
held-back structures it holds for `pinv_closed` (7.71 dB) and `buzz_match` (8.17 dB), on all ten
each; for `pinv_open` it has the same sign on all ten and is smaller, 9.07 dB against 11.21. The
comparison is of the band-average law on its banded target with the three others on the line target.
The follow-up article reads the same runs by how the control problem is set up, the number of
shakers and control gauges and which gauges warn of the over-test [@followup2026].

`band_average` and `shape_svd` give the lowest stress error on the square systems at every stage of
the study: 2.87 and 3.55 dB on the linear structure. On the linear structure `band_average` is lower
than `shape_svd` by a median 0.70 dB on the study's structures (17 of 20) and 0.49 dB on the held-back
ones (6 of 10), which holds. At the realistic size it is lower by 0.49 dB on the study's structures
(14 of 20) and by a larger 0.93 dB on the held-back ones (8 of 10). At the strong size no order
between them is stated: `shape_svd` was lower by a median 0.73 dB on the study's structures (13 of 20,
4 the other way) and by 0.26 dB on the held-back ones, which split five and five.

**On the systems with more control gauges than shakers,** five laws sit between 3.15 and 4.45 dB on
the linear structure. `band_average` is lower than `pinv_closed` by a median 0.56 dB (lower on 13 of
20 study structures, higher on 2) and lower than `shape_svd` by 0.97 dB (19 of 20); on the held-back
structures by 0.82 dB (8 of 10) and 1.42 dB (10 of 10), and both hold. `band_average` and `buzz_match`
differ by a median 0.05 dB (8 study structures one way, 7 the other), and no difference between them
is claimed. `min_drive`'s stress error in this class, 8.44 dB, is carried by the 3 x 12 system, where
its median is 19.94 dB (19.54 on the held-back structures); on the 6 x 12 and 12 x 24 systems its
medians are 3.26 and 2.57 dB, among the others.

What each law did, line by line, on the study's linear structures:

- **`pinv_closed`** held its control gauges to 6.58 dB on the systems with more control gauges, with
  stress near unbiased (-0.34 dB); on the square systems it held them to 3.92 dB while the held-out
  gauges read 10.73 dB and the stress was over by +11.08 dB.
- **`pinv_open`** came within about 0.6 dB of `pinv_closed` on every line on the first class (stress
  error 3.39 against 3.69 dB on the study's structures, 3.84 against 4.03 on the held-back ones); on
  the square systems its level was +5.42 dB and its stress bias +13.15 dB, and its stress error was
  14.29 dB against `pinv_closed`'s 11.68 on the study's structures, but 12.32 against 12.15 on the
  held-back ones, a difference under 0.2 dB, which is not claimed.
- **`shape_svd`** ran under the target on both classes (level -2.07 and -0.73 dB), with stress errors
  of 4.45 and 3.55 dB and the stress under rather than over (bias -2.92 and -1.84 dB).
- **`buzz_match`** had a stress error of 3.15 dB and a bias of -0.02 dB on the first class; on the
  square systems it held its control gauges to 3.96 dB with the held-out gauges at 10.77 dB and the
  stress over by +10.94 dB.
- **`min_drive`** ran under the target on the first class (level -3.60 dB) with the stress over
  (+5.99 dB), carried by the 3 x 12 system; on the square systems, its stress bias was +4.37 dB.
- **`band_average`**, on its banded target, held its control gauges to 4.69 and 2.12 dB and its
  held-out gauges to 5.35 and 5.53 dB, with worst over-tests of 19.4 and 22.5 dB and stress errors of
  3.29 and 2.87 dB.

### 3.3 Tuning

Each law's tuned setting against its defaults, on the same case, structures 0 to 9, systems 6 x 12
and 6 x 6 (@tbl-tuned-change).

```{=typst}
#block(breakable: false, width: 100%)[
```

| Law | 6 x 12, linear | 6 x 12, strong | 6 x 6, linear | 6 x 6, realistic | 6 x 6, strong |
|:---|---:|---:|---:|---:|---:|
| `pinv_closed` | +0.15 | -0.90 (8 down) | -6.39 (10 down) | -3.65 (10 down) | -3.11 (10 down) |
| `pinv_open` | +0.01 | -0.06 | -11.57 (10 down) | -9.54 (10 down) | -8.88 (10 down) |
| `shape_svd` | -0.53 (10 down) | +0.86 (8 up) | -0.00 | -0.12 | +1.03 (8 up) |
| `buzz_match` | +0.04 | -0.00 | -0.04 | +0.28 | -0.09 |
| `min_drive` | -0.01 | +0.06 | -0.72 | -0.54 | -0.46 |
| `band_average` | -0.00 | +0.03 | +0.00 | -0.00 | +0.05 |

: Change in the stress error from each law's defaults to its tuned setting, same case, median over the study's 10 structures, dB. Negative is closer to the stress in service. The count is of structures moving more than 0.2 dB that way, where it is 8 or more. Data: `data/study_change_tuned.csv`; the held-back structures' in `data/audit_change_tuned.csv`. {#tbl-tuned-change tbl-colwidths="[18,17,15,17,17,16]"}

```{=typst}
]
```

On the square systems, the tuned settings of `pinv_closed` and `pinv_open`, a regularization amount
of 0.1, lowered the stress error on every one of the ten study structures at every stage, and on
every one of the ten held-back structures. For `pinv_closed` the medians were 6.39, 3.65 and 3.11 dB
(linear, realistic, strong) on the study's structures and 6.30, 4.71 and 4.09 on the held-back ones,
larger at the strong size. For `pinv_open` they were 11.57, 9.54 and 8.88 dB, and 9.09, 10.24 and
8.26, smaller on the linear structure. The held-out gauges moved the same way, by 3.05 and 5.03 dB on
the study's linear structures. On the 6 x 12 system `shape_svd`'s tuned ratio of 0.1 lowered the
stress error on the linear structure by 0.53 dB (all 10 study structures) and by a larger 0.88 dB on
the held-back ones (all 10), and `pinv_closed`'s tuned setting lowered the strong size by 0.90 dB on
both sets (8 and 9 of 10). On the study's structures `shape_svd`'s tuned setting raised the 6 x 12
system's strong size by 0.86 dB (8 of 10); the held-back structures did not bear that out (-0.26 dB,
3 of 10 up), and it is not a finding. For `band_average`, whose tuned setting is its defaults,
`buzz_match`, and `pinv_open` on the 6 x 12 system, the median change on the study's structures is
under 0.2 dB.

### 3.4 Level-Dependent Structures

This section gives the change in each law's scores from the linear structure to stage 2, on the same
structure, system and law. The benchmark article gives the same runs pooled over the six laws.

**The article as tested is not in its service state.** The member's mode rises in service by a median
+0.35 percent at the realistic size (from 0.00 to +3.23 over the study's 20 structures) and +1.00
percent at the strong size (-0.01 to +7.44). On the shakers it rises further, by an amount the system
sets (@tbl-member), and the square systems drive it hardest. At the strong size, pooled over the
laws, the member as tested sits beyond its service state by +0.57 to +3.41 percentage points on the
four systems other than 3 x 12 on the study's structures, and by a larger +1.38 to +3.91 points on
the held-back ones. The softening modes, too, fall further as tested than in service: a median -4.72
percent against -3.02 on the study's structures at the strong size, and -4.68 against -3.02 on the
held-back ones. On 10 of the 20 study structures and 6 of the 10 held-back ones, the strong member
changes in service by less than a quarter of its design change of 4 percent; at the realistic size,
on 9 of 20 the member changes in service by less than a quarter of 1 percent. These are the
structures listed below as changing little in service.

```{=typst}
#block(breakable: false, width: 100%)[
```

| | Study, realistic | Study, strong | Held back, realistic | Held back, strong |
|:---|---:|---:|---:|---:|
| In service | +0.35 | +1.00 | +0.28 | +0.97 |
| 3 x 12 | +0.54 | +0.70 | +0.47 | +0.87 |
| 6 x 12 | +0.91 | +1.61 | +1.20 | +2.27 |
| 12 x 24 | +1.26 | +2.29 | +1.10 | +2.89 |
| 6 x 6 | +1.94 | +3.80 | +3.20 | +5.22 |
| 12 x 12 | +1.92 | +3.52 | +2.37 | +4.61 |
| Member only, 6 x 12 | +1.75 | +4.92 | +2.10 | +5.62 |
| Member only, 6 x 6 | +2.43 | +6.60 | +3.40 | +7.63 |

: The hardening member's mode, change in frequency in percent: in service, and as tested on each system (per structure the median over the six laws, then the median over structures; the last two rows with only the hardening member active, over structures 0 to 9 and the ten held-back structures). The scorer reads a rise as tested about 1.2 times high, a limit the benchmark article states. Data: `data/study_member_state.csv`, `data/audit_member_state.csv`. {#tbl-member tbl-colwidths="[24,19,19,19,19]"}

```{=typst}
]
```

**At the realistic size, on the systems with more control gauges than shakers,** no law's stress
error changes by more than 0.2 dB at the median on the study's structures (the largest is
`pinv_open`, +0.19 dB). **At the strong size** it rises for five laws (@tbl-change). These rises are on
the 6 x 12 and 12 x 24 systems; on the 3 x 12 system every law's median change at the strong size is
between -1.56 and +0.04 dB.

```{=typst}
#block(breakable: false, width: 100%)[
```

| Law | Systems | Realistic | Strong | Member moved |
|:---|:---|---:|---:|---:|
| `pinv_closed` | more control gauges | +0.01 | +1.16 (16 up) | +1.27 |
| `pinv_open` | more control gauges | +0.19 | +1.32 (18 up) | +1.14 |
| `shape_svd` | more control gauges | +0.04 | -0.28 (11 down) | -0.67 |
| `buzz_match` | more control gauges | +0.13 | +1.91 (18 up) | +2.03 |
| `min_drive` | more control gauges | -0.14 | +0.93 (16 up) | +1.32 |
| `band_average` | more control gauges | -0.05 | +0.77 (15 up) | +0.94 |
| `pinv_closed` | square | -1.72 (18 down) | +0.46 | +0.93 |
| `pinv_open` | square | +0.10 | +1.12 (15 up) | +1.72 |
| `shape_svd` | square | -0.04 | +0.44 | +0.54 |
| `buzz_match` | square | -1.50 (16 down) | +0.48 | +0.58 |
| `min_drive` | square | +1.55 (17 up) | +5.79 (20 up) | +6.29 |
| `band_average` | square | +0.06 | +2.27 (16 up) | +3.31 |

: Change in the stress error from the linear structure to stage 2, same law, structure and system, each law at its defaults: median over the study's 20 structures, dB; the count is of structures moving more than 0.2 dB that way, where it is 15 or more. "Member moved" is the strong size again, leaving out the structures whose member changes little in service (10 left at the strong size). Data: `data/study_change_linear_to_stage2.csv`, with quartiles, the control and held-out gauges, and the same without the flagged structures; the held-back structures' in `data/audit_change_linear_to_stage2.csv`. {#tbl-change tbl-colwidths="[19,27,18,18,18]"}

```{=typst}
]
```

On the systems with more control gauges than shakers, at the strong size, the medians on the study's
structures are `buzz_match` +1.91 dB [quartiles +0.89, +2.38], `pinv_open` +1.32 [+0.81, +1.69],
`pinv_closed` +1.16 [+0.25, +1.83], `min_drive` +0.93 [+0.45, +1.62] and `band_average` +0.77
[+0.21, +1.14]; on the held-back structures +1.57, +1.41, +1.29, +0.76 and +0.75 dB, up on 9, 10, 9, 7
and 9 of 10. All five hold. `shape_svd` did not change: -0.28 dB [-0.87, +0.33] on the study's
structures, with 7 up and 11 down, and -0.02 dB on the held-back ones. Leaving out the study
structures whose member changes little in service, and the flagged structures as well (9 left):
+1.95, +0.90, +1.27, +1.52, +0.82 and -0.77 dB. Over the same runs the control gauges moved by a
median of 0.21 dB or less for every law but `pinv_open` (+0.57 dB), and the held-out gauges by
0.29 dB or less.

On the square systems, at the strong size, the stress error rose for `min_drive` by a median 5.79 dB
[+3.40, +6.79] on all 20 study structures, for `band_average` by 2.27 dB [+0.59, +3.52] on 16, and for
`pinv_open` by 1.12 dB on 15; on the held-back structures by 4.36, 1.00 and 2.17 dB (up on 9, 8 and 9
of 10), and all three hold. Without the study structures whose member changes little in service and
the flagged structures (8 left): +6.57, +3.63 and +2.60 dB. At the realistic size `pinv_closed` and
`buzz_match` read a lower stress error than on the linear structure, by a median 1.72 dB (18 of 20
down) and 1.50 dB (16 down), from their high values on the linear structure, while `min_drive` rose
by 1.55 dB (17 up); on the held-back structures -2.13, -1.31 and +1.17 dB (9, 9 and 7 of 10 the same
way), and all three hold. On this class the control gauges moved more: at the strong size by a median
+1.56 dB (`pinv_closed`), +3.17 (`pinv_open`), +1.63 (`buzz_match`) and +2.18 (`min_drive`) on the
study's structures, and by 0.18 dB or less for `shape_svd` and `band_average`.

**Softening joints alone, and the hardening member alone.** On the 6 x 12 and 6 x 6 systems, each law
was also run with only one of the two effects active, on structures 0 to 9 and on the ten held-back
structures (@fig-effects). At the strong size on the 6 x 12 system, with the softening joints only,
the stress error rose by a median 1.97 dB for `pinv_closed` (9 of 10 study structures up), 1.32 for
`pinv_open`, 1.17 for `buzz_match`, 0.66 for `min_drive` and 0.59 for `band_average`; on the held-back
structures by 1.50, 1.62, 1.22, 0.69 and 0.61 dB (up on 9, 9, 8, 8 and 8 of 10), and all five hold. On
the 6 x 6 system softening alone raised `min_drive`'s stress error by 3.72 dB on the study's structures
and 3.93 on the held-back ones, and `band_average`'s by 1.83 and a smaller 1.10.

With the hardening member only, the median change in each law's stress error was within 0.2 dB on
every case with more control gauges than shakers, at both sizes, on both sets of structures (12 of 12
law and size combinations each). On the square 6 x 6 system it was not: on the study's structures
four laws moved by more than 0.2 dB (`pinv_closed` -0.22 dB at the realistic size; `min_drive` -1.34,
`pinv_open` -0.43 and `buzz_match` +0.21 dB at the strong size), and those moves did not repeat on the
held-back structures, where at the strong size `min_drive` moved +1.05 dB and `pinv_open` +1.13 dB.
Hardening alone moves single laws on that system by up to about 1 dB with no stable sign. As tested in
these runs the member did harden: its mode rose by a median 4.92 and 6.60 percent at the strong size
on the 6 x 12 and 6 x 6 systems (5.62 and 7.63 on the held-back structures; @tbl-member). The same
runs, structure by structure, are in `data/study_single_effects.csv` and
`data/audit_single_effects.csv`.

![The change in each law's stress error from the linear structure, at the strong size, on the study's structures 0 to 9: with both effects (filled circles, solid bars), with only the softening joints (open squares, dashed bars), and with only the hardening member (open diamonds, dotted bars). Median over the ten structures; the bars span the quartiles. The grey band is the 0.2 dB under which no difference is claimed.](figures/fig2_effects_by_law.png){#fig-effects fig-alt="Two panels, the 6 x 12 system on the left and the 6 x 6 system on the right, each with the six laws along the horizontal axis and the change in stress error in dB from about minus 3 to plus 5 on the vertical axis, with a grey band from minus 0.2 to 0.2. Each law has three markers: a filled blue circle with a solid bar for both effects, an open orange square with a dashed bar for softening only, an open purple diamond with a dotted bar for hardening only. Left: the circles and squares of pinv_closed, pinv_open, buzz_match, min_drive and band_average lie between about 0.6 and 2 dB, shape_svd's near minus 0.7; every diamond lies on the grey band. Right: min_drive's circle and square near 4.4 and 3.7 dB, band_average's near 2.7 and 1.8, pinv_closed's near minus 1.7 and minus 1.6, the others between about minus 0.7 and 0.9; the diamonds lie near zero except min_drive's at minus 1.3 and pinv_open's at minus 0.4." data="data/study_single_effects.csv"}

### 3.5 Response Measured Again

With the frequency response measured again every loop, on structures 0 to 9 at both sizes of stage 2,
the stress error rose for the pseudo-inverse laws and `buzz_match`: on the 6 x 12 system, `pinv_open`
by a median 5.56 dB at the realistic size and 4.48 dB at the strong size (all 10 structures up); on
the 6 x 6 system, `pinv_closed` by 4.85 and 3.75 dB and `buzz_match` by 4.65 and 3.65 dB (all 10).
`band_average`, with its own update on as well, moved by a median of 0.02 dB or less. The audit did
not run these cases, so this finding rests on the study's ten structures alone. The other medians are
in `data/study_change_measured_again.csv`.

## 4. Limits

- **One run per case.** Each case was run once, with one sequence of simulator noise. How much a score
  moves from run to run on the same case is not measured; the spread given is over structures only.
- **The checks were widened.** 97 percent of the results (2,800 of 2,877) are from runs with the
  checks widened. The scores describe what each law does when the growing-error and drive-change
  checks do not stop it, not what a run at the controller's defaults would give past the first loops
  at full level. The comparison of a run at default checks with its widened run rests on 12 cases, two
  laws and the linear structure only, and was not audited.
- **`buzz_match` leaves weak gauge pairs independent.** A pair whose coherence under the
  identification is below the law's floor is given no cross term, so its cross term starts at zero in
  the factor of the shared closed loop, and the loop cannot move a term at zero while its gauge reads
  high (the companion article's Section 6 [@primer2026]). No run was rerun for it, and neither the
  study's runs nor the audit's isolate it.
- **The shared loop can hold a gauge high near a mode.** The loop's second form of correction will not
  let a cross term grow while its gauge reads high, which can hold a gauge high near a mode when the
  measured frequency response is off. On the companion article's made-up structure the shipped loop
  does this with an independent target and with a target that has cross terms, and a line-by-line port
  of the published correction holds the gauge high in the same way when the target has cross terms
  (Section 6 of the companion article [@primer2026]); that is what was run, and no general claim is
  made from it. `pinv_closed`, `shape_svd` and `min_drive` ran targets with full cross terms, where the
  first limit does not act and this one can. No run here was rerun for it, and the study's runs do not
  isolate it.
- **`min_drive` keeps a floor, not an exact match.** By default it may leave any control gauge up to
  3 dB under its specified spectrum on average over the band, and further on single lines, since the
  study runs with no alarm lines; its results are read with that allowance (companion article,
  Section 6 [@primer2026]).
- **The tuned settings** were chosen on two structures and two systems and scored on ten structures
  and the same two systems, on both sets of structures. Where tuning changed a score, it is shown for
  those cases only.
- **Simulator only.** Nothing here has passed through real converters, amplifiers or shakers.
  Differences between laws under 0.2 dB are not claimed.
- **What the benchmark's own limits mean here.** The level rule is a stand-in for a true cubic
  stiffening to about a 4 percent rise; a mode follows its own amplitude where a real member follows
  its total motion; the envelope that sets a heavily damped mode's level lags it; the scorer reads a
  member's rise as tested about 1.2 times high. The member's state differs from structure to structure:
  on half the study's structures it changes in service by less than a quarter of its design size, and
  the findings on hardening rest on ten structures in each set. The structures the benchmark flags (5
  and 33, driven above 30 g RMS; 15 on the 12 x 12 system at the realistic size, whose calculation
  under the reference drive does not settle; 1 on the square systems, where the member would yield at
  full level) are kept in every table. Leaving them out moves no median change from the linear
  structure by more than 0.4 dB; where it moves another result more, the value without them is given
  beside it.
- **One article.** Every result is on one frame design with one hardening member. Structure 4, whose
  member changes most in service, is the largest rise of nearly every law on the systems with more
  control gauges than shakers; medians are not moved by it.
- **Targets differ by law.** `band_average` runs on the banded specification, which gives no cross
  terms, and the other five on the line target, a full spectral matrix, so a comparison between them
  is a comparison of two laws each with its own target, as a test would run them.

## Contribution Statement

Kevin Cross is the sole author. Brandon Zwink, who wrote the band-average law, took no part in the
design of this study, its runs or its analysis. Kevin Cross chose the five laws from the literature and directed their
implementation in Hertzforge, and directed the study, its design rules and its analysis. The
band-average law is Brandon Zwink's: he designed it and wrote its Python implementation, which the
shipped law is ported from.

## How This Was Made

The text, the figures, the code that draws them, and the study's runner and analysis scripts were
written with Claude Code, an AI coding assistant running Anthropic's Claude Opus models, under Kevin
Cross's direction. The author is responsible for every word, number and line of code.

## Acknowledgments

The closed-loop correction of a factor of the target, the extreme inputs and the minimum input trace
are the published work of D. O. Smallwood; the regularization choices, the statement of the buzz-test
method and the shape-constrained method are the published work of R. Schultz and of R. Schultz and
P. Avitabile; and the Pareto-optimal target is the published work of K. Coletti, R. B. Davis and
R. Schultz. These are works of Sandia National Laboratories, credited here to Sandia National
Laboratories. The shape-constrained method is also the work of the University of Massachusetts Lowell,
and the Pareto-optimal target of the University of Georgia. The buzz-test method is credited, as
Schultz credits it, to P. M. Daborn. The band-average law is Brandon Zwink's.

## References

## Implemented In

The six laws, the control service and the simulator are in Hertzforge, github.com/Hertzforge/Hertzforge,
main branch at commit b587d5a1: `crates/hertzforge-mimo-laws`, `crates/hertzforge-law-band-average-math`
and `crates/hertzforge-mimo-random`. The study's runs were made at commit 646c4ca4, which adds the
runner and the player to that commit. The runner and the player are the examples `x4_runner` and
`obs_play` of the crate `sds-control`, main branch at commit 268c3bfd. The problems are
in the data set [@obsdata2026], the scorecards and the audit's record in the results record
[@results2026], and the set's code and documents at https://github.com/Hertzforge/benchmarks (tag
v0.2).
