from providers.llm.openai_provider import OpenAIProvider
from providers.llm.groq_provider import GroqProvider
from providers.llm.local_provider import LocalProvider

from providers.llm.openai_provider import (
    OpenAIProvider
)

from providers.llm.groq_provider import (
    GroqProvider
)

from providers.llm.local_provider import (
    LocalProvider
)


class ProviderService:

    @staticmethod
    def get(provider: str):

        providers = {

            "openai": OpenAIProvider(),

            "groq": GroqProvider(),

            "local": LocalProvider()
        }

        return providers.get(
            provider,
            None
        )

    @staticmethod
    def stream(
        prompt: str,
        provider: str = "auto"
    ):

        # =====================================
        # AUTO
        # =====================================
        if provider == "auto":

            auto_order = [

                "groq",

                "openai",

                "local"
            ]

            for provider_name in auto_order:

                instance = ProviderService.get(
                    provider_name
                )

                if not instance:
                    continue

                try:

                    yield from instance.stream(
                        prompt
                    )

                    return

                except Exception as e:

                    print(
                        f"[ERROR] provider "
                        f"{provider_name}: {e}"
                    )

            raise Exception(
                "Nenhum provider disponivel"
            )

        # =====================================
        # FIXED
        # =====================================
        instance = ProviderService.get(
            provider
        )

        if not instance:

            raise Exception(
                f"Provider invalido: {provider}"
            )

        yield from instance.stream(
            prompt
        )