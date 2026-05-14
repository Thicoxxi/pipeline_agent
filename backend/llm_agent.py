import logging

from providers.llm.factory import (
    get_provider
)

logger = logging.getLogger(__name__)


# =========================================================
# STREAM LLM
# =========================================================
def stream_llm(
    prompt: str,
    provider="auto"
):

    logger.info(
        f"[LLM] provider={provider}"
    )

    prompt_lower = (
        prompt.lower().strip()
    )

    provider_instance = (
        get_provider(provider)
    )

    # =====================================================
    # GITLAB EXPLÍCITO
    # =====================================================
    if "gitlab" in prompt_lower:

        yaml = ""

        for chunk in provider_instance.stream(
            prompt
        ):
            yaml += chunk

        yield {
            "gitlab": yaml
        }

        return

    # =====================================================
    # GITHUB EXPLÍCITO
    # =====================================================
    if (
        "github" in prompt_lower
        or
        "actions" in prompt_lower
    ):

        yaml = ""

        for chunk in provider_instance.stream(
            prompt
        ):
            yaml += chunk

        yield {
            "github": yaml
        }

        return

    # =====================================================
    # GENÉRICO
    # =====================================================

    # -----------------------------
    # GITLAB
    # -----------------------------
    gitlab_yaml = ""

    for chunk in provider_instance.stream(
        f"gitlab ci pipeline: {prompt}"
    ):
        gitlab_yaml += chunk

    yield {
        "gitlab": gitlab_yaml
    }

    # -----------------------------
    # GITHUB
    # -----------------------------
    github_yaml = ""

    for chunk in provider_instance.stream(
        f"github actions workflow: {prompt}"
    ):
        github_yaml += chunk

    yield {
        "github": github_yaml
    }