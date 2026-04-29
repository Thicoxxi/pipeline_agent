import os
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Inicializa clientes com as variáveis de ambiente
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

def stream_openai(prompt):
    stream = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        stream=True,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta, "openai"

def stream_groq(prompt):
    stream = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        stream=True,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta, "groq"

def stream_local(prompt):
    yaml = """stages:
  - build
  - test

build:
  stage: build
  script:
    - echo "build..."

test:
  stage: test
  script:
    - echo "test..."
"""
    for c in yaml:
        yield c, "local"

def stream_llm(prompt, provider="auto"):

    if provider == "openai":
        yield from stream_openai(prompt)
        return

    if provider == "groq":
        yield from stream_groq(prompt)
        return

    if provider == "local":
        yield from stream_local(prompt)
        return

    try:
        print("🤖 OpenAI...")
        yield from stream_openai(prompt)
        return
    except Exception as e:
        print("⚠️ OpenAI falhou:", e)

    try:
        print("⚡ Groq...")
        yield from stream_groq(prompt)
        return
    except Exception as e:
        print("⚠️ Groq falhou:", e)

    print("🧠 Local fallback")
    yield from stream_local(prompt)
