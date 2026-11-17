"""Reference model for a Frames problem of the Hertzforge Open Benchmark Set (format 0.2-draft, set version 0.2).

Needs numpy and the Python standard library, nothing else. A copy of this file sits in every problem
folder as reference_model.py. It reads structure files of version 0.2-draft and 0.1-draft.

    import reference_model as rm
    st = rm.load_structure('frame-12x6_s00')              # the problem folder, or the path of structure.json
    f = rm.grid_lines(rm.load_json('frame-12x6_s00/problem.json')['grid'])
    H = rm.frf(st, f)                                     # (lines, outputs, drives), output unit per volt
    y = rm.simulate(st, drive, fs=8192.0)                 # (samples, outputs), linear structure only
    run = rm.simulate_level(st, drive, fs=8192.0)         # any structure, by the simulator's own step

The structure is a set of modes. Mode m has a natural frequency f_m (Hz), a damping ratio zeta_m, a
drive shape (one entry per drive, per volt) and an output shape (one entry per output). With
w = 2 pi f and w_m = 2 pi f_m, the modal displacement per unit modal force is

    h_m(f) = 1 / (w_m^2 - w^2 + 2j zeta_m w_m w)

and every output is an acceleration, so the frequency response function from drive j to output i is

    H_ij(f) = sum over m of  output_shape_m[i] * drive_shape_m[j] * (-w^2) * h_m(f)

The same sum with a row of the modal stress matrix in place of the output shape, and without the
factor -w^2, is the stress at one fibre point per volt (stress_frf).

Spectral matrices are one-sided, per Hz, G_ij = E[X_i conj(X_j)]. A drive matrix D (lines, drives,
drives) in V^2/Hz gives the response matrix H D H^H.

A structure that changes with level (kind "jointed") has a rule per mode (the mode's `level` object, or the
structure-wide `level_law` for a mode without one). With r_m the mode's displacement envelope over its
reference_amplitude:

    f_m    = f0_m ( 1 - drop_m min(1, r_m)^drop_exponent_m + rise_m min(rise_cap_m, r_m)^rise_exponent_m )
    zeta_m = min(MAX_DAMPING, zeta0_m (1 + damping_gain_m min(damping_cap_m, r_m)^damping_exponent_m))

A drop is softening (a joint), a rise is hardening (a stiffness that grows with displacement). frf() is the
small-signal response, level_state() is the rule, and simulate_level() steps the structure in time the way the
software's simulator does (the envelope, the exact step per sample, the delays).
"""
import json
import os
import numpy as np

SCHEMA_STRUCTURE = 'hertzforge-benchmark-structure/0.2-draft'
SCHEMA_PROBLEM = 'hertzforge-benchmark-problem/0.2-draft'
SCHEMA_STRUCTURE_01 = 'hertzforge-benchmark-structure/0.1-draft'
SCHEMA_PROBLEM_01 = 'hertzforge-benchmark-problem/0.1-draft'
STRUCTURE_SCHEMAS = (SCHEMA_STRUCTURE, SCHEMA_STRUCTURE_01)
MODEL_VERSION = '0.2-draft'
TWO_PI = 2.0 * np.pi
MAX_DAMPING = 0.9             # the simulator's ceiling on a mode's damping ratio (hertzforge-hal-sim, jointed.rs)
LEVEL_FIELDS = ('drop', 'drop_exponent', 'rise', 'rise_exponent', 'rise_cap', 'damping_gain', 'damping_exponent', 'damping_cap')
# damping_cap (spec change 2026-11-14): the amplitude ratio above which the damping stops growing. A level object written
# before it existed has none and keeps its old meaning (no cap): it is read as infinite here, and to_runner_structure leaves
# it out as the file does (the runner, which requires it since 2026-11-14, then refuses the case; give such a file a cap,
# or NO_CAP, the largest finite double, which the simulator applies as no cap).
NO_CAP = float(np.finfo(float).max)


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def read_array(folder, entry):
    """An array named by a file table entry: {"file", "dtype", "shape"}. Raw little-endian, C order."""
    return np.fromfile(os.path.join(folder, entry['file']), entry['dtype']).reshape(entry['shape'])


