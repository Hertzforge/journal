---
# Filled in by the editors at publication.
id: "2026-003"
version: 1
date: 2026-11-15
doi: "10.5281/zenodo.24254057"
doi_latest: "10.5281/zenodo.24254056"   # always resolves to the latest version
note: First published.

# Filled in by the authors.
title: "Multi-Shaker Sine Control: What Is Published, and Where It Stops"
type: Survey
evidence: published sources
evidence_note: "Published papers, reports, standards, a patent and controller makers' public pages, each read to the extent stated in its reference. The few numbers of its own are arithmetic, shown in full and marked as ours; no new experiments or simulations."
authors:
  - name: "Kevin Cross"
    orcid: "https://orcid.org/0009-0002-6608-9426"
implemented_in: ""
benchmarks: ""
contents: true
abstract: >
  A sine test with several shakers is controlled, as published, through a model of the test
  article measured at a low level before the test. This survey collects what is published: five
  forms of control law with their equations checked against the page, what the test standards ask
  of a sine test and of several exciters, what vendors and facilities say they do, the effect of
  sweep rate on a lightly damped resonance, how limits and notching are handled, what active noise
  control, helicopter vibration control and rotor balancing know about holding a tone with several
  actuators, and what nonlinear vibration testing does with feedback. The published laws are thin
  on evidence: one two-axis table test, two beam tests, one simulation and one run-to-run time-domain
  method, none on a structure whose resonances move with level. No standard read sets a phase
  tolerance or a sine clause for several exciters. Two pieces of arithmetic of our own, shown in
  full, tie the sources together: the number of its own time constants a mode is given while a
  sweep crosses its bandwidth, which shows that a correction alone cannot hold a lightly damped mode
  below a few hundred hertz at the rates tests are run; and the largest phase error of a low-level
  model at a resonance that has moved, which reaches 90 degrees, where a one-channel correction stops
  converging, after a move of one half-power bandwidth. Where the published work stops is stated
  gap by gap, worded to a search without subscription databases.
---

## Summary

A sine test drives a test article with one tone, swept slowly through a frequency range or held
at one frequency. With several shakers, the controller has to choose an amplitude and a phase for
each shaker's drive so that several accelerometers on the article each read what the test
specification asks for. It does this from a model of the article measured with low-level noise
before the test, and corrects the drives as the measured error comes in.

This article collects what is published about how that is done, so that a test engineer new to
multi-shaker sine testing can see what exists and where it ends. It does not propose or rank
control laws.

**What we found:**

- **Five published forms of control law,** each given here with its equations as printed. Four
  correct the drive through a model measured once at a low level. One, a 1990 patent, changes its
  model as the test runs; we found no published test of its equations as printed. The evidence for
  all five is small: one two-axis table test, two beam tests, one simulation and one method that
  corrects between whole runs.
- **The standards** set tolerances for each control channel, written for one shaker. None of those
  read has a sine clause for several exciters or a tolerance on the relative phase between control
  points.
- **Vendors and facilities** describe their practice in words: a model refined during the test, a
  pseudo-inverse where the model is nearly singular, a limit met by scaling the whole reference down,
  phase control units that hold several shakers within 4 to 10 degrees. None publishes its law or the
  control error through a resonance. We found one published account of a swept sine controlled at
  points on a flexible article: a laboratory plate on four small shakers.
- **Sweep rate.** A lightly damped mode needs time to build up. At the sweep rates the standards
  ask for, a mode with a Q of 50 below a few tens of hertz gets fewer than two of its own time
  constants while the tone is inside its bandwidth, and its peak comes late and low. We put the
  published sweep parameter into a form that can be checked with a stopwatch, and
  show from it that correcting after the error is measured cannot hold such a mode at those rates;
  the drive has to be moved ahead of the error.
- **Other fields** that hold a tone with several actuators (noise cancellation, helicopter vibration
  control, rotor balancing) print the condition for a correction to work when its model is wrong: for
  one channel, a phase error under 90 degrees.
- **A structure that changes with level.** Nonlinear vibration testing holds a tone through a moving
  resonance with feedback, but every such experiment we read uses one exciter. A low-level model's
  phase error reaches 90 degrees once the resonance has moved one half-power bandwidth, which is 2
  percent of the frequency for a Q of 50.

The published work stops short of a multi-shaker sine law with results on a structure whose
resonances move with level, of any rule for carrying the model along a sweep, and of any rule for
sharing a notch among several drives. Those statements are limited to our search, which had no
subscription databases.

## 1. What a Sine Test With Several Shakers Is

A **sine test** drives a structure with one tone at a time. The **test article** (or simply the
structure) is the thing being tested, mounted on a fixture or a slip table. **Shakers** apply the
motion. **Control accelerometers** on the fixture or on the article measure the response, and the
**controller** compares that response, at the tone, with the **reference**: the amplitude, and
sometimes the phase, that the test specification asks for at each control point. From the
difference it sets the **drive**, the voltage sent to each shaker's amplifier.

The tone is moved in one of three ways. In a **swept sine** the frequency moves continuously,
usually exponentially with time, so that the rate is stated in octaves per minute. In a **dwell**
the frequency is held, for a time or a count of cycles, often at a resonance. In a **stepped
sine** the frequency moves in steps and the controller lets the response settle at each step.
Before and after the main run most tests make a low-level sweep, a **resonance search**, to find
the article's resonances and to see whether they moved.

Several shakers are used when one is not enough: an article too large or too heavy for one
shaker, a long article whose ends need different motion, a table that must move in more than one
axis, or a test that must hold rotation and cross-axis motion down. On a stiff fixture the
shakers can often be run as one, in phase, with a small correction for their differences. On a
flexible article, or near the fixture's own resonances, they cannot: each shaker's drive must
differ in amplitude and phase from the others, and the right difference changes with frequency.

![A schematic drawing. A long gray beam, labeled "test article (flexible)" beneath it, rests on three blue hatched shakers drawn as boxes with an armature on top, labeled shaker 1, shaker 2 and shaker 3. Three orange triangles on the beam mark control accelerometers, labeled control 1 to 3, and one open green triangle between control 1 and control 2 marks a limit accelerometer. A dashed outline of the beam bent in its first mode shape is drawn over it. On the right a box labeled "controller" contains three smaller boxes in a row: "tracking filters: amplitude and phase of each channel at the tone", "compare with the reference R (amplitude and phase at each control)", and "update the drives D". Dotted orange arrows run from each control accelerometer and from the limit accelerometer to the tracking filters box; solid blue arrows run from the drive box back to each shaker, labeled d1, d2 and d3. A note under the controller reads "C = H D at each frequency: H is measured before the test".](figures/fig1_setup.png)

**Figure 1.** A sine test with several shakers and its loop. The control accelerometers are on the
article, which is flexible; the dashed line is its first bending shape. The controller measures
each channel's amplitude and phase at the tone, compares the controls with the reference, and
updates the drives. Drawn by script; not to scale. Data: `data/fig1_layout.csv`; code:
`code/fig1_setup.py`.

**The control problem in one line.** Call the number of shakers (drives) $m$ and the number of
control channels $n$. At one frequency, on a structure that behaves linearly and has settled to
the tone, the complex amplitudes of the controls $C$ (a list of $n$ numbers, each an amplitude and
a phase) follow from the complex drive amplitudes $D$ (a list of $m$) through the structure's
frequency response matrix $H$, an $n$ by $m$ table of how much each control moves per volt of each
drive:

$$C = H D.$$

Every source that states a multi-shaker sine law poses the problem this way (Musella and others
2019; Qiu and others 2019; Zhang, Chen and He 2015). The controller does not know $H$; it holds a
**model** $\hat{H}$, usually measured before the test by driving all shakers at once with low-level
random noise that is uncorrelated from shaker to shaker. The NASA Mechanical Vibration Facility
does this before a sine sweep (Winkel and others 2017). A second published way measures $H$ with
sine itself: the sweep is run $p$ times with different, independent patterns of drive phase, and
$H$ is solved from the responses, $H = U D^{-1}$, with $U$ the responses and $D$ the drive patterns
side by side (Zhang, Chen and He 2015, Eqs. 12 to 14). It costs $p$ runs at each level.

The **feedforward** drive is the model's inverse applied to the reference, $D_0 = Z R$, where $Z$
is the inverse of $\hat{H}$, or its pseudo-inverse when there are more controls than shakers. The
patent literature calls $Z$ the impedance matrix. **Feedback** then corrects $D$ from the error
$E = R - C$, measured by a **tracking filter**: a narrow filter that follows the tone and gives
each channel's amplitude and phase at the drive frequency, for example by correlating the signal
with a sine and a cosine at that frequency (Zhang, Chen and He 2015, Eqs. 7 to 9) or by a
least-squares fit over a few periods (Musella and others 2018).

