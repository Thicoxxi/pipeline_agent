import logging
import time

from openai import OpenAI, RateLimitError

from config import Config

logger = logging.getLogger(__name__)

# -----------------------------
# PROMPT PROFISSIONAL
# -----------------------------
SYSTEM_PROMPT = """
Você é um engenheiro DevOps SRE especialista em CI/CD.

Sua tarefa é gerar pipelines profissionais, seguras e funcionais.

REGRAS OBRIGATÓRIAS:

1. Retorne APENAS YAML puro
2. NÃO use markdown
3. NÃO use ``` ou qualquer formatação extra
4. NÃO explique nada
5. NÃO adicione texto antes ou depois do YAML

OBJETIVO:

- Se o usuário NÃO especificar plataforma:
  → gere um pipeline GitLab CI (.gitlab-ci.yml)

- Se o usuário mencionar "github", "actions" ou "workflow":
  → gere um GitHub Actions workflow

PADRÕES:

GitLab:
- usar stages
- jobs: build, test, deploy
- usar image adequada
- scripts reais

GitHub:
- name, on, jobs
- runs-on: ubuntu-latest
- steps com uses/run

QUALIDADE:
- YAML válido
- pronto para produção
"""

# -----------------------------
# CIRCUIT BREAKER
# -----------------------------
PROVIDER_STATE = {
    "openai": {"failures": 0, "blocked_until": 0},
    "groq": {"failures": 0, "blocked_until": 0},
}

FAIL_THRESHOLD = 2
BLOCK_TIME = 30  # segundos


def is_available(provider: str) -> bool:
    state = PROVIDER_STATE[provider]
    return time.time() > state["blocked_until"]


def mark_failure(provider: str):
    state = PROVIDER_STATE[provider]
    state["failures"] += 1

    if state["failures"] >= FAIL_THRESHOLD:
        state["blocked_until"] = time.time() + BLOCK_TIME
        logger.warning(f"{provider} bloqueado por {BLOCK_TIME}s")


def mark_success(provider: str):
    state = PROVIDER_STATE[provider]
    state["failures"] = 0
    state["blocked_until"] = 0


# -----------------------------
# CLIENTES
# -----------------------------
def get_openai_client():
    key = Config.openai_key()
    if not key:
        raise RuntimeError("openai_not_configured")
    return OpenAI(api_key=key)


def get_groq_client():
    key = Config.groq_key()
    if not key:
        raise RuntimeError("groq_not_configured")
    return OpenAI(
        api_key=key,
        base_url="https://api.groq.com/openai/v1"
    )


# -----------------------------
# STREAM BASE COM RETRY
# -----------------------------
def _stream(client, model: str, prompt: str, provider: str):
    if provider != "local" and not is_available(provider):
        raise RuntimeError("provider_blocked")

    retries = 2

    for attempt in range(retries + 1):
        try:
            stream = client.chat.completions.create(
                model=model,
                stream=True,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta, provider

            mark_success(provider)
            return

        except RateLimitError:
            logger.warning(f"{provider} sem quota")
            mark_failure(provider)
            raise RuntimeError("quota_exceeded")

        except Exception as e:
            logger.warning(f"{provider} erro tentativa {attempt+1}: {e}")

            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
                continue

            mark_failure(provider)
            raise RuntimeError("provider_error")


# -----------------------------
# PROVIDERS
# -----------------------------
def stream_openai(prompt: str):
    return _stream(get_openai_client(), "gpt-4o-mini", prompt, "openai")


def stream_groq(prompt: str):
    return _stream(get_groq_client(), "llama-3.3-70b-versatile", prompt, "groq")


def stream_local(prompt: str):
    fallback = """stages:
  - build

build:
  stage: build
  script:
    - echo "fallback local"
"""
    for c in fallback:
        yield c, "local"


# -----------------------------
# ORQUESTRADOR INTELIGENTE
# -----------------------------
def stream_llm(prompt: str):

    providers = []

    # prioridade dinâmica (Groq primeiro)
    if Config.has_groq():
        providers.append(("groq", stream_groq))

    if Config.has_openai():
        providers.append(("openai", stream_openai))

    providers.append(("local", stream_local))

    for name, fn in providers:

        if name != "local" and not is_available(name):
            logger.info(f"{name} pulado (bloqueado)")
            continue

        try:
            logger.info(f"Tentando: {name}")

            started = False

            for chunk, prov in fn(prompt):
                started = True
                yield chunk, prov

            if started:
                logger.info(f"{name} sucesso")
                mark_success(name)
                return

        except Exception as e:
            msg = str(e)

            if "quota" in msg:
                logger.info(f"{name} sem crédito")
            elif "blocked" in msg:
                logger.info(f"{name} bloqueado")
            elif "not_configured" in msg:
                logger.info(f"{name} não configurado")
            else:
                logger.warning(f"{name} falhou: {msg}")

    # fallback garantido
    logger.info("Fallback local ativado")

    for chunk, prov in stream_local(prompt):
        yield chunk, prov