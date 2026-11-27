"""Check that every number in the article's text is a number that suite_results.py wrote. Copyright
2026 Kevin Cross. MIT license.

    python3 check_numbers.py [ARTICLE] [--data DIR]

Reads the article, data/numbers.csv and, once the audit has been filled, data/audit_numbers.csv
(written by audit_fill.py). Every numeric token of the article's prose (front matter,
captions and body; not the figures' alt text, not code spans, not links) must appear as a token of
some text in those files, unless it is one of the kinds listed in ALLOWED: claim identifiers,
section and figure numbers, standard identifiers and clause numbers, years, DOIs, hashes, journal
article numbers, system and problem names, and the constants that the format document defines and
the text states as definitions (listed in DEFINED, each with where it is defined). Prints every
token that fails, with its line, and exits 1 if any does.
"""
import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NUM = re.compile(r'(?<![\w.])[-+]?\d+(?:,\d{3})*(?:\.\d+)?(?:e[-+]?\d+)?(?![\w])')

# Tokens that are names, not measurements.
ALLOWED = [
    r'R\d{4}',                                  # claim identifiers
    r'\d{4}-\d{3}',                             # journal article numbers
    r'\d{4}-\d{2}-\d{2}',                       # dates
    r'pull request \d+',                         # Hertzforge pull request numbers
    r'sample of 205 jobs',                       # the release's identity sample of the published code
    r'10\.5281/zenodo\.\d+',                    # DOIs
    r'[0-9a-f]{40}', r'[0-9a-f]{64}',           # commits and hashes
    r'\d+ x \d+',                               # systems, shakers x control gauges
    r'frame-\d+x\d+',                           # problem names
    r'60068-2-6(?::2007)?', r'MIL-STD-810H', r'5\d\d\.\d',  # standards and methods
    r'4\.\d(?:\.\d)*(?:\.\d)?',                 # IEC clause numbers
    r'Table 514\.8-III', r'Annex E',
    r'(?:Section|Sections) \d(?:\.\d)?(?: (?:to|and) \d(?:\.\d)?)?',
    r'Figure \d', r'fig\d_\w+',
    r'T[1-5]', r'L1',                           # test names
    r'^#+ \d(?:\.\d)?',                         # headings
    r'structures? \d+(?:(?:,| to|,? and) \d+)*',  # structure numbers
    r'from 100 up',
    r'0009-0002-6608-9426',                     # ORCID
    r'CC BY 4\.0', r'SHA-256',
]
# Constants of the suite that the text states as definitions, with where the format defines them.
DEFINED = {
    '0.1': 'draft 0.1 of the suite',
    '0.2': 'version 0.2 of the Random suite',
    '1': 'version 1, and "1 octave a minute", "1 V", "1 Hz", "1 for a completed run": FORMAT_SINE.md',
    '2': 'amendment 2, "2 percent", "2 s": FORMAT_SINE.md',
    '3': 'amendment 3, "3 dB over its flanks", 3 updates, 3 repeats: FORMAT_SINE.md',
    '4': '"4 octaves a minute": FORMAT_SINE.md',
    '0': '"0 dB or less", "an IEC share of 0": H_Claims_Rule.md',
    '-12': 'the ladder: FORMAT_SINE.md', '-9': 'the ladder', '-6': 'the ladder', '-3': 'the ladder',
    '-20': 'the identification level: FORMAT_SINE.md',
    '1e-3': 'Tikhonov and noise: FORMAT_SINE.md', '1e-5': 'the fixed-point table', '1e3': 'the table',
    '1/384': 'reference grid', '1/48': 'the scorer bin: scorer.py', '1/': 'the time constant',
    '5': 'the frequency tolerance band 5 to 50 Hz; 5 percent duration; 5 points',
    '50': 'IEC frequency and band edges', '500': 'IEC band edge', '25': 'IEC check point',
    '15': 'IEC reference point', '10': 'Method 514.8 tolerances; 10 V; 10 time constants; 10 s',
    '0.1': 'Method 514.8 frequency', '6': '6 dB, 6 time constants', '12': '12 steps, 12 of 20',
    '20': 'band edge, 20 time constants, 20 cycles, 20 dB, 20 structures', '2000': 'band edge',
    '30': 'dwell time constants', '100': 'abort updates; structures from 100 up',
    '8192': 'sample rate', '264': 'pipeline', '256': 'simulator block', '8': 'frames ahead',
    '9': 'default ceiling 9 V', '60': '60 s divergence', '16': 'controls when made',
    '24': 'controls now', '0.2': 'over-test threshold, mean-error tolerance',
}


def tokens(path):
    for no, line in enumerate(open(path), 1):
        line = re.sub(r'fig-alt="[^"]*"', '', line)
        line = re.sub(r'`[^`]*`', '', line)
        line = re.sub(r'data="[^"]*"', '', line)
        line = re.sub(r'\]\([^)]*\)', ']', line)
        line = re.sub(r'https?://\S+', '', line)
        for pat in ALLOWED:
            line = re.sub(pat, ' ', line)
        for m in NUM.finditer(line):
            yield no, m.group(0).lstrip('+')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('article', nargs='?', default=os.path.join(HERE, '..', 'article.md'))
    ap.add_argument('--data', default=os.path.join(HERE, '..', 'data'))
    a = ap.parse_args()
    known = set()
    files = ['numbers.csv'] + (['audit_numbers.csv']
                               if os.path.exists(os.path.join(a.data, 'audit_numbers.csv')) else [])
    for name in files:
        for r in csv.DictReader(open(os.path.join(a.data, name))):
            for m in NUM.finditer(r['text']):
                known.add(m.group(0).lstrip('+'))
    bad = [(no, t) for no, t in tokens(a.article) if t not in known and t not in DEFINED]
    for no, t in bad:
        print(f'line {no}: {t}')
    print(f'{len(bad)} numbers not found in', ' or '.join(files))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
