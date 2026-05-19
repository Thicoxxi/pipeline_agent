import logging

from groq import Groq
import groq as groq_lib
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
        # Tentativas com redução progressiva do tamanho máximo de saída.
        # Se o Groq retornar 400 pedindo para reduzir comprimento, tentamos novamente
        # com valores menores de max_output_tokens e, se necessário, um system prompt reduzido.
        attempts = [2048, 1024, 512]
        last_exc = None


        for max_tokens in attempts:
            try:
                # Ajustar prompts conforme a tentativa — não passamos max_output_tokens
                effective_system = system_prompt
                effective_prompt = prompt

                if max_tokens <= 1024:
                    effective_system = (
                        "Você é um engenheiro DevOps especialista em CI/CD. Retorne APENAS YAML puro, sem explicações."
                    )

                # Truncar prompt do usuário se estiver muito longo
                # usar os últimos caracteres para manter contexto relevante (caminho, instruções)
                if len(effective_prompt) > max_tokens * 2:
                    effective_prompt = effective_prompt[-(max_tokens * 2):]

                completion = self.client.chat.completions.create(
                    model=self.model,
                    stream=True,
                    temperature=0.2,
                    messages=[
                        {"role": "system", "content": effective_system},
                        {"role": "user", "content": effective_prompt},
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

                return

            except groq_lib.BadRequestError as e:
                logger.warning(f"[GROQ] BadRequestError on attempt with max_tokens_hint={max_tokens}: {e}")
                last_exc = e
                continue
            except Exception as e:
                logger.exception("[GROQ] erro inesperado no stream")
                last_exc = e
                break

        # se nenhuma tentativa obteve sucesso, propagar a última exceção
        if last_exc:
            raise last_exc
