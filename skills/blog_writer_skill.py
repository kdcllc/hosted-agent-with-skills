from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import re

from agent_framework import Skill, tool

_SKILL_MD = Path(__file__).resolve().parent / "SKILL.md"
_BLOG_DIR = Path(__file__).resolve().parent.parent / "blog"


def _read_skill_content() -> str:
    if not _SKILL_MD.exists():
        return "Generate professional technical blog posts in markdown format based on a given topic."
    return _SKILL_MD.read_text(encoding="utf-8")


blog_writer_skill = Skill(
    name="blog-writer",
    description=(
        "Generates professional technical blog posts in markdown format "
        "and saves them to the blog/ directory."
    ),
    content=_read_skill_content(),
)


@tool
def write_blog(topic: str) -> str:
    """Generate a markdown blog draft for the given topic and save it to the blog/ directory.

    Args:
        topic: The blog topic or title to write about.

    Returns:
        JSON string with path, topic, and date keys.
    """
    topic = (topic or "").strip()
    if not topic:
        return json.dumps({"error": "Please provide a non-empty blog topic."})

    today = datetime.now().strftime("%Y-%m-%d")
    slug = datetime.now().strftime("%Y%m%d%H%M%S%f")

    _BLOG_DIR.mkdir(parents=True, exist_ok=True)
    output_path = _BLOG_DIR / f"blog-{today}-{slug}.md"

    content = _render_markdown(topic=topic, date_iso=today)
    output_path.write_text(content, encoding="utf-8")

    return json.dumps({"path": str(output_path), "topic": topic, "date": today})


def _render_markdown(topic: str, date_iso: str) -> str:
    profile = _build_topic_profile(topic)
    description = (
        f"A practical technical guide to {topic} with architecture guidance, "
        f"implementation steps, and production-ready patterns."
    )
    outline = _build_outline(topic, profile)
    code_example = _build_code_example(topic, profile)
    references = _build_references(profile)
    best_practices = _build_best_practices(profile)
    validation_checklist = _build_validation_checklist(profile)

    return f'''---
title: "{topic}: Implementation Guide"
date: {date_iso}
description: "{description[:155]}"
tags: [{", ".join(profile["tags"])}]
author: "Blog Writer Agent"
readingTime: "{profile['reading_time']}"
difficulty: "{profile['difficulty']}"
---

# {topic}: Implementation Guide

## Introduction

{profile['intro']}

## Draft Outline

{outline}

## Section 1: Why This Matters

{profile['why_it_matters']}

## Section 2: Architecture and Design

{profile['architecture']}

## Section 2: Implementation Walkthrough

{code_example}

The snippet demonstrates a practical baseline for this topic. Tailor configuration, validation, and observability to your environment before production rollout.

## Section 3: Best Practices

{best_practices}

## Section 4: Common Pitfalls

{profile['pitfalls']}

## Section 5: Validation Checklist

{validation_checklist}

## Conclusion

{profile['conclusion']}

## References

{references}
'''


