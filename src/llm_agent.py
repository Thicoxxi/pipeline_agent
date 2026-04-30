import os
import logging
from typing import Generator, Tuple
from pathlib import Path

import yaml
from openai import OpenAI
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

# -----------------------------
# CONFIGURAÇÃO DE TEMPLATES
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
# CLIENTES LLM
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
# DETECÇÃO DE STACK
# -----------------------------
def detect_stack(prompt: str) -> str:
    """
    Detecta a stack de tecnologia a partir do texto do prompt.

    Args:
        prompt (str): Texto fornecido pelo usuário descrevendo o projeto.

    Returns:
        str: Nome da stack detectada (ex: "dotnet10", "python", "java").
             Retorna "unknown" se nenhuma stack for identificada.
    """
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
    """
    Renderiza um template Jinja2 e retorna o conteúdo como string.

    Args:
        template_path (Path): Caminho para o arquivo de template.

    Returns:
        str: Conteúdo renderizado do template.
    """
    template = env.get_template(template_path.name)
    return template.render()


def stream_local(prompt: str) -> Generator[Tuple[str, str], None, None]:
    """
    Gera YAML a partir de templates locais.
    Caso a stack não seja reconhecida, retorna um fallback genérico.

    Args:
        prompt (str): Texto fornecido pelo usuário.

    Yields:
        Tuple[str, str]: Caracteres do YAML e o provider ("local").
    """
    stack = detect_stack(prompt)

    if stack in TEMPLATES:
        logging.info(f"Usando template local: {stack}")
        content = render_template(TEMPLATES[stack])

        for c in content:
            yield c, "local"
        return

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
# STREAMING DE RESPOSTAS LLM
# -----------------------------
def _stream(client, model: str, prompt: str, provider: str) -> Generator[Tuple[str, str], None, None]:
    """
    Função genérica para streaming de respostas de um LLM.

    Args:
        client (OpenAI): Cliente configurado (OpenAI ou Groq).
        model (str): Nome do modelo a ser utilizado.
        prompt (str): Texto fornecido pelo usuário.
        provider (str): Nome do provedor ("openai" ou "groq").

    Yields:
        Tuple[str, str]: Fragmentos do YAML e o nome do provider.
    """
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


def stream_openai(prompt: str) -> Generator[Tuple[str, str], None, None]:
    """
    Streaming usando OpenAI GPT-4o-mini.

    Args:
        prompt (str): Texto fornecido pelo usuário.

    Returns:
        Generator: Fragmentos do YAML e provider "openai".
    """
    return _stream(openai_client, "gpt-4o-mini", prompt, "openai")


def stream_groq(prompt: str) -> Generator[Tuple[str, str], None, None]:
    """
    Streaming usando Groq LLaMA 3.3.

    Args:
        prompt (str): Texto fornecido pelo usuário.

    Returns:
        Generator: Fragmentos do YAML e provider "groq".
    """
    return _stream(groq_client, "llama-3.3-70b-versatile", prompt, "groq")


# -----------------------------
# VALIDAÇÃO DE YAML
# -----------------------------
def is_valid_yaml(content: str) -> bool:
    """
    Verifica se o conteúdo fornecido é um YAML válido.

    Args:
        content (str): Texto YAML a ser validado.

    Returns:
        bool: True se o YAML for válido e não vazio, False caso contrário.
    """
    try:
        yaml.safe_load(content)
        return len(content.strip()) > 20
    except Exception:
        return False


# -----------------------------
# ORQUESTRADOR
# -----------------------------
def stream_llm(prompt: str, provider: str = "auto") -> Generator[Tuple[str, str], None, None]:
    """
    Orquestra a geração de YAML utilizando múltiplos providers.

    Args:
        prompt (str): Texto fornecido pelo usuário.
        provider (str, optional): Provider específico ("openai", "groq", "local").
                                  Se "auto", tenta todos em ordem de prioridade.

    Yields:
        Tuple[str, str]: Fragmentos do YAML e o provider utilizado.
    """
    if provider == "openai":
        providers = [stream_openai]
    elif provider == "groq":
        providers = [stream_groq]
    elif provider == "local":
        providers = [stream_local]
    else:
        providers = [stream_openai, stream_groq, stream_local]

    last_error = None

    for fn in providers:
        try:
            logging.info(f"Tentando: {fn.__name__}")

            full = ""

            for chunk, prov in fn(prompt):
                full += chunk
                yield chunk, prov

            if not is_valid_yaml(full):
                raise RuntimeError("YAML inválido ou vazio")

            logging.info(f"Sucesso com {fn.__name__}")
            return

        except Exception as e:
            last_error = e
            logging.warning(f"{fn.__name__} falhou: {e}")

    logging.error("Todos providers falharam")

    for chunk, prov in stream_local(prompt):
        yield chunk, prov
