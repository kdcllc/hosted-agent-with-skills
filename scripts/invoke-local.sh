#!/usr/bin/env bash
set -euo pipefail

MESSAGE="${1:-Write a blog post about deploying Microsoft Agent Framework hosted agents to Microsoft AI Foundry}"

curl -sS -H "Content-Type: application/json" -X POST http://localhost:8088/responses \
  -d "{\"input\":\"${MESSAGE}\",\"stream\":false}" | cat

echo
