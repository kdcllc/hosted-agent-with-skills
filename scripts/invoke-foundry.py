import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai import BadRequestError
from dotenv import load_dotenv


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if value:
        return value
    raise RuntimeError(
        f"Missing required environment variable: {name}. "
        "Set it in your shell or .env before running invoke-foundry.py."
    )

load_dotenv(override=False)

PROJECT_ENDPOINT = _require_env("FOUNDRY_PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME", "blog-writer-agent")
PROMPT = os.environ.get(
    "PROMPT",
    "Write a blog post about building hosted agents with Microsoft Agent Framework and Foundry.",
)

client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
    allow_preview=True,
)
agent = client.agents.get(agent_name=AGENT_NAME)
openai_client = client.get_openai_client()

try:
    response = openai_client.responses.create(
        input=[{"role": "user", "content": PROMPT}],
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )
    print(response.output_text)
except BadRequestError as exc:
    message = str(exc)
    if "not in Running state" in message:
        raise RuntimeError(
            "Agent is deployed but not running yet. Start the hosted agent container in Foundry "
            "(or run the azd deployment flow) and retry in a few minutes."
        ) from exc
    raise
