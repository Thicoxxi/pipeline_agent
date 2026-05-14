from core.config import Config

from providers.llm.groq_provider import (
    GroqProvider
)

from providers.llm.openai_provider import (
    OpenAIProvider
)

from providers.llm.local_provider import (
    LocalProvider
)


def get_provider(provider="auto"):

    provider = (
        provider or "auto"
    ).lower()

    # =========================================
    # AUTO
    # =========================================
    if provider == "auto":

        if Config.GROQ_API_KEY:
            return GroqProvider()

        if Config.OPENAI_API_KEY:
            return OpenAIProvider()

        return LocalProvider()

    # =========================================
    # PROVIDERS
    # =========================================
    providers = {

        "groq": GroqProvider,

        "openai": OpenAIProvider,

        "local": LocalProvider
    }

    provider_class = providers.get(
        provider
    )

    if not provider_class:
        return LocalProvider()

    return provider_class()