The **reference** may give amplitude and phase at every control, with the phase stated relative to
the first control channel (Musella and others 2019), or amplitude only, leaving the relative phases
free (Zhang, Chen and He 2015). What goes wrong is also common to the sources: the model is measured
at a low level and the structure at test level is not the same, and a sweep never lets a lightly
damped resonance settle to the steady state that $C = H D$ describes. Sections 5 and 8 return to
both.

## 2. How a Sine Test Is Specified and Judged

A sine test specification gives the frequency range, the amplitude against frequency, the sweep
rate or dwell time, the tolerances on each, and how several control points are combined into one
reading. Tables 1 and 2 give what the standards we read require, at the clauses named.

**Table 1.** What the standards read for this survey say about sweep rate and tolerances. The
clauses read follow each standard's name.

| Standard | Sweep rate | Tolerances |
|------------|---------------|-----------------------|
| IEC 60068-2-6:2007, free preview (4.1.1, 4.1.6, 4.2) | One octave a minute, +/-10 %; "may be varied for a vibration response investigation" (4.1.6) | Not restated here (4.1.2 to 4.1.5 are outside what we re-read) |
| MIL-STD-810H, Method 514.8 (4.2.2.2, Table 514.8-III) | +/-10 % of the stated rate | Frequency +/-0.1 %; composite control +/-10 %; individual channels under average control +/-25 % below 500 Hz and +/-50 % above, under maximum control +10/-25 % and +10/-50 %; cross-axis under 50 % below 500 Hz, 100 % above; duration +/-5 %; filtered against unfiltered +/-5 %; the control system's uncertainty not over a third of these (4.2.2.2) |
| ECSS-E-ST-10-03C Rev.1 (Table 4-1; Tables 5-2, 5-4, 5-6, 6-2, 6-4, 6-6; 5.5.2.5; 6.5.2.8; 3.2.15) | 2 octaves a minute at qualification, 4 at acceptance and protoflight; 5 to 140 Hz for equipment, 5 to 100 Hz for an element | Frequency +/-2 % (or +/-1 Hz, whichever is greater); amplitude +/-10 %; sweep rate +/-5 %. Resonance searches before and after: under 5 % shift in frequency and under 20 % in amplitude for modes with effective mass over 10 % |
| ECSS-E-HB-10-03A, Annex A.7.3 (A.7.3.2 to A.7.3.4) | "Up to 4 octaves/min" for flight hardware; identification runs "typically 0,5 octaves/minute" (A.7.3.3) |  |
| ECSS-E-HB-32-26A, 5.2.3.3 | The effect of sweep rate on a resonance (Section 5) |  |
| ISO 7626-2:1990, 9.2.3 (a mobility measurement standard, one exciter) | A sweep slow enough that the response near a resonance is within 5 % of its true value (Section 5) |  |

**Table 2.** What the same standards say about several control points and about several exciters.
The clauses read are in Table 1; Method 527.2 of MIL-STD-810H appears only here. "Not found" is
worded to the word searches in Section 10.

| Standard | Several control points | Several exciters and phase |
|-----------|--------------------|--------------------|
| IEC 60068-2-6:2007, free preview | Average, weighted average (the formula follows the table), or extremal (MAX, MIN); "Use of multipoint control does not assure that the tolerances of each checkpoint are met" (4.2.1); multi-reference limiting and superseding (4.2.2) | No several-exciter clause; the fixing points "move substantially in phase and in straight parallel lines" (4.1.1) |
| MIL-STD-810H, Method 514.8 | Composite control: the average, maximum or minimum of all control channels (Table 514.8-III, footnote 1) | No phase tolerance; the fixing points "move substantially in phase with and parallel to the excitation axis" (4.2.2.2) |
| MIL-STD-810H, Method 527.2, the multi-exciter method (Annex A 1, Annex E 3) |  | Vendors "offer MET options for time waveform replication (TWR), sine, shock, and random" (Annex A 1). At publication "no commercially available multiple-input multiple-output (MIMO) solutions exist for swept narrowband random on random (NBROR) or sine-on-random (SOR) other than Procedure I - Time Waveform Replication based techniques" (Annex E 3). No other sine content found |
| ECSS-E-ST-10-03C Rev.1 |  | No several-exciter clause and no phase tolerance; notching approved by the customer; automatic protection against "excessive resonance build-up" (6.5.2.8) |
| ECSS-E-HB-10-03A, Annex A.7.3 | Control on the maximum or the average of the pilots; "Most of the time the test is controlled with the RMS level measured by the pilots"; "Increasing the number of channels in the control loop can slow down and degrade the control" (A.7.3.2) | "Sine vibration tests are usually performed on single-axis electro-dynamic shakers"; of multi-axis facilities, "the control is more difficult" (A.7.3) |
| ECSS-E-HB-32-26A, 5.2.3.3 |  | None found |
| ISO 7626-2:1990, 9.2.3 (a mobility measurement standard, one exciter) |  | Not in scope |

IEC 60068-2-6 prints the weighted average as
$a_C = (w_1 a_1 + \dots + w_n a_n)/(w_1 + \dots + w_n)$ (4.2.1.2).

Two things stand out. First, every tolerance is written per channel or for a composite of the
channels; none of the documents read sets a tolerance on the relative phase between control
points, and none has a sine clause for several exciters. Two say only that the fixing points move
"substantially in phase", which is a qualitative statement written for one shaker. Second, the
handbook's advice on control strategy (average or maximum of the pilots, how many channels to
close the loop on) is the single-axis practice. A multi-shaker sine test is therefore specified
today by carrying the single-shaker tolerances over to each control, and by whatever the test's
own procedure adds.

We did not read NASA GSFC-STD-7000, SMC-S-016, the NASA handbooks on vibration testing,
IEST-RP-DTE022 "Multi-shaker Test and Control", the 2015 edition of ISO 7626-2, or the parts of
IEC 60068-2-6 beyond its free preview. The levels of ECSS-E-ST-10-03C are factors from
ECSS-E-ST-32-10 times a limit load spectrum, and we did not read those factors.

## 3. The Published Control Laws

We found five published forms of a multi-shaker sine law with their equations. Each is given
below as its source prints it, then in one notation: $D_k$ is the drive vector at control update
$k$, $C_k$ the controls the tracking filters measured, $E_k = R - C_k$ the error, $Z$ the inverse
of the model, and $g$ a scalar gain between 0 and 1. Every equation below was checked against the
page of its source.

### 3.1 Correction Through a Fixed Inverse

The simplest law measures the model once, before the test, and corrects the drive through its
inverse at every update:

$$D_{k+1} = D_k + g\, Z\, (R - C_k).$$

Qiu and others (2019, Eq. 10) print it as $X_{new} = X_{old} + \beta H^{-1} E$ with
$0 \le \beta \le 1$, with the model $H = G_{XX}^{-1} G_{YX}$ estimated from random noise (their
Eq. 1). Zhang, Wang and Zeng (2017, Eqs. 15 to 18) start from $D_0 = H^{-1} R$, call
$G = H^{-1}$ "the impedance matrix", and correct with $D_k = D_{k-1} + c\, G\, E_{k-1}$. Of the
factor $c$ they write (our translation) that "in the sine amplitude correction process an
excessive error often leads to over-correction of the excitation, producing a shock effect", so a
compression factor $c$ between 0 and 1 is introduced to slow the correction; as $c$ approaches 1
"the convergence accuracy is high but the convergence speed is slower", and as it approaches 0 the
opposite; 0.4 to 0.6 is usual. The 1990 patent discussed next describes the same law as the prior
art it improves on, $D_{n+1} = D_n + g Z_m (R - C_n)$, with $Z_m$ "measured and determined prior
to beginning the first test cycle", and notes that "negative values of g have to be used when
phase errors greater than 90 degrees are present in measured values of the system response
matrix" (Underwood, US 5,299,459, cols. 5 and 6).

That note has a short explanation, which is ours. With a fixed $Z$ the error obeys
$E_{k+1} = (I - g H Z) E_k$. It shrinks from update to update only if every eigenvalue
$\lambda$ of $H Z$ satisfies $|1 - g\lambda| < 1$. With one channel, $H Z = \rho e^{j\theta}$,
and the condition is $0 < g \rho < 2 \cos\theta$: there is no positive gain that works once the
model's phase is more than 90 degrees from the structure's. Section 8 shows how easily that
happens at a resonance that moves.

