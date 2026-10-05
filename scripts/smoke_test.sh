#!/usr/bin/env bash
# Local smoke test — generates a short 720p clip
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
pytest -q
prompt2cinema "neon cyberpunk street in the rain, cinematic" \
  --preset 720p --duration 3 --style cinematic --out outputs/smoke
echo "OK → outputs/smoke/"
ls -lh outputs/smoke/
