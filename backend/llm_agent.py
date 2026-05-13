import logging

from providers.llm.groq_provider import GroqProvider
from providers.llm.openai_provider import OpenAIProvider
from core.config import Config
from services.pipeline_service import PipelineService

logger = logging.getLogger(__name__)

# =========================================================
# GET PROVIDER
# =========================================================
def get_provider(provider_name="auto"):
    if provider_name == "groq":
        return GroqProvider()

    if provider_name == "openai":
        return OpenAIProvider()

    try:
        if Config.has_groq():
            logger.info("[LLM] usando GROQ")
            return GroqProvider()
    except Exception as e:
        logger.error(f"[GROQ ERROR] {str(e)}")

    try:
        if Config.has_openai():
            logger.info("[LLM] usando OPENAI")
            return OpenAIProvider()
    except Exception as e:
        logger.error(f"[OPENAI ERROR] {str(e)}")

    raise Exception("Nenhum provider disponível")

# =========================================================
# STREAM (com buffer e resposta estruturada)
# =========================================================
def stream_llm(prompt: str, provider="auto", system_prompt=""):
    provider_instance = get_provider(provider)
    logger.info(f"[LLM] provider={provider}")

    buffer = ""
    prov_name = provider_instance.__class__.__name__.lower()

    # acumula tokens
    for chunk in provider_instance.stream(prompt=prompt, system_prompt=system_prompt):
        if isinstance(chunk, tuple) and len(chunk) == 2:
            delta, prov = chunk
            prov_name = prov
        else:
            delta = chunk
        buffer += delta

    # tenta montar resposta estruturada
    response = PipelineService.build_response(buffer) or {}

    # sempre informa o provider
    yield {"provider": prov_name}

    prompt_lower = prompt.lower().strip()

    # decide o que mandar pro frontend
    if "gitlab" in prompt_lower and "github" in prompt_lower:
        yield {"gitlab": response.get("yaml_gitlab", buffer)}
        yield {"github": response.get("yaml_github", buffer)}
    elif "gitlab" in prompt_lower:
        yield {"gitlab": response.get("yaml_gitlab", buffer)}
    elif "github" in prompt_lower:
        yield {"github": response.get("yaml_github", buffer)}
    else:
        # fallback: manda ambos
        yield {"gitlab": response.get("yaml_gitlab", buffer)}
        yield {"github": response.get("yaml_github", buffer)}
