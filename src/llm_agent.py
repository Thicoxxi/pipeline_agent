import os
import logging
from typing import Generator, Tuple
from pathlib import Path

import yaml
from openai import OpenAI
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

load_dotenv()
logging.basicConfig(level=logging.INFO)

# -----------------------------
# CONFIG
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

TEMPLATES = {
    "dotnet8": BASE_DIR / "dotnet8.yml.j2",
    "dotnet9": BASE_DIR / "dotnet9.yml.j2",
    "dotnet10": BASE_DIR / "dotnet10.yml.j2",
    "dotnetfx": BASE_DIR / "dotnetfx.yml.j2",
    "java": BASE_DIR / "java21.yml.j2",
    "python": BASE_DIR / "python312.yml.j2",
    "terraform": BASE_DIR / "terraform.yml.j2",
}

env = Environment(
    loader=FileSystemLoader(str(BASE_DIR)),
    trim_blocks=True,
    lstrip_blocks=True
)

# -----------------------------
# CLIENTS
# -----------------------------
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """
Você é especialista em GitLab CI.

RETORNE APENAS YAML VÁLIDO.
SEM explicações.
SEM markdown.
SEM ```.

Apenas o conteúdo do arquivo .gitlab-ci.yml.
"""

# -----------------------------
# TEMPLATE (LOCAL)
# -----------------------------
def detect_stack(prompt: str) -> str:
    p = prompt.lower()

    if "dotnet 10" in p or "net 10" in p:
        return "dotnet10"
    if "dotnet 9" in p or "net 9" in p:
        return "dotnet9"
    if "dotnet 8" in p or "net 8" in p:
        return "dotnet8"
    if ".net framework" in p or "4.8" in p:
        return "dotnetfx"
    if "java" in p:
        return "java"
    if "python" in p:
        return "python"
    if "terraform" in p:
        return "terraform"

    return "unknown"


def render_template(template_path: Path) -> str:
    template = env.get_template(template_path.name)
    return template.render()


def stream_local(prompt):
    stack = detect_stack(prompt)

    if stack in TEMPLATES:
        logging.info(f"Usando template local: {stack}")
        content = render_template(TEMPLATES[stack])

        for c in content:
            yield c, "local"
        return

    # fallback local genérico
    yaml_fallback = """stages:
  - build

build:
  stage: build
  script:
    - echo "fallback local"
"""
    for c in yaml_fallback:
        yield c, "local"


# -----------------------------
# CORE STREAM LLM
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

    except Exception as e:
        logging.exception(f"{provider} falhou")
        raise RuntimeError(f"{provider} error: {e}")


def stream_openai(prompt):
    return _stream(openai_client, "gpt-4o-mini", prompt, "openai")


def stream_groq(prompt):
    return _stream(groq_client, "llama-3.3-70b-versatile", prompt, "groq")


# -----------------------------
# VALIDAÇÃO
# -----------------------------
def is_valid_yaml(content: str) -> bool:
    try:
        yaml.safe_load(content)
        return len(content.strip()) > 20
    except Exception:
        return False


# -----------------------------
# ORCHESTRATOR
# -----------------------------
def stream_llm(prompt, provider="auto"):

    if provider == "openai":
        providers = [stream_openai]

    elif provider == "groq":
        providers = [stream_groq]

    elif provider == "local":
        providers = [stream_local]

    else:
        # 🔥 PRIORIDADE LLM
        providers = [
            stream_openai,
            stream_groq,
            stream_local
        ]

    last_error = None

    for fn in providers:
        try:
            logging.info(f"Tentando: {fn.__name__}")

            full = ""

            for chunk, prov in fn(prompt):
                full += chunk
                yield chunk, prov

            # 🔥 VALIDAÇÃO REAL (ESSENCIAL)
            if not is_valid_yaml(full):
                raise RuntimeError("YAML inválido ou vazio")

            logging.info(f"Sucesso com {fn.__name__}")
            return

        except Exception as e:
            last_error = e
            logging.warning(f"{fn.__name__} falhou: {e}")

    # fallback final garantido (local)
    logging.error("Todos providers falharam")

    for chunk, prov in stream_local(prompt):
        yield chunk, prov