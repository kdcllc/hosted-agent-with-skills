import asyncio
import json
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

from skills.blog_writer_skill import write_blog

load_dotenv(override=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hosted-agent-with-skills")

class SkillEnabledAgent(BaseAgent):
    """A hosted agent that always executes the write_blog skill tool."""

    def __init__(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        super().__init__(id=name or "blog-writer-agent", name=name, description=description)

    def run(
        self,
        messages: str | Message | Sequence[str | Message] | None = None,
        *,
        stream: bool = False,
        session: AgentSession | None = None,
        **kwargs: Any,
    ) -> AgentResponse | ResponseStream[AgentResponseUpdate, AgentResponse]:
        user_text = self._extract_user_text(messages)

        if stream:
            return ResponseStream(
                self._stream_updates(user_text),
                finalizer=AgentResponse.from_updates,
            )

        return self._run_once(user_text)

    async def _run_once(self, user_text: str) -> AgentResponse:
        if not user_text:
            return AgentResponse(
                messages=[
                    Message(
                        role="assistant",
                        text=(
                            "Hello! I am a hosted blog-writer agent powered by the blog-writer skill. "
                            "Send me a topic and I will generate a markdown blog post for you."
                        ),
                    )
                ],
                agent_id=self.id,
            )

        response_text = self._invoke_blog_skill(user_text)
        return AgentResponse(
            messages=[Message(role="assistant", text=response_text)],
            agent_id=self.id,
        )

    async def _stream_updates(self, user_text: str) -> AsyncIterable[AgentResponseUpdate]:
        if not user_text:
            yield AgentResponseUpdate(
                contents=[
                    Content.from_text(
                        "Hello! I am a hosted blog-writer agent powered by the blog-writer skill. "
                        "Send me a topic and I will generate a markdown blog post for you."
                    )
                ],
                role="assistant",
                agent_id=self.id,
            )
            return

        response_text = self._invoke_blog_skill(user_text)
        yield AgentResponseUpdate(
            contents=[Content.from_text(response_text)],
            role="assistant",
            agent_id=self.id,
        )

    def _invoke_blog_skill(self, topic: str) -> str:
        try:
            result = write_blog.func(topic=topic)
            payload = json.loads(result)
        except Exception as exc:
            logger.exception("Skill execution failed")
            return f"Failed to execute blog skill: {exc}"

        if payload.get("error"):
            return f"Skill error: {payload['error']}"

        path = payload.get("path", "")
        saved_topic = payload.get("topic", topic)
        date = payload.get("date", "")
        return (
            "Skill execution complete.\n"
            f"Topic: {saved_topic}\n"
            f"Date: {date}\n"
            f"Saved file: {path}"
        )

    def _extract_user_text(
        self, messages: str | Message | Sequence[str | Message] | None
    ) -> str:
        if messages is None:
            return ""
        if isinstance(messages, str):
            return messages.strip()
        if isinstance(messages, Message):
            return (messages.text or "").strip()
        for item in reversed(list(messages)):
            text = item.text if isinstance(item, Message) else str(item)
            if text and text.strip():
                return text.strip()
        return ""


def create_agent() -> SkillEnabledAgent:
    return SkillEnabledAgent(
        name="blog-writer-agent",
        description="Hosted agent with a built-in blog writer skill",
    )


async def main() -> None:
    logger.info("Starting hosted agent server on port 8088")
    await from_agent_framework(create_agent()).run_async()


if __name__ == "__main__":
    asyncio.run(main())
