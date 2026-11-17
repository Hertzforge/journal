//! Runs Hertzforge's shipped MIMO Random laws, unchanged, on the made-up structures of
//! `data/toy_structures.csv`, and writes what Figures 3 and 7 are drawn from, and the outputs
//! `check_against_shipped.py` compares with the article's own equations.
//!
//! ```text
//! cargo run --release -- <the article's data folder>
//! ```
//!
//! Every law is called as the controller calls it: built from its declared defaults (or the named
//! parameters), seeded with the measured frequency response, then iterated with the measured response at full
//! level. The measurement here is exact: the response is `H G H^H` of the true structure, with no
//! noise and no averaging. No core protection is applied; the laws' own per-loop limits are.
//! Copyright 2026 Kevin Cross. MIT license.
use hertzforge_mimo_laws::{
    buzz_reference, BandAverageLaw, BuiltinMimoLaw, MinimumDriveLaw, OpenLoopLaw, ParamVal,
    PseudoInverseLaw, ShapeConstrainedLaw,
};
use hertzforge_sdm::law::{
    DiagnosticData, MimoControlLaw, MimoLoopInputs, MimoLoopOutputs, MimoSetup, Tolerances,
};
use hertzforge_sdm::{linalg, HermitianStack, MatrixStack, C64};
use std::collections::BTreeMap;
use std::fs::File;
use std::io::{BufWriter, Write};

const DF: f64 = 0.5;
const LINES: usize = 1201; // 0 to 600 Hz

struct Modes {
    f_hz: Vec<f64>,
    zeta: f64,
    gauge: Vec<Vec<f64>>,
    shaker: Vec<Vec<f64>>,
}

fn read_structures(dir: &str) -> BTreeMap<String, Modes> {
    let text = std::fs::read_to_string(format!("{dir}/toy_structures.csv")).expect("toy_structures.csv");
    let mut out: BTreeMap<String, Modes> = BTreeMap::new();
    for row in text.lines().skip(1) {
        let c: Vec<&str> = row.split(',').collect();
        let (name, mode, f_hz, zeta, side, index, value) = (
            c[0].to_string(),
            c[1].parse::<usize>().unwrap(),
            c[2].parse::<f64>().unwrap(),
            c[3].parse::<f64>().unwrap(),
            c[4],
            c[5].parse::<usize>().unwrap(),
            c[6].parse::<f64>().unwrap(),
        );
        let m = out.entry(name).or_insert(Modes { f_hz: vec![], zeta, gauge: vec![], shaker: vec![] });
        if m.f_hz.len() <= mode {
            m.f_hz.push(f_hz);
            m.gauge.push(vec![]);
            m.shaker.push(vec![]);
        }
        let table = if side == "gauge" { &mut m.gauge[mode] } else { &mut m.shaker[mode] };
        assert_eq!(table.len(), index);
        table.push(value);
    }
    out
}

/// Gauges by shakers on every line: the sum over modes of `(f/fr)^2 / (1 - (f/fr)^2 + 2 i zeta f/fr)`
/// times the outer product of the mode's shapes.
fn frf(m: &Modes, lines: usize, df: f64) -> MatrixStack {
    let (nc, nd) = (m.gauge[0].len(), m.shaker[0].len());
    let mut data = vec![C64::new(0.0, 0.0); lines * nc * nd];
    for k in 0..lines {
        let f = df * k as f64;
        for (r, fr) in m.f_hz.iter().enumerate() {
            let x = f / fr;
            let term = C64::new(x * x, 0.0) / C64::new(1.0 - x * x, 2.0 * m.zeta * x);
            for i in 0..nc {
                for j in 0..nd {
                    data[(k * nc + i) * nd + j] += term * (m.gauge[r][i] * m.shaker[r][j]);
                }
            }
        }
    }
    MatrixStack::from_vec(lines, nc, nd, data).unwrap()
}

fn diagonal_reference(lines: usize, band: (usize, usize), d: &[f64]) -> HermitianStack {
    let mut g = HermitianStack::zeros(lines, d.len());
    for l in band.0..band.1 {
        for (i, v) in d.iter().enumerate() {
            g.set(l, i, i, C64::new(*v, 0.0));
        }
    }
    g
}

fn setup(nc: usize, nd: usize, lines: usize, df: f64, band: (usize, usize), r: HermitianStack) -> MimoSetup {
    MimoSetup { controls: nc, drives: nd, lines, df_hz: df, band, reference: r, tolerances: Tolerances::none(lines, nc) }
}

