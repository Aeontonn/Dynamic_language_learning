from typing import Protocol

import anthropic

from app.config import settings


class LLMClient(Protocol):
    """Anything that can turn a prompt into generated text. Implemented by
    AnthropicLLMClient for real use and swappable for a fake in tests."""

    def generate(self, prompt: str) -> str: ...


class AnthropicLLMClient:
    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def generate(self, prompt: str) -> str:
        response = self._client.messages.create(
            model=settings.llm_model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text


def get_llm_client() -> LLMClient:
    return AnthropicLLMClient()
