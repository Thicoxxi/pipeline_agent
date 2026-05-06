import logging
from pathlib import Path
from typing import Generator, Tuple

import yaml
from openai import OpenAI, RateLimitError
from jinja2 import Environment, FileSystemLoader

from config import Config

logger = logging.getLogger(__name__)

# -----------------------------
# TEMPLATES
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR.parent / "templates" / "pipelines"

TEMPLATES = {
    "dotnet8": TEMPLATES_DIR / "dotnet" / "dotnet8.yml.j2",
    "dotnet9": TEMPLATES_DIR / "dotnet" / "dotnet9.yml.j2",
    "java": TEMPLATES_DIR / "java" / "java21.yml.j2",
    "python": TEMPLATES_DIR / "python" / "python312.yml.j2",
    "terraform": TEMPLATES_DIR / "terraform" / "terraform.yml.j2",
}

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    trim_blocks=True,
    lstrip_blocks=True
)

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
""".strip()

# -----------------------------
# STACK DETECTION
# -----------------------------
def detect_stack(prompt: str) -> str:
    p = prompt.lower()
    if "dotnet 8" in p: return "dotnet8"
    if "dotnet 9" in p: return "dotnet9"
    if "java" in p: return "java"
    if "python" in p: return "python"
    if "terraform" in p: return "terraform"
    return "unknown"


def render_template(path: Path) -> str:
    rel = path.relative_to(TEMPLATES_DIR)
    return env.get_template(str(rel)).render()


# -----------------------------
# LOCAL
# -----------------------------
def stream_local(prompt: str):
    stack = detect_stack(prompt)

    if stack in TEMPLATES:
        logger.info(f"🧠 Template local: {stack}")
        content = render_template(TEMPLATES[stack])
    else:
        content = """stages:
  - build

build:
  stage: build
  script:
    - echo "fallback local"
"""

    for c in content:
        yield c, "local"


# -----------------------------
# PROVIDERS
# -----------------------------
def stream_provider(client, model, prompt, provider):
    stream = client.chat.completions.create(
        model=model,
        stream=True,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta, provider


def get_openai():
    return OpenAI(api_key=Config.openai_key())


def get_groq():
    return OpenAI(
        api_key=Config.groq_key(),
        base_url="https://api.groq.com/openai/v1"
    )


# -----------------------------
# VALIDATION
# -----------------------------
def clean_llm_output(text: str) -> str:
    return text.replace("```yaml", "").replace("```", "").strip()


def is_valid_yaml(text: str) -> bool:
    try:
        yaml.safe_load(text)
        return True
    except:
        return False


# -----------------------------
# MAIN
# -----------------------------
def stream_llm(prompt: str, provider: str = "auto"):

    logger.info(f"📥 provider: {provider}")

    # =========================
    # FORÇADO
    # =========================
    if provider == "local":
        logger.info("🎯 LOCAL")
        yield from stream_local(prompt)
        return

    if provider == "groq":
        logger.info("🎯 GROQ")
        yield from stream_provider(get_groq(), "llama-3.3-70b-versatile", prompt, "groq")
        return

    if provider == "openai":
        logger.info("🎯 OPENAI")
        yield from stream_provider(get_openai(), "gpt-4o-mini", prompt, "openai")
        return

    # =========================
    # AUTO → GROQ > OPENAI > LOCAL
    # =========================
    providers = [
        ("groq", lambda: stream_provider(get_groq(), "llama-3.3-70b-versatile", prompt, "groq")),
        ("openai", lambda: stream_provider(get_openai(), "gpt-4o-mini", prompt, "openai")),
    ]

    for name, fn in providers:
        try:
            logger.info(f"🚀 tentando {name}")

            full = ""
            buffer = []

            for chunk, prov in fn():
                full += chunk
                buffer.append((chunk, prov))

            if not is_valid_yaml(clean_llm_output(full)):
                raise Exception("YAML inválido")

            for item in buffer:
                yield item

            logger.info(f"✅ {name}")
            return

        except Exception as e:
            logger.warning(f"❌ {name}: {e}")

    logger.warning("⚠️ fallback LOCAL")
    yield from stream_local(prompt)