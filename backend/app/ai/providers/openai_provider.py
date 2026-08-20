"""
ai/providers/openai_provider.py
================================
Concrete OpenAI implementation of AIProvider.

Uses the official openai Python SDK (v1.x).
All provider-specific exceptions are caught and wrapped in AIProviderError.
"""
from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from openai import AsyncOpenAI, OpenAIError

from app.ai.base import (
    AIProvider,
    AIProviderError,
    ChatMessage,
    ChatResponse,
    ClassificationResult,
    EmbeddingResponse,
)

if TYPE_CHECKING:
    from app.core.config import Settings

logger = logging.getLogger(__name__)

# Embedding dimensions by model name
_EMBEDDING_DIMENSIONS: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


class OpenAIProvider(AIProvider):
    """
    OpenAI implementation of AIProvider.

    Supports:
    - Chat completions (gpt-4o, gpt-4o-mini, etc.)
    - Text embeddings (text-embedding-3-small, text-embedding-3-large)
    - Document classification (via structured JSON prompt)
    """

    def __init__(self, settings: "Settings") -> None:
        if not settings.OPENAI_API_KEY:
            raise AIProviderError(
                "OPENAI_API_KEY is not set. Add it to your .env file.",
                provider="openai",
            )
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._chat_model = settings.OPENAI_CHAT_MODEL
        self._embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self._configured_dimension = settings.VECTOR_DIMENSION

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def embedding_dimension(self) -> int:
        return _EMBEDDING_DIMENSIONS.get(self._embedding_model, self._configured_dimension)

    async def embed_text(self, text: str) -> EmbeddingResponse:
        """Embed a single text string."""
        try:
            response = await self._client.embeddings.create(
                input=[text],
                model=self._embedding_model,
            )
        except OpenAIError as exc:
            raise AIProviderError(str(exc), provider="openai", original=exc) from exc

        usage = response.usage
        return EmbeddingResponse(
            embedding=response.data[0].embedding,
            model=response.model,
            total_tokens=usage.total_tokens if usage else 0,
        )

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResponse]:
        """Embed multiple texts in a single API call."""
        if not texts:
            return []
        try:
            response = await self._client.embeddings.create(
                input=texts,
                model=self._embedding_model,
            )
        except OpenAIError as exc:
            raise AIProviderError(str(exc), provider="openai", original=exc) from exc

        usage = response.usage
        total_tokens = usage.total_tokens if usage else 0

        # Distribute tokens proportionally (OpenAI doesn't give per-item counts)
        per_item_tokens = total_tokens // max(len(texts), 1)

        return [
            EmbeddingResponse(
                embedding=item.embedding,
                model=response.model,
                total_tokens=per_item_tokens,
            )
            for item in sorted(response.data, key=lambda d: d.index)
        ]

    async def chat_completion(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
    ) -> ChatResponse:
        """Send a chat completion request."""
        openai_messages: list[dict[str, str]] = []

        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            openai_messages.append({"role": msg.role, "content": msg.content})

        kwargs: dict = {
            "model": self._chat_model,
            "messages": openai_messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        try:
            response = await self._client.chat.completions.create(**kwargs)
        except OpenAIError as exc:
            raise AIProviderError(str(exc), provider="openai", original=exc) from exc

        choice = response.choices[0]
        usage = response.usage

        return ChatResponse(
            content=choice.message.content or "",
            model=response.model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
        )

    async def classify_document(
        self,
        text: str,
        candidate_categories: list[str],
    ) -> ClassificationResult:
        """
        Classify a document using a structured JSON prompt.

        Instructs the model to respond in JSON so we can reliably
        parse the result. Falls back to 'unknown' if parsing fails.
        """
        categories_str = ", ".join(f'"{c}"' for c in candidate_categories)

        system = (
            "You are a document classification assistant. "
            "Respond ONLY with a valid JSON object — no markdown, no extra text."
        )
        user_content = (
            f"Classify the following document into one of these categories: [{categories_str}].\n\n"
            f"Respond with this exact JSON structure:\n"
            f'{{"category": "<chosen_category>", "confidence": <0.0-1.0>, '
            f'"sub_categories": [], "reasoning": "<brief reason>"}}\n\n'
            f"Document text (first 3000 chars):\n{text[:3000]}"
        )

        try:
            response = await self.chat_completion(
                messages=[ChatMessage(role="user", content=user_content)],
                temperature=0.0,
                system_prompt=system,
            )
            data = json.loads(response.content)
            return ClassificationResult(
                category=data.get("category", "unknown"),
                confidence=float(data.get("confidence", 0.0)),
                sub_categories=data.get("sub_categories", []),
                reasoning=data.get("reasoning", ""),
            )
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Failed to parse classification response: %s", exc)
            return ClassificationResult(category="unknown", confidence=0.0)
        except AIProviderError:
            raise
