#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required to build the specification. Install it from https://docs.astral.sh/uv/." >&2
  exit 1
fi

exec uv run \
  --with-requirements "$SCRIPT_DIR/requirements-spec.txt" \
  python "$SCRIPT_DIR/tools/build_spec.py" "$@"