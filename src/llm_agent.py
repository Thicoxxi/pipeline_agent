import logging
from pathlib import Path

import yaml
from openai import OpenAI, RateLimitError
from jinja2 import Environment, FileSystemLoader

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
# STREAM
# -----------------------------
def _stream(client, model: str, prompt: str, provider: str):
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

    except RateLimitError:
        logger.warning(f"{provider} sem quota")
        raise RuntimeError("quota_exceeded")

    except Exception as e:
        logger.warning(f"{provider} erro: {e}")
        raise RuntimeError("provider_error")


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
# ORQUESTRADOR
# -----------------------------
def stream_llm(prompt: str):
    providers = []

    if Config.has_openai():
        providers.append(stream_openai)

    if Config.has_groq():
        providers.append(stream_groq)

    providers.append(stream_local)

    for fn in providers:
        try:
            logger.info(f"Tentando: {fn.__name__}")
            for chunk, prov in fn(prompt):
                yield chunk, prov
            return
        except Exception as e:
            if "quota" in str(e):
                logger.info(f"{fn.__name__} sem crédito")
            else:
                logger.warning(f"{fn.__name__} falhou")

    for chunk, prov in stream_local(prompt):
        yield chunk, prov