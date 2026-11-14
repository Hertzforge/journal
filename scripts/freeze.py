"""The freeze rule, in code: a published version is written once and never changes.

Every version folder carries MANIFEST.sha256, the hash of each of its files, written when the
version was built. `verify_version` says what differs from it. Standard library only, so the
gate can run it anywhere.
"""

from __future__ import annotations

import hashlib
import pathlib
import re

MANIFEST = 'MANIFEST.sha256'


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as file:
        for block in iter(lambda: file.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def tree(folder: pathlib.Path) -> dict[str, str]:
    """{path inside the folder: hash} of every file in it but the manifest."""
    return {
        path.relative_to(folder).as_posix(): sha256(path)
        for path in sorted(folder.rglob('*')) if path.is_file() and path.name != MANIFEST
    }


def write_manifest(folder: pathlib.Path) -> None:
    lines = [f'{digest}  {name}\n' for name, digest in tree(folder).items()]
    (folder / MANIFEST).write_text(''.join(lines), encoding='utf-8')


def verify_version(folder: pathlib.Path) -> list[str]:
    """What differs between a frozen version and its manifest. Empty when it is as it was built."""
    manifest = folder / MANIFEST
    if not manifest.is_file():
        return [f'{folder}: has no {MANIFEST}']
    recorded = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        digest, _, name = line.partition('  ')
        recorded[name] = digest
    now = tree(folder)
    found = [f'{folder / name}: changed since it was frozen' for name in recorded if name in now and now[name] != recorded[name]]
    found += [f'{folder / name}: missing' for name in recorded if name not in now]
    found += [f'{folder / name}: added after the version was frozen' for name in now if name not in recorded]
    return found


def version_folders(published: pathlib.Path) -> list[pathlib.Path]:
    """Every published/<id>/v<n>/ folder, in order."""
    return sorted(
        (path for path in published.glob('*/v*') if path.is_dir() and re.fullmatch(r'v\d+', path.name)),
        key=lambda path: (path.parent.name, int(path.name[1:])),
    )
