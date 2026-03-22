from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class BlogDraft:
    path: str
    markdown: str


class BlogWriterSkill:
    """Creates markdown blog drafts using local skill instructions as guidance."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parent
        self.skill_file = self.root / "SKILL.md"
        self.blog_dir = self.root.parent / "blog"

    def write_blog(self, topic: str) -> BlogDraft:
        topic = (topic or "").strip()
        if not topic:
            raise ValueError("Please provide a non-empty blog topic.")

        skill_summary = self._load_skill_summary()
        today = datetime.now().strftime("%Y-%m-%d")
        slug = datetime.now().strftime("%Y%m%d%H%M%S")

        self.blog_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.blog_dir / f"blog-{today}-{slug}.md"

        content = self._render_markdown(topic=topic, date_iso=today, skill_summary=skill_summary)
        output_path.write_text(content, encoding="utf-8")

        return BlogDraft(path=str(output_path), markdown=content)

    def _load_skill_summary(self) -> str:
        if not self.skill_file.exists():
            return "Skill guidance file not found; generated with default blog structure."

        lines = self.skill_file.read_text(encoding="utf-8").splitlines()
        non_empty = [line.strip() for line in lines if line.strip()]
        if not non_empty:
            return "Skill guidance file was empty; generated with default blog structure."

        summary_lines = non_empty[:6]
        return " ".join(summary_lines)

    def _render_markdown(self, topic: str, date_iso: str, skill_summary: str) -> str:
        description = f"A practical technical guide to {topic} with examples and implementation tips."
        return f'''---
title: "{topic}: Practical Blog Guide"
date: {date_iso}
description: "{description[:155]}"
tags: [microsoft-foundry, agent-framework, blog-writing, developer-guide]
author: "Blog Writer Agent"
readingTime: "8 minutes"
difficulty: "Intermediate"
---

# {topic}: Practical Blog Guide

## Introduction

Building high-quality technical content should be repeatable and practical. This draft was produced by a hosted blog-writer agent that follows local skill guidance and outputs markdown ready for editing and publishing.

## Draft Outline

1. Why this topic matters now
1. Core concepts and architecture
1. Implementation walkthrough
1. Best practices and common pitfalls
1. Validation and next steps

## Section 1: Why This Matters

{topic} is increasingly relevant for developers building production-grade systems. A clear writing plan helps your team communicate architecture decisions, implementation trade-offs, and operational patterns.

## Section 2: Implementation Walkthrough

```python
from pathlib import Path


def create_article(topic: str) -> str:
    title = f"{{topic}}: Practical Blog Guide"
    return f"# {{title}}\\n\\nStart with context, then show implementation details."


print(create_article("{topic}"))
```

The snippet demonstrates a minimal, testable pattern for creating structured markdown content programmatically.

## Section 3: Best Practices

- Start with a concrete problem statement.
- Include runnable examples and expected outcomes.
- Add references to official documentation for credibility.
- Document risks, constraints, and operational guidance.

## Conclusion

This generated draft gives you a strong starting point. Expand each section with validated research, production examples, and team-specific conventions before publishing.

## Skill Guidance Snapshot

{skill_summary}

## References

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Hosted Agents in Microsoft AI Foundry](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents)
'''