fn call(
    law: &mut dyn MimoControlLaw,
    s: &MimoSetup,
    frf: &MatrixStack,
    response: &HermitianStack,
    loop_index: u64,
    sysid: Option<&HermitianStack>,
) -> MimoLoopOutputs {
    let coherence = vec![1.0; s.lines * s.controls];
    let inputs = MimoLoopInputs {
        reference: &s.reference,
        tolerances: &s.tolerances,
        response,
        response_dof: 100.0,
        frf,
        multiple_coherence: &coherence,
        df_hz: s.df_hz,
        band: s.band,
        loop_index,
        last_drive: None,
        response_drive_csd: None,
        sysid_response: sysid,
        sysid_drive: None,
        sysid_noise: None,
    };
    if loop_index == 0 { law.seed(&inputs).unwrap() } else { law.iterate(&inputs).unwrap() }
}

fn diagnostic(o: &MimoLoopOutputs, key: &str) -> Vec<f64> {
    match &o.diagnostics.iter().find(|d| d.key == key).expect("declared").data {
        DiagnosticData::PerLine(v) | DiagnosticData::PerControlLine(v) => v.clone(),
        DiagnosticData::Scalar(x) => vec![*x],
        _ => panic!("unexpected layout"),
    }
}

fn create(dir: &str, name: &str) -> BufWriter<File> {
    println!("wrote {name}");
    BufWriter::new(File::create(format!("{dir}/{name}")).unwrap())
}

/// Each gauge's error against its target on every in-band line, dB.
fn errors(true_frf: &MatrixStack, drive: &HermitianStack, band: (usize, usize), target: &[f64]) -> Vec<Vec<f64>> {
    let y = linalg::response_from_drive(true_frf, drive).unwrap();
    (band.0..band.1)
        .map(|l| y.diagonal(l).iter().zip(target).map(|(m, t)| 10.0 * (m / t).log10()).collect())
        .collect()
}

fn rms(e: &[Vec<f64>], c: usize) -> f64 {
    (e.iter().map(|v| v[c] * v[c]).sum::<f64>() / e.len() as f64).sqrt()
}

