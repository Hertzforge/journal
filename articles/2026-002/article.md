---
# Filled in by the editors at publication.
id: "2026-002"
version: 1
date: 2026-11-15
doi: "10.5281/zenodo.24252817"
doi_latest: "10.5281/zenodo.24252816"   # always resolves to the latest version
note: First published.

# Filled in by the authors.
title: "Shock Testing With Several Shakers: A Survey of Published Methods and Measurements"
type: Survey
evidence: published sources
evidence_note: "Published papers, reports, theses, standards, patents and controller makers' public pages, each read to the extent stated in its reference; no new experiments or simulations."
authors:
  - name: "Kevin Cross"
    orcid: "https://orcid.org/0009-0002-6608-9426"
implemented_in: ""
benchmarks: ""
contents: true
abstract: >
  This survey maps published work on shock testing with more than one shaker: how shock tests are
  specified, how one shaker is driven to meet a shock specification, how several shakers reproduce a
  waveform or meet a shock response spectrum (SRS) at several points, how the structures under test
  change with test level, and what learning-based methods offer. Reproducing a waveform with several
  shakers is well described for the first pulse. SRS control with several shakers is not: one patent
  application states its update law and was demonstrated at low levels, one journal paper could be
  read only as an abstract, controller makers rarely state their laws, and a published user report
  found that a commercial mode put about five times the specified peak acceleration on one axis.
  Measured frequency drops are about 0.1 to 4 % for well-tightened bolted joints at low force, about 6
  to 10 % for a lightly torqued joint, a single bolt and a press-fit foam-and-metal interface, and
  about 28 % on one beam driven into full slip, with damping rising about 1.4 to 20 times; on one
  friction interface, shaker shocks did not move the frequency that sine sweeps lowered. No
  multi-shaker SRS law tested on such a structure, no standard or tested acceptance rule for several
  control points, no rule for the timing between them, and no learned component in a multi-shaker
  shock control loop was found in a search of open English-language databases, the open web and
  patents, with a few Chinese-language web and patent queries, in November 2026. Several key papers
  could be read only as abstracts.
---

## Summary

A shock test puts a short, violent motion into a test article to show that it survives the shocks
it will see in service. Most shock tests are run on one shaker, one axis at a time. Real shocks
arrive in several directions at once, so test engineers have begun running shocks with several
shakers driving the article together. This survey sets out what has been published on doing that.

Most shocks are specified by a shock response spectrum (SRS): the peak response of a row of simple
oscillators driven by the shock. Many different waveforms share one SRS, so the standards also limit
duration. None of the standards read gives a tolerance on the timing between control points, or a
rule for accepting a shock judged at several control points with several drives; two that might
could not be read.

With one shaker, a waveform is built to match the SRS and corrected pulse by pulse as the level rises,
each correction kept smaller than the error because the structure changes with level. With several
shakers, reproducing a waveform on the first pulse is well described. Correcting between pulses is
described by controller makers in outline and in one 1979 report whose law was never run. The theory
of repeated trials gives a plain condition, proved for one drive and a linear structure: the model's
phase error must stay under 90 degrees at every frequency. Meeting an SRS at several points with
several shakers is thin in the literature.

Joints soften and gain damping as the level rises: by about 0.1 to 4 % in frequency when well
tightened, and more when loose, frictional or slipping. The few measurements made at shock level
disagree with hammer and sine tests. A model measured at low level describes the structure at low
level. Learning-based methods have not yet reached a multi-shaker shock control loop in print.

## How the Literature Was Searched and Read

**Scope.** Shock tests on electrodynamic or hydraulic shakers with more than one drive, the
single-shaker methods they build on, the standards that specify them, measurements of structures
whose response changes with test level, and learning-based methods that bear on any of these.
Resonant plates and six-degree-of-freedom tables are included as the multi-axis alternatives to
shaker shock. Seismic shaking tables and road simulators appear only as lineage.

