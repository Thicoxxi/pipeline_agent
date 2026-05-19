# 🚀 Pipeline Generator AI

Aplicação web para geração automática de pipelines CI/CD utilizando IA, com suporte para:
# Pipeline Agent / Pipeline Generator AI

Resumo rápido
-
Projeto que reúne um backend Python (Flask) que orquestra provedores LLM (OpenAI, Groq, local) para gerar e analisar pipelines CI/CD, e uma extensão VS Code (`vscode-extension/pipeline-generator-ai`) que fornece uma interface de chat e comandos para gerar/abrir pipelines no editor.

Principais componentes
-
- `backend/` — Flask app que expõe endpoints:
  - `POST /api/stream` — stream SSE para geração incremental de pipelines
  - `POST /api/analyze-project` — analisa arquivos do projeto e retorna YAML da pipeline
  - `POST /api/log` — endpoint para receber logs da extensão e persistir em `backend/logs/app.log` / `backend/logs/error.log`
  - `core/logger.py` — logger com `app.log` e `error.log` separados

- `vscode-extension/pipeline-generator-ai/` — extensão VS Code
  - comandos: `analyzeProject`, `generatePipeline`, `openChat`
  - `extension.js` — implementação do Webview chat, escaneamento do workspace e chamadas ao backend

Como rodar o backend (desenvolvimento)
-
1. Crie e ative um virtualenv (ex.: `.venv`) e instale dependências:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure variáveis de ambiente em `backend/.env` (ex.: `GROQ_API_KEY`, `OPENAI_API_KEY`, `GITHUB_TOKEN`, `GITLAB_TOKEN`).

3. Inicie o app:

```bash
python app.py
```

O servidor roda por padrão em `http://0.0.0.0:5000` e grava logs em `backend/logs/app.log` e `backend/logs/error.log`.

Como usar a extensão localmente
-
1. Abra a pasta `vscode-extension/pipeline-generator-ai` no VS Code.
2. Instale dependências da extensão (dentro da pasta da extensão):

```bash
cd vscode-extension/pipeline-generator-ai
npm install
```

3. Pressione F5 no VS Code para abrir um Extension Development Host. Certifique-se que o backend está em execução.

4. No Extension Host: use `Pipeline Generator AI: Open Chat` para abrir o webview, ou execute os comandos `Generate Pipeline` / `Analyze Project` via Command Palette.

Log forwarding
-
A extensão encaminha os `console.*` ao endpoint `POST /api/log` do backend, que grava as mensagens em `backend/logs/app.log` e mensagens `ERROR` em `backend/logs/error.log`.

Gerar o pacote `.vsix` (empacotar extensão)
-
Pré-requisitos: `node` e `npm` instalados. O projeto já inclui scripts em `vscode-extension/pipeline-generator-ai/package.json`.

1. Na pasta da extensão:

```bash
cd vscode-extension/pipeline-generator-ai
npm run package
# ou
npx vsce package --out pipeline-generator-ai-<version>.vsix
```

2. Teste instalando localmente no VS Code:

```bash
code --install-extension pipeline-generator-ai-<version>.vsix
```

Publicar no Visual Studio Marketplace
-
1. Crie um publisher no Marketplace e obtenha um Personal Access Token (PAT).
2. Faça login com `vsce` ou defina `VSCE_PAT`:

```bash
npx vsce login <publisher>
npx vsce publish
# ou com env var
export VSCE_PAT="<your_pat>"
npx vsce publish
```

Dicas e considerações
-
- Atualize `version` em `vscode-extension/pipeline-generator-ai/package.json` antes de publicar.
- Evite incluir segredos nos arquivos enviados ao backend — a extensão corta o conteúdo lido dos arquivos para evitar prompts enormes, mas revise o comportamento para dados sensíveis.
- Se encontrar erros do LLM (ex.: `Please reduce the length of the messages or completion`), o backend tenta re-tentar com prompts menores; você pode ajustar `providers/llm/groq_provider.py`.

Contribuições e troubleshooting
-
- Logs do backend: `backend/logs/app.log` e `backend/logs/error.log`.
- Se a extensão não abrir ou o comando falhar, verifique o Console do Extension Host (Help → Toggle Developer Tools → Console) e os logs do backend.
- Para dúvidas, abra uma issue no repositório ou me peça para rodar passos de diagnóstico.

---
Arquivo atualizado automaticamente pelo assistente de desenvolvimento.

- GitLab CI/CD
- GitHub Actions
- OpenAI
- Groq
- Templates locais
- Publicação automática em repositórios
- Analyzer inteligente de projetos
- VSCode Agents (Python e Node.js)
- Streaming SSE
- Logging centralizado

---

# ✨ Funcionalidades

## 🤖 Geração Inteligente de Pipelines

A aplicação utiliza modelos LLM para gerar pipelines profissionais automaticamente com base em prompts em linguagem natural.

Exemplos:

- Pipeline Python com pytest
- Pipeline Flask + Frontend JS
- Pipeline .NET 8/9
- Pipeline Terraform
- Pipeline Java Maven
- Pipeline Docker
- Pipeline GitHub Actions
- Pipeline GitLab CI

---

## 🔍 Analyzer Inteligente de Projetos

O projeto agora possui um analyzer inteligente capaz de:

- Detectar automaticamente stacks do projeto
- Identificar backend/frontend
- Detectar Flask, FastAPI, Django
- Detectar React, Vue, Next.js
- Detectar Docker, Terraform e Kubernetes
- Gerar pipeline real baseado no projeto inteiro
- Detectar testes e dependências
- Evitar falsos positivos de stacks

