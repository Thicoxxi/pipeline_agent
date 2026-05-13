import logging

from groq import Groq

from core.config import Config

logger = logging.getLogger(__name__)

# =========================================================
# DEFAULT PROMPT
# =========================================================
DEFAULT_SYSTEM_PROMPT = """
Você é um engenheiro DevOps SRE especialista em CI/CD.

Sua tarefa é gerar pipelines profissionais,
seguras e funcionais.

Retorne APENAS YAML puro.
""".strip()


# =========================================================
# PROVIDER
# =========================================================
class GroqProvider:

    name = "groq"

    def __init__(self):

        if not Config.GROQ_API_KEY:

            raise Exception(
                "GROQ_API_KEY nao configurada"
            )

        self.client = Groq(
            api_key=Config.GROQ_API_KEY
        )

        self.model = (
            "llama-3.3-70b-versatile"
        )

    # =====================================================
    # STREAM
    # =====================================================
    def stream(

        self,

        prompt,

        system_prompt=None
    ):

        logger.info(
            "[GROQ] iniciando stream"
        )

        system_prompt = (
            system_prompt
            or DEFAULT_SYSTEM_PROMPT
        )

        completion = (
            self.client.chat.completions.create(

                model=self.model,

                stream=True,

                temperature=0.2,

                messages=[

                    {
                        "role": "system",
                        "content": system_prompt
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        )

        for chunk in completion:

            try:

                content = (
                    chunk
                    .choices[0]
                    .delta
                    .content
                )

                if content:

                    yield content

            except Exception:

                continue