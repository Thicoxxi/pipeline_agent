#!/bin/bash

echo "🚀 Configurando ambiente..."

# Garante permissões SSH (caso venha do host)
chmod 700 ~/.ssh 2>/dev/null || true
chmod 600 ~/.ssh/* 2>/dev/null || true

# Atualiza pip
python -m pip install --upgrade pip

# Cria virtualenv automaticamente
if [ ! -d ".venv" ]; then
  echo "📦 Criando virtualenv..."
  python -m venv .venv
fi

# Ativa venv
source .venv/bin/activate

# Instala dependências
pip install -r requirements.txt

# Git sanity check
git --version

echo "✅ Ambiente pronto!"