**Evidence.** Qiu and others (2019) ran a two-axis sine test on a three-shaker 60 kN table, 5 to
200 Hz at 2 octaves a minute, X at 0 degrees and Y at 90 degrees: "most part of the magnitude
control curve are well within 10 % alarm tolerances and the phase control curve are well within
±10° alarm tolerances except for several level control points nearly 80 Hz as a result
of the platform modes". Zhang, Wang and Zeng (2017) controlled sine plus random on an aluminium
cantilever beam.

### 3.2 An Adaptive Model and a Complex Gain: US 5,299,459

Underwood's patent, "Adaptive control method for multiexciter sine tests" (filed 1990, granted
1994, listed as expired), keeps the drive update above but changes the model as the test runs. The
initial model is found "by stimulating the system under test 12 sequentially with individual
exciters 30 and measuring the response of the system 12 at each sensor 32" (col. 5). Each control
cycle has two steps. In the **learning** step a trial drive is sent,

$$\hat{D}_n = D_n + c_n Z_n (R - C_n),$$

and the structure answers with $\hat{C}_n$. From that answer a complex gain is computed (EQU2,
col. 8),

$$a_n = c_n \frac{\langle R - C_n,\; \hat{C}_n - C_n \rangle}{| \hat{C}_n - C_n |^2},$$

and the **control** step applies $S_n = a_n Z_n (R - C_n) = D_{n+1} - D_n$ (col. 7). The model is
then updated so that it maps the observed change in the controls onto the step that caused it
(the secant condition $Z_{n+1}(C_{n+1} - C_n) = S_n$, col. 7), by EQU1 (col. 6):

$$Z_{n+1} = \left( I_N + \frac{\left(S_n - Z_n (C_{n+1} - C_n)\right) S_n^{*}}{\langle Z_n (C_{n+1} - C_n),\; S_n \rangle} \right) Z_n .$$

(In the patent's printed learning-loop equation the left side carries no circumflex; the "where"
list defines $\hat{D}_n$. All quantities are per frequency.) The trial gain $c_n$ starts near 0.1
"in order to minimize control errors associated with using a possibly erroneous impedance
estimate" and is "allowed to approach 1.0" as confidence grows, measured by $a_n$, which the patent
calls "the best indicator of the instant reliability" of the model. The patent states that the
update converges to the true impedance in at most $N$ steps for a linear, time-invariant structure,
once marked "(hypothetically)" and once without the qualifier ("The process is essentially stable
and, converges in at most N iterations for linear and time invariant systems 12"); that for a
nonlinear or time-varying structure "the controller 10 will not converge exactly in a finite number
of steps"; and that the method "does potentially increase control error during initial iterations
due to potential errors in initial values assigned to the system response matrix 44. Careful
selection of values for c_n minimizes this problem" (cols. 7 and 8). The complex gain is presented
as a refinement of using a negative gain where the phase error passes 90 degrees.

**Evidence.** The patent reports no test. We found no published test or simulation of EQU1 and
EQU2 as printed. Musella and others (2018, Fig. 8) show a quasi-Newton controller that, as they
describe it, combines the patent's idea with an optimization method for complex variables, started from
an identity matrix; it is their own implementation, not the printed equations. Two articles by
Underwood and Keller (2001) and by Underwood, Keller and Ayres (2017) say the production law of
their controller refines the model during the closed loop by this method (Section 4).

### 3.3 Steepest Descent

Musella and others (2019) treat the drive as the unknown of a least-squares problem, cost
$J = e^H e$, and step down its gradient, $u_{n+1} = u_n + \alpha H^H e_n$ (their Eqs. 9 to 11, with
$u$ the drive and $e$ the error). The step's poles are $1 - \alpha \sigma_i^2$, with $\sigma_i$ the
singular values of $H$ (Eqs. 17 to 20), and the law they recommend is (Eq. 22)

$$u_{n+1} = u_n + K \frac{1}{\hat{\sigma}_{max}^2} \hat{H}^H e_n, \qquad 0 < K < 1,$$

which in our notation is $D_{k+1} = D_k + (g / \hat{\sigma}_{max}^2)\, \hat{H}^H (R - C_k)$. The
printed bound is $0 \le \alpha \le 1/\lambda_{max}$ with optimum $1/\sigma_{max}^2$ (Eq. 21), while
the caption of their Fig. 5 states $2/\sigma_{max}^2$; their book chapter on the same work (Musella
and others 2020, read in part through page summaries) states a bound for each principal coordinate
of $H$ separately. The authors are plain about the assumption: their
analysis is "a condition at the limit of stability, obtained considering that all the transients
have died out", which "can be a strong assumption for a swept sine test", and "no link has been
theoretically made between the convergence and the sweep rate" (Section 5.1).

**Evidence.** Simulation of two uncoupled virtual electrodynamic shakers, 10 to 2500 Hz, a linear
sweep of 2 Hz a second, with a 1 percent mass change between identification and test and step
disturbances, from which the loop recovered in about half a second to a second.

### 3.4 An Amplitude-Ratio Law

Zhang, Chen and He (2015) control the amplitudes of several points and leave their phases free.
The drive starts from the measured model, $D = H^{-1} r$; the model itself is measured by the
phase-varied sine runs of Section 1, $H = U D^{-1}$. With $D_k$ a drive amplitude, $A_k$ the
response and $A_r$ the reference, they define $E_q = A_r / A_k$ and print (Eq. 15)

$$D_{k+1} = D_k \frac{K + 1/E_q}{K + E_q} \;\; \text{if } E_q \le 1, \qquad D_{k+1} = D_k \frac{K + 1}{K + E_q} \;\; \text{if } E_q > 1,$$

with "K ... the correction factor, whose size determines the accuracy and speed of convergence"
(our translation); their Fig. 4 shows $K$ of 0.5, 1, 2 and 6, faster for smaller $K$. A note of
our own on the equation as printed: with $E_q$ defined as the reference over the response, the
second branch lowers the drive when the response is below the reference. The paper's Fig. 4 plots
the ratio of response to reference, so the printed definition may be the other way up; we give the
equation as the paper prints it. The paper sets its reference as
"amplitude and phase", and Eq. 15 then corrects amplitude only; the authors leave phase control to
further research.

**Evidence.** Two small electrodynamic shakers under a stainless steel beam 1115 by 50 by 14 mm,
drives and controls at 143 and 376 mm, alarm at +/-3 dB and abort at +/-6 dB; both points were held
within tolerance with some oscillation at the low and high ends of the band.

### 3.5 A Correction Between Whole Runs Through a Time-Domain Inverse

Zheng, Chen and Luo (2020) work in time. They estimate a multistep prediction model of the
structure, invert it with a truncated singular value decomposition ("the direct inverse of the T
matrix might induce numerical instability"), and run the reference time histories through the
inverse to make the drives. The correction is made **offline, between complete runs**: after each
run, at each frequency, the reference fed to the inverse is scaled by the ratio of the wanted to
the measured response spectrum, raised to a power $\varepsilon$ between 0 and 1 (their Eq. 29,
$R_{n+1} = R_n \, (R_0 / S_y)^{\varepsilon}$). They advise controlling at a lower level first, "then
restore the original level test". On a three-axis shaker with two axes driven and controlled, at
-6 dB, "After 4 iteration loops, the response spectra are controlled within acceptable
tolerances"; at full level the spectra "become slightly worse, but they are still within the alert
limits". This is not a correction within the sweep. The authors describe the 1990 patent as "a
patented frequency-domain control method with the tracking filters", and know of no multi-shaker
swept sine controlled by a time-domain method before theirs.

### 3.6 Sine on Random With Several Shakers

Zhang, Wang and Zeng (2017) control sine plus random on several shakers: the sine is separated by a
correlation integral at its known frequency, the random part is controlled through its spectra, and
the sine through the compressed impedance law of Section 3.1. Ma, Chen and Zheng (2022; 2024)
treat multi-axis swept sine on random and sine on random; we read only their abstracts and say
nothing of their update equations. MIL-STD-810H (2019) stated that no commercial multi-input
multi-output solution existed for sine on random other than time waveform replication (Table 2).

### 3.7 The Laws Side by Side

**Table 3.** The published multi-shaker sine laws found, in one notation. The update is in this
article's notation. The model column says how the model is measured and whether it is changed
during the test.

| Law | Update | Model | Demonstrated on |
|----------|-----------------|------------|-----------|
| Fixed inverse (Qiu and others 2019; Zhang, Wang and Zeng 2017) | $D_{k+1} = D_k + g Z (R - C_k)$; $g$ 0 to 1, 0.4 to 0.6 advised | Random noise before the test; never changed | Three-shaker table, two axes; two shakers on a cantilever beam (sine plus random) |
| Adaptive model and complex gain (US 5,299,459) | Trial step with $c_n$, complex gain $a_n$ (EQU2), step $a_n Z_n (R - C_n)$ | Shaker by shaker before the test; updated every cycle by a secant formula (EQU1) | No published test of the printed equations found |
| Steepest descent (Musella and others 2019) | $D_{k+1} = D_k + (g/\hat{\sigma}_{max}^2) \hat{H}^H (R - C_k)$ | Random noise before the test; never changed | Simulation of two uncoupled virtual shakers |
| Amplitude ratio (Zhang, Chen and He 2015) | Each drive amplitude scaled by a ratio law in $A_r / A_k$ with factor $K$ | Phase-varied sine runs before the test; never changed | Two shakers on a steel beam; amplitude only |
| Run-to-run time-domain inverse (Zheng, Chen and Luo 2020) | Reference spectra scaled by $(R_0/S_y)^{\varepsilon}$ between whole runs | Multistep prediction model estimated before the test | Two axes of a three-axis shaker |

Four of the five correct within the sweep through a model measured once at a low level; one changes
the model as it goes, and it is the one with no published test. None reports closed-loop results on
a structure whose resonances move with level.

## 4. What Vendors and Facilities Say They Do

**Vendor articles.** The most detailed public text from the commercial side is by Marcos
Underwood and Tony Keller, in two articles in Sound and Vibration (2001, read in full; 2017 with
Russ Ayres, read from section G to the end, since the copy we found lacks its opening pages). They
state that in multi-shaker sine the frequency response matrix "is obtained initially and refined
during the closed loop process by the same adaptive control method", the 1990 patent's, and they
define real-time adaptive control as control "which updates the System Impedance Matrix (SIM)
every loop to assure true control of non-linear responses rather than only updating the SIM at the
beginning of the test" (2001). Where the matrix is close to singular, "If the ratio of the smallest
to the largest singular value falls below a certain singularity threshold, the matrix is declared
singular and a pseudo-inverse calculation is performed"; the Moore-Penrose pseudo-inverse "mitigates
the tendency for the actuators to 'fight' and also limits the magnitude of the drives used for
control". Square control has "one phase/amplitude control transducer per shaker", with any further
channels used for "limit control of amplitudes, without affecting the phase parameters". No sine
equation is printed in either article.

The 2017 review adds three points. Multi-shaker swept sine for satellites "has so far been
primarily limited to vertical testing using four shakers", where "the requirement is to keep the
four Z responses in phase and at the same level", and analog phase control "may not be able to
operate correctly past the first flexible body resonance". In an eight-actuator sweep of a dummy
mass in the Y axis, "the Z-axis drives are now out of phase in pairs", which the authors credit with
cancelling the roll from the overturning moment. And of sine on random: "Those who have conducted
single-shaker tests using swept-sine-on-random or mixed-mode profiles know the difficulties that
can be encountered in trying to accurately control moving and sometimes overlapping sine tones and
harmonics. Now expand this concept to multiple shakers and even multiple axes and throw in the need
for realizable and achievable phase control with cross-coupling compensation." Their papers on
rectangular control, on response limiting during multi-shaker testing, and on an eight-actuator
satellite qualification system exist; we did not obtain them.

**A vendor page.** Data Physics' page on multi-shaker control, fetched on 2026-11-15, describes
"Realtime active notching, optimized to maintain stability and minimize overshoot"; "Preemptive
notching begins notching when a notch channel's slope indicates it will soon exceed its profile",
"preventing all control/limit channels from even reaching +3dB of the reference/notch profile. The
only phase excursions happen when notching dips the control amplitude into the noise"; and a
two-shaker case where "Two control points were controlled to be kept in-phase near the armature's
attachment points. Notching was applied to off-axis accelerometers." No method is given. Other vendor text this project
had read earlier could not be found again when checked, and we do not quote it.

**An open controller.** The open-source multi-axis vibration controller of Sandia National
Laboratories is described in a 2021 paper (Rohe, Schultz and Hunter) that covers random, transient
and time-history environments and no sine control, and in 2022 course slides (Rohe 2022) that list "Plans to
expand to MIMO Sine". We did not read its source code or documentation.

**Facilities.** The NASA Mechanical Vibration Facility "can support up to eight drive signals (i.e.,
independent references), up to twelve control accelerometers (i.e., control inputs), up to a total
of 32 response limiting channels, and another 32 monitoring channels", and for X-axis shakes "all
twenty actuators are active and driven by eight source signals" (Staab and others 2016). Before a
sine sweep "a low level random pretest characterization test run is performed with the 8 drive
signals being uncorrelated so the MVF vibration controller can identify the dynamics of the
integrated system" (Winkel and others 2017). Qiu and others (2022) survey several facilities:
ESTEC's four-shaker QUAD "sends one drive signal at the input of the amplifiers which is common to
the four systems", with an analog phase control unit "within +/-4 deg"; a dual-shaker system of two 200 kN shakers at BISEE in China, "within +/-10
deg"; BISEE's four-shaker 1400 kN system, "within +/-5 deg", whose phase control unit will "shut
down and decrease the drive signals quickly to zero if the phase difference among the shakers
beyond the abort value". Of the Mechanical Vibration Facility they write that its controller "must
cancel any cross axis or rotational vibration induced by load imbalance or structural resonance by
setting the other unwanted reference spectrum at a very low level", and that it is "capable of both
acceleration and force limiting". The design paper for ESTEC's hydraulic six-axis shaker (Brinkman
and Kretz 1992) describes sine and sine sweep among its test modes, an accuracy of "± 2,5 % of the
input signal", and on-line detection of the test item's "resonance frequencies ... to reduce the
input level automatically (notching)"; it is a design-stage text. None of these papers states the
control law used or reports the control error through a resonance.