**Search.** From 11 to 15 November 2026: OSTI (the U.S. Department of Energy's Office of Scientific
and Technical Information), Crossref, arXiv, the National Aeronautics and Space Administration's
(NASA's) Technical Reports Server, Google Patents and the open web, in English, with partial Semantic Scholar coverage, and references followed forward and
backward from the key papers. In Chinese: three web queries (27 results screened, on multi-shaker SRS
control, multi-axis shock waveform replication, and shock control patents) and one patent query.
Not searched: Google Scholar, Scopus, Web of Science, IEEE Xplore, the Chinese databases China National
Knowledge Infrastructure (CNKI) and Wanfang, the Defense Technical Information Center catalog (unavailable at the time), the full text of
SAE International and Institute of Environmental Sciences and Technology (IEST) papers, and the Shock and Vibration
Symposium archive. Where this survey says something was not found, it means not found in those
searches.

**Reading.** Each source obtained by an open route was read as text, with equations and numbers
checked on page images where needed, and its record checked against its registry. Each reference
states how much was read: in full; in part (sections named); abstract only (for a standard, the
publisher's public page and preview); or record only. A source read as an abstract is cited only for what its abstract says.
Numbers read off a figure's axis are marked "about" and given to no more than two significant figures.
Three published update laws carry a sign error in print; the text notes each, and writes the laws it
uses in the form that converges. Controller makers' pages were read on 15 November 2026.

## 1. How a Shock Test Is Specified

### 1.1 Classical Pulses

The oldest shock specification is a pulse of prescribed shape: a half-sine, a sawtooth or a
trapezoid, of stated peak and duration, inside a tolerance band. International Electrotechnical
Commission (IEC) standard 60068-2-27 (Test Ea) "is written in terms of prescribed pulse shapes" (its
scope; only its public page and preview were read). A shaker cannot end a test moving, so a classical
pulse on a shaker needs small pulses before and after it that bring the table's velocity and
displacement back to zero, which changes its SRS at low frequencies. In the U.S. Department of Defense
standard MIL-STD-810H with Change 1 (2022), Method 516.8, for functional shock, classical pulses "are unacceptable unless it can be demonstrated during tailoring that the
field shock environment time trace approximates such a form" (4.6.2).

### 1.2 The Shock Response Spectrum

A **shock response spectrum (SRS)** describes a shock by its effect rather than its waveform.
Imagine a row of simple oscillators, each a mass on a spring with a damper, each tuned to a different
natural frequency, all fixed to the point where the acceleration was measured. Drive them with the
measured acceleration and record the largest response of each. Plotted against the oscillators'
frequencies, those peaks are the SRS. The oscillators' damping is given as a quality factor Q; Q = 10
is 5 % of critical damping. A **maximax** SRS takes the largest absolute response at any time, during
or after the shock.

The SRS loses the waveform. Method 516.8 says it plainly: "There is no unique synthesized complex
transient pulse satisfying a given SRS" (2.3.3.1). Cap and Smallwood (1997) open with the
consequence: "it is commonly accepted that different agencies can generate vastly different time
domain test inputs whose SRS all satisfy the test requirements within a stated tolerance band." For
an SRS with a hump at low frequency and a lower flat plateau above it, Heitman and Cap (2019) show
that the plateau can be met "with little or no energy in that region", because the high-frequency
oscillators respond to the peak of the low-frequency motion.

Method 516.8 ranks how a shock should be run, best first: replication of a measured waveform; an SRS
from measured data; an SRS without measured data; and a classical pulse (2.3.2). An SRS from data is
computed with Q = 10 at one-twelfth-octave spacing or finer; when only one or two records exist, a
margin of 3 dB or 6 dB is added, chosen for the conservatism wanted. The tolerance (4.2.2.2) is -1.5 to +3 dB on at
least 90 % of the one-twelfth-octave points from 10 to 2,000 Hz, and -3 to +6 dB on the rest. Several
measurements in one zone may be judged by their average within stated bounds, and the standard warns
that "individual measurements may be substantially out of tolerance while the average is within
tolerance." Synthesis from an SRS "is applicable only for 'simple shocks'" (note to 2.3.1.2.3), and
splitting an SRS into a low-frequency and a high-frequency test "is unacceptable" (2.3.3.1).

### 1.3 Effective Duration

Because one SRS fits many waveforms, Method 516.8 also limits duration (Annex A 1.3). The duration
**Te** runs from the first zero crossing above the noise floor to the perceived end of the shock;
when unknown it defaults to 2.5 divided by the lowest frequency of interest. The **effective
duration TE** is the time that holds all the peaks above A/CF, where A is the largest peak and CF is
the largest crest factor found over short intervals of Te (about Te/10); CF is taken as 3 when TE is
not given. A test must hold 0.8 TE to 1.2 TE. Without measured data, TE is 2 divided by a cutoff
frequency, 45 Hz in most categories (Table 516.8-III).

### 1.4 Temporal Moments

Cap and Smallwood (1997) proposed describing a shock also by its **temporal moments**, over the
whole band or in frequency bands: the energy E (the integral of the squared acceleration), the
root-mean-square (RMS) duration D (the spread of that energy in time) and the root-energy amplitude R
(the square root of E/D), which play the parts of velocity change, pulse width and amplitude of a
classical pulse (their Appendix A, credited to Smallwood 1994, read only as an abstract). For a shaker
shock the authors offered, as a possibility, ±3 dB on the SRS, ±1 dB on E and R
in each band and ±10 % on D, and suggested the SRS tolerance might relax to ±6 dB once band moments
are held. Their Table III shows why: three inputs that all met one launch shock's SRS had energies of
45, 290 and 353 g²s against the field's 275 g²s, the shortest 7.9 dB low.

### 1.5 Waveforms

A shock can also be specified as a waveform and replicated. Method 525.2 (time waveform replication,
TWR, on one exciter) observes that the drive is compensated "by linear convolution of the exciter
system impulse response function estimate with the reference time trace", and that "The condition of
system linearity is almost never satisfied so that the reference time trace is averaged over time
through the linear convolution" (4.2.2 a). For a replicated shock it asks the SRS at 5 % damping to be
within -6 to +3 dB, and the largest positive and negative peaks (no more than 10 % of all peaks)
within ±20 % (4.2.2 c(2)). The method is not quite consistent with itself: 4.2.2 b says replication
tolerances should be no broader than those of other methods, yet -6 dB is broader on the low side
than Method 516.8's -1.5 dB.

Method 527.2 covers multi-exciter tests (METs) in two procedures: time-domain references (an
extension of TWR) and spectral references (an extension of random). There is no procedure for an SRS
specified at several points; shock enters only as a segment of a replicated waveform. The method does
not address "vendor-supplied software control strategy for a MET" (1.3 a), "generally does not
provide specific test tolerance information" (1.3 e), and states that "at this point in TWR test
philosophy, test tolerance specification is not well quantified" (Annex C 3). Annex C defines
energy-weighted global errors over all channels, including a global SRS error, with no tolerance
values.

### 1.6 Other Standards

IEC 60068-2-81:2003 (Test Ei) specifies tests with a synthesized SRS on a vibration generator with a
computer-based control system. IEST-RP-DTE022 (2014), "Multi-Shaker Test and Control", gives
recommendations for vibration or shock tests with multiple exciters. Only their public pages were
read. The North Atlantic Treaty Organization (NATO) Allied Environmental Conditions and Test
Publication AECTP-400, Method 421,
"Multi-Exciter Vibration and Shock Testing", read in its superseded 2006 edition, lists "SRS Shock
Synthesis - Tailored using wavelets, damped sinusoids or both. Different input shocks on each
exciter", takes its shock tolerances from its single-exciter methods, and says nothing about how the
shocks on each exciter should relate in time. Whether the current edition (2025) keeps the method was
not verified.

### 1.7 Several Axes at Once

Sisemore, Babuska and Flores (2020) set out what happens when three single-axis shock specifications
are run at once. Three equal shocks in phase on three axes add to a vector √3 times one of them, "a
4.78dB over-test in one direction that will not align to any of the component principal directions";
inverting one of them changes only the direction of that peak, not its size. If the specifications
describe one event measured in three axes, running them together may be acceptable, and may be more
appropriate; if they describe separate events, or the orientation is simply unknown, a simultaneous
test over-tests in some directions and under-tests in others. Hopkins and Sisemore (2019) make the
same point for a resonant plate: "if the three responses are in-phase, then the component may be
subjected to a much higher shock excitation in some arbitrary direction than in any of the three
principal directions." In the other direction, Sisemore, Babuska and Booher (2016) found that each of
the six single-axis pseudo-velocity SRS (the SRS in velocity units) of a six-degree-of-freedom shaker
shock lay well below the single-axis failure prediction for their beams, and the beams failed.

**What no standard gives.** None of the standards read gives a tolerance on the timing or phase
between control points in a shock test, and none gives an acceptance rule for a shock judged at
several control points with several drives; two that might (IEST-RP-DTE022 and the current AECTP-400)
could not be read. Method 516.8's zone average judges several measurements of one zone in a
single-exciter test, with its own warning.

## 2. Shock on One Shaker

### 2.1 Building a Waveform From an SRS

A shaker plays a waveform, so an SRS must first be turned into one, and the waveform must start and
end with the table at rest. Two building blocks are used. A **decaying sinusoid** of frequency f and
damping ratio ζ is $a(t) = A\, e^{-2\pi\zeta f t} \sin(2\pi f t)$. A **wavelet** of the kind used in
Smallwood's WAVSYN synthesis is a sine of frequency f that completes N half-cycles inside a half-sine
window, with N odd (Cap and Smallwood 1997, Eq. 3, which gives no reason for the odd N). Summing
decaying sinusoids "compensated for shaker velocity and displacement limitations" is the subject of
Smallwood and Nord (1974); that paper could not be obtained, and what it contains is known here only
from later papers.

Sandia National Laboratories' description of the fitting is in Heitman, Babuska, Cap and Reid
(2016). The user sets the frequencies, decay rates and signs of the components, and only their
amplitudes are fitted. "The algorithm steps from low frequency to high frequency because the low
frequencies can strongly affect the higher frequencies while the high frequencies only weakly affect
the low frequencies." For tone $i$ at frequency $f_i$, the sensitivity $s_i$ is estimated by
perturbing the amplitude once (the change in amplitude divided by the change in SRS at $f_i$), and the
amplitude is updated as

$$
A_i \leftarrow |A_i| + 0.8\, s_i \left[ \mathrm{SRS}_{\mathrm{ref}}(f_i) - \mathrm{SRS}(f_i) \right].
$$

After each sweep, a compensating pulse makes the acceleration, velocity and displacement begin and end
at zero, and the sweep is repeated, "typically done 1-2 times". A controller maker's manual states a plainer rule, each amplitude
multiplied by the ratio of reference to synthesized SRS at its frequency, and says of it: "it cannot
be assured that the SRS is controlled ... However, this equation is used because there is no other
good simple method" (IMV 2019, 7.3.4).

The choice of components matters beyond the SRS. With components above the shaker's first
resonance, the amplifier's peak voltage, not the table's acceleration, may decide whether a test can
run; keeping the best of many random component sets cut the predicted peak voltage by about 40 % for
about 10 % more peak acceleration (Cap, Heitman, Raymer and Hunt 2018). Sets meeting the same SRS
gave responses in a three-mass model with errors from 0.6 to 4.8 dB RMS above 200 Hz (Heitman and Cap
2019).

### 2.2 Correcting the SRS at the Test

The SRS achieved on the article differs from the one synthesized, because the drive passes through
the shaker, the fixture and the article. Coleman, Smallwood and Skousen (2016) describe how Sandia's
controller TSHAKER corrected it. A frequency response function (FRF), the ratio of response to drive
at each frequency, is measured from a low-level broadband pulse, and the drive for the waveform is
computed from it. After each pulse, the error at each frequency is the achieved SRS divided by the
reference SRS; limit channels count only where their error exceeds one; and the largest error at each
frequency sets the correction. "The drive waveform is modified by updating the magnitude of the
estimated FRF and not changing the phase." The correction is weighted, and "The weighting for the
correction is always less the 100% because of the non-linarites" [sic], the reasons given being that
"Damping often increases with level" and that "Low frequency response will change the SRS at higher
frequencies." The level rises "typically in 3dB increments", and the weights in use run from 50 % at
-12 dB to 80 to 90 % at full level (their Table 1). The paper gives no equation; "an experienced
operator is required to rationally pick these parameters."

Anaya and Babuska (2024, slides) report that TSHAKER has been replaced by scripts that step up from
about -12 dB and scale each pulse to full level to predict whether limits will be exceeded. Transmissibilities from low-level random "Tend to
over-estimate responses, thus over-limiting" and "Do not capture non-linear behavior";
transmissibilities computed from the step-up shocks themselves "produce better predictions as dB
level increases" but lag "one level behind". Babuska and Cap (2023) call shaker shocks "run open loop"
and "pre-planned", in the sense that each pulse is computed before it is fired.

### 2.3 Correcting a Waveform on One Shaker

Underwood's patent US 5,517,426 (first filed 1992, issued 1996) controls a waveform, not an SRS, on
one exciter with one control channel, between pulses. It names the problem with a fixed, pre-measured
frequency response: "non-linearities in the system's response (the variation of the transfer function
with the amplitude of the drive signal) and time variations in the system dynamics are not accounted
for. This can produce situations where the drive signal fails to converge". Its answer is to keep
learning the model from the test pulses. With D the drive, C the measured response and R the target
in the frequency domain, after pulse i:

$$
H_i = (1-\sigma)\, H_{i-1} + \sigma \frac{C_i}{D_{i-1}}, \qquad
D_i = D_{i-1} + \alpha\, \gamma_i \frac{R - C_i}{H_i},
$$

with σ "usually chosen to be equal to 0.125" and α "typically ... 0.75". Here $\gamma_i$ is a
confidence between 0 and 1 built from how well the model predicted the last pulse (a clipped ratio,
not a statistical coherence), and every division is guarded against noise. The first pulses are fired
at low amplitude, raised "as greater confidence is gained", and the test aborts if the error's peak
grows. The patent adds that "if the transfer function is known to be highly non-linear, i.e., its
value changes drastically from cycle to cycle, then [σ] should be set equal to 1". It gives no
convergence proof and no measured results.

Karshenas, Dunnigan and Williams (2000), read as an abstract, control a shock pulse on one
electrodynamic actuator with an adaptive inverse filter, and report convergence to the reference
pulse.

## 3. Several Shakers Reproducing a Waveform

### 3.1 Lineage

Driving several actuators together to reproduce several responses is called multiple-input,
multiple-output (MIMO) control. The earliest work found dates from the 1970s. Cryer, Nawrocki and
Lund (1976), read as an abstract, describe a road simulator for heavy trucks that finds the road
inputs from measured vehicle response "through a multiple input-multiple output systems analysis of
the vehicle"; the abstract says nothing about iteration. Fisher (1977) describes a four-actuator
electrohydraulic shaker of 0.62 MN, working from zero frequency to 500 Hz under direct digital
control. Cross-coupling between actuators "has been a severe problem in multiple-actuator systems",
and the cure is "a compensation matrix, which is simply the product of the desired system-transfer
matrix and the inverse of the measured transfer matrix", applied at many frequencies, with the matrix
measured "by perturbation techniques at the full test level to minimize nonlinear effects". A
transient program is listed for shock spectrum and seismic tests, but the report does not say how
transients were built or whether they were corrected between pulses.

Rader and Berry (1979), for NASA, drove two electrodynamic shakers on a truss to produce "two
independent transient waveforms to be applied simultaneously". A rapid sine sweep fed to each shaker
in turn gave the 2 by 2 transfer matrix; it was inverted at each frequency, multiplied by the target
spectra and transformed back to time. Wave shapes came out right and amplitudes did not, with a system whose memory allowed only 128
frequency lines over 50 Hz. They devised an iteration but could not run it for lack of memory. With E
the error spectrum, desired minus actual, it reads

$$
X_{\mathrm{new}} = X_{\mathrm{old}} + [\mathrm{TF}]^{-1} E,
$$

with [TF] the transfer matrix: a correction through its fixed inverse at unit gain. Their Eq. 12 prints a minus sign, which with E so
defined would move the drive away from the target; the form above is the one that converges. They
added that "not every analytically generated desired response is necessarily attainable."

Seat and durability rigs (De Cuyper and Verhaegen 2002), control with more control accelerometers
than exciters (Underwood and Keller 2004) and hydraulic seismic tables (Shen et al. 2018; Guan, Xu,
Xiong and Wang 2020), all known here from abstracts, use related inverse-model methods. Underwood's
sine patent (US 5,299,459, 1994) records that a fixed-gain multi-exciter correction needs a negative
gain "when phase errors greater than 90° are present"; it is steady sine only, as is Liu, Cai, Yu and
Yang (2017), whose printed drive update carries the same sign slip as Rader and Berry's.

In shock specifically, Xu, Chen and You (2010), read as an abstract, computed the inputs of two
shakers by a time-frequency transform and ran a shock on a cantilever beam within the tolerances of
the reference signals. Deng, Yan
and Niu (2017) replicated a classical pulse with three exciters (Section 4.4).

### 3.2 The Open-Loop Solve

At each frequency f, the responses at the control points Y(f) follow from the drives X(f) through the
matrix of FRFs H(f), measured beforehand: Y = H X. The drives that best reproduce a target $Y_t$, in
the least-squares sense, are

$$
X(f) = H^{+}(f)\, Y_t(f),
$$

where H⁺ is the **pseudo-inverse**: the ordinary inverse when H is square and well conditioned, and
otherwise the least-squares solution, usually computed through the singular value decomposition with
the weakest directions limited (regularized). The drives are then transformed back to time.

Schultz (2019) reports Sandia's first shock test with several shakers: two shakers on an aluminum
plate with twelve accelerometers, the target being the plate's response to a hammer blow. Without zero
padding, the frequency-domain solve wraps the end of the record onto its start (circular convolution);
padding the target with zeros removed those errors, and error remained near the onset of the shock. In
simulation, with forces standing in for shakers, more inputs helped mainly near the onset, and a search
over 153 pairs of locations found one pair that "allowed for very accurate replication of the target
response"; the worst pair lay on the plate's centerline and could not move certain modes. Schultz adds
that "Several commercial control systems allow for multiple-input shock control however this test
technique is still niche", and that "there is too much response information to condense down into a
single, scalar value to use as a pass/fail metric."

Schultz and Carter (2024) set the solve out in seven steps for records longer than the measured FRFs
can resolve: split the target into overlapping frames, zero pad each, transform, solve, transform
back, and add the drive frames with windows that sum to one. They advise band-limiting and high-pass
filtering the target, a sample rate "higher than just twice the maximum frequency of interest", and
regularization, which is "typically necessary to minimize the effects of noise". In a simulation where
the structure's modes moved by up to about 6 % after the FRFs were measured, the time-response
assurance criterion (TRAC, a normalized dot product of two time histories, 1 for the same shape and 0
for no likeness; Schultz 2019) fell to 0.96, 0.89 and 0.97, with under-tests at two outputs and a
slight over-test at the third. They warn that TRAC "will be sensitive to any phase shift or frequency
errors".

### 3.3 Pre-Echo and Errors in the Measured Response

Coletti, Carter and Schultz (2025) show that noise in the measured FRFs puts drive energy before the
first event: "if a shock event occurs at 2 seconds, Fourier deconvolution may yield high input levels
at 1.9 seconds, resulting in a 'pre-echo' in the output waveform, wherein the system responds to the
specification before it occurs." They compare four repairs: tapering the tail of the impulse
response, padding and truncating the response, enforcing causality with a Hilbert transform, and
fitting the measured responses with 1,200 single-mode curves under a minimum-energy penalty. In a
linear simulation of 3 inputs and 8 outputs the curve fit was best "by a significant margin", which
the authors call unsurprising in a linear simulation, and above about 30 dB signal-to-noise ratio the
taper and the Hilbert repair made the error worse. They state that "results may change if there are systematic FRF
errors (such as those from leakage) or if the system is nonlinear."

### 3.4 Correcting Between Pulses

Repeating a test and correcting the drive from the last error is called **iterative learning
control** in the control literature: a system repeats one task from the same starting state, and
after each trial the drive is updated from the error so that the error falls from trial to trial
(Owens, Hätönen and Daley 2006). The simplest form corrects through an inverse model Ĝ of the
article and shaker, with a learning gain β between 0 and 1:

$$
u_{k+1} = u_k + \beta\, \hat{G}^{-1} e_k, \qquad e_k = r - y_k .
$$

Rader and Berry's iteration is this law with β = 1; Underwood's is close to it with β = 0.75 and an
updated model. Let U be the ratio of the true
frequency response to the model's at each frequency. The error then falls on every trial, from any
starting error, if

$$
\left| \frac{1}{\beta} - U(e^{j\omega}) \right| < \frac{1}{\beta}
\quad \text{at every frequency, that is} \quad
\left| 1 - \beta U(e^{j\omega}) \right| < 1
$$

(Harte, Hätönen and Owens 2005, as quoted in Owens, Hätönen and Daley 2006; the second form follows by
multiplying through by β). In plain words: the model may be wrong in phase by anything less than 90
degrees at any frequency, and the larger its error, the smaller the gain must be (Harte 2007, Remark
5.3). Model errors at high frequency, such as resonances the model lacks, force a small gain and slow
learning. These results are for one input and one output and for linear, unchanging systems, and
the authors name several loops and nonlinearity as future work (journal version: Owens, Hätönen and
Daley 2009). No source read in the shock literature states a convergence condition for correcting
several drives between pulses. A survey of iterative learning control (Bristow, Tharayil and Alleyne
2006) was read only as an abstract. Method 527.2 adds a limit that applies to any update of a
multi-drive model: "for any frequencies for which the drive signals are fully correlated, corrections
to the system transfer function will not be possible" (Annex B 3.5, written for random control).

### 3.5 Identification

Every method above needs the matrix H measured first. Method 527.2 says the first drives "must be
statistically independent, and form vectors that are linearly independent with respect to the DOFs
[degrees of freedom] to be tested" (4.5.2 a, Step 3). Published practice uses uncorrelated random
noise or bursts on all drives at once (Spectral Dynamics 2007; Krieghbaum and Danforth 2026; the
patent CN115130506A), random noise (Deng, Yan and Niu 2017), or a sine sweep on each shaker in turn
(Rader and Berry 1979). The level at which H is measured
matters, as Section 5 shows: Fisher measured it at full test level, Underwood kept estimating it from
the test pulses, and Method 527.2 Annex D 3 (written for random) says controllers measure it at a very
low level and may update it, because "The updated transfer function accounts for certain vibration
system amplitude nonlinearities".

## 4. Several Shakers and an SRS

### 4.1 One Drive, an SRS at Several Points

The single-drive methods of Section 2 were extended at Sandia to several response points. Heitman,
Babuska, Cap and Reid (2016) compute each point's response from the drive through measured FRFs and
judge the match by each point's SRS error normalized by its own reference, averaged with weights
$\mu_j$ chosen by the user. The amplitude update, written in the sign of their single-point Eq. 4, is

$$
A_i \leftarrow A_i + c\, s_i\, \frac{\sum_j \mu_j \left[\mathrm{SRS}_{\mathrm{ref},j}(f_i) - \mathrm{SRS}_j(f_i)\right]}{\sum_j \mu_j},
$$

with $s_i$ the change of the tone's amplitude per change of the weighted SRS, from one perturbation,
and c a constant the paper does not define. Their Eq. 8 prints the difference the other way round,
which with c positive would move the amplitude away from the target; this is taken here as a printing
slip. On a model of springs and masses, the drive so derived gave responses "considerably closer" to
the targets than a drive fitted to the input SRS alone. The authors note that with one input a perfect match at several points is typically not
possible, and suggest a weighting that limits response to prevent an over-test at chosen points.
Babuska and Cap (2023, slides) describe the current form: the same tone-by-tone fitting with a
weighted sum of per-location errors, random choice of component frequencies with the best set kept,
and response limiting by the largest exceedance over limit channels, for which "Convergence is not
guaranteed"; on a test article, "The responses were not as accurate as expected". Cap, Heitman, Raymer
and Hunt (2018), despite "Single Input Multiple Output" in their title, fit one SRS at the control
point (Section 2.1). Ross, Schneider and Kalinich (2026) derived a single-axis table input from four
gauges on a bolted joint by inverting measured transmissibilities and specified the table by the SRS
of the result; they assumed linearity, and attribute their largest discrepancy, a mode shift near
170 Hz, possibly to nonlinear behavior.

### 4.2 Several Drives, an SRS at Several Points

The only published methods found for controlling an SRS at several points with several drives are two
items from one group at the Nanjing University of Aeronautics and Astronautics.

Zheng, Ma, Wei and Chen (2023, online 2022) could be read only as an abstract. It describes building a
reference waveform from an SRS by "random delay superposition" (component delays drawn from a normal
distribution) or by filtering measured shocks; drives from "A time-domain inverse system method ... based on a finite-difference equation"; and "A
closed-loop iteration control procedure ... to correct the drive signals according to the deviations
between the responses and corresponding reference values", shown in a simulation and a triaxial
shaker test. The correction law, its gain and any convergence argument are not in the abstract. The
random delays shape one waveform's decay; they are not a rule for timing between control points.

The patent application CN115130506A (Zheng, Chen and Wei 2022), filed 25 days after the paper went
online and deemed withdrawn in 2025, was read in full, its equations from the published images. For a
triaxial shaker with three control channels, it builds each reference waveform r(t) from filtered
copies of a measured field shock, computes the drive as $x(t) = H^{-1} r(t)$ from a frequency response
H measured once with uncorrelated white noise, and after each pulse corrects the target:

$$
S_c^{(k+1)} = E^{\beta}\, S_c^{(k)}, \qquad E = S_r\, S_y^{-1}, \qquad S_c^{(1)} = S_r ,
$$

where $S_r$ holds the reference SRS, $S_y$ the achieved SRS and $S_c$ the corrected target from which
the next reference waveform is synthesized, and β is called the convergence factor. The patent does not
say whether the inverse and the power act element by element; with one SRS value per channel and
frequency, the element-wise reading (each channel's target scaled by its own ratio of reference to
achieved SRS, raised to β) is the only one that makes sense, and it is an inference. In that reading
the law is the multi-drive counterpart of Coleman, Smallwood and Skousen's single-drive magnitude
correction, moved from the FRF to the target, with no update of H described. The demonstration held
all three axes within ±3 dB from 10 to 2,000 Hz at reference SRS levels of about 0.01 to 1 g (read off
a logarithmic plot), far below qualification levels. Nothing is said about level steps,
nonlinearity, timing between axes, drive limits, the value of β or convergence.

### 4.3 Shock on Random Vibration

A shock on top of random vibration adds a second problem: separating the two in the measured
response. Zou, Li and Wang (2019), of the China Aerospace Science and Industry Corporation, ran an
aluminum cylinder on five exciters, three for
random vibration and two for shock in a perpendicular plane, with two commercial controllers in
parallel, because MIMO vibration and MIMO shock follow different control principles and need separate
controllers. A real-time separator removed from the shock control signals the parts coherent with the
vibration, so the shock controller controlled only the shock-excited response. Three consecutive
10 g, 20 ms half-sines on 4.2 g RMS random met tolerance. The authors note that when vibration and
shock act in the same direction only waveform replication can do it, and that separation degrades
when nonlinearity lowers coherence.

The Nanjing group's work is known here from abstracts and a patent. Ma, Chen, Lu and Zheng (2023,
online 2022), read as an abstract, extract a half-sine from the mixed signal with an empirical
wavelet transform (a way of splitting a signal into bands fitted to its own spectrum) and correct the
shock amplitude and the random spectra separately. Of Zheng, Ren, Chen and Chen (2021) only the
record could be obtained, and nothing of its content is cited. The patent CN113155385B (Zheng and Chen
2022), read in part in machine translation, builds the random part from a factor of the reference
spectral matrix with random phases and the shock from a half-sine with two compensating pulses; after
each frame it finds the shock's amplitude and position as those that minimize the kurtosis
(peakedness) of what is left, and corrects the two parts separately, $L \leftarrow E_s L$ for the
random part's factor and $A \leftarrow E_k A$ for the shock amplitude. The definitions of $E_s$ and
$E_k$ are in equation images that were not opened.