---

## 🔄 Providers Suportados

| Provider | Descrição |
|---|---|
| OpenAI | GPT-4o-mini |
| Groq | llama-3.3-70b-versatile |
| Local | Templates Jinja2 |
| Auto | Fallback automático |

---

# 🧠 Arquitetura

## Backend

Tecnologias utilizadas:

- Python
- Flask
- OpenAI SDK
- Groq SDK
- Requests
- Jinja2
- PyYAML
- Logging Rotativo

### Estrutura Backend

```text
backend/
├── api/
│   └── routes/
├── core/
├── providers/
│   ├── llm/
│   └── scm/
├── services/
├── static/
├── templates/
├── tools/
├── logs/
└── app.py
```

---

## Frontend

Tecnologias:

- HTML5
- CSS3
- JavaScript Vanilla
- SSE Streaming

### Recursos Frontend

- Layout moderno DevOps
- Separação GitLab/GitHub
- Streaming em tempo real
- Editor YAML
- Conversão GitLab → GitHub
- Download de pipelines
- Aplicação automática em repositórios

---

# 🔌 VSCode Agents

O projeto agora possui agents para terminal/VSCode.

## Python Agent

Arquivo:

```text
tools/vscode_agent.py
```

Recursos:

- análise automática de projeto
- integração com analyzer
- logs próprios
- suporte GitLab/GitHub
- comunicação SSE

---

## Node.js Agent

Arquivo:

```text
tools/vscode_agent.js
```

Recursos:

- streaming em tempo real
- integração GitHub
- logs automáticos
- suporte analyze/chat/github

---

# 🛠️ Logging

O sistema possui logging centralizado.

## Logs Backend

```text
logs/app.log
```

## Logs Agents

```text
logs/vscode_agent.log
logs/vscode_agent_js.log
```

Recursos:

- RotatingFileHandler
- Request ID
- Logs estruturados
- Rastreamento de erros

---

# 🌊 Streaming SSE

O backend utiliza Server Sent Events (SSE) para:

- streaming em tempo real
- respostas incrementais
- atualização dinâmica do frontend
- compatibilidade com frontend e VSCode agents

---

# 📁 Estrutura Recomendada

```text
project/
│
├── api/
├── core/
├── providers/
├── services/
├── static/
├── templates/
├── tools/
├── logs/
│
├── app.py
├── requirements.txt
├── .env
└── README.md
```

---

# ⚙️ Configuração

## 1. Criar ambiente virtual

```bash
python -m venv .venv
```

### Linux/macOS

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

---

## 2. Instalar dependências

```bash
pip install -r requirements.txt
```

---

# 🔐 Variáveis de Ambiente

Crie um arquivo `.env`:

```env
# OPENAI
OPENAI_API_KEY=your_openai_key

# GROQ
GROQ_API_KEY=your_groq_key

# GITHUB
GITHUB_TOKEN=your_github_token

# GITLAB
GITLAB_TOKEN=your_gitlab_token
GITLAB_URL=https://gitlab.com/api/v4
```

---

# ▶️ Executando

```bash
python app.py
```

Aplicação disponível em:

```text
http://localhost:5000
```

---

# 🔌 Endpoints

## Stream

```http
POST /api/stream
```

Body:

```json
{
  "prompt": "pipeline flask docker",
  "provider": "auto"
}
```

---

## Analyze Project

```http
POST /api/analyze-project
```

Body:

```json
{
  "platform": "gitlab",
  "provider": "auto",
  "files": []
}
```

---

## GitHub Apply

```http
POST /api/github/apply
```

---

## GitLab Apply

```http
POST /api/gitlab/apply
```

---

# 🧩 Funcionamento Interno

## Fluxo da aplicação

1. Usuário envia prompt
2. Backend seleciona provider
3. LLM gera pipeline
4. YAML é validado
5. Frontend recebe SSE
6. Usuário pode editar/publicar

---

## Fluxo do Analyzer

1. Scanner detecta arquivos
2. Sistema detecta stacks
3. Projeto é resumido
4. LLM analisa contexto completo
5. Pipeline profissional é gerado

---

# 🛡️ Melhorias Técnicas

- limpeza automática de JSON residual
- remoção de markdown inválido
- suporte SSE e RAW mode
- parser robusto
- fallback automático
- logs estruturados
- detecção inteligente de stacks

---

# 🔄 Fallback Inteligente

Modo `auto`:

1. Groq
2. OpenAI
3. Template Local

---

# 📦 Templates Locais

Templates disponíveis:

- Python
- Java
- Terraform
- .NET 8
- .NET 9

Renderizados via Jinja2.

---

# 🚀 Melhorias Futuras

- Monaco Editor
- Histórico de pipelines
- OAuth GitHub/GitLab
- Docker deploy
- Kubernetes deploy
- Marketplace de templates
- Multi-workflow
- Banco de dados

---

# 🐳 Docker

```dockerfile
FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
```

---

# 📋 Dependências

```txt
flask
openai
groq
requests
jinja2
pyyaml
python-dotenv
```

---

# 🔥 Destaques Técnicos

## Backend

- SSE Streaming
- Fallback inteligente
- Logging avançado
- Analyzer inteligente
- Integração REST APIs

## Frontend

- Interface responsiva
- Atualização em tempo real
- Conversão GitHub
- Download YAML
- Separação visual GitLab/GitHub

---

# 📄 Licença

MIT License

---

# 👨‍💻 Autor

Thiago Liberati