**Talks.** Raman Sridharan of Data Physics taught a two-hour course, "Introduction to Multi-Shaker
Testing", at the 94th Shock and Vibration Symposium (2024), and gave a talk at the 34th Aerospace
Testing Seminar (2025) on coupled multi-actuator sine testing at the Mechanical Vibration Facility.
We found only the event listings; their content is not published.

**Swept sine controlled on a flexible article.** The only published account we found is in
Underwood and Keller (2001): "We also ran some MIMO-sine tests with four shakers. In this case the
aluminum plate was not as rigidly attached to the shakers." The plate is "approximately 2 ft
square", on "four mini electrodynamic shakers", swept from 5 to 80 Hz, and the results are given as
plots of control and drive amplitude and phase, with no tolerance stated and nothing said about
level. It is a laboratory demonstration, not a qualification test. In my experience, multi-shaker
swept sine controlled at points on a flexible test article has not been tried much. What I have run
is sine on random with several shakers, with the sweep controlled at fairly rigid fixture points.

## 5. Sweep Rate, Resonance and the Control Loop

A swept tone passes through a resonance in a few seconds, and a lightly damped resonance needs time
to build up. This section puts the published results on that into one set of numbers a test
engineer can check with a stopwatch, and then asks what that means for a control loop. The steps
that are published are cited; the others are our own arithmetic, and are marked so.

**Seconds inside the bandwidth (ours).** A logarithmic sweep at $s$ octaves a minute changes
frequency at $\dot{f} = f s \ln 2 / 60$ hertz a second. A mode at $f_r$ with quality factor
$Q = 1/(2\zeta)$, where $\zeta$ is its damping ratio, has a half-power bandwidth $f_r / Q$: the band
over which its response is within 3 dB of the peak. The tone spends

$$T_b = \frac{f_r / Q}{\dot{f}} = \frac{60}{Q\, s \ln 2} \approx \frac{86.6}{Q\, s} \text{ seconds}$$

inside that band, the same at every frequency: 1.7 s for a $Q$ of 50 at one octave a minute. The
number of cycles inside it, $f_r T_b$, grows with frequency: 17 at 10 Hz, 173 at 100 Hz. ECSS-E-HB-
10-03A (A.7.3.3) prints the same arithmetic: "1 octave per minute means 8,66 cycles per 0,1 Hz".

**The mode's own time constant (ours).** A mode's free response decays as $e^{-\zeta \omega_r t}$, so
its amplitude time constant is $\tau_m = 1/(\zeta \omega_r) = Q/(\pi f_r)$: 1.6 s at 10 Hz and
0.40 s at 40 Hz for a $Q$ of 50. It is roughly the time the mode takes to build up to a new steady
amplitude.

