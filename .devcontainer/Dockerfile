FROM mcr.microsoft.com/devcontainers/python:3.11

WORKDIR /workspace

# Copia requirements da raiz do projeto
COPY ../requirements.txt /workspace/requirements.txt

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r /workspace/requirements.txt

# Copia o projeto inteiro
COPY .. /workspace