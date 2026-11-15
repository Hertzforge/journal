"""Write every data file behind the figures and every number the article quotes.

The survey's own numbers are arithmetic on one mode (Section 5 and Section 8 of the article),
so this script computes them from their formulas; nothing is read from a run. Numbers quoted
from a source are listed in numbers.csv with the source and clause, and are not recomputed.

    python extract_data.py            # writes ../data/*.csv
"""
import csv
import math
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
LN2 = math.log(2.0)


def t_band(q, s):
    """Seconds a log sweep at s octaves a minute spends inside a half-power bandwidth f/Q."""
    return 60.0 / (q * s * LN2)


def tau_mode(q, f):
    """Amplitude time constant of a mode, Q / (pi f), seconds."""
    return q / (math.pi * f)


def n_const(q, s, f):
    """Number of the mode's time constants spent inside its bandwidth: 60 pi f / (Q^2 s ln 2)."""
    return t_band(q, s) / tau_mode(q, f)


def f_n_below_2(q, s):
    """Frequency below which N is under 2."""
    return 2.0 * q * q * s * LN2 / (60.0 * math.pi)


def write(name, header, rows):
    with open(DATA / name, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def main():
    DATA.mkdir(exist_ok=True)

    # Figure 1: schematic layout, positions in drawing units (not to scale).
    write("fig1_layout.csv", ["part", "label", "x", "y"], [
        ["beam", "test article (flexible)", 0.5, 2.2],
        ["beam", "", 7.5, 2.2],
        ["shaker", "shaker 1", 1.2, 0.0],
        ["shaker", "shaker 2", 4.0, 0.0],
        ["shaker", "shaker 3", 6.8, 0.0],
        ["control", "control 1", 1.2, 2.45],
        ["control", "control 2", 4.0, 2.45],
        ["control", "control 3", 6.8, 2.45],
        ["limit", "limit", 2.6, 2.45],
        ["controller", "controller", 9.0, 0.3],
    ])

    # Figure 2: N against frequency for four rates at Q = 50.
    q = 50.0
    rates = [0.5, 1.0, 2.0, 4.0]
    freqs = [5 * 10 ** (i / 40.0) for i in range(0, 81)]  # 5 to 500 Hz
    rows = []
    for f in freqs:
        rows.append([round(f, 4)] + [round(n_const(q, s, f), 5) for s in rates])
    write("fig2_sweep_n.csv", ["frequency_hz"] + [f"N_{s:g}_oct_per_min" for s in rates], rows)

    # Table 4 of the article.
    trows = []
    for s in rates:
        trows.append([s, round(t_band(q, s), 3), round(n_const(q, s, 10), 3), round(n_const(q, s, 40), 3),
                      round(n_const(q, s, 100), 3), round(f_n_below_2(q, s), 2)])
    write("table4_sweep.csv", ["oct_per_min", "seconds_in_bandwidth", "N_10Hz", "N_40Hz", "N_100Hz",
                               "N_under_2_below_hz"], trows)

    # Figure 3: largest phase difference 2 atan(delta), delta in half-power bandwidths.
    deltas = [i / 100.0 for i in range(0, 501)]
    write("fig3_phase_vs_shift.csv", ["shift_bandwidths", "max_phase_difference_deg"],
          [[d, round(math.degrees(2 * math.atan(d)), 4)] for d in deltas])
    marks = []
    for qq in (25.0, 50.0, 100.0):
        d = 0.01 * qq  # a 1 percent shift is 0.01 f, the bandwidth is f / Q
        marks.append([qq, d, round(math.degrees(2 * math.atan(d)), 2)])
    write("fig3_one_percent_marks.csv", ["Q", "shift_bandwidths", "max_phase_difference_deg"], marks)

    # Every number the text quotes.
    num = []

    def ours(where, what, value, formula):
        num.append([where, what, value, "ours: " + formula])

    def cited(where, what, value, source):
        num.append([where, what, value, source])

    ours("5", "seconds inside bandwidth, Q 50, 1 oct/min", round(t_band(50, 1), 3), "60/(Q s ln2)")
    ours("5", "constant 60/ln2", round(60 / LN2, 2), "60/ln2")
    ours("5", "cycles inside bandwidth at 10 Hz, Q 50, 1 oct/min", round(10 * t_band(50, 1), 1), "f T_b")
    ours("5", "cycles inside bandwidth at 100 Hz, Q 50, 1 oct/min", round(100 * t_band(50, 1), 1), "f T_b")
    cited("5", "cycles per 0.1 Hz at 1 oct/min", 8.66, "ECSS-E-HB-10-03A A.7.3.3; check 6/ln2 = %.3f" % (6 / LN2))
    ours("5", "tau_m at 10 Hz, Q 50 (s)", round(tau_mode(50, 10), 3), "Q/(pi f)")
    ours("5", "tau_m at 40 Hz, Q 50 (s)", round(tau_mode(50, 40), 3), "Q/(pi f)")
    ours("5", "constant 60 pi / ln2", round(60 * math.pi / LN2, 1), "N = 272 f/(Q^2 s)")
    ours("5", "constant 60 pi /(2 ln2) for N<2 frequency", round(60 * math.pi / (2 * LN2), 1), "Q^2 s / 136")
    for r in trows:
        ours("5, Table 4", f"row {r[0]} oct/min", ";".join(str(x) for x in r[1:]), "t_band, N, f(N=2)")
    ours("5", "N at 10 Hz, Q 50, 1 oct/min (ECSS case)", round(n_const(50, 1, 10), 3), "272 f/(Q^2 s)")
    cited("5", "ECSS case: identified frequency and damping errors", "2 % ; over 70 %", "ECSS-E-HB-32-26A 5.2.3.3")
    cited("5", "ISO limits", "54 f^2/Q^2 Hz/min ; 77.6 f/Q^2 oct/min", "ISO 7626-2:1990 9.2.3 via IS 14736-2")
    ours("5", "ISO eta limit", 54 / 60, "54/60")
    ours("5", "ISO N limit", round(math.pi / 0.9, 2), "pi/0.9")
    ours("5", "ISO log limit, 40 Hz, Q 50 (oct/min)", round(77.6 * 40 / 2500, 3), "77.6 f/Q^2")
    ours("5", "ECSS parameter over Davis parameter", 4, "eta_E = fdot/(f^2 zeta^2), eta_D = fdot/(4 f^2 zeta^2)")
    ours("5", "4/N at 40 Hz, Q 50, 1 oct/min", round(4 / n_const(50, 1, 40), 3), "4/N")
    ours("5", "frequency where 4/N = 0.1, Q 50, 1 oct/min (Hz)", round(40 / n_const(50, 1, 1), 1), "N = 40")
    ours("5", "2/N at 40 Hz, Q 50, 1 oct/min", round(2 / n_const(50, 1, 40), 3), "2/N")
    ours("5", "frequency where 2/N = 0.1, Q 50, 1 oct/min (Hz)", round(20 / n_const(50, 1, 1), 1), "N = 20")
    cited("5", "rates in use", "1 ; 2 and 4 ; up to 4 ; 0.5", "IEC 60068-2-6 4.1.6; ECSS-E-ST-10-03C Rev.1 tables; ECSS-E-HB-10-03A A.7.3.3")
    for d in (0.5, 1.0, 2.0):
        ours("8", f"2 atan({d}) degrees", round(math.degrees(2 * math.atan(d)), 2), "2 atan(delta)")
    ours("8", "one bandwidth as a frequency shift, Q 50 and Q 100 (percent)", "2 ; 1", "100/Q")
    ours("8", "ECSS 5 percent shift at Q 50 in bandwidths", 0.05 * 50, "0.05 Q")
    for m in marks:
        ours("8, Figure 3", f"1 percent shift at Q {m[0]:g}", f"{m[1]} bandwidths; {m[2]} deg", "0.01 Q; 2 atan")
    cited("3.1", "Qiu 2019 test", "60 kN; 5 to 200 Hz; 2 oct/min; 10 %; 10 deg; 80 Hz", "Qiu and others 2019 Section 3.3")
    cited("3.1", "compression factor advised", "0.4 to 0.6", "Zhang, Wang, Zeng 2017 p. 1091")
    cited("3.2", "c_n start and end", "0.1 ; 1.0", "US 5,299,459 col. 8")
    cited("3.3", "Musella 2019 simulation", "10 to 2500 Hz; 2 Hz/s; 1 percent; 0.5 to 1 s", "Musella and others 2019 Section 5, Table 1")
    cited("3.4", "Zhang 2015 test", "K 0.5,1,2,6; 1115x50x14 mm; 143, 376 mm; 3 dB; 6 dB", "Zhang, Chen, He 2015 pp. 200-201")
    cited("3.5", "Zheng 2020 result", "-6 dB; 4 loops", "Zheng, Chen, Luo 2020 4.2")
    cited("4", "MVF channels", "8 drives; 12 controls; 32 limit; 32 monitor; 20 actuators", "Staab and others")
    cited("4", "phase control accuracies", "4 ; 10 ; 5 deg; 200 kN; 1400 kN", "Qiu and others 2022")
    cited("4", "HYDRA accuracy", "2.5 %", "Brinkman and Kretz")
    cited("4", "plate account", "four shakers; 2 ft; 5 to 80 Hz", "Underwood and Keller 2001")
    cited("4", "eight-actuator example", "eight actuators", "Underwood, Keller, Ayres 2017")
    cited("7", "Knospe 1994", "2700, 4200 rpm; 30 s; 1500 to 5000 rpm; 2200; 2500 rpm", "Knospe and others 1994 p. 122")
    cited("7", "Knospe and Tamer 1996", "1.17 to 1.51; 20 to 45 percent", "Table 1")
    cited("7", "Johnson 1982", "50%", "p. 32")
    cited("8", "Hippold 2024 periods", "about 100", "abstract")
    write("numbers.csv", ["section", "what", "value", "source"], num)


if __name__ == "__main__":
    main()
