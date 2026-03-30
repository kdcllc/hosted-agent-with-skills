import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentProtocol,
    FoundryFeaturesOptInKeys,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if value:
        return value
    raise RuntimeError(
        f"Missing required environment variable: {name}. "
        "Set it in your shell or .env before running deploy-sdk.py."
    )


def _read_int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer, got: {raw!r}") from exc


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=ROOT_DIR / ".env", override=False)

# Allow IMAGE_URI to be inferred from ACR variables when not explicitly set.
if not os.environ.get("IMAGE_URI"):
    acr = os.environ.get("AZURE_CONTAINER_REGISTRY_NAME")
    repo = os.environ.get("IMAGE_REPOSITORY")
    tag = os.environ.get("IMAGE_TAG")
    if acr and repo and tag:
        os.environ["IMAGE_URI"] = f"{acr}.azurecr.io/{repo}:{tag}"

project_endpoint = _require_env("FOUNDRY_PROJECT_ENDPOINT")
agent_name = os.environ.get("AGENT_NAME", "blog-writer-agent")
image_uri = _require_env("IMAGE_URI")
model_name = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4.1")
protocol_version = os.environ.get("HOSTED_AGENT_PROTOCOL_VERSION", "v1")
hosted_cpu = os.environ.get("HOSTED_AGENT_CPU", "1")
hosted_memory = os.environ.get("HOSTED_AGENT_MEMORY", "2Gi")
desired_min_replicas = _read_int_env("HOSTED_AGENT_MIN_REPLICAS", 1)
desired_max_replicas = _read_int_env("HOSTED_AGENT_MAX_REPLICAS", 1)

if desired_min_replicas < 0 or desired_max_replicas < 0:
    raise RuntimeError("HOSTED_AGENT_MIN_REPLICAS and HOSTED_AGENT_MAX_REPLICAS must be >= 0")
if desired_max_replicas < desired_min_replicas:
    raise RuntimeError("HOSTED_AGENT_MAX_REPLICAS must be >= HOSTED_AGENT_MIN_REPLICAS")
if desired_min_replicas == 0 and desired_max_replicas == 0:
    raise RuntimeError("Replica values 0/0 keep the hosted agent inactive. Use 1/1 or 0/1.")

project = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
    allow_preview=True,
)

agent = project.agents.create_version(
    agent_name=agent_name,
    foundry_features=FoundryFeaturesOptInKeys.HOSTED_AGENTS_V1_PREVIEW,
    definition=HostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version=protocol_version)
        ],
        cpu=hosted_cpu,
        memory=hosted_memory,
        image=image_uri,
        environment_variables={
            "FOUNDRY_PROJECT_ENDPOINT": project_endpoint,
            "FOUNDRY_MODEL_DEPLOYMENT_NAME": model_name,
        },
    ),
)

print(f"Created agent version: name={agent.name}, version={agent.version}")
print(f"Created with protocol={protocol_version}, cpu={hosted_cpu}, memory={hosted_memory}")
print("Next step: start the hosted agent container in Foundry before invoking it.")
print("Replica min/max are configured when starting the hosted container, not in create_version.")
print(
    "Set these values when starting the container: "
    f"min={desired_min_replicas}, max={desired_max_replicas}."
)