def _build_topic_profile(topic: str) -> dict[str, str | list[str]]:
    normalized = re.sub(r"\s+", " ", topic.strip().lower())

    is_hydroponics = any(
        key in normalized
        for key in [
            "hydroponic",
            "hydroponics",
            "grow light",
            "nutrient solution",
            "ec",
            "ph",
            "lettuce",
            "deep water culture",
            "dwc",
        ]
    )

    is_ai = any(
        key in normalized
        for key in [
            "agent",
            "llm",
            "prompt",
            "copilot",
            "foundry",
            "model",
            "rag",
            "ai",
        ]
    )
    is_platform = any(
        key in normalized
        for key in ["kubernetes", "docker", "terraform", "azure", "aws", "gcp", "devops", "ci/cd"]
    )
    is_data = any(
        key in normalized
        for key in ["sql", "database", "data", "etl", "analytics", "kusto", "pipeline"]
    )

    if is_hydroponics:
        return {
            "difficulty": "Beginner to Intermediate",
            "reading_time": "11 minutes",
            "tags": ["hydroponics", "controlled-environment-agriculture", "beginner-guide", "practical-how-to"],
            "intro": (
                f"{topic} is easiest when you treat your setup like a repeatable system: stable water chemistry, "
                "predictable lighting, and a simple monitoring routine. This guide gives you the practical baseline "
                "to get your first successful harvest."
            ),
            "why_it_matters": (
                "Hydroponics can produce faster growth and cleaner results in limited space, but beginners often fail "
                "because they change too many variables at once. A structured process helps you isolate problems and "
                "recover quickly."
            ),
            "architecture": (
                "Choose a low-complexity system first (Kratky or DWC), then standardize four controls: light duration, "
                "solution strength (EC), acidity (pH), and reservoir temperature. Keep each control in target range "
                "before experimenting with additives or advanced techniques."
            ),
            "pitfalls": (
                "- Overfeeding nutrients early; seedlings need weaker solution than mature plants.\n"
                "- Ignoring pH drift for several days, which locks out calcium/magnesium uptake.\n"
                "- Underestimating heat from grow lights, causing root stress and slow growth.\n"
                "- Starting with fruiting crops before mastering leafy greens."
            ),
            "conclusion": (
                "Start with one crop (for example lettuce), one nutrient line, and one repeatable schedule. "
                "Consistency beats complexity in early hydroponic success."
            ),
            "domain": "hydroponics",
        }

    if is_ai:
        return {
            "difficulty": "Intermediate",
            "reading_time": "10 minutes",
            "tags": [
                "microsoft-foundry",
                "agent-framework",
                "ai-engineering",
                "developer-guide",
            ],
            "intro": (
                f"{topic} can move quickly from prototype to production when you treat instructions, tools, "
                "evaluation, and observability as first-class concerns. This guide gives you a practical path "
                "to design and deliver reliable outcomes."
            ),
            "why_it_matters": (
                f"{topic} matters because teams need predictable, testable AI behavior instead of one-off demos. "
                "A clear architecture reduces hallucination risk, improves maintainability, and speeds up iteration."
            ),
            "architecture": (
                "Start with a layered design: intent handling, tool invocation boundaries, safety/validation checks, "
                "and telemetry. Keep prompts versioned, tool schemas explicit, and model-specific behavior behind "
                "well-defined abstractions."
            ),
            "pitfalls": (
                "- Treating prompts as static text without versioning and tests.\n"
                "- Allowing tools to run without validation or guardrails.\n"
                "- Skipping evaluation datasets and relying only on manual spot checks."
            ),
            "conclusion": (
                "Focus on repeatability: version your instructions, validate tool calls, and evaluate outputs against "
                "known datasets. That foundation turns AI features into durable product capabilities."
            ),
            "domain": "ai",
        }

    if is_platform:
        return {
            "difficulty": "Intermediate",
            "reading_time": "9 minutes",
            "tags": ["cloud-architecture", "platform-engineering", "devops", "developer-guide"],
            "intro": (
                f"{topic} succeeds when architecture and operations are designed together. "
                "This guide emphasizes deployment flow, runtime reliability, and operational safeguards."
            ),
            "why_it_matters": (
                f"{topic} is often where delivery speed meets reliability requirements. "
                "Strong platform patterns reduce downtime and help teams ship confidently."
            ),
            "architecture": (
                "Separate build, deploy, and runtime concerns. Use immutable artifacts, staged rollouts, and "
                "environment parity to reduce drift across development and production."
            ),
            "pitfalls": (
                "- Coupling build-time assumptions to runtime configuration.\n"
                "- Missing health checks and rollback strategies.\n"
                "- Weak secret management and environment isolation."
            ),
            "conclusion": (
                "Make platform delivery boring in the best way: consistent pipelines, observable runtime behavior, "
                "and controlled rollouts."
            ),
            "domain": "platform",
        }

    if is_data:
        return {
            "difficulty": "Intermediate",
            "reading_time": "9 minutes",
            "tags": ["data-engineering", "analytics", "architecture", "developer-guide"],
            "intro": (
                f"{topic} requires balancing data quality, performance, and maintainability. "
                "This guide focuses on robust data flow design and practical operational patterns."
            ),
            "why_it_matters": (
                f"{topic} shapes decision quality across your product and organization. "
                "Reliable pipelines and well-defined contracts prevent silent data regressions."
            ),
            "architecture": (
                "Design around contracts, lineage, and validation checkpoints. Keep transformations explicit, "
                "idempotent where possible, and instrumented for latency and quality metrics."
            ),
            "pitfalls": (
                "- Missing schema evolution strategy.\n"
                "- No data quality gates before downstream consumption.\n"
                "- Limited observability into freshness and failed batches."
            ),
            "conclusion": (
                "Treat data reliability as a product feature: clear contracts, automated checks, and fast recovery "
                "when issues appear."
            ),
            "domain": "data",
        }

    return {
        "difficulty": "Beginner to Intermediate",
        "reading_time": "8 minutes",
        "tags": ["software-engineering", "architecture", "implementation", "developer-guide"],
        "intro": (
            f"{topic} can be implemented effectively with a clear architecture, practical examples, and "
            "incremental validation. This guide gives you a reusable blueprint."
        ),
        "why_it_matters": (
            f"{topic} influences both delivery speed and long-term maintainability. "
            "A structured implementation plan reduces rework and improves quality."
        ),
        "architecture": (
            "Define boundaries, interfaces, and ownership early. Keep core logic testable, external dependencies "
            "isolated, and runtime behavior observable."
        ),
        "pitfalls": (
            "- Jumping into implementation without clear scope.\n"
            "- Missing edge-case handling and failure paths.\n"
            "- Weak documentation for operational handoff."
        ),
        "conclusion": (
            "Start small, validate quickly, and iterate with measurable outcomes. "
            "That approach keeps implementation focused and production-ready."
        ),
        "domain": "general",
    }


