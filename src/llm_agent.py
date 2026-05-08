import logging
from pathlib import Path
from typing import Generator, Tuple
import yaml
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from config import Config

logger = logging.getLogger(__name__)

# =========================================================
# PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = (
    BASE_DIR.parent / "templates" / "pipelines"
).resolve()

# =========================================================
# TEMPLATES
# =========================================================
TEMPLATES = {
    "dotnet8": TEMPLATES_DIR / "dotnet" / "dotnet8.yml.j2",
    "dotnet9": TEMPLATES_DIR / "dotnet" / "dotnet9.yml.j2",
    "java": TEMPLATES_DIR / "java" / "java21.yml.j2",
    "python": TEMPLATES_DIR / "python" / "python312.yml.j2",
    "terraform": TEMPLATES_DIR / "terraform" / "terraform.yml.j2",
}

# =========================================================
# JINJA
# =========================================================
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    trim_blocks=True,
    lstrip_blocks=True
)

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

# =========================================================
# STACK DETECTION
# =========================================================
def detect_stack(prompt: str) -> str:

    p = prompt.lower()

    if "dotnet 8" in p:
        return "dotnet8"

    if "dotnet 9" in p:
        return "dotnet9"

    if "java" in p:
        return "java"

    if "python" in p:
        return "python"

    if "terraform" in p:
        return "terraform"

    return "unknown"


# =========================================================
# TEMPLATE RENDER
# =========================================================
def render_template(path: Path) -> str:

    try:

        rel = path.relative_to(TEMPLATES_DIR)

        template_name = rel.as_posix()

        logger.info(
            f"[LOAD] carregando template: {template_name}"
        )

        return env.get_template(
            template_name
        ).render()

    except TemplateNotFound as e:

        logger.error(
            f"[ERROR] template nao encontrado: {e}"
        )

        raise

    except Exception as e:

        logger.exception(
            f"[ERROR] falha ao renderizar template: {e}"
        )

        raise


# =========================================================
# YAML VALIDATION
# =========================================================
def clean_llm_output(text: str) -> str:

    return (
        text
        .replace("```yaml", "")
        .replace("```", "")
        .strip()
    )


def is_valid_yaml(text: str) -> bool:

    try:

        yaml.safe_load(text)

        return True

    except Exception:

        return False


# =========================================================
# LOCAL PROVIDER
# =========================================================
def stream_local(prompt: str):

    stack = detect_stack(prompt)

    logger.info(
        f"[STACK] detectada: {stack}"
    )

    if stack in TEMPLATES:

        logger.info(
            f"[TEMPLATE] usando template local: {stack}"
        )

        try:

            content = render_template(
                TEMPLATES[stack]
            )

        except Exception:

            logger.warning(
                "[FALLBACK] erro template local"
            )

            content = """
stages:
  - build

build:
  stage: build
  script:
    - echo "fallback local"
"""

    else:

        logger.warning(
            "[FALLBACK] stack desconhecida"
        )

        content = """
stages:
  - build

build:
  stage: build
  script:
    - echo "fallback local"
"""

    for c in content:
        yield c, "local"


# =========================================================
# OPENAI/GROQ STREAM
# =========================================================
def stream_provider(
    client,
    model,
    prompt,
    provider
):

    stream = client.chat.completions.create(
        model=model,
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

    for chunk in stream:

        delta = chunk.choices[0].delta.content

        if delta:
            yield delta, provider


# =========================================================
# PROVIDERS
# =========================================================
def get_openai():

    return OpenAI(
        api_key=Config.openai_key()
    )


def get_groq():

    return OpenAI(
        api_key=Config.groq_key(),
        base_url="https://api.groq.com/openai/v1"
    )


# =========================================================
# MAIN
# =========================================================
def stream_llm(
    prompt: str,
    provider: str = "auto"
):

    logger.info(
        f"[INFO] provider selecionado: {provider}"
    )

    # =====================================================
    # LOCAL
    # =====================================================
    if provider == "local":

        logger.info(
            "[LOCAL] provider LOCAL"
        )

        yield from stream_local(prompt)

        return

    # =====================================================
    # GROQ
    # =====================================================
    if provider == "groq":

        logger.info(
            "[GROQ] provider GROQ"
        )

        yield from stream_provider(
            get_groq(),
            "llama-3.3-70b-versatile",
            prompt,
            "groq"
        )

        return

    # =====================================================
    # OPENAI
    # =====================================================
    if provider == "openai":

        logger.info(
            "[OPENAI] provider OPENAI"
        )

        yield from stream_provider(
            get_openai(),
            "gpt-4o-mini",
            prompt,
            "openai"
        )

        return

    # =====================================================
    # AUTO
    # =====================================================
    providers = [

        (
            "groq",
            lambda: stream_provider(
                get_groq(),
                "llama-3.3-70b-versatile",
                prompt,
                "groq"
            )
        ),

        (
            "openai",
            lambda: stream_provider(
                get_openai(),
                "gpt-4o-mini",
                prompt,
                "openai"
            )
        )
    ]

    for name, fn in providers:

        try:

            logger.info(
                f"[TRY] tentando {name}"
            )

            full = ""
            buffer = []

            for chunk, prov in fn():

                full += chunk

                buffer.append(
                    (chunk, prov)
                )

            cleaned = clean_llm_output(full)

            if not is_valid_yaml(cleaned):

                raise Exception(
                    "YAML invalido"
                )

            for item in buffer:
                yield item

            logger.info(
                f"[OK] provider {name}"
            )

            return

        except Exception as e:

            logger.warning(
                f"[ERROR] provider {name}: {e}"
            )

    # =====================================================
    # FALLBACK LOCAL
    # =====================================================
    logger.warning(
        "[FALLBACK] usando LOCAL"
    )

    yield from stream_local(prompt)