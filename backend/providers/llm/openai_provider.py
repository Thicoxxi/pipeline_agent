import logging

from openai import OpenAI

from core.config import Config

from providers.llm.base import (
    BaseProvider
)

logger = logging.getLogger(__name__)

# =========================================================
# SYSTEM PROMPT
# =========================================================
SYSTEM_PROMPT = """
Você é um engenheiro DevOps SRE especialista em CI/CD.

Sua tarefa é gerar pipelines profissionais,
seguras e funcionais.

REGRAS OBRIGATÓRIAS:

1. Retorne APENAS YAML puro
2. NÃO use markdown
3. NÃO use ``` ou qualquer formatação extra
4. NÃO explique nada
5. NÃO adicione texto antes ou depois do YAML

OBJETIVO:

- Se o usuário NÃO especificar plataforma:
  gere GitLab CI (.gitlab-ci.yml)

- Se o usuário mencionar:
  github, actions ou workflow
  gere GitHub Actions

PADRÕES:

GitLab:
- usar stages
- jobs build/test/deploy
- usar image adequada
- scripts reais

GitHub:
- name
- on
- jobs
- runs-on: ubuntu-latest
- steps uses/run

QUALIDADE:
- YAML válido
- pronto para produção
""".strip()


class OpenAIProvider(BaseProvider):

    def __init__(self):

        self.client = OpenAI(
            api_key=Config.openai_key()
        )

        self.model = "gpt-4o-mini"

    def stream(
        self,
        prompt: str
    ):

        logger.info(
            "[OPENAI] iniciando stream"
        )

        stream = (
            self.client.chat.completions.create(

                model=self.model,

                stream=True,

                temperature=0.1,

                messages=[

                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        )

        for chunk in stream:

            delta = (
                chunk
                .choices[0]
                .delta
                .content
            )

            if delta:

                yield delta, "openai"