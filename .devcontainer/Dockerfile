FROM mcr.microsoft.com/devcontainers/python:3.11

WORKDIR /workspace

# Agora funciona porque o context é a raiz do projeto
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt