#!/bin/bash
# Installs what the build needs, without sudo:
#
#   Quarto, at the version pinned in pipeline/tools.json, from its release tarball, checked
#   against the recorded checksum, into $HERTZFORGE_TOOLS (default ~/dev/tools);
#   a Python environment in .venv, from requirements.lock.
#
# Also needed, and not installed here: a Chrome or Chromium browser (it renders each figure's
# static picture and runs the browser checks) and Python 3.10 or later.
set -euo pipefail
cd "$(dirname "$0")/.."
TOOLS="${HERTZFORGE_TOOLS:-$HOME/dev/tools}"
PY="${PYTHON:-$(command -v python3.14 || command -v python3.13 || command -v python3.12 || command -v python3)}"

VERSION=$("$PY" -c "import json; print(json.load(open('pipeline/tools.json'))['quarto']['version'])")
case "$(uname -s)-$(uname -m)" in
  Darwin-*) FILE="quarto-$VERSION-macos.tar.gz" ;;
  Linux-x86_64) FILE="quarto-$VERSION-linux-amd64.tar.gz" ;;
  Linux-aarch64 | Linux-arm64) FILE="quarto-$VERSION-linux-arm64.tar.gz" ;;
  *) echo "setup: no Quarto tarball is recorded for $(uname -s) $(uname -m)"; exit 1 ;;
esac
DEST="$TOOLS/quarto-$VERSION"

if [ -x "$DEST/bin/quarto" ] && [ "$("$DEST/bin/quarto" --version)" = "$VERSION" ]; then
  echo "setup: Quarto $VERSION is already in $DEST"
else
  WANT=$("$PY" -c "import json; print(json.load(open('pipeline/tools.json'))['quarto']['sha256']['$FILE'])")
  BASE=$("$PY" -c "import json; print(json.load(open('pipeline/tools.json'))['quarto']['source'])")
  mkdir -p "$TOOLS/_download"
  echo "setup: downloading $FILE"
  curl -fsSL -o "$TOOLS/_download/$FILE" "$BASE$FILE"
  GOT=$(shasum -a 256 "$TOOLS/_download/$FILE" | cut -d' ' -f1)
  if [ "$GOT" != "$WANT" ]; then
    echo "setup: $FILE does not match its recorded checksum; it was not installed"
    exit 1
  fi
  rm -rf "$DEST" && mkdir -p "$DEST"
  tar -xzf "$TOOLS/_download/$FILE" -C "$DEST"
  # Some of the tarballs hold one folder; lift its contents up.
  if [ ! -x "$DEST/bin/quarto" ]; then
    INNER=$(find "$DEST" -mindepth 1 -maxdepth 1 -type d | head -1)
    if [ -x "$INNER/bin/quarto" ]; then mv "$INNER"/* "$DEST"/ && rmdir "$INNER"; fi
  fi
  rm -f "$TOOLS/_download/$FILE"
  echo "setup: Quarto $("$DEST/bin/quarto" --version) installed in $DEST"
fi

if command -v uv >/dev/null 2>&1; then
  [ -d .venv ] || uv venv --quiet --python "$PY" .venv
  uv pip install --quiet --python .venv/bin/python -r requirements.lock
else
  [ -d .venv ] || "$PY" -m venv .venv
  .venv/bin/pip install --quiet --upgrade pip
  .venv/bin/pip install --quiet -r requirements.lock
fi
echo "setup: Python environment ready in .venv ($(.venv/bin/python --version))"