**How many time constants the mode gets (ours, tied to a published parameter).** The ratio

$$N = \frac{T_b}{\tau_m} = \frac{60 \pi f_r}{Q^2 s \ln 2} \approx \frac{272 f_r}{Q^2 s}$$

is the number of its own time constants the mode is given while the tone is inside its bandwidth.
It is the published sweep parameter in other words. Davis, Durham and Brown (2010, Eq. 10) plot the
ratio of a single mode's peak swept response to its steady response against
$\eta = Q^2 K / (60 f_n^2)$, with $K$ the sweep rate in hertz a minute, and find the curve
"insensitive to changes in oscillator natural frequency and damping, provided the damping ratio is
low (< 0.03)"; they give the curve as consistent with the earlier work of Lollock (2002), which we
did not read. With $\dot{f} = K/60$, $\eta = Q^2 \dot{f} / f_r^2$ and $N = \pi / \eta$. Applying
Davis's parameter, written for a linear sweep, at the local rate of a logarithmic sweep is our step;
Cronin (1965, read as its abstract only) reports that resonant behaviour depends mainly on the rate
of change of frequency at the resonance. The ECSS loads handbook uses
$\eta_E = (R \ln 2 / 60)/(f_k \zeta_k^2)$ with $R$ in octaves a minute (ECSS-E-HB-32-26A, 5.2.3.3),
which is four times Davis's $\eta$ (our derivation; same physics, a different constant).

**Table 4.** Time inside the half-power bandwidth and the number of the mode's time constants it
spends there, for a $Q$ of 50 (ours). The last column is the frequency below which $N$ is under 2;
for another $Q$ it is $Q^2 s / 136$ hertz.

| Octaves a minute | Seconds in bandwidth | $N$ at 10 Hz | $N$ at 40 Hz | $N$ at 100 Hz | $N$ under 2 below |
|---|---|---|---|---|---|
| 0.5 | 3.5 | 2.2 | 8.7 | 22 | 9 Hz |
| 1 | 1.7 | 1.1 | 4.3 | 11 | 18 Hz |
| 2 | 0.87 | 0.54 | 2.2 | 5.4 | 37 Hz |
| 4 | 0.43 | 0.27 | 1.1 | 2.7 | 74 Hz |

![A log-log plot of N, the mode's time constants spent inside its half-power bandwidth, against frequency from 5 to 500 Hz, for a Q of 50. Four straight parallel lines rise with frequency: 0.5 octaves a minute (blue solid line, circles), 1 octave a minute (orange dashed line, squares), 2 octaves a minute (green dash-dot line, triangles) and 4 octaves a minute (purple dotted line, diamonds). A horizontal gray band below N = 2 is labeled "N under 2: the mode does not settle; its peak comes late and low". A dashed black horizontal line at N = 3.5 is labeled "ISO 7626-2 limit, N = 3.5". At 40 Hz the lines read 8.7, 4.3, 2.2 and 1.1.](figures/fig2_sweep_time_constants.png)

**Figure 2.** How many of its own time constants a mode with a $Q$ of 50 is given inside its
half-power bandwidth, against frequency, at four sweep rates (ours, $N = 272 f / (Q^2 s)$). The
dashed line is the ISO 7626-2:1990 limit in the same terms. Data: `data/fig2_sweep_n.csv`; code:
`code/fig2_sweep_time_constants.py`.

**What the structure does when $N$ is small (published).** ECSS-E-HB-32-26A (5.2.3.3): "A frequency
sweep decreases the amplitude of the peak, shifts the position of the peak along the direction of
the sweep, broadens the peak width and distorts the shape of the peak", effects "proportional to the
sweep rate, R, and inversely proportional to the natural frequency f k and (approximately) to the
square of the damping". For a mode at 10 Hz with a $Q$ of 50 swept at one octave a minute
($N$ = 1.1 in Table 4), the handbook reports that the frequency and damping identified from the swept
response by the half-power method have "2 % error in frequency but over 70 % error in damping".
ISO 7626-2:1990 (clause 9.2.3, read through IS 14736 (Part 2):1999, which states it is identical)
requires a measurement sweep slow enough that, within 10 percent of a resonance, the measured
response "is within 5 % of the true value": no faster than $54 f_n^2 / Q^2$ hertz a minute for a
linear sweep and $77.6 f_n / Q^2$ octaves a minute for a logarithmic one. In the terms above that
is $\eta$ under 0.9, or $N$ over 3.5 (ours). For a 40 Hz mode with a $Q$ of 50 it allows 1.2
octaves a minute.

**The rates tests are run at (published, and my experience).** IEC 60068-2-6 asks for one octave a
minute. ECSS-E-ST-10-03C Rev.1 asks for 2 octaves a minute at qualification and 4 at acceptance and
protoflight. ECSS-E-HB-10-03A (A.7.3.3) says "A high sweep rate (e.g. up to 4 octaves/min) is
selected to reduce the number of cycles when the flight hardware is tested", and also that "A low
sweep rate usually makes the control easier and leads to higher amplification on the modes. To
solve control issues, it is possible to modify the sweep rate locally around a mode". In my
experience 4 octaves a minute is not unheard of, but it is at the upper end for aerospace testing.
Table 4 shows what those rates mean for a lightly damped mode: at 2 octaves a minute $N$ for a mode
with a $Q$ of 50 is under 2 below 37 Hz, so a test article whose first modes are in the tens of hertz
is swept through them before they settle.

**What a correction-only loop can and cannot do (ours).** A law of Section 3.1 or 3.3 holds the
control by correcting the error after it is measured. Inside the bandwidth, the drive that would
hold the control turns through 90 degrees and changes by 3 dB on each side of its minimum, a
relative change of about 2 over the time $T_b$, faster than anywhere else in the sweep. A
correction that removes the error with a time constant $\tau$ (for the laws above,
$\tau = \Delta t / g$, with $\Delta t$ the time between updates) follows a drive that changes at
that rate with a standing error of about $2\tau / T_b$ of the reference, which is
$2 (\tau / \tau_m) / N$. The loop cannot be made fast enough to shrink that freely: a correction
faster than the mode can respond reads the mode's own build-up as error, which is the assumption
Musella and others name in Section 3.3. With the loop held to between one and two of the mode's
time constants, a correction alone leaves a standing error of roughly $2/N$ to $4/N$ of the
reference.

How fast the loop may safely run is our round figure, not a published one, so read this as an
order of magnitude. At 40 Hz, a $Q$ of 50 and one octave a minute ($N$ = 4.3) it is half to nine
tenths of the reference. For an error near a tenth of the reference (about 1 dB), $N$ must be 20
to 40, which for a $Q$ of 50 at one octave a minute means above about 180 to 370 Hz, and twice
that at 2 octaves a minute. A correction alone cannot hold a lightly damped mode below a few
hundred hertz at the rates tests are run, and no setting of its gain changes that.

**Carrying the drive along the sweep.** In my experience it is common practice with one shaker to
move the drive ahead of the error: as the tone moves, the controller changes the drive by what the
measured frequency response predicts, and the correction takes care of the rest. The usual control
setting is the share of the drive's change that is taken from the measured response. We found no
published multi-shaker sine law that says how its model, its gain or its correction is carried from
one frequency to the next during a continuous sweep, and Musella and others state that no link
between convergence and sweep rate had been made. Where $N$ is small a carried drive is not enough
either, because the structure is not in the steady state that any model of $C = H D$ describes: in
the handbook's case above ($N$ = 1.1) the frequency of the peak is 2 percent off, which for a $Q$
of 50 is one whole bandwidth. Slowing the sweep around the mode, as the ECSS handbook suggests, is
the remedy that is published.

## 6. Limits and Notching With Several Shakers

A **limit channel** is an accelerometer or force gauge, not a control, with a bound the test must
not exceed; **notching** is "reduction of the input level or spectrum to limit structural responses
at resonant frequencies according to qualification or acceptance loads" (ECSS-E-ST-10-03C Rev.1,
3.2.15). The standard asks that "Notching criteria and implementation shall be approved by the
customer" and that "Automatic protection measures shall be implemented during the test to prohibit
excessive resonance build-up leading to hardware damage", "by means of abort and notch
accelerometers control" (6.5.2.8). IEC 60068-2-6 (4.2.2) states the multi-reference rule for
limiting: "All control signals shall be beneath their appropriate reference". The ECSS testing
handbook warns that "Increasing the number of channels in the control loop can slow down and degrade
the control" and recommends "not to change the parameters for high vibration levels if they have
not been tested at lower level" (A.7.3.2). All of this is written for one shaker.