def check_level(lv, where='a mode'):
    """Refuse a `level` object outside the spec's ranges; the message says which field."""
    missing = [k for k in LEVEL_FIELDS[:7] if k not in lv]
    if missing:
        raise ValueError(f'{where}: the level object lacks {", ".join(missing)}')
    v = {k: float(lv[k]) for k in LEVEL_FIELDS[:7]}
    if 'damping_cap' in lv:
        v['damping_cap'] = float(lv['damping_cap'])
        if not (np.isfinite(v['damping_cap']) and v['damping_cap'] > 0.0):
            raise ValueError(f'{where}: damping_cap {v["damping_cap"]} is not positive and finite')
    else:
        v['damping_cap'] = np.inf                       # a level object from before the cap: no cap, as it meant then
    bad = [k for k, x in v.items() if k != 'damping_cap' and not np.isfinite(x)]
    if bad:
        raise ValueError(f'{where}: {", ".join(bad)} is not finite')
    if not 0.0 <= v['drop'] < 1.0:
        raise ValueError(f'{where}: drop {v["drop"]} is not in [0, 1)')
    if v['rise'] < 0.0:
        raise ValueError(f'{where}: rise {v["rise"]} is negative')
    if v['rise_cap'] <= 0.0:
        raise ValueError(f'{where}: rise_cap {v["rise_cap"]} is not above 0')
    if v['damping_gain'] < 0.0:
        raise ValueError(f'{where}: damping_gain {v["damping_gain"]} is negative')
    for k in ('drop_exponent', 'rise_exponent', 'damping_exponent'):
        if v[k] <= 0.0:
            raise ValueError(f'{where}: {k} {v[k]} is not positive')
    return v


def law_as_level(law):
    """The structure-wide rule of version 0.1 (delta, freq_exponent, damping_gain, damping_exponent) as a level
    object: no rise, and a cap of 1 (unused when the rise is zero)."""
    return dict(drop=float(law['delta']), drop_exponent=float(law['freq_exponent']), rise=0.0, rise_exponent=2.0, rise_cap=1.0,
                damping_gain=float(law['damping_gain']), damping_exponent=float(law['damping_exponent']))


class Structure:
    """The modal data of structure.json as arrays. Shapes: f_hz, zeta (modes); drive_shape (modes, drives);
    output_shape (modes, outputs). `raw` is the file as read.

    rules: None for a linear structure, else a dict of arrays (one value per mode) named as LEVEL_FIELDS, the rule
    each mode follows: its own `level` object, or the structure-wide `level_law` where it has none.
    """

    def __init__(self, raw):
        assert raw['schema'] in STRUCTURE_SCHEMAS, raw['schema']
        self.raw = raw
        self.version = raw['schema'].rsplit('/', 1)[1]
        self.kind = raw['kind']
        self.f_hz = np.array([m['f_hz'] for m in raw['modes']], float)
        self.zeta = np.array([m['zeta'] for m in raw['modes']], float)
        self.drive_shape = np.array([m['drive_shape'] for m in raw['modes']], float)
        self.output_shape = np.array([m['output_shape'] for m in raw['modes']], float)
        self.outputs = raw['outputs']
        self.drives = raw['drives']
        self.level_law = raw.get('level_law')
        self.n_modes, self.n_drives = self.drive_shape.shape
        self.n_outputs = self.output_shape.shape[1]
        assert self.n_outputs == len(self.outputs) == raw['n_outputs'] and self.n_drives == raw['n_drives']
        self.rules = self._rules()
        self.reference_amplitude = (np.array([m['reference_amplitude'] for m in raw['modes']], float)
                                    if self.rules is not None else None)

    def _rules(self):
        own = [m.get('level') for m in self.raw['modes']]
        if self.version == '0.1-draft':
            assert not any(own), 'a 0.1-draft structure has no per-mode level objects'
        if not self.level_law and not any(own):
            return None
        law = self.level_law or {}
        fallback = law_as_level(law) if 'delta' in law else None
        rows = []
        for k, lv in enumerate(own):
            if lv is None:
                if fallback is None:
                    raise ValueError(f'mode {k} has no level object and the structure has no structure-wide rule')
                rows.append(fallback)
            else:
                rows.append(check_level(lv, f'mode {k}'))
        return {f: np.array([r.get(f, np.inf) if f == 'damping_cap' else r[f] for r in rows], float) for f in LEVEL_FIELDS}

    @property
    def decay_cycles(self):
        return float((self.level_law or {}).get('decay_cycles', 3.0))

    def rows(self, role=None, group=None):
        """Indices of the outputs with a role (control, held_out, monitor) and, if given, a group."""
        return np.array([i for i, o in enumerate(self.outputs)
                         if (role is None or o['role'] == role) and (group is None or o.get('group') == group)], int)


