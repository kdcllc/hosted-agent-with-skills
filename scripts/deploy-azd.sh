#!/usr/bin/env bash
set -euo pipefail

if ! command -v azd >/dev/null 2>&1; then
  echo "azd is required. Install Azure Developer CLI first."
  exit 1
fi

if [[ ! -f agent.yaml ]]; then
  echo "agent.yaml was not found in current directory"
  exit 1
fi

azd ai agent init -m agent.yaml
azd up

echo "Deployment completed through azd."