Cross, Melendez, Arnold, Brenner, Throneberry and Soine (2025) combined a gas-gun pyroshock on a
resonant plate with 12-shaker MIMO random vibration. The shock was not controlled: the gun pressure was
stepped and the gun fired by hand. The shock clipped the random control channels, and in the test shown
random control was lost after the pulse.

### 4.4 Three Exciters and a Classical Pulse

Deng, Yan and Niu (2017), of the China Academy of Engineering Physics, replicated a classical pulse
in three axes with three exciters, one per axis. The matrix H was measured with broadband random, and
the drive was computed from its inverse and corrected from the deviation between the measured and
target responses; the correction law is not stated.
After several corrections a 10 g, 5 ms half-sine on all three axes met the Chinese military
tolerance on the main pulse, with local exceedances in the compensating segments before and after it.

### 4.5 Six-Degree-of-Freedom Tables and Resonant Plates

Sandia has run shocks on a six-degree-of-freedom shaker table. Sisemore, Babuska and Booher (2016,
2017) applied 3,424 shocks "simultaneously in all six degrees of freedom" to 68 cantilever beams; how
the six-axis drive was synthesized or controlled is not described. Owens, Tipton and McDowell (2015)
ran six-degree-of-freedom random tests on a commercial table and treated shock by analysis only.

Resonant plates make several axes with no drive control at all. Hopkins and Sisemore (2019) moved the
projectile impact off the center of a plate to excite three axes in one hit, at the cost of about 50 %
more impulse, and met three single-axis specifications at once (average errors -0.8, +2.6 and +4.8
dB). Sisemore, Babuska and Flores (2020) answer that
off-center tests "are actually not three-axis shock tests, but rather single axis shocks at an
arbitrary angle". Bouma, Schoenherr and Soine (2023) design a fixture for the purpose by simulation,
noting that multi-axis shock tests "are not always repeatable and greatly depend on the fixture";
Alvis and Mesh (2025, slides) optimize the plate's geometry.

### 4.6 A User's Report of a Commercial Multi-Shaker SRS Mode

Krieghbaum and Danforth (2026), of Los Alamos National Laboratory, attempted a three-axis flight
shock with one large axial shaker and two small modal shakers on stingers, three drives and one
triaxial control point. The commercial MIMO shock
mode they used would not accept a waveform for each control axis: "the user must specify the SRS,
then the software will generate an arbitrary time waveform." The result was an over-test, with a peak
Y acceleration of 16.1 g against a specified 3.08 g. "Unfortunately, the software is proprietary, so
we are unable to explore what strategy the controller was using to create this shock pulse." They
conclude that "the SRS alone does not provide enough information about control performance and data
quality", and that what alarm and abort percentages are acceptable in multi-shaker tests has had "no
investigation".

