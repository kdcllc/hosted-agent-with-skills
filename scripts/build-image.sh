#!/usr/bin/env bash
set -euo pipefail

: "${AZURE_CONTAINER_REGISTRY_NAME:?Set AZURE_CONTAINER_REGISTRY_NAME}"
IMAGE_REPOSITORY="${IMAGE_REPOSITORY:-blog-writer-agent}"
IMAGE_TAG="${IMAGE_TAG:-$(date +%Y%m%d%H%M%S)}"
DOCKERFILE_PATH="${DOCKERFILE_PATH:-Dockerfile}"
SOURCE_ACR_AUTH_ID="${SOURCE_ACR_AUTH_ID:-}"

REMOTE_IMAGE="${AZURE_CONTAINER_REGISTRY_NAME}.azurecr.io/${IMAGE_REPOSITORY}:${IMAGE_TAG}"

echo "Submitting cloud build to Azure Container Registry"
echo "Registry: ${AZURE_CONTAINER_REGISTRY_NAME}"
echo "Image: ${REMOTE_IMAGE}"
echo "Dockerfile: ${DOCKERFILE_PATH}"

build_command=(
	az acr build
	--registry "${AZURE_CONTAINER_REGISTRY_NAME}"
	--image "${IMAGE_REPOSITORY}:${IMAGE_TAG}"
	--platform linux/amd64
	--file "${DOCKERFILE_PATH}"
)

if [[ -n "${SOURCE_ACR_AUTH_ID}" ]]; then
	echo "Source registry auth identity: ${SOURCE_ACR_AUTH_ID}"
	build_command+=(--source-acr-auth-id "${SOURCE_ACR_AUTH_ID}")
fi

build_command+=(.)

"${build_command[@]}"

echo "Cloud build complete: ${REMOTE_IMAGE}"
echo "Export IMAGE_TAG=${IMAGE_TAG} and IMAGE_URI=${REMOTE_IMAGE} before deploy."
