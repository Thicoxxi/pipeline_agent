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


# =========================================================
# PROVIDER
# =========================================================
class GroqProvider:

    name = "groq"

    def __init__(self):
        if not Config.GROQ_API_KEY:
            raise Exception("GROQ_API_KEY nao configurada")

        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    # =====================================================
    # STREAM
    # =====================================================
    def stream(self, prompt, system_prompt=None):
        logger.info("[GROQ] iniciando stream")

        system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

        completion = self.client.chat.completions.create(
            model=self.model,
            stream=True,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )

        for chunk in completion:
            try:
                content = chunk.choices[0].delta.content
                if content:
                    # remove qualquer ``` que o modelo insista em gerar
                    if content.strip().startswith("```"):
                        continue
                    yield content
            except Exception:
                continue
