#!/usr/bin/env bash
# Vercel build: use a project venv (PEP 668 blocks system pip on Vercel's uv-managed Python).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m venv .venv --clear
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/validate.py
.venv/bin/python scripts/validate_entities.py
.venv/bin/python scripts/build_links_index.py
.venv/bin/python scripts/build_db.py

cd site
npm install
npm run build
