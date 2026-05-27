#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install -r requirements.txt
fi

if [ ! -f .env ]; then
  echo "Missing .env — copy .env.example to .env and set ANTHROPIC_API_KEY." >&2
  exit 1
fi

exec .venv/bin/python -m agent.main "$@"
