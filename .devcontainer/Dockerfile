FROM mcr.microsoft.com/devcontainers/python:3.11

WORKDIR /workspace

# Instala ferramentas essenciais
RUN apt-get update && apt-get install -y \
    git \
    openssh-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configuração SSH (evita prompt)
RUN mkdir -p /home/vscode/.ssh \
    && chmod 700 /home/vscode/.ssh \
    && ssh-keyscan github.com >> /home/vscode/.ssh/known_hosts \
    && ssh-keyscan gitlab.com >> /home/vscode/.ssh/known_hosts

# Copia requirements
COPY requirements.txt /workspace/requirements.txt

# Instala dependências
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r /workspace/requirements.txt

# Copia projeto
COPY . /workspace

# Ajusta permissões
RUN chown -R vscode:vscode /workspace \
    && chmod -R 775 /workspace \
    && chmod +x /workspace/.devcontainer/post-create.sh \
    && ./.devcontainer/post-create.sh

# Define usuário
USER vscode