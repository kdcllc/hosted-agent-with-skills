#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Install from https://docs.astral.sh/uv/getting-started/installation/"
  exit 1
fi

uv sync --prerelease allow

echo "Environment is ready. Start local server with: uv run python main.py"
