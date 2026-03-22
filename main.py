import asyncio
import logging
from collections.abc import AsyncIterable, Sequence
from typing import Any

from agent_framework import (
    AgentResponse,
    AgentResponseUpdate,
    AgentSession,
    BaseAgent,
    Content,
    Message,
    ResponseStream,
)
from azure.ai.agentserver.agentframework import from_agent_framework
from dotenv import load_dotenv

from skills.blog_writer_skill import BlogWriterSkill

load_dotenv(override=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hosted-agent-with-skills")


class SkillEnabledAgent(BaseAgent):
    """A hosted agent that uses a built-in blog-writer skill."""

    def __init__(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        skill: BlogWriterSkill,
    ) -> None:
        self.skill = skill
        super().__init__(id=name or "blog-writer-agent", name=name, description=description)

    def run(
        self,
        messages: str | Message | Sequence[str | Message] | None = None,
        *,
        stream: bool = False,
        session: AgentSession | None = None,
        **kwargs: Any,
    ) -> AgentResponse | ResponseStream[AgentResponseUpdate, AgentResponse]:
        normalized_messages = self._normalize_messages(messages)
        response_text = self._handle_messages(normalized_messages)

        if stream:
            return ResponseStream(
                self._stream_updates(response_text),
                finalizer=AgentResponse.from_updates,
            )

        return self._run_once(response_text)

    async def _run_once(self, response_text: str) -> AgentResponse:
        return AgentResponse(
            messages=[Message(role="assistant", text=response_text)],
            agent_id=self.id,
        )

    async def _stream_updates(
        self,
        response_text: str,
    ) -> AsyncIterable[AgentResponseUpdate]:
        words = response_text.split()
        for i, word in enumerate(words):
            chunk = word if i == 0 else f" {word}"
            yield AgentResponseUpdate(
                contents=[Content.from_text(chunk)],
                role="assistant",
                agent_id=self.id,
            )
            await asyncio.sleep(0.01)

    def _handle_messages(self, normalized_messages: list[Message]) -> str:
        if not normalized_messages:
            return (
                "Hello. I am a hosted Microsoft Agent Framework blog writer agent. "
                "Send your topic and I will generate a markdown blog post file."
            )

        last_message = normalized_messages[-1]
        user_text = (last_message.text or "").strip()
        if not user_text:
            return "I received an empty message. Try: Write a blog about Microsoft AI Foundry hosted agents."

        topic = user_text
        if user_text.lower().startswith("blog:"):
            topic = user_text.split(":", 1)[1].strip()

        try:
            draft = self.skill.write_blog(topic=topic)
            return (
                f"Blog draft generated successfully for topic: '{topic}'. "
                f"Saved to: {draft.path}\n\n{draft.markdown}"
            )
        except ValueError as exc:
            logger.warning("Skill rejected request: %s", exc)
            return f"Skill error: {exc}"

    def _normalize_messages(
        self,
        messages: str | Message | Sequence[str | Message] | None,
    ) -> list[Message]:
        if messages is None:
            return []

        if isinstance(messages, str):
            return [Message(role="user", text=messages)]

        if isinstance(messages, Message):
            return [messages]

        normalized_messages: list[Message] = []
        for item in messages:
            if isinstance(item, Message):
                normalized_messages.append(item)
            else:
                normalized_messages.append(Message(role="user", text=item))

        return normalized_messages


def create_agent() -> SkillEnabledAgent:
    return SkillEnabledAgent(
        name="blog-writer-agent",
        description="Hosted agent with a built-in blog writer skill",
        skill=BlogWriterSkill(),
    )


async def main() -> None:
    logger.info("Starting hosted agent server on port 8088")
    await from_agent_framework(create_agent()).run_async()


if __name__ == "__main__":
    asyncio.run(main())
