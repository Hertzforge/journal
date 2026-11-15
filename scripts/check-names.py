"""The journal's gate, run before every push.

1. Unaffiliated. No employer, client, laboratory or partner is named as an affiliation in any
   tracked file. The list of names is the software repository's own (tools/check_tree.py there,
   held as hashes so the list that keeps the names out does not publish them), read from a
   checkout of it. Articles, their published versions and their reviews may cite and credit
   published prior work and its institutions by name. In those folders a credited laboratory
   (CREDITED_HERE) may be named on any line, a line about a hardware test included, because
   articles cite hardware tests; every other listed name is refused there as anywhere. Whether
   an article claims that Hertzforge supports hardware it does not is the editors' check
   (policies/EDITORS.md), not this one.
2. No strong copyleft. Every Python package the build installs (requirements.lock) is read from
   the build environment's own metadata by the software repository's license checker; GPL, AGPL
   and SSPL are refused, and so is a package whose license cannot be read. The tools that are
   not Python packages are pinned, with their licenses, in pipeline/tools.json.
3. Frozen. Every published version still matches the manifest written when it was built, and
   nothing about to be pushed changes or removes a file of a version the remote already has.

    python3 scripts/check-names.py          # exit 0 clean, 1 with findings

HERTZFORGE_SRC names the software checkout (default ~/dev/sds). Needs Python 3.10 or later.
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys
from importlib import metadata

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOFTWARE = pathlib.Path(os.environ.get('HERTZFORGE_SRC', pathlib.Path.home() / 'dev' / 'sds'))
CREDIT_FOLDERS = ('articles/', 'published/', 'reviews/', 'tests/articles/', 'tests/revision/')

#: Listed names that an article, a published version or a review may hold, as the source of
#: published work it cites or credits: the laboratory the software's own acknowledgments credit
#: (read from the software's list), a second laboratory, in both the forms it is listed under,
#: allowed by the editors on 2026-11-14 for the citation of its published work, and a third,
#: allowed on 2026-11-15 for the same reason (the 1977 report cited by article 2026-002), and the
#: web address under which the first laboratory publishes a cited user's manual, allowed on
#: 2026-11-15 so the citation can give that manual's own address. Held as hashes, as the list
#: itself is. Add one with the software's `tools/check_tree.py --hash`.
CREDITED_HERE = frozenset({'e2a3af9c1d2aa535', 'e07681543d5c76d6', 'bef51514796755a0',
                           'd6c6d1247e12746b'})

#: Packages whose metadata names their license in words the checker cannot read as an
#: identifier, each with what was read by hand: {normalized name: what its own license file says}.
REVIEWED = {
    'kaleido': 'MIT: its metadata says "The MIT License (MIT)" and its LICENSE.md is the MIT text',
    'logistro': 'MIT: its metadata says "MIT License" and its LICENSE file is the MIT text',
}

sys.path.insert(0, str(ROOT / 'scripts'))
import freeze  # noqa: E402


def licenses(check_licenses) -> list[str]:
    """Every locked package, as installed in .venv, under a license the project allows."""
    lock = ROOT / 'requirements.lock'
    locked = dict(re.findall(r'^([A-Za-z0-9][A-Za-z0-9._-]*)==(\S+)', lock.read_text(encoding='utf-8'), re.M))
    site = sorted((ROOT / '.venv').glob('lib/python*/site-packages'))
    if not site:
        return ['requirements.lock: no build environment (.venv) to read licenses from; run scripts/setup.sh']
    installed = {check_licenses.normalized(d.metadata['Name']): d for d in metadata.distributions(path=[str(site[0])])}
    found = []
    for name, version in locked.items():
        dist = installed.get(check_licenses.normalized(name))
        if dist is None:
            found.append(f'requirements.lock: {name} is not installed in .venv; run scripts/setup.sh')
        elif dist.version != version:
            found.append(f'requirements.lock: {name} is {dist.version} in .venv, {version} in the lock; run scripts/setup.sh')
    wanted = {check_licenses.normalized(name) for name in locked}
    found += [f'requirements.lock: {line}' for line in
              check_licenses.check_installed([d for key, d in installed.items() if key in wanted], reviewed=REVIEWED)]
    return found


def frozen() -> list[str]:
    """Published versions as they were built, here and against what the remote already has."""
    found = [line for folder in freeze.version_folders(ROOT / 'published') for line in freeze.verify_version(folder)]
    found = [line.replace(str(ROOT) + '/', '') for line in found]
    has_remote = subprocess.run(['git', 'rev-parse', '-q', '--verify', 'origin/main'], cwd=ROOT, capture_output=True).returncode == 0
    if has_remote:
        changed = subprocess.run(['git', 'diff', '--name-status', '--no-renames', 'origin/main', 'HEAD', '--', 'published'],
                                 cwd=ROOT, capture_output=True, text=True, check=True).stdout
        for line in changed.splitlines():
            status, _, path = line.partition('\t')
            if status in ('M', 'D') and re.match(r'published/[^/]+/v\d+/', path):
                found.append(f'{path}: a published version is never changed; this commit {"removes" if status == "D" else "changes"} it')
    return found


def _binary(line: str) -> bool:
    """A line of a PDF that is compressed stream data rather than text. A built PDF keeps its words
    in compressed streams, so a byte scan of it reads only its metadata and noise; four bytes of
    noise once spelled a listed name (2026-002, 2026-11-15). The article's source, from which the
    PDF is built, is checked as text in full, and a PDF's readable metadata is still checked."""
    if not line:
        return False
    printable = sum(1 for ch in line if ch.isprintable() and ch != '�')
    return printable / len(line) < 0.9


def credit_names(files, check_tree) -> list[str]:
    """Listed names in the credit folders. A credited laboratory may be named on any line there;
    every other listed name is a finding, as it is anywhere. The finding gives the place, never
    the word."""
    allowed = check_tree.CREDITED | CREDITED_HERE
    found = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if path.name in check_tree.SKIPPED or rel in check_tree.NOTICES:
            continue
        text = check_tree._text(path)
        if text is None:
            continue
        for number, line in enumerate([rel, *text.splitlines()]):
            if path.suffix == '.pdf' and number > 0 and _binary(line):
                continue
            words = check_tree._WORD.findall(check_tree.without_references(line, check_tree.REFERENCES).lower())
            runs = (' '.join(words[i:i + size]) for size in (1, 2, 3) for i in range(len(words) - size + 1))
            hits = {check_tree.phrase_hash(run) for run in runs} & check_tree.NAMES
            if number > 0:
                hits -= allowed
            if hits:
                found.append(f'{rel}: {"its path" if number == 0 else f"line {number}"} names a listed organization')
    return found


def main() -> int:
    sys.path.insert(0, str(SOFTWARE / 'tools'))
    try:
        import check_licenses
        import check_tree
    except ImportError:
        print(f'check-names: no software checkout at {SOFTWARE} (set HERTZFORGE_SRC)')
        return 1
    files = check_tree.tracked_files(ROOT)
    in_credit = [path for path in files if path.relative_to(ROOT).as_posix().startswith(CREDIT_FOLDERS)]
    elsewhere = [path for path in files if path not in set(in_credit)]
    found = check_tree.check_names(elsewhere, ROOT, credit_files=frozenset())
    found += credit_names(in_credit, check_tree)
    found += licenses(check_licenses)
    found += frozen()
    for line in found:
        print(line)
    print(f'check-names: {len(found)} findings')
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main())
