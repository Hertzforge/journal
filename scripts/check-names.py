"""The journal's gate, run before every push.

1. Unaffiliated. No employer, client, laboratory or partner is named as an affiliation in any
   tracked file. The list of names is the software repository's own (tools/check_tree.py there,
   held as hashes so the list that keeps the names out does not publish them), read from a
   checkout of it. Articles, their published versions and their reviews may cite and credit
   published prior work and its institutions by name: those folders are read the way the
   software's acknowledgments file is, where a credited name is allowed on a line that makes no
   hardware claim.
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


def main() -> int:
    sys.path.insert(0, str(SOFTWARE / 'tools'))
    try:
        import check_licenses
        import check_tree
    except ImportError:
        print(f'check-names: no software checkout at {SOFTWARE} (set HERTZFORGE_SRC)')
        return 1
    files = check_tree.tracked_files(ROOT)
    credit = frozenset(
        rel for rel in (path.relative_to(ROOT).as_posix() for path in files) if rel.startswith(CREDIT_FOLDERS)
    )
    found = check_tree.check_names(files, ROOT, credit_files=credit)
    found += licenses(check_licenses)
    found += frozen()
    for line in found:
        print(line)
    print(f'check-names: {len(found)} findings')
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main())