With one shaker there is one drive to lower. With several, a limit can be met in more than one way:
lower every drive together, lower only the drives that excite the limit channel, or change the
reference so that the controls ask for less of the motion that loads the limit point. Each changes
the test differently. What is published:

- Underwood, Keller and Ayres (2017): "to preserve the prespecified coherence and phase
  relationships between control-channels, it was sufficient to reduce the magnitude of either the
  reference vector or the reference spectral density ... at those frequencies where a limit level is
  being exceeded. Additionally, this limit control method can be used for both MIMO random and MIMO
  sine applications"; the method "reduces the magnitude of the reference the controller is using in
  proportion to the particular limit exceedance". That is one factor applied to the whole reference,
  chosen because it keeps the relative phases. Their results are shown for random.
- Underwood and Keller (2001): channels beyond one per shaker used for "limit control of amplitudes,
  without affecting the phase parameters".
- Data Physics (page fetched 2026-11-15): real-time and preemptive notching, the latter starting
  "when a notch channel's slope indicates it will soon exceed its profile", with phase excursions
  only "when notching dips the control amplitude into the noise".
- Brinkman and Kretz (1992): on-line resonance detection to reduce the input automatically, at the
  design stage.

We found no published equation for how a multi-shaker sine controller shares a notch among its
drives, and none for changing the reference's amplitudes and relative phases to hold a limit with
the least change to the test. Nor did we find a published law for a tracked resonance dwell with
several shakers in environmental testing.

## 7. What Other Fields Know About Holding a Tone With Several Actuators

Holding a tone with several actuators is an old problem outside vibration testing. Active noise and
vibration control cancels a tone at several microphones or sensors with several loudspeakers or
actuators; helicopter higher harmonic control cancels the rotor's tonal vibration in the cabin by
pitching the blades; magnetic bearing controllers cancel a rotor's unbalance response at the running
speed. All three use the same structure as a sine test controller: a known frequency, a matrix of
responses from the actuators to the sensors at that frequency, and an update of the actuator
amplitudes and phases from the measured error, with the matrix known only approximately. The
condition for such an update to converge when its matrix is wrong is printed in sources we read:

- **One channel, small gain, model identified as it runs.** The update converges if and only if the
  phase difference between the model and the true response is less than 90 degrees: "the difference
  of phase between the estimated plant model and the true plant dynamics must be less than
  90°", and "the instability for phase difference greater than 90° is only local" (Pigg
  and Bodson 2011, Eq. 18; "plant" is their word for the system being controlled).
- **Several channels, small gain.** Wu and Bodson (2004) give the averaged form for several
  channels: the eigenvalues of the true response matrix times the correction matrix must have
  positive real parts, which with one channel is the 90 degree condition.
- **Several channels, a full step.** For the harmonic steady-state update of helicopter control,
  "the HSS algorithm is stable if and only if" the spectral radius of the correction matrix times
  the model error is below one (Chandrasekar and others 2004, Eq. 5.8).
- **One channel, a full step, by hand.** Johnson (1982) states that the estimate "must have the same
  sign and at least 50% the magnitude of the true value". He also describes, from earlier
  work by Shaw, a fixed-gain controller that became unstable when the response matrix changed with
  flight speed and was made stable by identifying the matrix as it flew.
- **Through a critical speed.** Knospe and others (1994) carried a rotor's unbalance control through
  two critical speeds, 2700 and 4200 rpm, in a 30 s run-up from 1500 to 5000 rpm, using gain
  matrices tabulated by speed and interpolated between them. A single gain designed at 2200 rpm
  went unstable above 2500 rpm, because "the T matrix changes rapidly with speed near the first
  critical". Knospe and Tamer (1996) instead designed fixed gains to tolerate a range of speed, with
  design goals of 1.17 to 1.51 for the ratio of the vibration under the tolerant gain to that under
  the best gain, over ranges of plus or minus 20 to 45 percent; only the widest range spanned the
  first critical speed.

The classic papers on multichannel active control with an error in the model (Elliott, Boucher and
Nelson 1992; Boucher, Elliott and Nelson 1991) were read as abstracts only, and we do not attribute
the condition to them. The helicopter and rotor results matter here for a plain reason: a rotor run
up through a critical speed is a sweep through a resonance, and the response matrix changes fastest
where the mode is.

## 8. A Tone on a Structure That Changes With Level

Bolted joints, friction interfaces and thin members make a structure's resonances move with the
level of the test: down and with more damping as joints slip, up as a thin member stretches. The
field of nonlinear vibration testing holds a tone on such a structure with feedback, and its
methods are close to what a sine controller would need.

**Phase-locked loops** adjust the frequency until the phase between response and excitation equals a
set value, which tracks a nonlinear resonance as the level changes. Hippold and others (2024) track
a backbone curve with "only about 100 periods" per point, and note that earlier loop settings had
been chosen "in a strictly heuristic way"; their tests use one shaker. In a companion method,
Hippold and others (2025) remove the unwanted harmonics of the applied excitation with an integral
loop on each harmonic; the loop's stability sign "may change when Ω is varied around resonance",
and the remedy they give is a large enough proportional gain and a light exciter against the mode's
damping, chosen through the exciter and drive point. They state that their method is restricted to
an imposed excitation frequency. It uses one exciter.

**Control-based continuation** follows a branch of periodic responses, stable or not, with a feedback
controller. Sieber and Krauskopf (2008) introduced it on a simulated, autonomous dry-friction
oscillator; it "does not require a mathematical model" and "relies on feedback stabilizability".
Abeloos and others (2021) made it stepped and swept with an adaptive filter, and show that a large
enough derivative gain gives "a unique, stable" orbit.

**Response-controlled stepped sine** holds the response amplitude at the drive point constant, which
"yields quasi-linear frequency response functions directly" (Karaağaçlı and Özgüven 2021). The
authors state that it "can also be applied by using multi-point excitation", in theory, and that near
a turning point a "standard force-controller cannot avoid jumping from one stable branch to another".
A review of experimental continuation (Raze, Abeloos and Kerschen 2025) finds that the method
"was not able to stabilize unstable" solutions, and notes that "an adaptation for multi-input-multi-
output test case was sketched" in a 2020 conference paper (Tang, Stephan and Boeswald 2020), which
we read as an abstract only: it extends a single-input phase-locked loop to several inputs by modal
blending, to find the phase resonance of one mode. Peeters and others (2011) name "a more general
constructive procedure for NNM force appropriation, resorting to several shakers with harmonics of
the fundamental frequency" as future research. Peter and Leine (2017), Denis and others (2018) and
Renson and others (2016) were read as abstracts only.

Worded to our search: every phase-locked loop, continuation and response-controlled experiment we
read uses one exciter, and we found nothing that holds a specified amplitude at several points with
several exciters through a nonlinear resonance.

**How far a resonance may move under a low-level model (ours).** Sections 3 and 7 meet here. Take one
mode, its damping unchanged, whose resonance at test level sits $\delta$ half-power bandwidths away
from where the low-level model put it. Near a resonance the phase of the response turns through 180
degrees over a few bandwidths, following $\arctan$ of the distance from the resonance in
half-bandwidths. The model's phase and the structure's phase then differ most midway between the
two resonances, by

$$\theta_{max} = 2 \arctan(\delta),$$

which is 53 degrees at half a bandwidth, 90 degrees at one bandwidth and 127 degrees at two. By the
one-channel, small-gain condition of Pigg and Bodson, a correction through the low-level model stops
converging near that midpoint once the resonance has moved about one half-power bandwidth, and the
fixed-inverse law of Section 3.1 has no positive gain left there. We give this as the one-channel
condition; we do not claim it as a general result for several channels, where the eigenvalues of
Section 7 decide. One half-power bandwidth is a small move: 2 percent of the frequency for a $Q$ of
50 and 1 percent for a $Q$ of 100. For scale only, the ECSS standard accepts shifts under 5 percent
between the resonance searches before and after a test (Table 1), which for a $Q$ of 50 is 2.5
bandwidths. The 1990 patent's background speaks of negative gains beyond 90 degrees, and the patent
adapts its model during the test.

![A line plot of the largest phase difference between a low-level model and the structure, in degrees from 0 to 180, against how far the resonance has moved, in half-power bandwidths from 0 to 5. A single blue solid curve, 2 arctan of the shift, rises steeply from 0 and bends over toward 180 degrees, passing 53 degrees at 0.5, 90 degrees at 1 and 127 degrees at 2. A dashed black horizontal line at 90 degrees is labeled "90 degrees: a one-channel correction stops converging". Three open orange markers on the curve, with labels, show where a 1 percent shift falls for a Q of 25 (0.25 bandwidth, 28 degrees), 50 (0.5, 53 degrees) and 100 (1.0, 90 degrees).](figures/fig3_phase_vs_shift.png)