### 4.7 What Controller Makers Publish

MIL-STD-810H Method 527.2 Annex A records that "As of the inclusion of this new test method into
MIL-STD-810G, the primary vibration control system vendors offer MET options for time waveform
replication (TWR), sine, shock, and random"; that statement dates from 2008. The public pages read on
15 November 2026 describe multi-shaker shock or SRS modes (Crystal Instruments, with Zhuge 2024; Data
Physics; Siemens, Musella 2023; Vibration Research) but state no correction law. Siemens synthesizes
sets of shocks to meet "a specific max cross-correlation requirement and maximum SRS error". The two
that state the most are in Table 1: a 2007 Spectral Dynamics data sheet gives equalization by "Inverse
Frequency Response Matrix", gains from 0.05 to 1, level steps of 0.1 to 10 dB, and output one level
step above full level "for difficult nonlinear test conditions"; IMV's 2019 manual runs an SRS shock
as waveform control of a synthesized reference. The pages that could be read from two further makers
(their own pages were blocked) described no multi-shaker SRS mode.

### 4.8 The Open-Source Controller Rattlesnake

Rattlesnake, Sandia's open-source controller, has a MIMO transient environment, documented in Rohe,
Schultz and Hunter (2022) and in its user's manual (2024), whose prose was read; its source code was
not. It takes a set of time histories as its specification. Its FRFs come from a system
identification before the test, and "During control, the environment will not attempt to update the
transfer function relationships, though control can still be updated using the previously acquired
responses to the signal." The user supplies the control law; the manual's worked examples load a
pseudo-inverse law and start at -12 dB "so we don't break anything", and on modal shakers "the initial
impulse cannot be achieved as well with the modal shakers as it was with the impact hammer." The
documentation describes no SRS control.

### 4.9 The Published Update Laws Together

**Table 1.** Published correction laws for shock on shakers, as read. "Sensitivity" is the change of
amplitude per change of SRS, estimated by one perturbation. Where a printed law has a sign error, the
text gives the form that converges.

| Source | Drives and target | Update between pulses | Model of the article | Shown on | Read |
|---|---|---|---|---|---|
| Heitman et al. 2016 | One drive; SRS at one or several points | Each tone: amplitude plus 0.8 (or c) times its sensitivity times the SRS shortfall; Eq. 8 printed with the sign reversed | None for one point; measured frequency responses for several; computed before the test | A spring-mass model | In full |
| Coleman, Smallwood and Skousen 2016 | One drive; SRS at control and limit points | FRF magnitude scaled by the worst achieved-to-reference ratio with a weight below 100 %; phase unchanged; no equation | FRF from a low-level pulse | Electrical loopback; a simulated store | In full |
| IMV 2019 | Synthesis for one SRS | Amplitude times reference SRS over synthesized SRS | None (synthesis) | Not stated | In part |
| Underwood 1996 | One exciter; waveform | Drive plus 0.75 times confidence times error over a model blended with weight 0.125 | Updated from each pulse | No results | In full |
| Rader and Berry 1979 | Two shakers; waveforms | Drive plus inverse of a fixed matrix times error (printed with a minus sign) | Fixed, from a sweep | Proposed, not run | In full |
| CN115130506A 2022 | Three drives; one SRS per channel | Target SRS times (reference over achieved) to the power β; waveform re-synthesized | Fixed, from white noise | Triaxial shaker at about 0.01 to 1 g SRS | In full |
| Zheng et al. 2023 | Several drives; SRS per point | "Closed-loop iteration ... to correct the drive signals"; law not in the abstract | Time-domain inverse | Simulation; triaxial shaker | Abstract |
| CN113155385B 2022 | Several drives; random plus half-sine | Random factor and shock amplitude each multiplied by an error matrix | Inverse of the FRF matrix | Triaxial shaker | In part |
| Deng, Yan and Niu 2017 | Three exciters; same half-sine per axis | Corrected from the deviation; law not stated | From broadband random | Three-axis shaker, 10 g | In full |
| Spectral Dynamics 2007 | Several exciters; waveform | Inverse FRF matrix; gain and update rate 0.05 to 1 | Updated after every output | Not stated | In full |

## 5. Structures That Change With Level

### 5.1 Terms

Every model in Sections 2 to 4 is a set of FRFs measured before the test. A structure whose FRFs
depend on how hard it is driven is said here to **change with level**. Bolted joints are the usual
cause. Under small loads the contact surfaces stick everywhere but at their edges, where they slip a
little (**microslip**); the joint loses a little stiffness and dissipates energy, so the resonance
moves down (**softening**) and the **damping ratio** (the fraction of critical damping) rises. Under
large loads the whole interface slides (**macroslip**). Thin plates and panels change with level for
reasons of geometry: as they deflect, their midplanes stretch and they stiffen (**hardening**), or a
curved panel first softens. A curve of a mode's frequency or damping against its amplitude is called
its **backbone**.

### 5.2 What Has Been Measured

Figure 1 and Table 2 collect the measurements read for this survey.

![A chart with one row per measured case, each labeled with the structure and its source, and a horizontal axis from -31 to +35 percent change of the resonance frequency from low level to the highest level tested. Rows are grouped under six colored headings. Well-tightened bolted joints: nine rows, all between about -0.1 and -4 percent, inside a gray band from -0.1 to -4 percent. Lightly torqued or friction joints: a two-beam structure at about -6 percent, a slug in press-fit foam cups at about -8 to -10 percent under shaker sine, one bolt at about -10 percent under shaker random. Bolted joint in macroslip: a Brake-Reuss beam at about -28 percent. Measured at shock level: the foam-cup slug at 0 percent under shaker shock pulses, and a resonant plate from -1.6 to -12.7 percent on five modes and +19.8 percent on one, between a hammer test and projectile shocks. Bolted joint hardening, cause not identified: the S4 beam's first mode at about +1.6 percent. Geometry: rows from -12 percent (a curved beam clamped by bolted joints) to +32 percent (a cantilever with a clamped thin strip), with thin plates at about +13 and +18 percent, a curved panel at about -7 to -8 percent, a bolted curved panel at about -3 to -7 percent before rising again, and a cross beam at +4.7 percent. Marker shape gives the excitation: circle for hammer, square for shaker, triangle for shaker shock pulses, diamond for a hammer test compared with projectile shock, plus sign for a hammer test compared with a shaker. Filled markers are numbers stated in the source's text; open markers were read off a figure's axis.](figures/fig1_measured_frequency_change.png)

**Figure 1.** Measured change of a resonance frequency with level, by joint condition and excitation.
Each row names its source. Open markers were read off a figure's axis and are approximate; bars span
modes, assemblies or tests. The gray band, about 0.1 to 4 %, is the range for well-tightened bolted
joints at low force. Data: `data/fig1_measured_frequency_change.csv`; code:
`code/fig1_measured_frequency_change.py`.

**Table 2.** Measured changes of frequency and damping with level. "Axis" means read off a figure and
approximate. Damping changes are ratios of the highest to the lowest level unless given otherwise.

| Structure and joint | Excitation and level | Frequency change | Damping change | Source |
|---|---|---|---|---|
| Catalytic converters, bolted flanges at 45 N m, modes 1 and 2 | Hammer, about 500 N | -0.8 %, -0.2 % | ×2.4, ×1.5 | Roettgen 2016, Table 12 |
| Cylinder-plate-beam, bolted joint and foam-held internal mass, modes 7 to 15 | Hammer, 23 N against 180 to 400 N | -1 to -4 % | -9 % to +190 % | Roettgen 2016, Table 15 (Mayes et al. 2016 is the same data) |
| Brake-Reuss beam, three bolts at 10 N m, modes 1 and 2 | Hammer | -3.8 %, -1.3 % | ×11, ×4.4 | Roettgen 2016, Table 27 |
| Brake-Reuss beam, 15 N m, mode 1 | Hammer, 100 to 2,000 N | About -3.5 % | About ×6 to ×8 | Kuether and Brake 2016, Fig. 8 (axis) |
| Brake-Reuss beam, 20 N m, mode 1 | Shaker stepped sine, 0.1 to 2 N | About -1.2 % | About ×1.4 | Lacayo et al. 2019, Fig. 10 (axis) |
| S4 beam, 2,224 N preload, mode 2 | Hammer, about 100 to 700 N | About -0.1 to -0.2 % | Up to about ×10 between hits at one point | Wall, Allen and Kuether 2022 |
| S4 beam, 500 lb preload, mode 2 | Hammer | About -0.5 % | About ×20 | Clark, Allen and Pacini 2023, slides (axis) |
| Two-beam structure, bolts at 3.39 N m, mode 1 | Hammer, 24 to about 1,440 N | About -6 % (text: about 7 Hz) | Not given as a ratio | Deaner et al. 2015, Fig. 5 (axis) |
| Slug in press-fit foam cups (Ministack), axial mode | Shaker swept sine, 1 to 10 g | About -10 %; about -8 % after reassembly | About ×2 | Kuether and Najera 2017, Fig. 8 (axis) |
| One bolt, axial mode | Shaker random, 0.14 to 18 lbf RMS | About -10 % | Rises, then falls above about 5 lbf RMS | Khan et al. 2021, slides only |
| Brake-Reuss beam, torque not stated, mode 1 | Hammer, up to 8,000 N | About -28 % in macroslip; about -11 % permanent after | Not given | Bonney et al. 2016 |
| Ministack, different foam cups | Shaker shock pulses, 8.5 to 35 g | None (about 2,200 Hz throughout) | Not cited (figure and text disagree) | Jacobs-O'Malley and Hofer 2017 (axis) |
| Resonant plate, damping bars bolted loosely over rubber, six modes | Hammer (about 200 lbf) against projectile shock (tens of thousands of lbf) | -3.1, +19.8, -4.8, -9.4, -12.7, -1.6 % | ×1.2 to ×6.9 | Schoenherr, Soine and Witt 2022, Table 2 |
| C-beam pairs, bolts at 325 in-lbf | Shaker force appropriation, to about 600 m/s² | About -0.2 % within a run; about -6 % between runs (fatigue cracks) | Not read | Davis et al. 2024 (axis) |
| Industrial structure, several bolted joints | Hammer, then shaker to about 300 g | Low-level frequency moved about 7 % over the series | Low-level damping moved about 20 % | Pacini 2025 |
| S4 beam, 2,224 N preload, mode 1 (cause not identified) | Hammer | About +2 % (hardening) | Falls by almost half | Wall, Allen and Kuether 2022 |
| Cantilever with a clamped thin strip (benchmark) | Hammer against shaker appropriation | +32 % | None reported | Peeters, Kerschen and Golinval 2011 |
| Clamped thin plate; free-edge thin plate; curved thin panel | Shaker stepped sine | About +13 %; about +18 %; about -7 to -8 % | More than ×2.5; about ×2.8; +50 % | Amabili, Ferrari and Balasubramanian 2017 (axis) |
| Bolted curved panel (Tribomechadynamics Research Challenge) | Base sine on a slip table, to about 1.5 thicknesses | Down about 3 to 7 %, then back up | About 0.3 to 0.5 % rising to 0.4 to 0.7 %, then flat or falling | Bhattu et al. 2024, Fig. 8 (axis) |
| Curved beam clamped by bolted joints | Base excitation, phase-locked | About -12 % (geometric) | About ×9 | Müller et al. 2022 |

**Well-tightened bolted joints at low force soften about 0.1 to 4 %.** Mayes, Pacini and Roettgen
(2016) put the picture in a sentence: "Many structural dynamic systems are mildly nonlinear in
stiffness (few percent modal frequency change) and significantly nonlinear in damping (hundreds of
percent damping ratio change) as a function of amplitude". None of these tests reached macroslip, so
"one cannot know whether the frequency would shift further if even larger forces were applied"
(Roettgen 2016, p. 68). A joint's stiffness loss stays hidden because "the elastic subsystem is
generally much more compliant than the interface until the interface has been forced into the
vicinity of macro-slip" (Segalman 2002).

**Looser and friction joints soften more.** The two-beam structure's abstract calls all its levels
"below macro-slip", while its Section 6 suggests macroslip began at the highest (Deaner et al. 2015).
The press-fit slug is a friction interface, not a bolt, and part of its shift may be preload lost
during testing, which averaged 162 to 352 lbf (Jacobs-O'Malley and Hofer 2017). The single bolt's
figures come from slides, and its damping turned down above about 5 lbf RMS, which other sources read
as the onset of macroslip (Clark, Allen and Pacini 2023; Wall, Allen and Kuether 2022). The 28 % is
one beam hammered into "definite macroslip"; afterwards it stayed about 11 % low (Bonney et al. 2016).

**Damping rises about 1.4 to 20 times, and sometimes falls**: on the single bolt, and on one S4 beam
mode whose damping halved as its frequency rose about 2 %. That mode's authors could not identify the
cause: "the nonlinear response is dominated by some unknown mechanism other than microslip" (Wall,
Allen and Kuether 2022).

**Other hardening, and softening then hardening, come from geometry.** A cantilever stretching a
clamped thin strip (a purpose-built benchmark), thin flat plates, and a clamped cross beam after an
initial fall that its authors attribute to gravity sag and imperfect clamping all harden; curved
panels soften first. Amabili (2018), read as an abstract, puts geometric frequency shifts at commonly
10 to 25 % at most for shells, plates and beams. For a bolted curved panel, its authors judge that
"the effect of the frictional clamping on the amplitude-dependent modal properties is rather weak,
whereas a pronounced frequency variation is evident from the geometric nonlinearity" (Bhattu et al.
2024); models of it with friction alone predicted only 2 to 4 % softening, and the contact "has a
crucial effect on the geometrically nonlinear behavior" (Krack et al. 2025).

**One mode can depend on another.** On the S4 beam the damping of mode 2 depended on how strongly
mode 1 was excited, and not the reverse (Wall, Allen and Kuether 2022). A loosely bolted tester showed
modes coupled through an internal resonance (Cenedese et al. 2022), and with two modes 0.5 Hz apart a
single shaker could not hold a beam on one nonlinear mode (Renson et al. 2016).

**Structures scatter and change during a test.** Preload for a given torque varied by up to 70 to
100 % between assemblies of one beam (Wall, Allen and Kuether 2022); C-beams cracked by fatigue between
runs (Davis et al. 2024). An industrial
structure's low-level frequency and damping moved about 7 % and 20 % over its test series (Pacini
2025): "the underlying linear properties can change throughout the test series." A review of joint
experiments reports that "the uncertainty measured is often greater than the nonlinear characteristics
being studied" (Brake, Schwingshackl and Reuß 2019, read as an abstract).

