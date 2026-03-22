#!/usr/bin/env bash
set -euo pipefail

echo "push-image.sh is only needed for a legacy local Docker build workflow."
echo "If you use scripts/build-image.sh, Azure Container Registry already builds and pushes the image for you."