def load_structure(path):
    if os.path.isdir(path):
        path = os.path.join(path, 'structure.json')
    return Structure(load_json(path))


def grid_lines(grid):
    """The band line frequencies of a problem's grid: (lo_line + i) * fs_hz / nfft."""
    df = grid['fs_hz'] / grid['nfft']
    return (grid['lo_line'] + np.arange(grid['n_lines'])) * df


def receptance(st, f_hz, fn=None, zeta=None):
    """Modal displacement per unit modal force, (modes, lines). fn, zeta: the modes' state (default small signal)."""
    fn = st.f_hz if fn is None else np.asarray(fn, float)
    zeta = st.zeta if zeta is None else np.asarray(zeta, float)
    w = TWO_PI * np.asarray(f_hz, float)[None, :]
    wn = TWO_PI * fn[:, None]
    return 1.0 / (wn ** 2 - w ** 2 + 2j * zeta[:, None] * wn * w)


def frf(st, f_hz, rows=None, fn=None, zeta=None):
    """Acceleration frequency response per volt, (lines, outputs, drives). Small signal unless fn and zeta are given
    (for instance from level_state)."""
    f_hz = np.asarray(f_hz, float)
    osh = st.output_shape if rows is None else st.output_shape[:, rows]
    return np.einsum('mo,mf,md->fod', osh, receptance(st, f_hz, fn, zeta) * -(TWO_PI * f_hz) ** 2, st.drive_shape, optimize=True)


def stress_frf(st, stress_modal, f_hz):
    """Fibre stress per volt, (lines, stress rows, drives). stress_modal is (stress rows, modes), stress per unit modal displacement."""
    return np.einsum('rm,mf,md->frd', stress_modal, receptance(st, f_hz), st.drive_shape, optimize=True)


def response_sdm(H, D):
    """H D H^H for every line: the response spectral matrix under a drive spectral matrix."""
    return H @ D @ np.conj(H).transpose(0, 2, 1)


def frequency_factor(st, r):
    """Each mode's frequency over its small-signal value at amplitude ratio r (one value per mode, or one for all)."""
    if st.rules is None:
        return np.ones_like(st.f_hz)
    R = st.rules
    r = np.broadcast_to(np.asarray(r, float), st.f_hz.shape)
    return 1.0 - R['drop'] * np.minimum(1.0, r) ** R['drop_exponent'] + R['rise'] * np.minimum(R['rise_cap'], r) ** R['rise_exponent']


def level_state(st, r):
    """Frequency and damping of every mode at amplitude ratio r (one value per mode, or one for all).

    r_m is the mode's displacement envelope over its reference_amplitude. The rule (FORMAT.md, 0.2-draft):
        f    = f0 (1 - drop min(1, r)^drop_exponent + rise min(rise_cap, r)^rise_exponent)
        zeta = min(MAX_DAMPING, zeta0 (1 + damping_gain min(damping_cap, r)^damping_exponent))
    Returns (f_hz, zeta). A linear structure returns its own values.

    A version 0.1 structure gives what the 0.1 draft gave, to the last bit: one rule, no rise, and no damping
    ceiling (the 0.1 draft did not apply MAX_DAMPING, so above a damping ratio of 0.9 it differs from the
    simulator; simulate_level applies the ceiling for every version, as the simulator does).
    """
    if st.rules is None:
        return st.f_hz.copy(), st.zeta.copy()
    R = st.rules
    r = np.broadcast_to(np.asarray(r, float), st.f_hz.shape)
    f = st.f_hz * frequency_factor(st, r)
    z = st.zeta * (1.0 + R['damping_gain'] * np.minimum(R['damping_cap'], r) ** R['damping_exponent'])
    if st.version != '0.1-draft':
        z = np.minimum(MAX_DAMPING, z)
    return f, z


def frequency_change(st, r):
    """Each mode's signed fractional frequency change at amplitude ratio r: negative for a drop, positive for a rise."""
    return frequency_factor(st, r) - 1.0


def max_frequency(st):
    """The highest frequency each mode can reach, f0 (1 + rise rise_cap^rise_exponent), Hz. The simulator refuses a
    structure whose highest frequency is too high for its sample rate."""
    if st.rules is None:
        return st.f_hz.copy()
    R = st.rules
    return st.f_hz * (1.0 + R['rise'] * R['rise_cap'] ** R['rise_exponent'])