**Shock is not sine.** Jacobs-O'Malley and Hofer (2017) tested the same kind of friction interface
both ways. Sine sweeps from 1 to 10 g lowered its frequency about 8 to 10 % (Kuether and Najera 2017,
read off a figure); shaker shock pulses from 8.5 to 35 g did not change it: "This result suggests that
when the excitation is transient in nature, the system stiffness does not change with amplitude as it
does with the harmonic excitation." The authors offer as a possible explanation that the dominant
nonlinearity depends on the type of excitation. Different foam cups were used for the shock tests,
and the section's damping results contradict its text, so only the frequency result is cited.

**At pyroshock level.** Schoenherr, Soine and Witt (2022) fitted modal parameters to a resonant plate
during projectile shocks. Against a hammer test about two orders of magnitude lower in force, five
modes moved down 1.6 to 12.7 % and one rose 20 %, its damping from 1.4 % to 9.6 %; between low-level
and high-level shocks the changes were small. The plate's damping bars are bolted loosely over rubber,
and the shock responses have about 24 Hz line spacing, which limits precision. The authors write that
"predicting the shifts in frequency and damping is very difficult or impossible without data", and
that the nonlinearities "do not prevent the use of a linearized model that is calibrated to the
dynamics present at shock type input loads." A later paper on the same plate found its 582 Hz mode no
longer proportional to hammer force above about 7,500 N (Soine 2024).

### 5.3 What This Means for a Test Controlled From a Low-Level Model

Identification theory states the general point. The **best linear approximation** (BLA) of a
nonlinear system is the linear model that best fits its output, in the mean-square sense, for a given
class of inputs; what it cannot fit behaves like noise. Schoukens, Vaes and Pintelon (2016) show that
it depends on the excitation: "Be aware that the BLA varies in general as a function of the power
spectrum and amplitude distribution of the excitation signal. For that reason, the excitation signals
during the experiments should match as well as possible the signals that will be applied later on to
the model". A linear model fitted at one level "fails completely" above it. An FRF measured with
low-level random noise is the BLA for that level and that kind of signal, not for a full-level shock
pulse.

Measured consequences are of the order of a factor of two. A linear model over-predicted some modes of
a jointed structure at high level by a factor of 2 (Mayes, Pacini and Roettgen 2016, slides), and
linear models of two industrial structures over-predicted their peak responses by up to 2 and by 1.5
to 1.8 (Pacini 2025). Clark, Allen and Pacini (2023) go further with a single-mode joint model fitted
to measured damping and extrapolated past the measured data into macroslip, with the frequency held
fixed. In that model, raising the environment a thousand times in microslip raised the response only
53 times, while near macroslip doubling the force raised it more than 6,000 times; their slides
conclude that "A small increase in the shaker power will increase the response greatly" and "may lead
to difficulties in control". That hazard is a result of the model extrapolated beyond the data, not a
measured control event. Their paper warns that a model made at low level and extrapolated up "can be
highly over conservative of [sic] highly under conservative depending on whether the joints are
exercised above or below macro slip".

Practice points the same way: corrections weighted below 100 % because of nonlinearity, predictions
from the step-up shocks rather than low-level random (Section 2.2), and models learned from the test
pulses or measured at full level (Sections 2.3 and 3.1). Lacayo et al. (2019) abandoned constant-force stepped sine
above 2 N because the force could not be held constant near resonance. Larsen (2018), whose thesis was
read only as an abstract, reports a method "to estimate high amplitude shock inputs from low amplitude
frequency response functions". No published account was found of a multi-shaker shock controller run
on a structure measured to change with level.

## 6. Learning-Based Approaches

Here **learning-based** means a model whose form is fitted to data, usually a neural network (a
flexible function with many adjustable weights), rather than derived from physics.

**Shaker drives.** Peláez-Rodríguez, Magdaleno, Salcedo-Sanz and Lorenzana (2023) and the extended
paper of 2024 drive one inertial electrodynamic actuator to reproduce human bouncing and walking
forces of 1 to 2.5 Hz. The network is trained entirely in simulation through a fitted linear model of
the actuator; the reported errors (53.26 N and 62.72 N RMS on average) are simulated, and no classical
method was run beside it. Larbi et al. (2020)
placed a small network in the acceleration feedback path of a small electric shaking table beside its
position controller; on earthquake records the time-domain error fell from 54 to 67 % to 13 to 18 %,
against the table's own displacement controller as the only baseline, and the peak error on one record
got worse (2.56 % to 10.56 %). Najera-Flores (2019, slides) learned the map from measured responses to
the base input of a six-degree-of-freedom shaker from ground-test data, which "could be white noise".

**From an SRS to a waveform.** Watts, Jeon, Newton and Bowering (2026a, arXiv, not peer reviewed), of
Los Alamos National Laboratory with the University of Rochester, train a conditional variational
autoencoder (a network that learns to generate examples matched to a given input) on 400,000
synthetic and 99,682 measured shocks to map one SRS to one acceleration record. On four held-out sets
its mean logarithmic SRS error was lower than a classical decaying-sinusoid fit (0.095 against 0.206
on one set), in about 0.3 ms against 5 to 8 s. Nothing in the method constrains shaker displacement,
velocity or force, and a single reconstruction "may not be feasible for a given shaker table". The
follow-on (Watts et al. 2026b, arXiv) trains 104 models to give several candidate waveforms, because
single models gave "nearly identical waveforms" under sampling, and found "Spectral agreement alone
does not establish physical suitability". A 2026 report (Watts 2026, slides) moves to a diffusion
model (a network that builds a sample by removing noise step by step), whose baseline "does not
consistently meet the target SRS tolerance" without a refinement step. All three are one channel and
open loop, with no shaker.

**Inverse models with physics.** Bolderman et al. (2024) build a feedforward controller for an
industrial linear motor from a physical model plus a small network kept near the physics where there
is no data; it cut the mean tracking error about two times against the physical model alone. They
state the risk plainly: networks "suffer from bad extrapolation outside the training data set, which
makes them unsafe for implementation in industry".

**Further away from a shaker.** A transformer (the network type behind large language models) trained
on many simulated systems of one class predicts a new system's output without retraining; when the
class was widened at test time its simulation error rose from 0.013 to 0.066, about five times
(Forgione, Pura and Piga 2023, who set 0.066 against their one-step-ahead figure, 0.009). Networks
fitted to jointed structures serve as surrogates of physics models (Najera-Flores et al. 2024) or are
fitted to one measured decay and tested on its later, lower-amplitude part (Sharma et al. 2024), or
learn a correction to a physical model with displacement and velocity measured everywhere (Lai et al.
2021); none was tested above the level of its data.

**What was not found.** In the searches described above, which for this topic were in English only,
no learned component was found inside a multi-shaker shock or SRS control loop, open or closed. No
learned shaker drive law on hardware was found compared with offline waveform replication or iterative
learning control, and none was tested above the level of its training data on a structure that
changes with level.

## 7. Where the Published Work Stops

Each gap below is stated to the limits of the search described at the start. Figure 2 shows the
record in time: waveform replication with several drives has fifty years of lineage, while SRS control
with several drives appears in print only from 2022.

![A timeline in seven horizontal bands, with a horizontal axis of years broken between 1986 and 2001. Waveform replication with several drives, blue circles: Cryer et al. 1976, Fisher 1977 and Rader and Berry 1979; De Cuyper and Verhaegen 2002; Underwood and Keller 2004; Xu, Chen and You 2010; Shen et al. 2016; Deng, Yan and Niu 2017; Schultz 2019; Guan et al. 2020; Rohe, Schultz and Hunter 2022; Schultz and Carter 2023; Coletti, Carter and Schultz 2025. One shaker, SRS at several points, orange squares: Coleman et al. and Heitman et al. 2015; Babuska and Cap 2023; Anaya and Babuska 2024; Ross et al. 2026. SRS with several drives, red diamonds: Zheng et al. (open, abstract only) and CN115130506A in 2022; Krieghbaum and Danforth 2026. Shock on random vibration, green triangles: Zou, Li and Wang 2019; Zheng et al. (open) and CN113155385B 2021; Ma et al. (open) 2022; Cross et al. 2025. Six-degree-of-freedom tables and resonant plates, pink downward triangles: Owens, Tipton and McDowell 2015; Sisemore et al. 2016 and 2017; Hopkins and Sisemore 2018; Sisemore et al. 2020; Bouma et al. 2023; Alvis and Mesh 2025. Learning-based, light blue plus signs: Najera-Flores 2019; Larbi et al. 2020; Peláez-Rodríguez et al. 2023 and 2024; three Watts items in 2026. Controller makers' descriptions, black crosses: Spectral Dynamics 2007, IMV 2019, Siemens 2023, Crystal Instruments 2024. Filled markers were read in full or in part; open markers only as an abstract or record.](figures/fig2_timeline.png)

**Figure 2.** Published work on shock testing with several shakers, by the year it first appeared
(online, presented or filed) and by kind. Filled markers were read in full or in part, open markers as
an abstract or record only. Road, seat and seismic simulators are included in the first band as
lineage. Makers' pages without a date are not shown. Data: `data/fig2_timeline.csv`; code:
`code/fig2_timeline.py`.

**No multi-shaker SRS law tested on a structure that changes with level.** The one readable law
(CN115130506A) identifies its model once, describes no update of it, and was shown at SRS levels of
about 0.01 to 1 g. The one journal paper (Zheng et al. 2023) could be read only as an abstract. The
one published user report (Krieghbaum and Danforth 2026) found an over-test from a law the users
could not see. Single-shaker practice deals with level by weighting corrections below 100 % and
re-estimating from the step-up shocks; no multi-shaker counterpart has been published. A companion
article in preparation reports simulation work on this problem.

**No multi-drive SRS sensitivity step.** Sandia's published practice, as of 2023, adjusts each
component's amplitude of one drive through a single scalar sensitivity, before the pulse (Heitman et
al. 2016; Babuska and Cap 2023). No source was found that corrects component amplitudes through the
sensitivity of each SRS point to each of several drives, or that uses the derivative of the maximax
SRS with respect to the drives. The nearest are quasi-Newton waveform methods on hydraulic tables
(methods that improve their own estimate of the sensitivities from each trial), known from abstracts.

