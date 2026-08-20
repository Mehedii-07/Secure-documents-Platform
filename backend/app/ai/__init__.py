"""
ai/__init__.py
==============
AI provider factory — resolves the configured provider at runtime.

Usage anywhere in the application:
    from app.ai import get_ai_provider
    provider = get_ai_provider()
    response = await provider.embed_text("hello")

The factory is cached so the same provider instance is reused
across requests (avoiding repeated object creation).
"""
from __future__ import annotations

from functools import lru_cache

from app.ai.base import AIProvider
from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_ai_provider() -> AIProvider:
    """
    Return the configured AI provider instance.

    The concrete provider class is determined by the AI_PROVIDER setting.
    Import is deferred so unused providers' dependencies are never imported.

    Raises:
        ValueError: If AI_PROVIDER is set to an unsupported value.
        ImportError: If the provider's SDK is not installed.
    """
    settings = get_settings()
    provider_name = settings.AI_PROVIDER

    if provider_name == "openai":
        from app.ai.providers.openai_provider import OpenAIProvider
        return OpenAIProvider(settings)

    if provider_name == "anthropic":
        from app.ai.providers.anthropic_provider import AnthropicProvider  # type: ignore[import]
        return AnthropicProvider(settings)

    if provider_name == "azure_openai":
        from app.ai.providers.azure_openai_provider import (
            AzureOpenAIProvider,  # type: ignore[import]
        )
        return AzureOpenAIProvider(settings)

    if provider_name == "ollama":
        from app.ai.providers.ollama_provider import OllamaProvider  # type: ignore[import]
        return OllamaProvider(settings)

    raise ValueError(
        f"Unsupported AI_PROVIDER: '{provider_name}'. "
        "Supported values: openai, anthropic, azure_openai, ollama"
    )


__all__ = ["AIProvider", "get_ai_provider"]
