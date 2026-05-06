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
    "dotnet10": TEMPLATES_DIR / "dotnet" / "dotnet10.yml.j2",
    "dotnetfx": TEMPLATES_DIR / "dotnet" / "dotnetfx.yml.j2",
    "java": TEMPLATES_DIR / "java" / "java21.yml.j2",
    "python": TEMPLATES_DIR / "python" / "python312.yml.j2",
    "terraform": TEMPLATES_DIR / "terraform" / "terraform.yml.j2",
}

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    trim_blocks=True,
    lstrip_blocks=True
)

# -----------------------------
# SYSTEM PROMPT (SEU MODELO)
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
""".strip()

# -----------------------------
# STACK DETECTION
# -----------------------------
def detect_stack(prompt: str) -> str:
    p = prompt.lower()
    if "dotnet 10" in p or "net 10" in p:
        return "dotnet10"
    if "dotnet 9" in p or "net 9" in p:
        return "dotnet9"
    if "dotnet 8" in p or "net 8" in p:
        return "dotnet8"
    if ".net framework" in p:
        return "dotnetfx"
    if "java" in p:
        return "java"
    if "python" in p:
        return "python"
    if "terraform" in p:
        return "terraform"
    return "unknown"


def render_template(path: Path) -> str:
    rel = path.relative_to(TEMPLATES_DIR)
    return env.get_template(str(rel).replace("\\", "/")).render()

# -----------------------------
# LOCAL PROVIDER
# -----------------------------
def stream_local(prompt: str) -> Generator[Tuple[str, str], None, None]:
    stack = detect_stack(prompt)

    if stack in TEMPLATES:
        logger.info(f"🧠 Template local: {stack}")
        content = render_template(TEMPLATES[stack])

        for c in content:
            yield c, "local"
        return

    logger.info("⚠️ fallback local genérico")

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
# LLM STREAM
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

# -----------------------------
# CLIENTES
# -----------------------------
def get_openai():
    return OpenAI(api_key=Config.openai_key())


def get_groq():
    return OpenAI(
        api_key=Config.groq_key(),
        base_url="https://api.groq.com/openai/v1"
    )

# -----------------------------
# LIMPEZA E VALIDAÇÃO
# -----------------------------
def clean_llm_output(text: str) -> str:
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            return parts[1].replace("yaml", "").replace("yml", "").strip()
    return text.strip()


def is_valid_yaml(text: str) -> bool:
    try:
        cleaned = clean_llm_output(text)
        parsed = yaml.safe_load(cleaned)
        return isinstance(parsed, dict) and len(cleaned) > 20
    except Exception:
        return False

# -----------------------------
# ORQUESTRADOR
# -----------------------------
def stream_llm(prompt: str, provider: str = "auto"):

    # -----------------------------
    # FORÇADO
    # -----------------------------
    if provider == "local":
        logger.info("🎯 FORÇADO: local")
        yield from stream_local(prompt)
        return

    if provider == "groq":
        logger.info("🎯 FORÇADO: groq")
        yield from stream_provider(
            get_groq(),
            "llama-3.3-70b-versatile",
            prompt,
            "groq"
        )
        return

    if provider == "openai":
        logger.info("🎯 FORÇADO: openai")
        yield from stream_provider(
            get_openai(),
            "gpt-4o-mini",
            prompt,
            "openai"
        )
        return

    # -----------------------------
    # AUTO (LLM PRIMEIRO)
    # -----------------------------
    providers = []

    if Config.has_groq():
        providers.append(("groq", lambda: stream_provider(
            get_groq(),
            "llama-3.3-70b-versatile",
            prompt,
            "groq"
        )))

    if Config.has_openai():
        providers.append(("openai", lambda: stream_provider(
            get_openai(),
            "gpt-4o-mini",
            prompt,
            "openai"
        )))

    last_error = None

    for name, fn in providers:
        try:
            logger.info(f"🚀 Tentando {name}")

            full = ""
            buffer = []

            for chunk, prov in fn():
                full += chunk
                buffer.append((chunk, prov))

            cleaned = clean_llm_output(full)

            if not is_valid_yaml(cleaned):
                raise RuntimeError("YAML inválido")

            for item in buffer:
                yield item

            logger.info(f"✅ {name} sucesso")
            return

        except RateLimitError:
            logger.warning(f"{name} sem quota")

        except Exception as e:
            last_error = e
            logger.warning(f"{name} falhou: {e}")

    # -----------------------------
    # FALLBACK LOCAL
    # -----------------------------
    logger.warning("⚠️ Todos LLMs falharam → usando LOCAL")

    yield from stream_local(prompt)