**No rule for timing between control points.** None of the standards read gives one. The nearest
published reasoning is about polarity and in-phase combination (Section 1.7); one maker synthesizes
sets of shocks to a cross-correlation limit (Musella 2023).

**No standard or tested acceptance rule for several control points.** Method 527.2 defines global
errors without values. A user report asks for alarm and abort limits that "there has been no
investigation" into, and argues that the SRS alone is not enough; Schultz (2019) finds no single
scalar that will do; per-axis SRS can understate a simultaneous shock (Sisemore, Babuska and Booher
2016). Cross and Zwink (2026) proposed a practice for judging multi-shaker tests, including shock:
keep some accelerometers out of the control and judge with them, report what the setup could reach,
what the controller achieved and what the article saw, and judge a controller first by its safety. In
their simulations, twenty synthesized pulses matching one multi-point SRS target about equally differed
by about 1.5 dB (one standard deviation) in element peak stress, and a zone-average rule sorted the
pulses little better than chance. That is a proposal resting on simulation, not a standard.

**Few measurements of joints under shock.** The shock-level measurements found are the Ministack
ring-downs under shaker shock and the resonant plate at pyroshock level. No measurement was found of
one jointed structure under shaker shock at several qualification levels, with an identification at
low level compared against the full-level response.

**No convergence statement for correcting several drives between shocks.** The conditions available
are general results of iterative learning control for one input and one output.