**Figure 3.** The largest phase difference between a model measured before a resonance moved and the
structure after it moved, against the move in half-power bandwidths (ours, $2 \arctan\delta$, one
mode, damping unchanged). The markers show a 1 percent frequency shift at three values of $Q$. Data:
`data/fig3_phase_vs_shift.csv`; code: `code/fig3_phase_vs_shift.py`.

## 9. Where the Published Work Stops

Each statement is worded to the searches in Section 10; a wider search may find what ours did not.

1. **Few laws, little evidence.** Five published forms, four of which correct through a model
   measured once at a low level. The evidence is one two-axis table test that missed tolerance near
   the table's own modes at 80 Hz, a two-shaker beam controlled in amplitude only, a cantilever beam
   under sine plus random, a simulation of two uncoupled shakers, and a run-to-run correction on two
   axes of a three-axis shaker. The one law that changes its model during the test has no published
   test of its printed equations.
2. **No published result on a structure whose resonances move with level** under closed-loop
   multi-shaker sine control.
3. **The model along a sweep.** No published law says how its model, gain or correction is carried
   from one frequency to the next in a continuous sweep, and no published analysis ties the speed of
   the correction to the sweep rate for several shakers.
4. **Control on a flexible article.** One laboratory account (four small shakers under an aluminium
   plate, 5 to 80 Hz, figures only). No account of a qualification test controlled at points on a
   flexible article that reports tolerances through resonance or resonances that moved with level.
5. **Limits and notching.** Published behaviour (scale the whole reference; notch early from a
   slope), and no equation for sharing a notch among several drives or reshaping the reference to hold
   a limit, for sine.
6. **Standards.** No sine clause for several exciters and no tolerance on relative phase in the
   standards read.
7. **Sweep effects.** Published for one mode and one exciter (ECSS, Davis and others, ISO 7626-2);
   nothing for several drives or for a resonance that moves with level.
8. **Nonlinear structures.** Phase-locked loops, continuation and response control are published for
   one exciter; nothing found holds amplitude at several points with several exciters through a
   nonlinear resonance.
9. **Free relative phases.** Amplitude-only references are used (Section 3.4), but no published law
   chooses the free phases, for example for the least drive or for continuity along the sweep.

## 10. Limits of This Survey

The search was made in one research effort, with general web search, publisher and repository pages,
the NASA Technical Reports Server, OSTI, Crossref, Google Patents and the Internet Archive. We had no
subscription databases (no Scopus, Web of Science, Compendex or Google Scholar access), and we did
not search the proceedings of IMAC, ISMA, the Shock and Vibration Symposium, the Aerospace Testing
Seminar, ESTECH or the European Conference on Spacecraft Structures, Materials and Environmental
Testing beyond what general search returned. Patents were searched with three Google Patents queries
only. A statement here that something was not found is limited to that search.

Each source is marked by how much of it we read. Read as abstracts only: Ma, Chen and Zheng (2022;
2024); Tang, Stephan and Boeswald (2020); Peter and Leine (2017); Denis and others (2018); Renson and
others (2016); Elliott, Boucher and Nelson (1992); Boucher, Elliott and Nelson (1991); Cronin (1965).
Read in part: Underwood, Keller and Ayres (2017), from section G to the end; Musella and others
(2020), through page summaries, so we cite it in words and not for its equations; the IEC standard,
through its free preview. Not obtained: Lollock (2002); Underwood and Keller's papers on rectangular
control, response limiting and the eight-actuator system; the early multi-shaker sine papers of the
1970s; the NASA and Air Force standards and handbooks named in Section 2; the 2015 edition of
ISO 7626-2. ISO 7626-2:1990 was read through its Indian adoption, which states it is identical. Two
vendor pages that had been read earlier were gone or changed when checked again, and are not quoted.

This is a survey. It does not propose, rank or score control laws; candidate laws and the ideas that
did not work are the subject of separate articles in preparation. The numbers marked as ours are
arithmetic on one mode, shown in full, and have not been compared with a test.

## How This Was Made

AI tools were used in this work. The searches, the reading of sources, the arithmetic, the figure
code and the drafting of the text were done with Claude Code, an AI coding assistant running
Anthropic's Claude models, under Kevin Cross's direction; the author is responsible for every
word, number and line of code.

## Acknowledgments

This survey rests on the published work of others, credited by name: the authors of the control laws
(Underwood; Musella, Peeters, Marulo, Guillaume and co-authors; Qiu, Feng and co-authors; Zhang,
Chen, He, Wang and Zeng; Zheng, Chen and Luo; Ma, Chen and Zheng), the vendor articles of Underwood,
Keller and Ayres, and the open multi-axis controller of Sandia National Laboratories (Rohe and
Schultz of Sandia National Laboratories, with Hunter). The facility accounts are the published work
of NASA's Glenn Research Center and their co-authors (Staab, Winkel and others), of ESA's ESTEC
(Brinkman and Kretz), and of Qiu and others on the facilities in Europe and China. The sweep-rate
results are from Davis, Durham and Brown of NASA's Marshall Space Flight Center, the ECSS handbooks
and ISO 7626-2. The work from other fields is that of Bodson, Pigg and Wu; Chandrasekar, Liu, Patt,
Friedmann and Bernstein; Johnson of NASA; Knospe and co-authors; and, in nonlinear testing, Hippold,
Krack and co-authors, Sieber and Krauskopf, Abeloos, Raze, Kerschen and co-authors, Karaağaçlı and
Özgüven, and Peeters, Kerschen and Golinval.

## References

- Abeloos, G., Renson, L., Collette, C., Kerschen, G. (2021). Stepped and swept control-based
  continuation using adaptive filtering. Nonlinear Dynamics 104(4), 3793-3808.
  DOI 10.1007/s11071-021-06506-z.
- Boucher, C. C., Elliott, S. J., Nelson, P. A. (1991). Effect of errors in the plant model on the
  performance of algorithms for adaptive feedforward control. IEE Proceedings F 138(4), 313-319.
  DOI 10.1049/ip-f-2.1991.0042. Read as an abstract.
- Brinkman, P. W., Kretz, D. (1992). The design concept of the 6-degree-of-freedom hydraulic shaker
  at ESTEC. The Seventeenth Space Simulation Conference: Terrestrial Test for Space Success, NASA
  Goddard Space Flight Center. NTRS 19930006411.
- Chandrasekar, J., Liu, L., Patt, D., Friedmann, P. P., Bernstein, D. S. (2004). Adaptive harmonic
  steady state control for disturbance rejection. Proceedings of the 2004 American Control
  Conference, 1247-1252. DOI 10.23919/ACC.2004.1386744.
- Cronin, D. L. (1965). Response of linear, viscous damped systems to excitations having
  time-varying frequency. California Institute of Technology, Dynamics Laboratory report
  (CaltechEERL:1965.DYNL.1965.003). Read as an abstract.
- Data Physics. Advanced multi-shaker control technologies. dataphysics.com/?p=713, fetched
  2026-11-15.
- Davis, R. B., Durham, R. C., Brown, A. M. (2010). The response of a mechanical oscillator due to
  swept and dithered excitation. NASA Marshall Space Flight Center, NTRS 20100021009.
- Denis, V., Jossic, M., Giraud-Audine, C., Chomette, B., Renault, A., Thomas, O. (2018).
  Identification of nonlinear modes using phase-locked-loop experimental continuation and normal
  form. Mechanical Systems and Signal Processing 106, 430-452. DOI 10.1016/j.ymssp.2018.01.014. Read
  as an abstract.
- ECSS-E-HB-10-03A (2022). Space engineering: Testing guidelines. 31 May 2022.
- ECSS-E-HB-32-26A (2013). Space engineering: Spacecraft mechanical loads analysis handbook.
  19 February 2013.
- ECSS-E-ST-10-03C Rev.1 (2022). Space engineering: Testing. 31 May 2022.
- Elliott, S. J., Boucher, C. C., Nelson, P. A. (1992). The behavior of a multiple channel active
  control system. IEEE Transactions on Signal Processing 40(5), 1041-1052. DOI 10.1109/78.134467.
  Read as an abstract.
