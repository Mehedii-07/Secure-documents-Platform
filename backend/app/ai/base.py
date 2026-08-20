"""
ai/base.py
==========
Abstract AI Provider — the contract all concrete providers must implement.

Design goals:
- Business logic NEVER imports a specific provider (OpenAI, Anthropic, etc.)
- Business logic imports AIProvider and calls its methods
- The concrete provider is resolved at startup from the AI_PROVIDER setting
- Swapping providers requires zero changes to business logic

Usage:
    from app.ai import get_ai_provider

    provider = get_ai_provider()
    embedding = await provider.embed_text("Hello world")
    response = await provider.chat_completion(messages=[...])
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# ------------------------------------------------------------------ #
# Data contracts (provider-agnostic)
# ------------------------------------------------------------------ #

@dataclass
class ChatMessage:
    """A single message in a conversation."""
    role: str      # "system" | "user" | "assistant"
    content: str


@dataclass
class ChatResponse:
    """Response from the chat completion endpoint."""
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    raw: dict[str, Any] = field(default_factory=dict)  # provider-specific raw response


@dataclass
class EmbeddingResponse:
    """Response from the embedding endpoint."""
    embedding: list[float]
    model: str
    total_tokens: int


@dataclass
class ClassificationResult:
    """Document classification output."""
    category: str
    confidence: float
    sub_categories: list[str] = field(default_factory=list)
    reasoning: str = ""


# ------------------------------------------------------------------ #
# Abstract Provider — the contract
# ------------------------------------------------------------------ #

class AIProvider(ABC):
    """
    Abstract base class for all AI providers.

    All methods are async because LLM API calls are I/O-bound.
    Implementations must raise `AIProviderError` on failure,
    not propagate provider-specific exceptions.
    """

    @abstractmethod
    async def embed_text(self, text: str) -> EmbeddingResponse:
        """
        Generate a vector embedding for the given text.

        Args:
            text: Text to embed. Will be truncated to model's token limit.

        Returns:
            EmbeddingResponse with the embedding vector and token usage.

        Raises:
            AIProviderError: If the provider call fails.
        """
        ...

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResponse]:
        """
        Generate embeddings for multiple texts in a single API call.

        More efficient than calling embed_text() in a loop.
        """
        ...

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
    ) -> ChatResponse:
        """
        Send a chat completion request.

        Args:
            messages: Conversation history. The last message is the user's query.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens to generate. None = provider default.
            system_prompt: Optional system instruction prepended to messages.

        Returns:
            ChatResponse with the assistant's reply and token usage.

        Raises:
            AIProviderError: If the provider call fails.
        """
        ...

    @abstractmethod
    async def classify_document(
        self,
        text: str,
        candidate_categories: list[str],
    ) -> ClassificationResult:
        """
        Classify document text into one of the candidate categories.

        Args:
            text: Document text (may be truncated for long documents).
            candidate_categories: List of valid category names.

        Returns:
            ClassificationResult with the chosen category and confidence.

        Raises:
            AIProviderError: If the provider call fails or returns invalid JSON.
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name, e.g. 'openai' or 'anthropic'."""
        ...

    @property
    @abstractmethod
    def embedding_dimension(self) -> int:
        """
        The dimension of vectors produced by embed_text().
        Must match the VECTOR_DIMENSION setting and the pgvector column size.
        """
        ...


# ------------------------------------------------------------------ #
# Provider-agnostic exception
# ------------------------------------------------------------------ #

class AIProviderError(Exception):
    """
    Raised by any AIProvider implementation when a call fails.

    Wraps provider-specific errors so callers never need to handle
    OpenAIError, anthropic.APIError, etc. directly.
    """

    def __init__(self, message: str, provider: str, original: Exception | None = None) -> None:
        self.provider = provider
        self.original = original
        super().__init__(f"[{provider}] {message}")