def _build_outline(topic: str, profile: dict[str, str | list[str]]) -> str:
    domain = str(profile.get("domain", "general"))
    if domain == "hydroponics":
        items = [
            "1. Pick the right beginner system (Kratky vs DWC)",
            "2. Set target ranges for pH, EC, and water temperature",
            "3. Build a weekly nutrient and maintenance routine",
            "4. Diagnose common plant stress symptoms",
            "5. Scale from first harvest to repeatable production",
        ]
    elif domain == "ai":
        items = [
            "1. Problem framing and expected agent behavior",
            "2. Prompt and tool design",
            "3. Evaluation strategy and quality gates",
            "4. Production hardening and observability",
            "5. Rollout strategy and iteration loop",
        ]
    elif domain == "platform":
        items = [
            "1. Architecture baseline and non-functional requirements",
            "2. Build and deployment workflow",
            "3. Runtime configuration and secret management",
            "4. Reliability patterns and scaling",
            "5. Operational runbook",
        ]
    elif domain == "data":
        items = [
            "1. Data contracts and source mapping",
            "2. Pipeline design and transformation strategy",
            "3. Data quality checks and validation",
            "4. Performance and cost optimization",
            "5. Monitoring and incident response",
        ]
    else:
        items = [
            "1. Problem definition and scope",
            "2. Architecture decisions",
            "3. Implementation walkthrough",
            "4. Testing and validation",
            "5. Operational best practices",
        ]
    return "\n".join(items)


def _build_code_example(topic: str, profile: dict[str, str | list[str]]) -> str:
    domain = str(profile.get("domain", "general"))
    if domain == "hydroponics":
        return '''```markdown
### Starter Targets (Leafy Greens)

| Metric | Seedling Stage | Vegetative Stage | Notes |
|---|---:|---:|---|
| pH | 5.8-6.2 | 5.8-6.3 | Adjust slowly; avoid large daily swings |
| EC (mS/cm) | 0.8-1.2 | 1.2-1.8 | Increase gradually as plants mature |
| Water Temp (C) | 18-22 | 18-22 | Warmer reservoirs reduce oxygen availability |
| Light Cycle | 14-16 h/day | 14-16 h/day | Keep light height consistent |

### Weekly Routine
1. Measure pH and EC at the same time each day.
2. Top up with plain water first, then re-check EC.
3. Trim dead leaves and inspect roots (white/cream is healthy).
4. Refresh reservoir every 7-14 days for stability.
```
'''

    if domain == "ai":
        return f'''```python
from agent_framework import Agent


async def run_workflow(client, skills_provider, write_blog_tool, user_topic: str):
    instructions = (
        "You are a practical technical writer. "
        "Load the relevant skill instructions and call write_blog to generate output."
    )
    async with Agent(
        client=client,
        name="blog-writer-assistant",
        instructions=instructions,
        context_providers=[skills_provider],
        tools=[write_blog_tool],
    ) as agent:
        return await agent.run(f"Write a detailed blog post about: {{user_topic}}")
```
'''

    if domain == "platform":
        return f'''```bash
# Example deployment validation flow
set -euo pipefail

echo "1) Lint and test"
uv run ruff check .
uv run pytest -q

echo "2) Start local agent server"
uv run python main.py

echo "3) Smoke test endpoint"
bash ./scripts/invoke-local.sh "{topic}"
```
'''

    if domain == "data":
        return f'''```python
from dataclasses import dataclass


@dataclass
class DataQualityReport:
    total_rows: int
    invalid_rows: int


def validate_dataset(records: list[dict]) -> DataQualityReport:
    invalid = sum(1 for r in records if not r.get("id") or r.get("value") is None)
    return DataQualityReport(total_rows=len(records), invalid_rows=invalid)


print(validate_dataset([{{"id": 1, "value": 42}}, {{"id": None, "value": 7}}]))
```
'''

    return f'''```bash
# Start hosted agent locally
uv run python main.py

# In another terminal, invoke the agent with your topic
bash ./scripts/invoke-local.sh "{topic}"
```

```python
import json
import subprocess


def create_article_via_hosted_agent(topic: str) -> str:
    cmd = ["bash", "./scripts/invoke-local.sh", topic]
    raw = subprocess.check_output(cmd, text=True)
    payload = json.loads(raw)
    text = payload["output"][0]["content"][0]["text"]
    return text


print(create_article_via_hosted_agent("{topic}"))
```
'''


