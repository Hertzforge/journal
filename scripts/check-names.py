"""The journal's gate, run before every push.

No employer, client, laboratory or partner is named as an affiliation in any tracked file. The
list of names is the software repository's own (tools/check_tree.py there, held as hashes so the
list that keeps the names out does not publish them), read from a checkout of it.

Articles, their published versions and their reviews may cite and credit published prior work
and its institutions by name. Those folders are read the way the software's acknowledgments file
is: a credited name is allowed on a line that makes no hardware claim.

    python3 scripts/check-names.py          # exit 0 clean, 1 with findings

HERTZFORGE_SRC names the software checkout (default ~/dev/sds). Needs Python 3.10 or later.
"""

from __future__ import annotations

import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOFTWARE = pathlib.Path(os.environ.get('HERTZFORGE_SRC', pathlib.Path.home() / 'dev' / 'sds'))
CREDIT_FOLDERS = ('articles/', 'published/', 'reviews/')


def main() -> int:
    sys.path.insert(0, str(SOFTWARE / 'tools'))
    try:
        import check_tree
    except ImportError:
        print(f'check-names: no software checkout at {SOFTWARE} (set HERTZFORGE_SRC)')
        return 1
    files = check_tree.tracked_files(ROOT)
    credit = frozenset(
        rel for rel in (path.relative_to(ROOT).as_posix() for path in files) if rel.startswith(CREDIT_FOLDERS)
    )
    found = check_tree.check_names(files, ROOT, credit_files=credit)
    for line in found:
        print(line)
    print(f'check-names: {len(found)} findings')
    return 1 if found else 0


if __name__ == '__main__':
    sys.exit(main())