def simulate(st, drive, fs, rows=None, tail_s=None):
    """Time response of the linear structure to drive samples (samples, drives) in volts: (samples, outputs).

    The drive is padded with zeros so the response of the lightest-damped mode has died away before the record
    wraps, then every output is the inverse transform of H(f) times the transform of the drive. Exact for the
    continuous-time model inside the Nyquist band; the drive should hold no energy near fs / 2. Noise is not added.
    A structure that changes with level is stepped by simulate_level instead.
    """
    if st.rules is not None:
        raise NotImplementedError('the structure changes with level: use simulate_level')
    drive = np.atleast_2d(np.asarray(drive, float))
    n, nd = drive.shape
    assert nd == st.n_drives
    if tail_s is None:      # eight time constants of the slowest decay, at most 30 s (the suspension modes ring for longer than that)
        tail_s = min(30.0, 8.0 / float(np.min(st.zeta * TWO_PI * st.f_hz)))
    n_fft = int(2 ** np.ceil(np.log2(n + int(tail_s * fs))))
    f = np.fft.rfftfreq(n_fft, 1.0 / fs)
    X = np.fft.rfft(drive, n_fft, axis=0)                              # (bins, drives)
    osh = st.output_shape if rows is None else st.output_shape[:, rows]
    out = np.zeros((n, osh.shape[1]))
    step = 4096                                                         # frequency bins a block, to bound memory
    Y = np.zeros((f.size, osh.shape[1]), complex)
    for a in range(0, f.size, step):
        fa = f[a:a + step]
        q = (receptance(st, fa) * -(TWO_PI * fa) ** 2) * (st.drive_shape @ X[a:a + step].T)      # (modes, bins)
        Y[a:a + step] = (osh.T @ q).T
    out[:] = np.fft.irfft(Y, n_fft, axis=0)[:n]
    return out


# ---------------------------------------------------------------------------------------------- the time stepper
# The method of the software simulator's jointed structure (hertzforge-hal-sim, jointed.rs, MIT), restated in numpy.
# Per sample: the drive passes the common transport delay; every mode advances by the exact solution of its
# oscillator over one sample period with that sample's frequency and damping held and the modal force varying
# linearly from the previous sample to this one; the mode's amplitude sqrt(q^2 + (v / w)^2) feeds a peak follower
# that decays by exp(-1) in decay_cycles periods of the small-signal frequency; the next sample's frequency and
# damping come from that envelope through the rule. Each output is the modal accelerations through the output
# shapes, plus the residual and feedthrough, then its own delay (a four-tap Lagrange fraction).

# The equalized step (simulator option `step: {"kind": "equalized", "band_hz", "half_taps"}`, in a structure file under
# `simulator.step`): a symmetric FIR of 2 half_taps + 1 taps on each (transport-delayed) drive ahead of the modal force,
# fitted so its zero-phase response times sinc^2(w dt / 2) is one up to band_hz; the direct part of each mode's
# acceleration, the residual and the feedthrough take the drive delayed half_taps samples. Without a step, or with
# {"kind": "triangle_hold"}, the old step (the default) is used.

def step_of(st):
    """The structure's step: None for the triangle hold, else (band_hz, half_taps)."""
    s = (st.raw.get('simulator') or {}).get('step')
    if s is None or s.get('kind', 'triangle_hold') == 'triangle_hold':
        return None
    if s['kind'] != 'equalized':
        raise ValueError(f'step kind {s["kind"]!r} is not known (triangle_hold, equalized)')
    return float(s['band_hz']), int(s.get('half_taps', 2))


def equalizer_taps(band, d):
    """The symmetric FIR c[0..2d] (centred at d) of the equalized step, band in cycles per sample: the least-squares fit
    of h0 + 2 sum_k h_k cos(k w) times sinc^2(w / 2) to one, weighted by 1 / w^2 on 2000 points up to the band and by 0.01
    on 400 points above it to pi (relative error, so the cancellation of a mode's acceleration below its resonance holds).
    The simulator's equalizer_taps restated; solved by numpy's QR."""
    wb = TWO_PI * band
    w = np.concatenate([wb * np.arange(1, 2001) / 2000.0, wb + (np.pi - wb) * np.arange(1, 401) / 400.0])
    wt = np.concatenate([1.0 / w[:2000] ** 2, np.full(400, 0.01)])
    s = (np.sin(0.5 * w) / (0.5 * w)) ** 2
    A = np.column_stack([s * wt] + [2.0 * np.cos(j * w) * s * wt for j in range(1, d + 1)])
    Q, Rr = np.linalg.qr(A)
    h = np.linalg.solve(Rr, Q.T @ wt)
    return np.array([h[abs(k - d)] for k in range(2 * d + 1)])