def _build_references(profile: dict[str, str | list[str]]) -> str:
    domain = str(profile.get("domain", "general"))
    common = [
        "- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)",
        "- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)",
    ]

    if domain == "hydroponics":
        common = [
            "- [University of Florida IFAS: Hydroponic Vegetable Production](https://edis.ifas.ufl.edu/publication/HS405)",
            "- [Royal Horticultural Society: Hydroponics Overview](https://www.rhs.org.uk/advice/profile?pid=711)",
            "- [FAO Protected Cultivation Resources](https://www.fao.org/)",
        ]
    elif domain == "ai":
        common.extend(
            [
                "- [Hosted Agents Concepts](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents)",
                "- [Prompt Engineering Guide](https://learn.microsoft.com/azure/ai-services/openai/concepts/prompt-engineering)",
            ]
        )
    elif domain == "platform":
        common.extend(
            [
                "- [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/)",
                "- [Azure Deployment Best Practices](https://learn.microsoft.com/azure/architecture/best-practices/)",
            ]
        )
    elif domain == "data":
        common.extend(
            [
                "- [Data Engineering on Azure](https://learn.microsoft.com/azure/architecture/data-guide/)",
                "- [Data Quality Overview](https://learn.microsoft.com/azure/architecture/data-guide/technology-choices/data-ingestion)",
            ]
        )
    else:
        common.append("- [Microsoft Learn](https://learn.microsoft.com/)")

    return "\n".join(common)


def _build_best_practices(profile: dict[str, str | list[str]]) -> str:
    domain = str(profile.get("domain", "general"))
    if domain == "hydroponics":
        return "\n".join(
            [
                "- Start with one crop and one nutrient program for your first 4-6 weeks.",
                "- Calibrate pH and EC meters regularly; bad readings cause most beginner errors.",
                "- Keep a simple daily log (pH, EC, water temp, visual leaf/root notes).",
                "- Change only one variable at a time when troubleshooting.",
                "- Prioritize airflow and reservoir cleanliness to reduce disease pressure.",
            ]
        )
    return "\n".join(
        [
            "- Define measurable success criteria before implementation.",
            "- Keep configuration externalized and environment-specific.",
            "- Add tests around critical flows, including error paths.",
            "- Add logging and telemetry from day one.",
            "- Document rollback and recovery procedures for production changes.",
        ]
    )


def _build_validation_checklist(profile: dict[str, str | list[str]]) -> str:
    domain = str(profile.get("domain", "general"))
    if domain == "hydroponics":
        return "\n".join(
            [
                "- Confirm pH and EC meters are calibrated this week.",
                "- Verify reservoir temperature stays between 18-22C.",
                "- Ensure roots are light-colored and odor-free.",
                "- Check light schedule consistency (timer and distance from canopy).",
                "- Inspect for tip burn, chlorosis, or droop before adjusting nutrients.",
            ]
        )
    return "\n".join(
        [
            "- Verify local development setup and dependency versions.",
            "- Run linting, tests, and smoke tests for the target workflow.",
            "- Validate authentication and permissions in the target environment.",
            "- Confirm telemetry and alerting are emitting expected signals.",
            "- Perform a canary or staged rollout before full release.",
        ]
    )