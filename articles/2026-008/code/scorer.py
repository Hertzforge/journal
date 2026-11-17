"""Scorer for the Frames problems of the Hertzforge Open Benchmark Set (format 0.2-draft, set version 0.2).

Reads problem folders of version 0.2-draft and 0.1-draft. Every number it gives on a 0.1 problem is the number
the 0.1 scorer gave (the regression check holds it to that, value for value).

One file. Needs numpy and the Python standard library, nothing else, and imports no study module.

    python scorer.py score PROBLEM_FOLDER RUN_FOLDER [--target banded|line] [--out scorecard.json]

PROBLEM_FOLDER  a staged problem folder (problem.json, structure.json, target_line.c16, scoring/).
RUN_FOLDER      a run result: manifest.json (grid, outcome), drive_sdm_played.c16 (lines, drives, drives; V^2/Hz;
                the drive the structure was handed over the record), response_psd_played.f8 or .f4 (lines, outputs;
                the outputs as read back) and, on a structure that changes with level, response_moments_played.f8
                (2, monitors, monitors). This is what the study keeps of every run.

What it writes: a scorecard, not a verdict.
  outcome      completed, or stopped: which guard, at which loop, on which control or drive (requirement R10)
  report_card  the six lines of the report card (MIMO acceptance proposal, item 4; working paper, section 5)
               and the reference measures R1 and R3 beside them
  stress       the stress in every beam element against the article's stress in service (the problem's stress truth)
  ers          response spectra (Q = 10 and 50) at the held-out gauges and the component tips, against service
  card         the same report-card figures under the study's key names (x4_truth.py), kept so the two can be compared
  structure_state  on a structure that changes with level: each mode's frequency change as played, with its sign (a drop
               negative, a rise positive), per mode and in summary by effect (softening, hardening), against the
               structure's level_targets. The 0.1 figures (drop_pct_..., drop_over_target_p50, ...) are kept beside it.
               service_line (0.2.1): beside the state as played, the problem's service_state (unit B in service): the
               member's mode played against in service, and the softening modes' spread played against in service.
A run that stopped before its record, or inside it with fewer than 40 Welch frames, has an outcome and no scores.
The stress block is optional: a problem with no stress truth (scoring/stress_truth and stress_modal absent) is
scored on its gauges and its stress block is null; with no service_b_psd the ers block is null. The scorecard's
problem block carries the problem's stage (1: the structure does not change with level; 2: it does) and effects.

Two routes to what the article saw, named by the problem (problem.json, scorecard.stress_route):
  drive          the structure does not change with level: stress and gauge responses are the played drive taken
                 through the structure's own modal model.
  played_modal   the structure changes with level: gauge responses are the played output autospectra, stress comes
                 from the modal monitors' displacement band moments, and the structure's state as played is reported.

Every number that x4_truth.py also computes is held to it: see the parity check and the study's notes.
Starting values (1.5 dB level; grades at 3, 4.5 and 6 dB; alarm at +6 dB) are provisional.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

SCORER_VERSION = '0.2.1-draft'      # 0.2.1 (the study, 2026-11-15): structure_state.service_line added; every earlier number unchanged
SCORECARD_SCHEMA = 'hertzforge-benchmark-scorecard/0.2.1-draft'
SCORECARD = 'mimo-metrics-report-card/0.1-provisional'
COND = 1e3                    # singular values under the largest / COND are dropped when "what the system can reach" is computed
DAMAGE_EXPONENTS = (8, 4)
LEVEL_DB = 1.5                # line 1 starting value
GRADES = (('A', 3.0), ('B', 4.5), ('C', 6.0))      # line 2 starting values
ALARM_DB = 6.0                # line 3
UNDER_DB = -3.0               # line 4
EXACT_FIT_DB = 1.0            # line 6: a control residual under this with as many drives as controls is flagged (provisional, not from the proposal)
MIN_PARTIAL_FRAMES = 40       # a run that stopped inside its record is scored only with at least this many Welch frames
TWO_PI = 2.0 * np.pi


# ---------------------------------------------------------------------------------------------- small helpers
def db10(a, b):
    return 10 * np.log10(np.maximum(a, 1e-300) / np.maximum(b, 1e-300))


def herm(A):
    return np.conj(A).transpose(0, 2, 1)


def band_matrix(f, per_octave):
    """(B, band_of_line): B (bands, lines) averages the lines of each band; a line belongs to band round(N log2(f / 1000))."""
    idx = np.round(per_octave * np.log2(f / 1000.0)).astype(int)
    u = np.unique(idx)
    B = (idx[None, :] == u[:, None]).astype(float)
    return B / B.sum(1, keepdims=True), (B > 0).argmax(0)


def sdof_kernel(f, df, q):
    """Rows: one natural frequency each, one-twelfth octave apart across the band. A row times an acceleration
    autospectrum is the mean-square absolute acceleration of an oscillator of quality factor q on that base."""
    fn = 1000 * 2.0 ** (np.arange(np.ceil(12 * np.log2(f[0] / 1000.0)), np.floor(12 * np.log2(f[-1] / 1000.0)) + 1) / 12)
    z = 1 / (2 * q)
    r = f[None, :] / fn[:, None]
    return (1 + (2 * z * r) ** 2) / ((1 - r ** 2) ** 2 + (2 * z * r) ** 2) * df


def pinv_trunc(H):
    """Pseudo-inverse of every line's matrix, singular values under the largest / COND dropped. Also the singular values."""
    U, s, Vh = np.linalg.svd(H, full_matrices=False)
    sinv = np.where(s >= s[:, :1] / COND, 1 / s, 0)
    return herm(Vh) @ (sinv[:, :, None] * herm(U)), s