def _mode_step(w, zeta, dt):
    """The state transition exp(A dt) of each mode, held parameters: (p0, p1, p2, p3), row-major."""
    sigma = zeta * w
    wd = w * np.sqrt(1.0 - zeta * zeta)
    e = np.exp(-sigma * dt)
    s, c = np.sin(wd * dt), np.cos(wd * dt)
    return e * (c + sigma / wd * s), e * s / wd, -e * w * w / wd * s, e * (c - sigma / wd * s)


def discrete_frf(st, f_hz, fs, rows=None, r=None):
    """The exact frequency response of the stepped structure with every mode frozen at amplitude ratio r (default
    0, the small signal): what simulate_level gives at a steady low level. (lines, outputs, drives), per volt.
    Includes the residual, the feedthrough and the delays of the simulator block. The simulator's
    frf_at_envelope of its jointed model, restated."""
    f_hz = np.asarray(f_hz, float)
    dt = 1.0 / fs
    fn, ze = level_state(st, 0.0 if r is None else r)
    ze = np.minimum(MAX_DAMPING, ze)                                     # the simulator's ceiling, whatever the file's version
    w = TWO_PI * fn
    p0, p1, p2, p3 = _mode_step(w, ze, dt)
    w2 = w * w
    c = 2.0 * ze / (w * dt)
    tw = 1.0 / (dt * w2)
    a0 = (c / w2, -tw); a1 = ((1.0 - c) / w2, tw); b0 = ((1.0 + c) / w2, -tw); b1 = (-c / w2, tw)
    mul = lambda b: (p0 * b[0] + p1 * b[1], p2 * b[0] + p3 * b[1])
    pb0, pb1 = mul(b0), mul(b1)
    g0 = (a0[0] - pb0[0], a0[1] - pb0[1]); g1 = (a1[0] - pb1[0], a1[1] - pb1[1])
    om = TWO_PI * f_hz / fs
    z = np.exp(1j * om)[:, None]                                         # (lines, 1)
    g = (z * g1[0] + g0[0], z * g1[1] + g0[1])
    m11, m22 = z - p0, z - p3
    det = m11 * m22 - p1 * p2
    xq = (m22 * g[0] + g[1] * p1) / det
    xv = (g[0] * p2 + m11 * g[1]) / det
    resp = 1.0 - xq * w2 - xv * (2.0 * ze * w)                         # (lines, modes): the mode's acceleration per unit force
    step = step_of(st)
    if step is not None:                                                 # the FIR on the restoring part, the delay on every path
        c = equalizer_taps(step[0] / fs, step[1])
        g0 = (np.exp(-1j * om[:, None] * np.arange(c.size)[None]) @ c) * np.exp(1j * om * step[1])
        resp = 1.0 - g0[:, None] * (1.0 - resp)
    osh = st.output_shape if rows is None else st.output_shape[:, rows]
    H = np.einsum('mo,fm,md->fod', osh, resp, st.drive_shape, optimize=True)
    sim = st.raw.get('simulator') or {}
    H = H + float(sim.get('feedthrough', 0.0))
    res = sim.get('residual') or []
    if len(res):
        R = np.asarray(res, float).reshape(st.n_outputs, st.n_drives)
        H = H + (R if rows is None else R[rows])[None]
    H = H * np.exp(-1j * om * (int(sim.get('transport_delay_samples', 0)) + (0 if step is None else step[1])))[:, None, None]
    od = sim.get('output_delays_s') or []
    if len(od):
        idx = np.arange(st.n_outputs) if rows is None else np.asarray(rows)
        for col, i in enumerate(idx):
            n0, h = _frac_delay(float(od[i]) * fs)
            H[:, col, :] *= sum(hk * np.exp(-1j * om * (n0 + k)) for k, hk in enumerate(h))[:, None]
    return H


def _frac_delay(samples):
    """(n0, four Lagrange taps) of a delay of `samples`: n0 whole samples then a fraction in [1, 2) (else the delay
    itself when under one sample), as the simulator builds it."""
    if samples < 1.0:
        n0, d = 0, samples
    else:
        n0 = int(np.floor(samples)) - 1
        d = samples - n0
    h = []
    for k in range(4):
        v = 1.0
        for m in range(4):
            if m != k:
                v *= (d - m) / (k - m)
        h.append(v)
    return n0, h