fn main() {
    let dir = std::env::args().nth(1).expect("usage: shipped-laws <data folder>");
    let toys = read_structures(&dir);

    // Figure 3: pinv_closed and pinv_open at their defaults on a wrong estimate.
    let band = (40, LINES); // 20 Hz to 600 Hz
    let (truth, estimate) = (frf(&toys["loop_true"], LINES, DF), frf(&toys["loop_estimate"], LINES, DF));
    let s = setup(2, 2, LINES, DF, band, diagonal_reference(LINES, band, &[1.0, 1.0]));
    let mut closed = PseudoInverseLaw::with_params(&s, &[]).unwrap();
    let mut open = OpenLoopLaw::with_params(&s, &[]).unwrap();
    let (mut oc, mut oo) = (call(&mut closed, &s, &estimate, &s.reference, 0, None),
                            call(&mut open, &s, &estimate, &s.reference, 0, None));
    let (mut kept, mut rows) = (BTreeMap::new(), vec![]);
    for k in 0..=30u64 {
        let (ec, eo) = (errors(&truth, &oc.drive, band, &[1.0, 1.0]), errors(&truth, &oo.drive, band, &[1.0, 1.0]));
        rows.push((k, rms(&ec, 0), rms(&ec, 1), rms(&eo, 0), rms(&eo, 1)));
        if [0, 5, 30].contains(&k) {
            kept.insert(k, ec);
        }
        if k < 30 {
            let yc = linalg::response_from_drive(&truth, &oc.drive).unwrap();
            let yo = linalg::response_from_drive(&truth, &oo.drive).unwrap();
            oc = call(&mut closed, &s, &estimate, &yc, k + 1, None);
            oo = call(&mut open, &s, &estimate, &yo, k + 1, None);
        }
    }
    let mut f = create(&dir, "fig3_closed_loop_lines.csv");
    writeln!(f, "frequency_hz,control1_after_0_loops_db,control1_after_5_loops_db,control1_after_30_loops_db,control2_after_0_loops_db,control2_after_5_loops_db,control2_after_30_loops_db").unwrap();
    for (i, l) in (band.0..band.1).enumerate() {
        let v = |k: u64, c: usize| kept[&k][i][c];
        writeln!(f, "{},{:.9e},{:.9e},{:.9e},{:.9e},{:.9e},{:.9e}", DF * l as f64, v(0, 0), v(5, 0), v(30, 0), v(0, 1), v(5, 1), v(30, 1)).unwrap();
    }
    let mut f = create(&dir, "fig3_closed_loop_rms.csv");
    writeln!(f, "loop,control1_rms_db,control2_rms_db,open_loop_control1_rms_db,open_loop_control2_rms_db").unwrap();
    for (k, a, b, c, d) in rows {
        writeln!(f, "{k},{a:.9e},{b:.9e},{c:.9e},{d:.9e}").unwrap();
    }

    // Figure 7: band_average's first solve at its defaults, one gauge, one shaker, 40 to 500 Hz.
    let bband = (80, 1001);
    let h = frf(&toys["band"], LINES, DF);
    let s = setup(1, 1, LINES, DF, bband, diagonal_reference(LINES, bband, &[1.0]));
    let mut law = BandAverageLaw::with_params(&s, &[]).unwrap();
    let o = call(&mut law, &s, &h, &s.reference, 0, None);
    let threshold = diagnostic(&o, "threshold");
    let mut f = create(&dir, "fig7_band_average_drive.csv");
    writeln!(f, "frequency_hz,drive,band_threshold").unwrap();
    for l in bband.0..bband.1 {
        writeln!(f, "{},{:.9e},{:.9e}", DF * l as f64, o.drive.get(l, 0, 0).re, threshold[l]).unwrap();
    }

    // Checks of the other figures. shape_svd: the directions kept on each line, at the defaults.
    let h = frf(&toys["shape"], LINES, DF);
    let s = setup(6, 4, LINES, DF, band, diagonal_reference(LINES, band, &[1.0; 6]));
    let mut law = ShapeConstrainedLaw::with_params(&s, &[]).unwrap();
    let o = call(&mut law, &s, &h, &s.reference, 0, None);
    let mut f = create(&dir, "shipped_check_shape.csv");
    writeln!(f, "frequency_hz,directions_kept").unwrap();
    for (l, k) in diagnostic(&o, "kept").iter().enumerate().skip(band.0) {
        writeln!(f, "{},{k}", DF * l as f64).unwrap();
    }
    // buzz_match: the modified reference, from the response to uncorrelated unit drives.
    let h = frf(&toys["buzz"], LINES, DF);
    let ident = linalg::response_from_drive(&h, &diagonal_reference(LINES, (0, LINES), &[1.0; 3])).unwrap();
    let g = buzz_reference(&diagonal_reference(LINES, band, &[1.0, 1.0]), &ident, band, 0.1).unwrap();
    let mut f = create(&dir, "shipped_check_buzz.csv");
    writeln!(f, "frequency_hz,reference_coherence,reference_phase_deg").unwrap();
    for l in band.0..band.1 {
        let x = g.get(l, 0, 1);
        let coherence = x.norm_sqr() / (g.get(l, 0, 0).re * g.get(l, 1, 1).re);
        writeln!(f, "{},{coherence:.9e},{:.9e}", DF * l as f64, x.arg().to_degrees()).unwrap();
    }
    // min_drive: one line at 200 Hz, every fixed trade-off of the grid, then the automatic one.
    let m = &toys["min_drive"];
    let one = frf(m, 2, 200.0); // lines 0 and 200 Hz; line 1 is the one in band
    let s = setup(2, 2, 2, 200.0, (1, 2), {
        let mut r = diagonal_reference(2, (1, 2), &[1.0, 0.5]);
        r.set(0, 0, 0, C64::new(0.0, 0.0));
        r
    });
    let mut f = create(&dir, "shipped_check_min_drive.csv");
    writeln!(f, "tradeoff_relative,drive_power,target1_over_spec,target2_over_spec").unwrap();
    for v in [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6] {
        let given = [("tradeoff", ParamVal::Choice("fixed".into())), ("tradeoff_value", ParamVal::Number(v))];
        let mut law = MinimumDriveLaw::with_params(&s, &given).unwrap();
        let o = call(&mut law, &s, &one, &s.reference, 0, None);
        let r = diagnostic(&o, "target_ratio");
        writeln!(f, "{v:e},{:.9e},{:.9e},{:.9e}", diagnostic(&o, "drive_power")[1], r[2], r[3]).unwrap();
    }
    let mut law = MinimumDriveLaw::with_params(&s, &[]).unwrap();
    let o = call(&mut law, &s, &one, &s.reference, 0, None);
    let r = diagnostic(&o, "target_ratio");
    writeln!(f, "auto {:e},{:.9e},{:.9e},{:.9e}", diagnostic(&o, "tradeoff")[0], diagnostic(&o, "drive_power")[1], r[2], r[3]).unwrap();
}
