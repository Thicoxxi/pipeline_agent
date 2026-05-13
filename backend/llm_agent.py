import logging

from providers.llm.groq_provider import (
    GroqProvider
)

from providers.llm.openai_provider import (
    OpenAIProvider
)

from core.config import Config

logger = logging.getLogger(__name__)

# =========================================================
# GET PROVIDER
# =========================================================
def get_provider(provider_name="auto"):

    # =====================================================
    # GROQ
    # =====================================================
    if provider_name == "groq":

        return GroqProvider()

    # =====================================================
    # OPENAI
    # =====================================================
    if provider_name == "openai":

        return OpenAIProvider()

    # =====================================================
    # AUTO
    # =====================================================
    try:

        if Config.has_groq():

            logger.info(
                "[LLM] usando GROQ"
            )

            return GroqProvider()

    except Exception as e:

        logger.error(
            f"[GROQ ERROR] {str(e)}"
        )

    try:

        if Config.has_openai():

            logger.info(
                "[LLM] usando OPENAI"
            )

            return OpenAIProvider()

    except Exception as e:

        logger.error(
            f"[OPENAI ERROR] {str(e)}"
        )

    raise Exception(
        "Nenhum provider disponível"
    )

# =========================================================
# STREAM
# =========================================================
def stream_llm(

    prompt: str,

    provider="auto",

    system_prompt=""
):

    provider_instance = get_provider(
        provider
    )

    logger.info(
        f"[LLM] provider={provider}"
    )

    for chunk in provider_instance.stream(

        prompt=prompt,

        system_prompt=system_prompt
    ):

        yield chunk