class LevelRun:
    """What simulate_level returns. outputs (samples, outputs); peak_envelope, envelope (modes): the largest and the
    final displacement envelope; q, v (modes): the final modal state. With keep_modes: modal (samples, modes) the
    modal displacement and env (samples, modes) the envelope after each sample."""

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def peak_ratio(self, st):
        return self.peak_envelope / st.reference_amplitude


def simulate_level(st, drive, fs, rows=None, keep_modes=False, block=8192, state=None):
    """Step the structure through drive samples (samples, drives), volts, from rest, by the simulator's method.

    Works for any structure: a linear one is stepped with its small-signal modes held. No noise is added. The
    outputs are every output of the structure (or `rows`), in the structure's units, delays included. The step is
    the structure's `simulator.step` (the triangle hold when absent; the equalized step adds half_taps samples of
    delay on every path).

    state: None to start from rest, or the `state` of the LevelRun of the previous call with the same structure, fs and
    rows, to continue where it stopped; a long record can then be played in pieces with no change in the samples (each
    piece's modal forces are formed by one matrix product, so the samples can differ from one call by rounding only).
    Returns a LevelRun. Speed: one Python step per sample over arrays of modes; see the study's notes for timings.
    """
    drive = np.atleast_2d(np.asarray(drive, float))
    n, nd = drive.shape
    assert nd == st.n_drives, f'{nd} drive columns for a structure with {st.n_drives} drives'
    if np.any(st.f_hz <= 0) or np.any(st.f_hz >= 0.5 * fs):
        raise ValueError('a mode is not between 0 and the Nyquist frequency')
    if np.any(max_frequency(st) >= 0.5 * fs):
        raise ValueError(f'a mode can rise to {max_frequency(st).max():.1f} Hz, at or above the Nyquist frequency {0.5 * fs} Hz')
    sim = st.raw.get('simulator') or {}
    dt = 1.0 / fs
    nm = st.n_modes
    w0 = TWO_PI * st.f_hz
    z0 = st.zeta.copy()
    rules = st.rules
    if rules is not None:
        a_ref = st.reference_amplitude
        R = rules
        decay = np.exp(-st.f_hz * dt / st.decay_cycles)
    osh = st.output_shape if rows is None else st.output_shape[:, rows]
    out_idx = np.arange(st.n_outputs) if rows is None else np.asarray(rows)
    od = sim.get('output_delays_s') or []
    delays = [_frac_delay(float(od[i]) * fs) for i in out_idx] if len(od) else []
    # the common transport delay (whole samples), and the drive and output history a continued call needs
    D = int(sim.get('transport_delay_samples', 0))
    step = step_of(st)
    hd = 0 if step is None else step[1]
    Hd = D + 2 * hd + 1
    Ho = 1 + max([n0 + 3 for n0, _ in delays], default=0)
    if state is None:
        hist_d = np.zeros((Hd, nd)); hist_c = np.zeros((Ho, out_idx.size))
        q = np.zeros(nm); v = np.zeros(nm); u_prev = np.zeros(nm); env = np.zeros(nm); peak = np.zeros(nm)
    else:
        hist_d, hist_c = state['hist_d'], state['hist_c']
        q, v, u_prev, env, peak = (state[k].copy() for k in ('q', 'v', 'u_prev', 'env', 'peak'))
    ext = np.vstack([hist_d, drive])                                       # (Hd + n, drives)
    ne = ext.shape[0]
    delayed = np.zeros_like(ext)
    delayed[D:] = ext[:ne - D] if D else ext
    if step is None:
        forced = direct = delayed
    else:                                       # the equalized step: the FIR'd drive forces the modes, the rest is delayed
        c = equalizer_taps(step[0] / fs, step[1])
        forced = np.zeros_like(delayed)
        for kk, ck in enumerate(c):
            forced[kk:] += ck * delayed[:ne - kk]
        direct = np.zeros_like(delayed)
        direct[hd:] = delayed[:ne - hd]
    forced, direct = forced[Hd:], direct[Hd:]                              # this call's samples
    clean = float(sim.get('feedthrough', 0.0)) * direct.sum(1)[:, None] * np.ones((1, out_idx.size))
    res = sim.get('residual') or []
    if len(res):
        clean = clean + direct @ np.asarray(res, float).reshape(st.n_outputs, st.n_drives)[out_idx].T
    w, ze = w0.copy(), z0.copy()                                           # with rules, recomputed from env before each step
    p0, p1, p2, p3 = _mode_step(w, ze, dt)
    acc = np.empty((min(block, n), nm))
    modal = np.empty((n, nm)) if keep_modes else None
    envs = np.empty((n, nm)) if keep_modes else None
    for a in range(0, n, block):
        b = min(n, a + block)
        U = forced[a:b] @ st.drive_shape.T                                # (samples, modes): the modal forces
        Ud = None if step is None else direct[a:b] @ st.drive_shape.T     # the direct part (equalized step)
        for t in range(b - a):
            if rules is not None:
                r = env / a_ref
                pos = r > 0.0
                ff = 1.0 - R['drop'] * np.minimum(1.0, r) ** R['drop_exponent'] + R['rise'] * np.minimum(R['rise_cap'], r) ** R['rise_exponent']
                dz = np.minimum(z0 * (1.0 + R['damping_gain'] * np.minimum(R['damping_cap'], r) ** R['damping_exponent']), MAX_DAMPING)
                w = np.where(pos, w0 * ff, w0)
                ze = np.where(pos, dz, z0)
                p0, p1, p2, p3 = _mode_step(w, ze, dt)
            u1 = U[t]
            w2 = w * w
            k = (u1 - u_prev) / dt
            pq = (u_prev - 2.0 * ze * k / w) / w2
            pv = k / w2
            dq, dv = q - pq, v - pv
            q = pq + k * dt / w2 + p0 * dq + p1 * dv
            v = pv + p2 * dq + p3 * dv
            acc[t] = u1 - 2.0 * ze * w * v - w2 * q
            if Ud is not None:
                acc[t] += Ud[t] - u1
            u_prev = u1
            if rules is not None:
                env = np.maximum(np.hypot(q, v / w), env * decay)
                peak = np.maximum(peak, env)
            if keep_modes:
                modal[a + t] = q
                envs[a + t] = env
        clean[a:b] += acc[:b - a] @ osh
    cext = np.vstack([hist_c, clean])
    out = clean
    if delays:
        y = np.zeros_like(cext)
        for col, (n0, h) in enumerate(delays):
            for kk, hk in enumerate(h):
                s = n0 + kk
                y[s:, col] += hk * cext[:cext.shape[0] - s, col]
        out = y[Ho:]
    new_state = dict(q=q, v=v, u_prev=u_prev, env=env, peak=peak, hist_d=ext[-Hd:].copy(), hist_c=cext[-Ho:].copy())
    return LevelRun(outputs=out, peak_envelope=peak, envelope=env, q=q, v=v, modal=modal, env=envs, state=new_state)


