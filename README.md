# Hosted Agent With Skills (Python + uv)

This project scaffolds a **Microsoft Agent Framework** hosted agent for **Microsoft AI Foundry** with:

- one built-in Python skill (`BlogWriterSkill`)
- `uv` dependency management
- Docker containerization
- CLI-first deployment scripts

## Project Layout

- `main.py`: Hosted agent runtime entrypoint (`/responses` protocol via hosting adapter)
- `skills/blog_writer_skill.py`: built-in blog writer skill implementation
- `skills/SKILL.md`: blog-writing skill instructions consumed by the agent
- `agent.yaml`: hosted agent manifest
- `Dockerfile`: linux/amd64-compatible container image build
- `scripts/`: bootstrap/build/push/deploy/invoke helpers
- `.foundry/agent-metadata.yaml`: environment metadata for repeatable ops

The skill assets now live together under `skills/`.

## Prerequisites

1. Python 3.10+
2. `uv`
3. Azure CLI (`az`) and authenticated session (`az login`)
4. Docker
5. Optional: Azure Developer CLI (`azd`) for one-command deployment flow

## 1) Local Development (uv)

1. Copy environment template:

```bash
cp .env.example .env
```

1. Install dependencies:

```bash
./scripts/bootstrap.sh
```

1. Run the hosted agent locally:

```bash
uv run python main.py
```

1. Test locally in another terminal:

```bash
./scripts/invoke-local.sh "Write a blog post about deploying hosted agents to Microsoft AI Foundry"
```

## 2) Build and Push Docker Image

1. Load this project's environment values:

```bash
set -a 
source .env
set +a
```

1. Set a unique image tag for this build:

```bash
export IMAGE_TAG=$(date +%Y%m%d%H%M%S)
```

Do not use `latest` for hosted agent deployments. A unique tag makes redeploys and rollbacks predictable.

1. Build image in Azure Container Registry using ACR Tasks:

```bash
bash scripts/build-image.sh
```

This uses:

```bash
az acr build --registry <acr-name> --image <repository>:<tag> --platform linux/amd64 --file Dockerfile .
```

If your registry uses `RBAC Registry + ABAC Repository Permissions` and the quick build must authenticate to a source registry, set this before the build:

```bash
export SOURCE_ACR_AUTH_ID='[caller]'
```

For this repo's current local-context build, leave `SOURCE_ACR_AUTH_ID` unset.

1. Export the image URI for deployment:

```bash
export IMAGE_URI=${AZURE_CONTAINER_REGISTRY_NAME}.azurecr.io/${IMAGE_REPOSITORY}:${IMAGE_TAG}
```

1. Optional: verify the tag exists in ACR:

```bash
az acr repository show-tags \
  --name "${AZURE_CONTAINER_REGISTRY_NAME}" \
  --repository "${IMAGE_REPOSITORY}" \
  --output table
```

`push-image.sh` is not required when using ACR Tasks because the remote build already publishes the image.

## 3) Deploy to Microsoft AI Foundry

### Option A (recommended for repeatable app-level deploy): Azure Developer CLI

```bash
./scripts/deploy-azd.sh
```

This runs:

- `azd ai agent init -m agent.yaml`
- `azd up`

### Option B (direct SDK-based hosted version creation)

1. Set required environment values:

```bash
set -a
source .env
set +a
export IMAGE_URI=${AZURE_CONTAINER_REGISTRY_NAME}.azurecr.io/${IMAGE_REPOSITORY}:${IMAGE_TAG}
```

1. Create hosted agent version:

```bash
uv run python scripts/deploy-sdk.py
```

Example `.env` values using the placeholder format from `.env.example`:

```bash
FOUNDRY_PROJECT_ENDPOINT=https://<your-account>.services.ai.azure.com/api/projects/<your-project>
FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-5.4-mini
AZURE_CONTAINER_REGISTRY_NAME=<your-acr-name>
IMAGE_REPOSITORY=blog-writer-agent
AGENT_NAME=blog-writer-agent
```

## 4) Validate Deployed Agent

Invoke from Foundry using SDK helper:

```bash
export PROMPT="Write a blog post about Microsoft Agent Framework for Python"
uv run python scripts/invoke-foundry.py
```

## Skill Behavior

This hosted agent intentionally demonstrates **skill-first behavior**:

- Input format: any blog topic prompt (optionally prefixed with `blog:`)
- Example: `blog: Building AI agent deployment pipelines on Foundry`
- The built-in skill reads local guidance from `skills/SKILL.md`
- It writes a markdown draft file under `blog/` and returns the saved path plus the full generated markdown in the response

## Microsoft Learn References (MCP-grounded)

The deployment flow in this scaffold aligns with Microsoft Learn guidance for hosted agents:

1. [Hosted agents concepts and creation](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents)
1. [Deploy hosted agent how-to](https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent)
1. [Azure Developer CLI Foundry extension](https://learn.microsoft.com/azure/developer/azure-developer-cli/extensions/azure-ai-foundry-extension)

If your environment has Microsoft Learn MCP tools enabled, query the same topics with:

- `mcp_microsoftdocs_microsoft_docs_search` for quick grounding
- `mcp_microsoftdocs_microsoft_docs_fetch` for full page procedures
- `mcp_microsoftdocs_microsoft_code_sample_search` for current snippets

## Notes

- Hosted agent containers must be built for `linux/amd64`.
- For the ACR Tasks workflow, local Docker is not required for image creation or push.
- Keep pinned preview versions for Agent Framework/AgentServer packages.
- If your Foundry project uses managed identity for runtime pulls, ensure ACR pull permissions are granted to the project identity.