- Hippold, P., Kleyman, G., Woiwode, L., Wei, T., Müller, F., Schwingshackl, C., Scheel, M.,
  Tatzko, S., Krack, M. (2025). An iteration-free approach to excitation harmonization. Mechanical
  Systems and Signal Processing 233, 112732. DOI 10.1016/j.ymssp.2025.112732. arXiv 2410.17830.
- Hippold, P., Scheel, M., Renson, L., Krack, M. (2024). Robust and fast backbone tracking via
  phase-locked loops. Mechanical Systems and Signal Processing 220, 111670.
  DOI 10.1016/j.ymssp.2024.111670. arXiv 2403.06639.
- IEC 60068-2-6:2007, Edition 7.0. Environmental testing, Part 2-6: Tests, Test Fc: Vibration
  (sinusoidal). Read through the free preview.
- ISO 7626-2:1990. Vibration and shock: Experimental determination of mechanical mobility, Part 2:
  Measurements using single-point translation excitation with an attached vibration exciter. Read
  through IS 14736 (Part 2):1999, which states that it is identical.
- Johnson, W. (1982). Self-tuning regulators for multicyclic control of helicopter vibration. NASA
  Technical Paper 1996, NTRS 19820012314.
- Karaağaçlı, T., Özgüven, H. N. (2021). Experimental modal analysis of nonlinear systems by using
  response-controlled stepped-sine testing. Mechanical Systems and Signal Processing 146, 107023.
  DOI 10.1016/j.ymssp.2020.107023.
- Knospe, C. R., Hope, R. W., Fedigan, S. J., Williams, R. D. (1994). New results in the control of
  rotor synchronous vibration. Fourth International Symposium on Magnetic Bearings, ETH Zurich,
  119-124.
- Knospe, C. R., Tamer, S. M. (1996). Experiments in robust unbalance response control. Fifth
  International Symposium on Magnetic Bearings, Kanazawa.
- Lollock, J. A. (2002). The effect of swept sinusoidal excitation on the response of a single
  degree-of-freedom oscillator. 43rd AIAA/ASME/ASCE/AHS/ASC Structures, Structural Dynamics, and
  Materials Conference, AIAA 2002-1230. Not read; cited as Davis and others cite it.
- Ma, Y., Chen, H., Zheng, R. (2022). Control strategy for multi-axial swept sine on random mixed
  vibration testing. Journal of Sound and Vibration 527, 116846. DOI 10.1016/j.jsv.2022.116846. Read
  as an abstract.
- Ma, Y., Chen, H., Zheng, R. (2024). Investigation of multi-input multi-output sine on random mixed
  vibration control. Proceedings of the Institution of Mechanical Engineers, Part C 238(12),
  5565-5579. DOI 10.1177/09544062231219544. Read as an abstract.
- MIL-STD-810H (2019). Environmental Engineering Considerations and Laboratory Tests, Methods 514.8
  and 527.2. 31 January 2019.
- Musella, U., Longo, R., Vettori, S., Waimer, S., Di Lorenzo, E., Peeters, B., Marulo, F.,
  Guillaume, P. (2018). Recent advances in swept sine controlled excitation and processing for MIMO
  FRFs estimation. Proceedings of ISMA 2018, Leuven.
- Musella, U., Peeters, B., Marulo, F., Guillaume, P. (2020). Multi-input multi-output swept sine
  control: a steepest descent solution for a challenging problem. In Special Topics in Structural
  Dynamics and Experimental Techniques, Volume 5 (Conference Proceedings of the Society for
  Experimental Mechanics), 83-94. DOI 10.1007/978-3-030-12243-0_13. Read in part.
- Musella, U., Waimer, S., Peeters, B., Marulo, F., Guillaume, P. (2019). Development of a
  steepest-descent control solution for multi-input multi-output swept sine testing in a virtual
  shaker environment. Journal of Physics: Conference Series 1264, 012002.
  DOI 10.1088/1742-6596/1264/1/012002.
- Peeters, M., Kerschen, G., Golinval, J. C. (2011). Modal testing of nonlinear vibrating structures
  based on nonlinear normal modes: experimental demonstration. Mechanical Systems and Signal
  Processing 25(4), 1227-1247. DOI 10.1016/j.ymssp.2010.11.006.
- Peter, S., Leine, R. I. (2017). Excitation power quantities in phase resonance testing of nonlinear
  systems with phase-locked-loop excitation. Mechanical Systems and Signal Processing 96, 139-158.
  DOI 10.1016/j.ymssp.2017.04.011. Read as an abstract.
- Pigg, S., Bodson, M. (2011). Adaptive harmonic steady-state disturbance rejection with frequency
  tracking. Asian Journal of Control, preprint. A version was presented at the 49th IEEE Conference
  on Decision and Control (2010), 887-892, DOI 10.1109/CDC.2010.5717729.
- Qiu, H., Feng, Y., Fan, S., Du, X., Zhang, W. (2019). Study on multi-axis sine vibration test
  control techniques. Vibroengineering Procedia 28, 46-51. DOI 10.21595/vp.2019.21011.
- Qiu, H., Feng, Y., Liu, C., Li, X., Fan, S., Li, S., Sun, T. (2022). Investigation of in-phase
  vibration control technology for large multi-shaker test facility. Vibroengineering Procedia 42,
  33-38. DOI 10.21595/vp.2022.22486.
- Raze, G., Abeloos, G., Kerschen, G. (2025). Experimental continuation in nonlinear dynamics: recent
  advances and future challenges. Nonlinear Dynamics 113(6), 4949-4997.
  DOI 10.1007/s11071-024-10543-9. Read as arXiv 2408.00138.
- Renson, L., Gonzalez-Buelga, A., Barton, D. A. W., Neild, S. A. (2016). Robust identification of
  backbone curves using control-based continuation. Journal of Sound and Vibration 367, 145-158.
  DOI 10.1016/j.jsv.2015.12.035. Read as an abstract.
- Rohe, D. P., Schultz, R., Hunter, N. (2021). Rattlesnake: an open-source multi-axis and combined
  environments vibration controller. SAND2021-13012C, OSTI 1893280.
- Rohe, D. P. (2022). Rattlesnake: a custom combined-environments vibration controller with
  flexible control strategies. IMAC XL MIMO Vibration Short Course, slides. SAND2022-1034C,
  OSTI 2001671.
- Sieber, J., Krauskopf, B. (2008). Control based bifurcation analysis for experiments. Nonlinear
  Dynamics 51(3), 365-377. DOI 10.1007/s11071-007-9217-2.
- Staab, L. D., Winkel, J. P., Suarez, V. J., Jones, T. M., Napolitano, K. L. (2016). Fixed base modal
  testing using the NASA GRC Mechanical Vibration Facility. International Modal Analysis Conference.
  NTRS 20160001308.
- Tang, M., Stephan, C., Boeswald, M. (2020). Phase resonance method for nonlinear mechanical
  structures with phase locked loop control. Proceedings of ISMA 2020 and USD 2020, Leuven,
  1805-1818. Read as an abstract.
- Underwood, M. A. (1994). Adaptive control method for multiexciter sine tests. US Patent 5,299,459,
  filed 1990, granted 5 April 1994.
- Underwood, M. A., Keller, T. (2001). Recent system developments for multi-actuator vibration
  control. Sound and Vibration, October 2001.
- Underwood, M. A., Keller, T., Ayres, R. (2017). Multi-shaker control: a review of the evolving
  state-of-the-art. Sound and Vibration, August 2017. Read in part.
- Winkel, J. P., Akers, J. C., Suarez, V. J., Staab, L. D., Napolitano, K. L. (2017). Fixed base modal
  survey of the MPCV Orion European Service Module structural test article. SEM International Modal
  Analysis Conference. NTRS 20170009147.
- Wu, B., Bodson, M. (2004). Multi-channel active noise control for periodic sources: indirect
  approach. Automatica 40(2), 203-212. DOI 10.1016/j.automatica.2003.09.014.
- Zhang, B., Chen, H., He, X. (2015). New control method for the MIMO swept-sine test (in Chinese).
  Journal of Vibration and Shock 34(8), 198-202.
- Zhang, B., Wang, R., Zeng, F. (2017). MIMO random plus sine vibration test J-impedance composite
  control algorithm (in Chinese). Journal of Vibration, Measurement and Diagnosis 37(6).
  DOI 10.16450/j.cnki.issn.1004-6801.2017.06.003.
- Zheng, W., Chen, H., Luo, Z. (2020). Multi-input-multi-output continuous swept-sine vibration test
  realization by inverse multistep prediction model. Shock and Vibration 2020, 8869802.
  DOI 10.1155/2020/8869802.