# ---------------------------------------------------------------------------------------------- bands and targets
def band_matrix(f_hz, per_octave=3, centre_hz=1000.0):
    """The band partition the set uses: line k belongs to band round(per_octave * log2(f_k / centre_hz)).

    Returns (B, band_of_line, index): B (bands, lines) averages the lines of each band (rows sum to one),
    band_of_line gives each line's band as a row of B, index is each band's integer (centre = centre_hz * 2^(index / per_octave)).
    """
    f_hz = np.asarray(f_hz, float)
    idx = np.round(per_octave * np.log2(f_hz / centre_hz)).astype(int)
    u = np.unique(idx)
    B = (idx[None, :] == u[:, None]).astype(float)
    return B / B.sum(1, keepdims=True), (B > 0).argmax(0), u


def expand_banded(values, band_of_line):
    """The banded target as the full matrix a controller takes: (lines, controls, controls), each control's band
    value held flat across its band, no cross terms. values is (controls, bands)."""
    values = np.asarray(values, float)
    nc = values.shape[0]
    G = np.zeros((len(band_of_line), nc, nc), complex)
    i = np.arange(nc)
    G[:, i, i] = values[:, band_of_line].T
    return G


# ---------------------------------------------------------------------------------------------- the runner's structure object
def to_runner_structure(st):
    """The "structure" object of the Hertzforge research runner's case file for this structure.

    A version 0.1 structure, or a 0.2 one with no per-mode level object, gives the mm-x4-case/1 structure exactly as
    the 0.1 draft did. A structure whose modes carry `level` objects gives the mm-x4-case/2 structure: every mode with
    its `level`, and `joint` holding what the structure-wide `level_law` holds (at least decay_cycles).
    The simulator block of structure.json holds what is the software's own business (how the continuous model is
    made discrete, which outputs carry measurement noise); the modes come from the structure itself.
    """
    raw, sim = st.raw, st.raw['simulator']
    base = dict(n_outputs=st.n_outputs, n_drives=st.n_drives, feedthrough=sim['feedthrough'], residual=sim['residual'],
                transport_delay_samples=sim['transport_delay_samples'])
    if st.kind == 'modal':
        modes = [dict(f_hz=m['f_hz'], q=float(1 / (2 * m['zeta'])), drive_shape=m['drive_shape'], output_shape=m['output_shape'],
                      response='acceleration') for m in raw['modes']]
        return dict(kind='modal', **base, modes=modes, softening=sim['softening'], noisy_outputs=sim['noisy_outputs'],
                    discretization=sim['discretization'])
    law = st.level_law or {}
    per_mode = any('level' in m for m in raw['modes'])
    modes = []
    for m in raw['modes']:
        mode = dict(f_hz=m['f_hz'], zeta=m['zeta'], drive_shape=m['drive_shape'], output_shape=m['output_shape'],
                    reference_amplitude=m['reference_amplitude'])
        if 'level' in m:
            mode['level'] = {k: m['level'][k] for k in LEVEL_FIELDS if k in m['level']}   # damping_cap carried when the file has it
        modes.append(mode)
    if not per_mode:
        joint = dict(delta=law['delta'], damping_gain=law['damping_gain'], freq_exponent=law['freq_exponent'],
                     damping_exponent=law['damping_exponent'], decay_cycles=law['decay_cycles'])
    else:
        joint = {k: law[k] for k in ('delta', 'damping_gain', 'freq_exponent', 'damping_exponent', 'decay_cycles') if k in law}
    return dict(kind='jointed', **base, modes=modes, joint=joint, output_delays_s=sim['output_delays_s'])