def factor(D):
    """A factor Fd of a drive spectral matrix, D = Fd Fd^H on every line (negative eigenvalues set to zero)."""
    D = (D + herm(D)) / 2
    lam, V = np.linalg.eigh(D)
    return V * np.sqrt(np.clip(lam, 0, None))[:, None, :]


def stats(x):
    x = np.asarray(x, float)
    return dict(mean=float(x.mean()), rms=float(np.sqrt(np.mean(x ** 2))), max=float(x.max()), min=float(x.min()))


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for blk in iter(lambda: fh.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


# ---------------------------------------------------------------------------------------------- the problem
def stage_and_effects(meta, st):
    """(stage, effects). A 0.2 problem states them. A 0.1 problem is stage 1 when its structure is linear and stage 2
    when it has a level law; a 0.1 level law can only lower a frequency, so its effect is softening."""
    if 'stage' in meta:
        return int(meta['stage']), list(meta.get('effects', []))
    law = st.get('level_law')
    if not law:
        return 1, []
    return 2, (['softening'] if float(law.get('delta', 0.0)) > 0 else [])


def target_change(lt):
    """Each mode's signed target frequency change (fraction) from a structure's level_targets: 0.2 states it as
    frequency_change; 0.1 as frequency_drop, a positive fraction, so the change is its negative."""
    if 'frequency_change' in lt:
        return np.array(lt['frequency_change'], float)
    return -np.array(lt['frequency_drop'], float)


class Problem:
    """A problem folder as arrays. Channel order of the physical outputs: controls, held-out gauges, tips."""

    def __init__(self, folder):
        self.folder = folder
        with open(os.path.join(folder, 'problem.json')) as fh:
            self.meta = json.load(fh)
        with open(os.path.join(folder, self.meta['structure']['file'])) as fh:
            st = json.load(fh)
        self.structure = st
        g = self.meta['grid']
        self.df = g['fs_hz'] / g['nfft']
        self.f = (g['lo_line'] + np.arange(g['n_lines'])) * self.df
        self.w = TWO_PI * self.f
        self.fn = np.array([m['f_hz'] for m in st['modes']], float)
        self.zeta = np.array([m['zeta'] for m in st['modes']], float)
        self.dshape = np.array([m['drive_shape'] for m in st['modes']], float)       # (modes, drives), per volt
        self.oshape = np.array([m['output_shape'] for m in st['modes']], float)      # (modes, outputs)
        self.fpv = float(st['force_per_volt'])
        role = [(o['role'], o.get('group')) for o in st['outputs']]
        self.i_c = np.array([i for i, r in enumerate(role) if r[0] == 'control'], int)
        self.i_h = np.array([i for i, r in enumerate(role) if r == ('held_out', 'gauge')], int)
        self.i_t = np.array([i for i, r in enumerate(role) if r == ('held_out', 'tip')], int)
        self.i_m = np.array([i for i, r in enumerate(role) if r[0] == 'monitor'], int)
        self.n_phys = self.i_c.size + self.i_h.size + self.i_t.size
        assert np.array_equal(np.r_[self.i_c, self.i_h, self.i_t], np.arange(self.n_phys)), 'physical outputs must come first: controls, gauges, tips'
        assert np.array_equal(self.i_m, np.arange(self.n_phys, len(role))), 'monitors must come last'
        sc = self.meta['scoring']
        nc, nh, nt = self.i_c.size, self.i_h.size, self.i_t.size
        a = self.array(sc['service_a_psd'])
        self.GA_c, self.GA_h = a[:nc], a[nc:nc + nh]                                # unit A in service: the report card's reference
        if 'service_b_psd' in sc:
            b = self.array(sc['service_b_psd'])
            self.GB_h, self.GB_t = b[:nh], b[nh:nh + nt]                            # unit B in service: the response spectra's reference
        else:
            self.GB_h = self.GB_t = None                                            # no response-spectrum reference: no ers block
        self.has_stress = 'stress_truth' in sc and 'stress_modal' in sc
        if self.has_stress:
            t = self.array(sc['stress_truth'])
            self.truth = dict(rms=t[0], d8=t[1], d4=t[2])
            self.SB = self.array(sc['stress_modal'])                                # (8 x elements, modes)
        else:
            self.truth = self.SB = None                                             # no stress truth: scored on its gauges
        self.stage, self.effects = stage_and_effects(self.meta, st)
        self.GA_full = self.array(self.meta['targets']['line'])                     # (lines, controls, controls)
        self.mon_scale = self.array(sc['modal_monitor_scale']) if 'modal_monitor_scale' in sc else None
        self.route = self.meta['scorecard']['stress_route']
        self.B3, self.band_of_line = band_matrix(self.f, 3)

    def array(self, entry):
        return np.fromfile(os.path.join(self.folder, entry['file']), entry['dtype']).reshape(entry['shape']).astype(
            complex if 'c' in entry['dtype'] else float)

    def receptance(self):
        wn = TWO_PI * self.fn[:, None]
        return 1.0 / (wn ** 2 - self.w[None, :] ** 2 + 2j * self.zeta[:, None] * wn * self.w[None, :])      # (modes, lines)

    def frf(self, rows):
        """Small-signal acceleration response per volt at the given outputs, (lines, rows, drives)."""
        return np.einsum('mo,mf,md->fod', self.oshape[:, rows], self.receptance() * -self.w ** 2, self.dshape, optimize=True)


# ---------------------------------------------------------------------------------------------- the run result
def read_run(folder, problem):
    """(manifest, D, psd or None, moments or None). D in V^2/Hz, (lines, drives, drives)."""
    with open(os.path.join(folder, 'manifest.json')) as fh:
        man = json.load(fh)
    g, pg = man['grid'], problem.meta['grid']
    assert g['lo_line'] == pg['lo_line'] and g['n_lines'] == pg['n_lines'] and abs(g['df_hz'] - problem.df) < 1e-12, 'the run is not on the problem\'s grid'
    nf, nd = pg['n_lines'], problem.dshape.shape[1]
    D = psd = mom = None
    p = os.path.join(folder, 'drive_sdm_played.c16')
    if os.path.exists(p):
        D = np.fromfile(p, '<c16').reshape(nf, nd, nd)
    for name, dt in (('response_psd_played.f8', '<f8'), ('response_psd_played.f4', '<f4')):
        p = os.path.join(folder, name)
        if os.path.exists(p):
            psd = np.fromfile(p, dt).astype(float).reshape(nf, -1)
            break
    p = os.path.join(folder, 'response_moments_played.f8')
    if os.path.exists(p):
        M = np.fromfile(p, '<f8')
        n = int(round(np.sqrt(M.size / 2)))
        mom = M.reshape(2, n, n)
    return man, D, psd, mom


def outcome_of(man):
    """Completed, or stopped with the guard, the loop and the reason."""
    oc = man['outcome']
    out = dict(completed=bool(oc['completed']), protections=(man.get('protections') or {}).get('preset'),
               record=dict(status=oc.get('record_window_status'), frames=oc.get('record_frames_drive'),
                           loops_recorded=oc.get('record_loops_recorded'), loops_asked=oc.get('record_loops_asked')),
               full_level_loops=oc.get('loops_at_full'), stop=None)
    if not oc['completed']:
        t = oc.get('trip_record')
        if t:
            fl = t.get('fields') or {}
            out['stop'] = dict(guard=t['kind'], loop=t['at_loop'], level_db=t['at_level_db'], at_full_level=t['at_full_level'],
                               full_level_loops_done=t['full_level_loops_done'], control=t.get('control'), control_name=t.get('control_name'),
                               drive=t.get('drive'), error_db=fl.get('error_db', fl.get('worst_db')), lines=fl.get('abort_lines', fl.get('lines')),
                               consecutive_loops=fl.get('consecutive_loops'), words=t['words'])
        else:
            out['stop'] = dict(guard='run_error' if oc.get('run_error') else 'stopped_early', words=oc.get('run_error'), loop=oc.get('loops_total'))
    out['scored'] = bool(oc['completed'] or (oc.get('record_window_status') == 'partial' and (oc.get('record_frames_drive') or 0) >= MIN_PARTIAL_FRAMES))
    return out


# ---------------------------------------------------------------------------------------------- stress
def element_stress(m0, m2):
    """Per element, the worst of its 8 fibre points: RMS stress, and a damage rate for each exponent b (rate of
    zero crossings times RMS^b)."""
    rms = np.sqrt(m0.reshape(-1, 8))
    nu = np.sqrt(m2 / np.maximum(m0, 1e-300)).reshape(-1, 8)
    return dict(rms=rms.max(1), **{f'd{b}': (nu * rms ** b).max(1) for b in DAMAGE_EXPONENTS})


def stress_summary(lab, truth):
    """Element stress as played against the stress truth, in dB over the elements."""
    x = 20 * np.log10(lab['rms'] / truth['rms'])
    out = dict(rms=float(np.sqrt(np.mean(x ** 2))), bias=float(x.mean()), p5=float(np.percentile(x, 5)), p95=float(np.percentile(x, 95)),
               in3=float(np.mean(np.abs(x) <= 3)), max=float(x.max()))
    for b in DAMAGE_EXPONENTS:
        d = db10(lab[f'd{b}'], truth[f'd{b}'])
        out[f'd{b}_rms'] = float(np.sqrt(np.mean(d ** 2)))
        out[f'd{b}_bias'] = float(d.mean())
    return out


def stress_moments_drive(pr, Fd):
    """m0 and m2 of every fibre stress row from a drive factor through the structure's modal model."""
    A = (pr.dshape[None] @ Fd) * pr.receptance().T[:, :, None]            # modal displacement factor, (lines, modes, r)
    nm = pr.dshape.shape[0]

    def mom(Aw):
        A2 = Aw.transpose(1, 0, 2).reshape(nm, -1)
        C = (A2.real @ A2.real.T + A2.imag @ A2.imag.T) * pr.df
        return np.einsum('rm,mn,rn->r', pr.SB, C, pr.SB, optimize=True)
    return mom(A), mom(A * pr.f[:, None, None])


def stress_moments_modal(pr, M):
    """m0 and m2 of every fibre stress row from the modal monitors' displacement band moments M (2, modes, modes).

    Monitor m is scale_m times the acceleration of mode m, and the runner's M0_ij is the sum over the band lines of
    Re(G_ij) df / (2 pi f)^4 (M2 the same with f^2 inside), so M / (scale_i scale_j) is the covariance of the modal
    displacements as played, whatever the modes' frequencies and damping did.
    """
    sc = pr.mon_scale
    C0, C2 = M[0] / np.outer(sc, sc), M[1] / np.outer(sc, sc)
    return np.einsum('rm,mn,rn->r', pr.SB, C0, pr.SB, optimize=True), np.einsum('rm,mn,rn->r', pr.SB, C2, pr.SB, optimize=True)


# ---------------------------------------------------------------------------------------------- the card
def card_of(pr, D, G_c, G_h):
    """The report-card figures under the study's key names. G_c, G_h: autospectra as played, (channels, lines)."""
    B3, bol, nb = pr.B3, pr.band_of_line, pr.B3.shape[0]
    card, Eb = {}, {}
    for tag, Gl, Gr in (('c', G_c, pr.GA_c), ('h', G_h, pr.GA_h)):
        Eb[tag] = db10(Gl @ B3.T, Gr @ B3.T)
        card[f'{tag}_b3_rms'] = float(np.sqrt(np.mean(Eb[tag] ** 2)))
        card[f'{tag}_sum3_rms'] = float(np.sqrt(np.mean(db10(Gl.sum(0) @ B3.T, Gr.sum(0) @ B3.T) ** 2)))
        card[f'{tag}_line_rms'] = float(np.sqrt(np.mean(db10(Gl, Gr) ** 2)))
    allb = np.concatenate([Eb['c'], Eb['h']])
    alll = db10(np.concatenate([G_c, G_h]), np.concatenate([pr.GA_c, pr.GA_h]))
    card.update(level_mean=float(allb.mean()), worst_over_b3=float(allb.max()), worst_over_line=float(alll.max()),
                share_over6_b3=float(np.mean(allb > ALARM_DB)), share_over6_line=float(np.mean(alll > ALARM_DB)),
                held_under3_b3=float(np.mean(Eb['h'] < UNDER_DB)), ctrl_under6_b3=float(np.mean(Eb['c'] < -6)))
    # what the system can reach at its controls: P G P^H with P = H pinv(H), the structure's small-signal model
    Hc = pr.frf(pr.i_c)
    Z, s = pinv_trunc(Hc)
    P = Hc @ Z
    gp = np.real(np.einsum('fii->if', P @ pr.GA_full @ herm(P)))
    dev = db10(gp @ B3.T, pr.GA_c @ B3.T)
    vs = db10(G_c @ B3.T, gp @ B3.T)
    card.update(declared_b3_rms=float(np.sqrt(np.mean(dev ** 2))), declared_b3_max=float(dev.max()), declared_b3_min=float(dev.min()),
                vs_declared_b3_rms=float(np.sqrt(np.mean(vs ** 2))))
    Dss = np.real(np.einsum('fii->fi', D))                                 # (lines, drives), V^2/Hz
    vrms = np.sqrt(Dss.sum(0) * pr.df)
    card['drive_rms'] = [float(v * pr.fpv) for v in vrms]                  # newtons, as the study reports it
    card['drive_line_to_band_db'] = [float(10 * np.log10(max(
        Dss[bol == b, j].max() / max(Dss[bol == b, j].mean(), 1e-300) for b in range(nb)))) for j in range(Dss.shape[1])]
    extra = dict(Eb=Eb, cond=s[:, 0] / s[:, -1], drive_vrms=[float(v) for v in vrms], G_c=G_c)
    return card, extra


def grade(v):
    for name, lim in GRADES:
        if v <= lim:
            return name
    return 'below C'


def report_card(pr, card, extra):
    """The six lines, and the reference measures R1 and R3, from the card figures."""
    nd, nc = pr.dshape.shape[1], pr.i_c.size
    Eh, cond, G_c = extra['Eb']['h'], extra['cond'], extra['G_c']
    E = db10(G_c, pr.GA_c)                                                  # control line errors, (controls, lines)
    inside = np.where(pr.f[None, :] <= 500.0, np.abs(E) <= 3.0, np.abs(E) <= 6.0)
    ratio = np.sqrt(G_c.sum(1) / pr.GA_c.sum(1))
    wgt = pr.GA_c / pr.GA_c.sum(0, keepdims=True)
    e527 = (wgt * E).sum(0)
    return dict(
        scorecard=SCORECARD, provisional=True,
        line_1_level=dict(mean_error_db=card['level_mean'], starting_value_db=LEVEL_DB, within=bool(abs(card['level_mean']) <= LEVEL_DB),
                          what='mean dB error over controls and held-out gauges and one-third-octave bands'),
        line_2_pattern=dict(
            held_out=dict(summed_rms_db=card['h_sum3_rms'], per_channel_rms_db=card['h_b3_rms'], grade=grade(card['h_sum3_rms'])),
            controls=dict(summed_rms_db=card['c_sum3_rms'], per_channel_rms_db=card['c_b3_rms'], grade=grade(card['c_sum3_rms'])),
            grades_db=dict(GRADES), what='RMS dB error of the summed autospectra in one-third-octave bands, with the per-channel band error beside it'),
        line_3_over_test=dict(worst_band_db=card['worst_over_b3'], share_of_bands_over_alarm=card['share_over6_b3'],
                              worst_line_db=card['worst_over_line'], share_of_lines_over_alarm=card['share_over6_line'],
                              alarm_db=ALARM_DB, alarm=bool(card['worst_over_b3'] > ALARM_DB), what='controls and held-out gauges, any band'),
        line_4_under_test=dict(share_of_held_out_bands_more_than_3_db_under=card['held_under3_b3'],
                               share_of_control_bands_more_than_6_db_under=card['ctrl_under6_b3'],
                               held_out_band_error_p10_db=float(np.percentile(Eh, 10)), what='reported; it does not stop a run'),
        line_5_declared=dict(declared_deviation_rms_db=card['declared_b3_rms'], declared_deviation_max_db=card['declared_b3_max'],
                             declared_deviation_min_db=card['declared_b3_min'], law_error_rms_db=card['vs_declared_b3_rms'],
                             what='what the system can reach at its controls against the target, and the played response against that, one-third-octave bands'),
        line_6_rig=dict(drives=int(nd), controls=int(nc), condition_median=float(np.median(cond)), condition_p95=float(np.percentile(cond, 95)),
                        condition_max=float(cond.max()), control_residual_rms_db=card['c_b3_rms'],
                        exact_fit_flag=bool(nd >= nc and card['c_b3_rms'] < EXACT_FIT_DB), exact_fit_flag_under_db=EXACT_FIT_DB,
                        what='condition of the control response matrix over the band lines; a near-zero control residual with as many drives as controls is flagged'),
        reference_r1=dict(share_of_control_lines_inside=float(inside.mean()), controls_with_overall_rms_inside_15_percent=float(np.mean(np.abs(ratio - 1) <= 0.15)),
                          what='3 dB to 500 Hz and 6 dB above, per line and control; overall RMS per control within 15 percent',
                          source='MIMO acceptance proposal, line R1; not yet checked against the text of the standard'),
        reference_r3=dict(global_error_rms_db=float(np.sqrt(np.mean(e527 ** 2))), global_error_max_abs_db=float(np.abs(e527).max()),
                          share_of_lines_beyond_3_db=float(np.mean(np.abs(e527) > 3)),
                          what='per line, the dB error over the controls weighted by each control\'s share of the reference',
                          source='as an earlier study computed it (g527); not yet checked against the text of the standard'))


def modal_state(pr, D, psd, span=4.0):
    """Each mode's frequency and apparent damping as played, from the modal monitors (structures that change with level).

    |H_m|^2 = G_am / (phi_m^T G_dd phi_m), and for one mode w^4 / |H_m|^2 = w^4 + (4 zeta^2 - 2) wn^2 w^2 + wn^4, linear in
    ((4 zeta^2 - 2) wn^2, wn^4): fitted by least squares on the lines within `span` half-power bandwidths of the mode
    (at least 6 lines), weighted by |H|^2, recentred twice.
    """
    f, w, df = pr.f, pr.w, pr.df
    Ga = psd[:, pr.i_m].T / (pr.mon_scale[:, None] ** 2)
    Gu = np.real(np.einsum('ms,fst,mt->mf', pr.dshape, D, pr.dshape, optimize=True))
    n = pr.i_m.size
    fn = np.full(n, np.nan)
    ze = np.full(n, np.nan)
    for m in range(n):
        if not (f[0] + 5 < pr.fn[m] < f[-1] - 5):
            continue
        for _ in range(3):
            fc = pr.fn[m] if np.isnan(fn[m]) else fn[m]
            zc = pr.zeta[m] if np.isnan(ze[m]) else max(ze[m], pr.zeta[m])
            half = max(span * zc * fc, 6 * df)
            k = np.flatnonzero((np.abs(f - fc) <= half) & (Gu[m] > 0) & (Ga[m] > 0))
            if k.size < 6:
                break
            w2 = w[k] ** 2
            H2 = Ga[m, k] / Gu[m, k]
            y = w2 ** 2 / H2 - w2 ** 2
            wt = H2 / H2.max()
            A = np.stack([w2, np.ones_like(w2)], 1) * wt[:, None]
            b, cc = np.linalg.lstsq(A / np.abs(y).max(), y * wt / np.abs(y).max(), rcond=None)[0]
            if cc <= 0:
                break
            wn2 = np.sqrt(cc)
            z2 = (b / wn2 + 2) / 4
            if z2 <= 0:
                break
            fn[m] = np.sqrt(wn2) / TWO_PI
            ze[m] = np.sqrt(z2)
    return fn, ze


def structure_state(pr, D, psd):
    """What a structure that changes with level did at full level: realized frequency drop and damping factor."""
    lt = pr.structure.get('level_targets')
    if lt is None or pr.i_m.size == 0:
        return None
    fn, ze = modal_state(pr, D, psd)
    el = np.arange(pr.fn.size) >= pr.structure.get('rigid_modes', 6)
    tc = target_change(lt)
    td, tz = -tc, np.array(lt['damping_factor'])
    ok = ~np.isnan(fn) & el & (2 * pr.zeta * pr.fn >= 2.0)                  # resolved: a half-power width of four lines
    drop, zf = 1 - fn / pr.fn, ze / pr.zeta
    q = lambda v: [float(np.percentile(v, p)) for p in (10, 50, 90)] if np.size(v) else None
    out = dict(kind=pr.structure['kind'], modes_fitted=int(ok.sum()), drop_pct_p10_p50_p90=q(100 * drop[ok]), zfac_p10_p50_p90=q(zf[ok]),
               target_drop_pct_p10_p50_p90=q(100 * td[ok]), target_zfac_p10_p50_p90=q(tz[ok]),
               drop_over_target_p50=float(np.median(drop[ok] / td[ok])) if (td[ok] > 0).all() else None,
               zrise_over_target_p50=float(np.median((zf[ok] - 1) / (tz[ok] - 1))) if (tz[ok] > 1).all() else None)
    out['signed'] = signed_state(pr, fn, ze, tc, tz, ok)
    out['service_line'] = service_line(pr, fn, ze, tc, ok)
    return out


def member_mode(pr):
    """The member's mode on the shakers: the mode whose own level rule has the largest rise (None if no mode rises)."""
    rise = np.array([((m.get('level') or {}).get('rise') or 0.0) for m in pr.structure['modes']], float)
    return int(np.argmax(rise)) if rise.size and rise.max() > 0 else None


def service_line(pr, fn, ze, tc, ok):
    """The state as played beside the problem's service_state (unit B in service, problem.json; added in 0.2.1).

    The member: its mode on the shakers (member_mode), the change and damping factor as played (the modal fit), the
    same in service, and played less service. The softening modes: the p10, p50 and p90 of the resolved softening modes'
    change and damping factor as played, the service article modes' (service_state.article), and played less service.
    The service modes are those of the article in service, not the lab modes, so only the spreads are compared. None
    when the problem has no service_state."""
    ss = pr.meta.get('service_state')
    if not ss:
        return None
    q = lambda v: [float(np.percentile(v, p)) for p in (10, 50, 90)] if np.size(v) else None
    out = dict(what='the state as played beside the state in service (unit B): the member\'s mode, and the softening modes in summary; '
                    'changes in percent of the small-signal frequency, differences in percentage points (played less service)',
               unit=ss.get('unit'), member=None, softening=None)
    m = member_mode(pr)
    sm = ss.get('member')
    if m is not None and sm is not None:
        fitted = bool(np.isfinite(fn[m]))
        ch = float(100 * (fn[m] / pr.fn[m] - 1)) if fitted else None
        zf = float(ze[m] / pr.zeta[m]) if fitted else None
        sc, sz = 100 * float(sm['frequency_change']), float(sm['damping_factor'])
        out['member'] = dict(mode=m, f0_hz=float(pr.fn[m]), resolved=bool(ok[m]), fitted=fitted,
                             change_pct_played=ch, change_pct_service=sc, change_pct_target=float(100 * tc[m]),
                             difference_pct_points=None if ch is None else ch - sc,
                             zfac_played=zf, zfac_service=sz, zfac_difference=None if zf is None else zf - sz,
                             service_f0_hz=float(sm['f0_hz']))
    sa = ss.get('article')
    if sa is not None:
        sel = ok & (tc < 0)
        pc, pz = q(100 * (fn[sel] / pr.fn[sel] - 1)), q(ze[sel] / pr.zeta[sel])
        scq = [100 * float(v) for v in sa['frequency_change_p10_p50_p90']]
        szq = [float(v) for v in sa['damping_factor_p10_p50_p90']]
        out['softening'] = dict(modes_played=int(sel.sum()), modes_service=int(sa['modes']),
                                change_pct_played_p10_p50_p90=pc, change_pct_service_p10_p50_p90=scq,
                                difference_pct_points_p10_p50_p90=None if pc is None else [a - b for a, b in zip(pc, scq)],
                                zfac_played_p10_p50_p90=pz, zfac_service_p10_p50_p90=szq,
                                zfac_difference_p10_p50_p90=None if pz is None else [a - b for a, b in zip(pz, szq)])
    return out


def signed_state(pr, fn, ze, tc, tz, ok):
    """The structure's state as played with its sign: each fitted mode's frequency change (fraction, negative for a
    drop and positive for a rise) against its target, and the summary by effect. A mode's effect is the sign of its
    target: softening (target below zero), hardening (above), unchanged (zero)."""
    ch = fn / pr.fn - 1.0
    q = lambda v: [float(np.percentile(v, p)) for p in (10, 50, 90)] if np.size(v) else None
    eff = np.where(tc < 0, 'softening', np.where(tc > 0, 'hardening', 'unchanged'))

    def summary(sel):
        s = ok & sel
        n = int(s.sum())
        blk = dict(modes_fitted=n, change_pct_p10_p50_p90=q(100 * ch[s]), target_change_pct_p10_p50_p90=q(100 * tc[s]),
                   error_pct_points_p10_p50_p90=q(100 * (ch[s] - tc[s])), abs_error_pct_points_p50=float(np.median(100 * np.abs(ch[s] - tc[s]))) if n else None,
                   zfac_p10_p50_p90=q(ze[s] / pr.zeta[s]), target_zfac_p10_p50_p90=q(tz[s]))
        nz = s & (tc != 0)
        blk['change_over_target_p50'] = float(np.median(ch[nz] / tc[nz])) if nz.any() else None
        blk['sign_right_share'] = float(np.mean(np.sign(ch[nz]) == np.sign(tc[nz]))) if nz.any() else None
        return blk
    by = {e: summary(eff == e) for e in ('softening', 'hardening', 'unchanged') if (ok & (eff == e)).any()}
    modes = [dict(mode=int(m), effect=str(eff[m]), f0_hz=float(pr.fn[m]), f_played_hz=float(fn[m]), change=float(ch[m]),
                  target_change=float(tc[m]), zfac=float(ze[m] / pr.zeta[m]), target_zfac=float(tz[m])) for m in np.flatnonzero(ok)]
    return dict(what='each mode\'s frequency change as played, signed: negative is a drop (softening), positive a rise (hardening); '
                     'percent of the small-signal frequency, against the target at full level',
                all=summary(np.ones(ch.size, bool)), by_effect=by, modes=modes)


# ---------------------------------------------------------------------------------------------- the score
def score_drive(pr, D):
    """Stress, response spectra and card with the played drive taken through the structure's modal model."""
    Fd = factor(D)
    stress = stress_summary(element_stress(*stress_moments_drive(pr, Fd)), pr.truth) if pr.has_stress else None
    H = pr.frf(np.arange(pr.n_phys))
    Gu = (np.abs(H @ Fd) ** 2).sum(2).T                                     # (physical outputs, lines)
    nc, nh = pr.i_c.size, pr.i_h.size
    return stress, Gu[:nc], Gu[nc:nc + nh], Gu[nc + nh:]


def score_played(pr, psd, moments):
    """Stress from the modal monitors' band moments, gauges from the played output autospectra."""
    stress = None
    if pr.has_stress:
        assert moments is not None and pr.mon_scale is not None, 'this route needs the modal monitors\' band moments'
        stress = stress_summary(element_stress(*stress_moments_modal(pr, moments)), pr.truth)
    return stress, psd[:, pr.i_c].T, psd[:, pr.i_h].T, psd[:, pr.i_t].T


def ers_of(pr, G_h, G_t):
    if pr.GB_h is None:
        return None
    out = {}
    for q in (10, 50):
        K = sdof_kernel(pr.f, pr.df, q)
        out[f'q{q}_tip'] = stats(db10(G_t @ K.T, pr.GB_t @ K.T))
        out[f'q{q}_held'] = stats(db10(G_h @ K.T, pr.GB_h @ K.T))
    return out


def score(problem_folder, run_folder, target=None):
    """The scorecard of one run result on one problem, as a dict."""
    pr = problem_folder if isinstance(problem_folder, Problem) else Problem(problem_folder)
    man, D, psd, mom = read_run(run_folder, pr)
    oc = outcome_of(man)
    sid = pr.meta['structure']['id']
    out = dict(schema=SCORECARD_SCHEMA,
               scorer=dict(file='scorer.py', version=SCORER_VERSION, sha256=sha256(os.path.abspath(__file__))),
               set=pr.meta['set'], evidence_level=pr.meta['evidence_level'],
               problem=dict(id=f'{sid}/{target}' if target else sid, structure=sid, target=target, seed=pr.meta['structure']['seed'],
                            structure_sha256=pr.meta['structure']['sha256'], limits=pr.meta['limits']['id'],
                            stage=pr.stage, effects=pr.effects, format=pr.meta['schema'].rsplit('/', 1)[1]),
               run=dict(case_id=man.get('case_id'), law=man.get('law', {}).get('id'), law_parameters=man.get('law', {}).get('params_given'),
                        model=man.get('frf_mode'), noise_seed=man.get('sim_seed'), software_commit=man.get('code_commit'),
                        frames_per_loop=(man.get('estimation') or {}).get('frames_per_loop'), full_level_loops_asked=man.get('loops_at_full_asked')),
               outcome=oc, scored=oc['scored'], route=None, report_card=None, stress=None, ers=None, card=None,
               scored_on='gauges and stress' if pr.has_stress else 'gauges (the problem has no stress truth)')
    if not oc['scored'] or D is None:
        out['scored'] = False
        return out
    if pr.route == 'drive':
        stress, G_c, G_h, G_t = score_drive(pr, D)
    else:
        stress, G_c, G_h, G_t = score_played(pr, psd, mom)
    card, extra = card_of(pr, D, G_c, G_h)
    out.update(route=pr.route, stress=stress, ers=ers_of(pr, G_h, G_t), card=card, report_card=report_card(pr, card, extra),
               drive=dict(vrms=extra['drive_vrms'], rms_n=card['drive_rms'], line_to_band_db=card['drive_line_to_band_db']))
    if pr.route != 'drive':     # the size of the drive route's error on a structure that changed, and the structure's state as played
        s2, c2, h2, _ = score_drive(pr, D)
        out['by_drive_route'] = dict(stress=s2, card=card_of(pr, D, c2, h2)[0],
                                     what='the same figures with the played drive taken through the small-signal model; not the score')
        out['structure_state'] = structure_state(pr, D, psd)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Score one run result on one staged Frames problem (draft).')
    ap.add_argument('cmd', choices=('score',))
    ap.add_argument('problem')
    ap.add_argument('run')
    ap.add_argument('--target', choices=('banded', 'line'), default=None, help='which of the problem folder\'s targets the law was given (a label)')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    txt = json.dumps(score(a.problem, a.run, a.target), indent=1)
    if a.out:
        with open(a.out, 'w') as fh:
            fh.write(txt)
    else:
        print(txt)
    sys.exit(0)