**Leads not followed.** Every reference states how much of it was read. Favour's 1974 review of
transient waveform control (cited in Underwood's shock patent), papers by Spectral Dynamics engineers
at the 2008 and 2010 Shock and Vibration Symposia on multi-shaker waveform replication, and Larsen et
al. (2020) on judging multi-axis SRS results, of which only the record was found, were not read.

## How This Was Made

AI tools were used in this work. The literature search, the reading of the sources and the checking
of each record, the figure code and the drafting of the text were done with Claude Code, an AI coding
assistant running Anthropic's Claude Opus models, under Kevin Cross's direction. The author is
responsible for every word, number and line of code.

## Acknowledgments

Most of the work surveyed here is published work of Sandia National Laboratories, credited here to
Sandia National Laboratories: shaker shock synthesis, response limiting and single-input,
multiple-output derivations (Smallwood; Cap; Heitman; Babuska; Coleman and Skousen; Raymer; Anaya;
Ross, Schneider and Kalinich; with Reid of the Massachusetts Institute of Technology and Hunt of ATA
Engineering), multi-shaker waveform replication and its errors (Schultz, Carter and Coletti), the
Rattlesnake controller and its documentation (Rohe and Schultz, with Hunter), six-degree-of-freedom
and resonant-plate shock (Sisemore, Booher, Flores, Hopkins, Bouma, Schoenherr, Soine, Alvis, Mesh,
Owens, Tipton, McDowell), combined pyroshock and random vibration (Cross, Melendez, Arnold, Brenner,
Throneberry and Soine), and measurements, models and learned models of jointed and level-dependent
structures (Segalman, Mayes, Pacini, Roettgen, Kuether, Najera-Flores, Jacobs-O'Malley, Hofer, Khan,
Witt, Davis and co-authors).

The measurements and models behind Sections 5 and 6 also come from the University of
Wisconsin-Madison (Roettgen's dissertation); the University of Stuttgart, Rice University, Imperial
College London and the other institutions of the Tribomechadynamics Research Challenge (Bhattu, Krack
and co-authors), with Müller and co-authors at Stuttgart; the University of Liège (Peeters, Kerschen
and Golinval); the University of Bristol (Renson and co-authors); McGill University (Amabili and
co-authors); ETH Zürich (Cenedese and co-authors, with the University of Wisconsin-Madison; Lai and
co-authors, with Rice University); the Vrije Universiteit Brussel (Schoukens, Vaes and Pintelon);
Eindhoven University of Technology and ASML (Bolderman and co-authors); the University of California
San Diego and ATA Engineering (Sharma, Najera-Flores, Todd and Kramer); the IDSIA Dalle Molle Institute for
Artificial Intelligence (Forgione, Pura and Piga); the Universidad de Alcalá and the Universidad de
Valladolid (Peláez-Rodríguez and co-authors); and the University of Saad Dahleb and the Ecole
Nationale Polytechnique, Algeria (Larbi and co-authors). The review of joint variability is the work
of Brake, Schwingshackl and Reuß.

The work of Los Alamos National Laboratory on learning-based SRS synthesis (Watts, Young, Jeon and
Newton, with Bowering of the University of Rochester) and on three-axis shock with supplemental
shakers (Krieghbaum and Danforth) is credited to Los Alamos National Laboratory. The multi-shaker SRS
and shock-on-random control work of Zheng, Chen, Wei, Ma, Lu and co-authors is credited to the Nanjing
University of Aeronautics and Astronautics. Multi-axis classical shock control is the work of Deng,
Yan and Niu of the China Academy of Engineering Physics, and combined vibration and shock testing that
of Zou, Li and Wang of the China Aerospace Science and Industry Corporation. The early multi-actuator
work is that of Fisher at Lawrence Livermore Laboratory and of Rader and Berry of Martin Marietta
Corporation for NASA Langley Research Center. The iterative learning control results are from the
University of Sheffield (Owens, Hätönen, Daley and Harte).

## References

**Standards**

- IEC 60068-2-27:2008. Environmental testing, Part 2-27: Tests, Test Ea and guidance: Shock. Edition
  4.0. Read: public page and preview only.
- IEC 60068-2-81:2003. Environmental testing, Part 2-81: Tests, Test Ei: Shock, Shock response
  spectrum synthesis. Edition 1.0. Read: public page and preview only.
- IEST-RP-DTE022. Multi-Shaker Test and Control. Institute of Environmental Sciences and Technology,
  first printing October 2014. Read: public page only.
- MIL-STD-810H with Change 1. Environmental Engineering Considerations and Laboratory Tests. U.S.
  Department of Defense, 18 May 2022. Methods 516.8 (Shock), 525.2 (Time Waveform Replication) and
  527.2 (Multi-Exciter Test). Read in part: the paragraphs cited.
- NATO AECTP-400, Edition 3 (2006). Mechanical Environmental Tests. Methods 417 (SRS Shock) and 421
  (Multi-Exciter Vibration and Shock Testing). Read in part (Method 421 sections 1 to 2.3, 5.1, 5.2, 5.5 and
  5.7; Method 417 section 5.1). Current edition E (2025) not read.

**Papers, Reports and Theses**

- Alvis, T. H., Mesh, M. (2025). Generating Three-Axis Shock Response on Resonant Plates without
  Additional Dynamic Fixturing through Geometric Optimization. Slides, IMAC XLIII. SAND2025-01766C,
  DOI 10.2172/3018831. Read in part (slides 1 to 13).
- Amabili, M. (2018). Nonlinear damping in large-amplitude vibrations: modelling and experiments.
  Nonlinear Dynamics 93(1), 5-18. DOI 10.1007/s11071-017-3889-z. Read: abstract only.
- Amabili, M., Ferrari, G., Balasubramanian, P. (2017). Nonlinear identification of damping in large
  amplitude vibrations of plates and shells. 9th European Nonlinear Dynamics Conference (ENOC 2017),
  Budapest, extended abstract 417. Read in full.
- Anaya, G., Babuska, V. (2024). Using Test Configuration Transmissibility Functions to Limit Shock
  Responses. Slides, 94th Shock and Vibration Symposium. SAND2024-15056C, DOI 10.2172/3001145. Read in
  full.
- Babuska, V., Cap, J. S. (2023). Response Limiting & Optimizing Shaker Shocks. Slides, Aerospace
  Shock Test Working Group. SAND2023-05167C, DOI 10.2172/2430937. Read in full.
- Bhattu, A., Hermann, S., Jamia, N., Müller, F., Scheel, M., Schwingshackl, C., Özgüven, H. N.,
  Krack, M. (2024). Experimental analysis of the TRC benchmark system. Journal of Structural Dynamics,
  special issue, 26-45. DOI 10.25518/2684-6500.206. Read in full.
- Bolderman, M., Butler, H., Koekebakker, S., van Horssen, E., Kamidi, R., Spaan-Burke, T.,
  Strijbosch, N., Lazar, M. (2024). Physics-guided neural networks for feedforward control with
  input-to-state-stability guarantees. Control Engineering Practice 145, 105851.
  DOI 10.1016/j.conengprac.2024.105851. Read in part (preprint arXiv 2301.08568).
- Bonney, M. S., Robertson, B. A., Schempp, F., Mignolet, M., Brake, M. R. W. (2016). Experimental
  Determination of Frictional Interface Models. In Dynamics of Coupled Structures, Volume 4, 473-490.
  DOI 10.1007/978-3-319-29763-7_47. SAND2015-9817C. Authors in the order of the SAND paper; Crossref
  lists Mignolet before Schempp. Read in part (sections 3.1, 4 and 5).
- Bouma, A. J., Schoenherr, T. F., Soine, D. E. (2023). Fixture Design and Analysis for Multi-axis
  Mechanical Shock Testing. In Dynamic Substructures, Volume 4, 121-124. DOI
  10.1007/978-3-031-36694-9_14. SAND2022-14805C. Read in full (manuscript).
- Brake, M. R. W., Schwingshackl, C. W., Reuß, P. (2019). Observations of variability and
  repeatability in jointed structures. Mechanical Systems and Signal Processing 129, 282-307.
  DOI 10.1016/j.ymssp.2019.04.020. Read: abstract only.
- Bristow, D. A., Tharayil, M., Alleyne, A. G. (2006). A Survey of Iterative Learning Control. IEEE
  Control Systems Magazine 26(3), 96-114. DOI 10.1109/MCS.2006.1636313. Read: abstract only.
- Cap, J. S., Heitman, C., Raymer, M., Hunt, T. (2018). Monte Carlo Optimization of a Hybrid Spectral /
  Temporal Single Input Multiple Output (SIMO) Input Derivation for an Oscillatory Decaying Shock. 88th
  Shock and Vibration Symposium (2017). SAND2018-1791C, OSTI 1497550. Read in full.
- Cap, J. S., Smallwood, D. O. (1997). A Methodology for Defining Shock Tests Based on Shock Response
  Spectra and Temporal Moments. 68th Shock and Vibration Symposium. SAND97-1480C, OSTI 548713. Read in
  full.
- Cenedese, M., Axås, J., Yang, H., Eriten, M., Haller, G. (2022). Data-driven nonlinear model
  reduction to spectral submanifolds in mechanical systems. Philosophical Transactions of the Royal
  Society A 380(2229), 20210194. DOI 10.1098/rsta.2021.0194. Read in part (preprint, section 3).
- Clark, B., Allen, M. S., Pacini, B. R. (2023). Case Study on the Effect of Nonlinearity in Dynamic
  Environment Testing. In Nonlinear Structures & Systems, Volume 1, 97-100.
  DOI 10.1007/978-3-031-36999-5_13. SAND2022-14802C; slides SAND2023-12019C, DOI 10.2172/2432026. Read
  in full (paper and slides).
- Coleman, R., Smallwood, D., Skousen, T. (2016). Response Limited Shaker Shock Testing. 86th Shock
  and Vibration Symposium (2015). SAND2016-1335C, OSTI 1344695. Read in full.
- Coletti, K., Carter, S., Schultz, R. (2025). FRF Error Mitigation Methods for Time Waveform
  Replication. In Topics in Modal Analysis & Parameter Identification II, Volume 10, chapter 9, 71-80.
  River Publishers. DOI 10.13052/97887-438-0155-9_9. SAND2025-00265C. Read in full.
- Cross, K., Melendez, G., Arnold, F., Brenner, K., Throneberry, G., Soine, D. (2025). Combining
  Pyroshock with MIMO Vibration. IMAC XLIII. SAND2024-13407C, OSTI 2999362. Read in full.
- Cross, K., Zwink, B. (2026). What Is a Good Multi-Shaker Test? A Proposed Practice for Judging MIMO
  Vibration and Shock Tests on Flexible Articles. Hertzforge Journal 1, 2026-001.
  DOI 10.5281/zenodo.24235533. Read in part (abstract and sections 4.8 and 5 to 7).
- Cryer, B. W., Nawrocki, P. E., Lund, R. A. (1976). A Road Simulation System for Heavy Duty Vehicles.
  SAE Technical Paper 760361. DOI 10.4271/760361. Read: abstract only.
- Davis, C. G., Moldenhauer, B. J., Roettgen, D. R., Pacini, B. R., Kuether, R. J., Najera-Flores, D.
  A. (2024). Experimental Backbone Curves from Bolted Interfaces with Measured As-Built Surface
  Topography. IMAC XLII. SAND2025-11054C, OSTI 3683814. Read in full.
- De Cuyper, J., Verhaegen, M. (2002). State Space Modeling and Stable Dynamic Inversion for
  Trajectory Tracking on an Industrial Seat Test Rig. Journal of Vibration and Control 8(7),
  1033-1050. DOI 10.1177/107754602029580. Read: abstract only.
- Deaner, B. J., Allen, M. S., Starr, M. J., Segalman, D. J., Sumali, H. (2015). Application of
  Viscous and Iwan Modal Damping Models to Experimental Measurements From Bolted Structures. Journal of
  Vibration and Acoustics 137(2), 021012. DOI 10.1115/1.4029074. Read in part (accepted manuscript).
- Deng, T., Yan, X., Niu, B. (2017). Multi-dimensional classical shock waveform control technology (in
  Chinese). Information and Control 46(6), 746-751. DOI 10.13976/j.cnki.xk.2017.0746. Read in full.
- Fisher, D. K. (1977). Computer-Controlled Multiple-Actuator Shaker Offers Versatile Test
  Capabilities. Lawrence Livermore Laboratory, UCID-17347. DOI 10.2172/7328357. Read in full.
- Forgione, M., Pura, F., Piga, D. (2023). From System Models to Class Models: An In-Context Learning
  Paradigm. IEEE Control Systems Letters 7, 3513-3518. DOI 10.1109/LCSYS.2023.3335036. Read in full
  (preprint).
- Guan, G., Xu, X., Xiong, W., Wang, H. (2020). Adaptive acceleration waveform control of
  two-degree-of-freedom dual electrohydraulic shaking tables. Journal of Vibration and Control
  26(23-24), 2274-2285. DOI 10.1177/1077546320919320. Read: abstract only.
- Harte, T. J. (2007). Discrete-time model-based Iterative Learning Control: stability, monotonicity
  and robustness. PhD thesis, University of Sheffield. White Rose eTheses 3624. Read in part (pp. 62 to
  65).
- Harte, T. J., Hätönen, J., Owens, D. H. (2005). Discrete-time inverse model-based iterative learning
  control: stability, monotonicity and robustness. International Journal of Control 78(8), 577-586.
  DOI 10.1080/00207170500111606. Read: abstract only.
- Heitman, C., Babuska, V., Cap, J. S., Reid, J. B. (2016). Development of a Single Input Multiple
  Output (SIMO) Input Derivation Algorithm for Oscillatory Decaying Shocks. 86th Shock and Vibration
  Symposium (2015). SAND2016-3995C, OSTI 1365337. Read in full.
- Heitman, C., Cap, J. S. (2019). Derivation of Shaker Shock Input of an Oscillatory Decaying Shock to
  Optimize High Frequency SRS. 89th Shock and Vibration Symposium (2018). SAND2019-1566C, OSTI 1639221.
  Read in full.
- Hopkins, R., Sisemore, C. (2019). Design of a Resonant Plate Shock Test for Simultaneous Multi-Axis
  Excitation. 89th Shock and Vibration Symposium (2018). SAND2019-0777C, OSTI 1596217. Read in full.
- Jacobs-O'Malley, L. D., Hofer, J. H. (2017). Nonlinear Feature Extraction and Energy Dissipation of
  Foam/Metal Interfaces. SAND2017-4293. DOI 10.2172/1595879. Read in part (sections 1, 3.1, 3.3, 3.4
  and the summary).
- Karshenas, A. M., Dunnigan, M. W., Williams, B. W. (2000). Adaptive inverse control algorithm for
  shock testing. IEE Proceedings, Control Theory and Applications 147(3), 267-276.
  DOI 10.1049/ip-cta:20000166. Read: abstract only.
- Khan, M. Y., Hunter, P., Pacini, B. R., Roettgen, D. R., Schoenherr, T. F. (2021). Evaluation of
  Joint Modeling Techniques Using Calibration and Fatigue Assessment of a Bolted Structure. In
  Nonlinear Structures & Systems, Volume 1, 33-52. DOI 10.1007/978-3-030-77135-5_4. Read in part
  (slides SAND2020-13875C only).
- Krack, M., Brake, M. R. W., Schwingshackl, C., and 29 co-authors (2025). The Tribomechadynamics
  Research Challenge: Confronting blind predictions for the linear and nonlinear dynamics of a
  thin-walled jointed structure with measurement results. Mechanical Systems and Signal Processing
  224, 112016. DOI 10.1016/j.ymssp.2024.112016. Read in part (sections 4 and 5).
- Krieghbaum, R., Danforth, S. M. (2026). Investigating Three-Axis Shock and Vibration with a
  "Supplemental Shaker" Frame. In Dynamic Environments and Durability Testing, Volume 7, chapter 3,
  35-50. River Publishers. DOI 10.13052/rp-9788743814184a03. Read in full.
- Kuether, R. J., Brake, M. R. W. (2016). Instantaneous Frequency and Damping from Transient Ring-Down
  Data. In Dynamics of Coupled Structures, Volume 4, 253-263. DOI 10.1007/978-3-319-29763-7_24.
  SAND2015-9173C. Read in full.
- Kuether, R. J., Najera, D. A. (2017). Modeling Nonlinear Energy Dissipation of the Ministack
  Assembly. SAND2017-10517. DOI 10.2172/1596201. Read in part (sections 1, 2.3, 3, 4, 5 and 7).
- Lacayo, R., Pesaresi, L., Groß, J., Fochler, D., Armand, J., Salles, L., Schwingshackl, C., Allen,
  M., Brake, M. (2019). Nonlinear modeling of structures with bolted joints: A comparison of two
  approaches based on a time-domain and frequency-domain solver. Mechanical Systems and Signal
  Processing 114, 413-438. DOI 10.1016/j.ymssp.2018.05.033. Read in part.
- Lai, Z., Mylonas, C., Nagarajaiah, S., Chatzi, E. (2021). Structural identification with
  physics-informed neural ordinary differential equations. Journal of Sound and Vibration 508,
  116196. DOI 10.1016/j.jsv.2021.116196. Read in part (author version).
- Larbi, S. H., Bourahla, N., Benchoubane, H., Choutri, K., Badaoui, M. (2020). Earthquake Ground
  Motion Matching on a Small Electric Shaking Table Using a Combined NN-PDFF Controller. Shock and
  Vibration 2020, 7260590. DOI 10.1155/2020/7260590. Read in full.
- Larsen, W. (2018). Analysis of the Shock Response Spectrum and Resonant Plate Testing Methods. MS
  thesis, Michigan Technological University. Read: abstract only.
- Larsen, W., Blough, J. R., DeClerck, J., VanKarsen, C., Soine, D., Jones, R. J. (2020).
  Understanding Multi-Axis SRS Testing Results. In Sensors and Instrumentation, Aircraft/Aerospace,
  Energy Harvesting & Dynamic Environments Testing, Volume 7, 377-385. DOI
  10.1007/978-3-030-12676-6_36. Record only.
- Liu, Z., Cai, C., Yu, M., Yang, M. (2017). Multi-Exciter Vibration Control for Spatial Orbit Motion.
  Joint IMEKO TC3, TC5 and TC22 International Conference, Helsinki, paper IMEKO-TC22-2017-011. Read in
  full.
- Ma, Y., Chen, H., Lu, X., Zheng, R. (2023). Half sine shock on random control method for
  multi-axial vibration testing. Journal of Vibration and Control 29(13-14), 2995-3005 (online 2022).
  DOI 10.1177/10775463221090008. Read: abstract only.
- Mayes, R. L., Pacini, B. R., Roettgen, D. R. (2016). A Modal Model to Simulate Typical Structural
  Dynamic Nonlinearity. In Dynamics of Coupled Structures, Volume 4, 57-76.
  DOI 10.1007/978-3-319-29763-7_7. Read in part (slides SAND2016-0079C only).
- Müller, F., Woiwode, L., Gross, J., Scheel, M., Krack, M. (2022). Nonlinear damping quantification
  from phase-resonant tests under base excitation. Mechanical Systems and Signal Processing 177,
  109170. DOI 10.1016/j.ymssp.2022.109170. Read in part (preprint, section 5).
- Najera-Flores, D. A. (2019). Machine Learning to Replicate Launch Vibration Conditions with Ground
  Testing. Slides, Spacecraft and Launch Vehicle Dynamic Environments Workshop. SAND2019-5886C,
  OSTI 1640181. Read in full.
- Najera-Flores, D. A., Ortiz, J., Khan, M. Y., Kuether, R. J., Miles, P. R. (2024). A Bayesian
  Multi-Fidelity Neural Network to Predict Nonlinear Frequency Backbone Curves. Journal of
  Verification, Validation and Uncertainty Quantification 9(2), 021003. DOI 10.1115/1.4064776. Read in
  part (accepted manuscript).
- Owens, B., Tipton, G., McDowell, M. (2015). 6 Degree of Freedom Shock and Vibration: Testing and
  Analysis. Shock and Vibration Exchange, Orlando. SAND2016-1583C, OSTI 1345305. Read in full.
- Owens, D. H., Hätönen, J., Daley, S. (2006). Robust Gradient-based Discrete-time Iterative Learning
  Control Algorithms. Research Report 916, Department of Automatic Control and Systems Engineering,
  University of Sheffield. Read in part (sections 1 to 7, the example and the conclusions).
- Owens, D. H., Hätönen, J. J., Daley, S. (2009). Robust monotone gradient-based discrete-time
  iterative learning control. International Journal of Robust and Nonlinear Control 19(6), 634-661.
  DOI 10.1002/rnc.1338. Read: abstract only.
- Pacini, B. R. (2025). Industrial Applications of Nonlinear Modal Modeling: Two Case Studies. In
  Nonlinear Structures & Systems, Volume 1, 49-62. River Publishers. DOI
  10.13052/97887-438-0146-7_8. SAND2024-13378C. Read in part (section 4).
- Peeters, M., Kerschen, G., Golinval, J. C. (2011). Modal testing of nonlinear vibrating structures
  based on nonlinear normal modes: Experimental demonstration. Mechanical Systems and Signal
  Processing 25(4), 1227-1247. DOI 10.1016/j.ymssp.2010.11.006. Read in full.
- Peláez-Rodríguez, C., Magdaleno, Á., García Terán, J. M., Pérez-Aracil, J., Salcedo-Sanz, S.,
  Lorenzana, A. (2024). An iterative neural network approach applied to human-induced force
  reconstruction using a non-linear electrodynamic shaker. Heliyon 10(12), e32858.
  DOI 10.1016/j.heliyon.2024.e32858. Read in full.
- Peláez-Rodríguez, C., Magdaleno, Á., Salcedo-Sanz, S., Lorenzana, A. (2023). Human-induced force
  reconstruction using a non-linear electrodynamic shaker applying an iterative neural network
  algorithm. Bulletin of the Polish Academy of Sciences: Technical Sciences 71(3), e144615.
  DOI 10.24425/bpasts.2023.144615. Read in full.
- Rader, P., Berry, R. (1979). Experimental Investigation of Launch Vehicle Transient Input Simulation
  in Payload Tests. NASA CR-145349, Martin Marietta Corporation report MCR-78-555, for NASA Langley
  Research Center. Read in full.
- Renson, L., Ehrhardt, D. A., Barton, D. A. W., Neild, S. A., Cooper, J. E. (2016). Connecting
  nonlinear normal modes to the forced response of a geometric nonlinear structure with closely spaced
  modes. Proceedings of ISMA 2016, 2775-2784. Read in full.
- Roettgen, D. R. (2016). Experimental Dynamic Substructuring Using Nonlinear Modal Joint Models. PhD
  dissertation, University of Wisconsin-Madison. Read in part (sections 1.4, 3, 5.3 and 5.5,
  chapters 6 and 7).
- Rohe, D. P., Schultz, R., Hunter, N. (2022). Rattlesnake: An Open-Source Multi-Axis and Combined
  Environments Vibration Controller. IMAC XL. SAND2021-13012C, OSTI 1893280. Read in part (all prose).
- Rohe, D. P., Schultz, R., Hunter, N. (2024). Rattlesnake User's Manual, Version 3. SAND2024-14378.
  DOI 10.2172/2480206. Read in part (prose of sections 3.4 to 3.6, chapter 13, parts of chapters 14
  and 16, Appendices B and C).
- Ross, M., Schneider, R., Kalinich, D. (2026). Derivation of Shaker Table Inputs for Sub-system
  Response Specifications: Vibration and Shock. IMAC XLIV. SAND2025-12615C, OSTI 17086462. Read in
  full.
- Schoenherr, T. F., Soine, D. E., Witt, B. L. (2022). Experimental Modal Analysis of a Resonant Plate
  During a Mid-Field Pyroshock Replication Test. In Sensors and Instrumentation, Aircraft/Aerospace and
  Dynamic Environments Testing, Volume 7, 41-52. DOI 10.1007/978-3-031-05415-0_4. SAND2021-12649C. Read
  in full.
- Schoukens, J., Vaes, M., Pintelon, R. (2016). Linear System Identification in a Nonlinear Setting:
  Nonparametric Analysis of the Nonlinear Distortions and Their Impact on the Best Linear
  Approximation. IEEE Control Systems Magazine 36(3), 38-69. DOI 10.1109/MCS.2016.2535918. Read in part
  (postprint arXiv 1804.09587).
- Schultz, R. (2019). Explorations in Multiple-Input Shaker Shock Testing. Shock and Vibration
  Symposium, Atlanta. SAND2019-13075C, OSTI 1643016. Read in full.
- Schultz, R., Carter, S. (2024). A MIMO Time Waveform Replication Control Implementation. In Dynamic
  Environments Testing, Volume 7 (IMAC XLI, 2023), 131-140. DOI 10.1007/978-3-031-34930-0_13.
  SAND2022-13874C. Read in full (submitted version).
- Segalman, D. J. (2002). A Four-Parameter Iwan Model for Lap-Type Joints. SAND2002-3828.
  DOI 10.2172/805877. Journal version: Journal of Applied Mechanics 72(5), 752-760 (2005). Read in
  part (the report).
- Sharma, H., Najera-Flores, D. A., Todd, M. D., Kramer, B. (2024). Lagrangian operator inference
  enhanced with structure-preserving machine learning for nonintrusive model reduction of mechanical
  systems. Computer Methods in Applied Mechanics and Engineering 423, 116865.
  DOI 10.1016/j.cma.2024.116865. Read in part (preprint arXiv 2404.05040).
- Shen, G., Zhu, Z.-C., Li, X., Wang, Q.-G., Li, G., Tang, Y. (2018). Acceleration waveform replication
  on six-degree-of-freedom redundant electro-hydraulic shaking tables using an inverse model
  controller with a modelling error. Transactions of the Institute of Measurement and Control 40(3),
  968-986 (online 2016). DOI 10.1177/0142331216675671. Read: abstract only.
- Sisemore, C., Babuska, V., Booher, J. (2016). 6-DOF Mechanical Shock Failure Predictions of a
  Cantilever Structure Using Energy Response Spectra Methods. 87th Shock and Vibration Symposium.
  SAND2017-1908C, OSTI 1458250. Read in full.
- Sisemore, C., Babuska, V., Booher, J. (2017). Energy Based Representation of 6-DOF Shaker Shock
  Low-Cycle Fatigue Tests. IMAC XXXV, 115-124. DOI 10.1007/978-3-319-54735-0_13. SAND2016-11182C. Read
  in full (manuscript).
- Sisemore, C., Babuska, V., Flores, R. (2020). Multi-Axis Resonant Plate Shock Testing Evaluation and
  Test Specification Development. SAND2020-10224. DOI 10.2172/1670873. Read in part (abstract,
  sections 9 and 10).
- Smallwood, D. O. (1994). Characterization and Simulation of Transient Vibrations Using Band Limited
  Temporal Moments. Shock and Vibration 1(6), 507-527. DOI 10.1155/1994/940635. Read: abstract only.
- Smallwood, D. O., Nord, A. O. (1974). Matching Shock Spectra With Sums of Decaying Sinusoids
  Compensated for Shaker Velocity and Displacement Limitations. Shock and Vibration Bulletin 44, Part 3.
  Not obtained (record as cited by Cap and Smallwood 1997).
- Soine, D. E. (2024). Resonant plate shock test response with isolated damping bars. ISMA 2024.
  SAND2024-06818C, OSTI 2585153. Read in part (section 2.3).
- Underwood, M., Keller, T. (2004). Rectangular Control of Multi-Shaker Systems: Theory and Practical
  Results. Journal of the IEST 47(1), 80-86. DOI 10.17764/jiet.47.1.u8558668l644n166. Read: abstract
  only.
- Wall, M., Allen, M. S., Kuether, R. J. (2022). Observations of modal coupling due to bolted joints in
  an experimental benchmark structure. Mechanical Systems and Signal Processing 162, 107968.
  DOI 10.1016/j.ymssp.2021.107968. Read in full (accepted manuscript).
- Watts, A. (2026). Inverse Reconstruction of Novel Time Series From Shock Response Spectrum Curves
  With Machine Learning. Slides for IMAC 2027. LA-UR-26-28272, DOI 10.2172/3874857. Read in full.
- Watts, A., Jeon, A., Newton, D., Bowering, R. (2026a). Inverse Reconstruction of Shock Time Series
  from Shock Response Spectrum Curves using Machine Learning. arXiv 2603.03229v3. Not peer reviewed.
  Read in full.
- Watts, A., Young, C., Bowering, R., Jeon, A., Newton, D. (2026b). Inverse Synthesis of Shock Time
  Series from Shock Response Spectra Using Ensembles of Conditional Variational Autoencoders. arXiv
  2610.12820v1. Not peer reviewed. Read in part.
- Xu, H., Chen, H., You, W. (2010). Study on multiple-input multiple-output shock vibration testing
  (in Chinese). Journal of Vibration, Measurement and Diagnosis 30(2), 143-148. Read: abstract only.
- Zheng, R., Ma, Y., Wei, X., Chen, H. (2023). Multi-shaker shock response spectra replication
  control. Journal of Vibration and Control 29(15-16), 3744-3755 (online 30 May 2022).
  DOI 10.1177/10775463221104577. Read: abstract only.
- Zheng, R., Ren, S., Chen, G., Chen, H. (2021). Multi-shaker half sine shock on random mixed vibration
  control. Journal of Sound and Vibration 512, 116372. DOI 10.1016/j.jsv.2021.116372. Record only.
- Zou, X., Li, H., Wang, H. (2019). Composite environmental test technique of multi-axial vibration and
  shock (in Chinese). Journal of Vibration and Shock 38(3), 237-243.
  DOI 10.13465/j.cnki.jvs.2019.03.033. Read in full.

**Patents**

- Underwood, M. A. (1994). Adaptive control method for multiexciter sine tests. US Patent 5,299,459,
  issued 5 April 1994. Read in full.
- Underwood, M. A. (1996). Apparatus and method for adaptive closed loop control of shock testing
  system. US Patent 5,517,426, issued 14 May 1996 (priority 29 October 1992). Read in full.
- Zheng, R., Chen, H. (2022). System and method for multi-shaker shock plus random vibration testing
  (in Chinese). Chinese patent CN113155385B, Nanjing University of Aeronautics and Astronautics, filed
  9 June 2021, granted 28 June 2022. Read in part (machine translation; equation images not opened).
- Zheng, R., Chen, H., Wei, X. (2022). Shock response spectrum reproduction control method for
  multi-axis shock vibration testing (in Chinese). Chinese patent application CN115130506A, Nanjing
  University of Aeronautics and Astronautics, filed 24 June 2022; deemed withdrawn 22 August 2025. Read
  in full.

**Controller Makers' Public Material** (read 15 November 2026)

- Crystal Instruments. Multiple Axis Vibration Testing; MIMO Shock Response Spectrum Vibration
  Testing; Multiple-Input Multiple-Output Shock Vibration Test. Web pages. Read in full.
- Data Physics. Multi-Shaker Vibration Controllers; Multi-Axis Testing in Any Arrangement and
  Configuration; SRS Shock Synthesis and Control. Web pages. Read in full.
- IMV Corporation (2019). Multi-axis Multi-point Control System for Finite Length Waveforms
  Replication, K2 BMAC Instruction Manual, revision 14.3.0. Read in part (sections 1.1, 4.3.6, 4.9,
  4.10, 6.5.7, 6.14, 7.3.3 and 7.3.4).
- Musella, U. (2023). Realistic shock replication: Simcenter Testlab 2306 Shock & MIMO Shock Control.
  Siemens Simcenter blog, 23 October 2023. Read in full.
- Spectral Dynamics (2007). Multiple-Exciter Shock (Transient Waveform Control), Technical
  Specifications, JAGUAR Systems. Data sheet MShock0507. Read in full.
- Vibration Research. 3-axis Control. Web page. Read in full.
- Zhuge, J. (2024). MIMO SRS Vibration Testing on Dual Shaker Vertical Configuration. Crystal
  Instruments blog, 6 March 2024. Read in full.