def from_runner_structure(case_structure, outputs=None):
    """A Structure from a runner case file's jointed structure object (mm-x4-case/1 or /2): for stepping a case the
    simulator ran (the stepper parity check). outputs: the case file's outputs list (names, roles), optional."""
    assert case_structure['kind'] == 'jointed', 'only the jointed structure is stepped here'
    joint = case_structure.get('joint')
    modes = []
    for m in case_structure['modes']:
        mode = dict(f_hz=m['f_hz'], zeta=m['zeta'], drive_shape=m.get('drive_shape', m.get('input_shape')),
                    output_shape=m['output_shape'], reference_amplitude=m.get('reference_amplitude', 1.0))
        if m.get('level') is not None:
            mode['level'] = m['level']
        modes.append(mode)
    law = None
    if joint:
        # the runner's defaults for a joint that leaves them out (JointLaw::new: both exponents 0.5, three cycles)
        law = dict(kind='jointed', **{'freq_exponent': 0.5, 'damping_exponent': 0.5, 'decay_cycles': 3.0, **joint})
    outs = outputs or [dict(name=f'o{i}', role='control') for i in range(case_structure['n_outputs'])]
    raw = dict(schema=SCHEMA_STRUCTURE, kind='jointed', n_outputs=case_structure['n_outputs'], n_drives=case_structure['n_drives'], outputs=outs,
               drives=[dict(name=f'd{j + 1:02d}') for j in range(case_structure['n_drives'])], level_law=law, modes=modes,
               simulator=dict(feedthrough=case_structure.get('feedthrough', 0.0), residual=case_structure.get('residual', []),
                              transport_delay_samples=case_structure.get('transport_delay_samples', 0),
                              output_delays_s=case_structure.get('output_delays_s', [])))
    if case_structure.get('step') is not None:
        raw['simulator']['step'] = case_structure['step']
    return Structure(raw)


if __name__ == '__main__':
    import sys
    st = load_structure(sys.argv[1])
    roles = {}
    for o in st.outputs:
        key = o['role'] + ('/' + o['group'] if o.get('group') else '')
        roles[key] = roles.get(key, 0) + 1
    print(f"{st.raw['structure_id']} seed {st.raw['seed']}: kind {st.kind}, {st.n_modes} modes "
          f"({st.f_hz[6]:.1f} to {st.f_hz[-1]:.1f} Hz elastic), {st.n_drives} drives, {st.n_outputs} outputs {roles}")
    if st.rules is not None:
        ch = frequency_change(st, 1.0)
        print(f'  at the reference amplitude: frequency change {100 * ch.min():+.2f} to {100 * ch.max():+.2f} percent; '
              f'highest reachable frequency {max_frequency(st).max():.1f} Hz')
