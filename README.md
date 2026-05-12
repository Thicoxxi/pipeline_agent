# 🚀 Pipeline Generator AI

Aplicação web para geração automática de pipelines CI/CD utilizando IA, com suporte para:

- GitLab CI/CD
- GitHub Actions
- OpenAI
- Groq
- Templates locais
- Publicação automática em repositórios

---

# ✨ Funcionalidades

## 🤖 Geração Inteligente de Pipelines

A aplicação utiliza modelos LLM para gerar pipelines profissionais automaticamente com base em prompts em linguagem natural.

Exemplos:

- Pipeline Python com pytest
- Pipeline .NET 9
- Pipeline Terraform
- Pipeline Java Maven
- Pipeline Docker
- Pipeline GitHub Actions
- Pipeline GitLab CI

---

## 🔄 Providers Suportados

A aplicação possui suporte para múltiplos providers:

| Provider | Descrição |
|---|---|
| OpenAI | Utiliza GPT-4o-mini |
| Groq | Utiliza llama-3.3-70b-versatile |
| Local | Utiliza templates Jinja locais |
| Auto | Faz fallback automático entre providers |

---

# 🧠 Arquitetura

## Backend

Tecnologias utilizadas:

- Python
- Flask
- OpenAI SDK
- Jinja2
- PyYAML
- Requests

Principais arquivos:

| Arquivo | Responsabilidade |
|---|---|
| `app.py` | API Flask principal |
| `llm_agent.py` | Integração com IA |
| `config.py` | Configurações e variáveis |
| `gitlab_client.py` | Integração GitLab |
| `github_client.py` | Integração GitHub |

---

## Frontend

Tecnologias:

- HTML5
- CSS3
- JavaScript Vanilla

Principais arquivos:

| Arquivo | Responsabilidade |
|---|---|
| `index.html` | Estrutura principal |
| `chat.css` | Interface visual |
| `chat.js` | Lógica frontend |

---

# 🎨 Interface

A aplicação possui:

- Layout moderno estilo DevOps Dashboard
- Separação visual GitLab/GitHub
- Editor YAML integrado
- Validação automática YAML
- Conversão GitLab → GitHub Actions
- Download dos pipelines
- Aplicação automática nos repositórios

---

# 📁 Estrutura Recomendada

```text
project/
│
├── app/
│   ├── app.py
│   ├── llm_agent.py
│   ├── config.py
│   ├── gitlab_client.py
│   └── github_client.py
│
├── templates/
│   ├── index.html
│   └── pipelines/
│
├── static/
│   ├── chat.css
│   └── chat.js
│
├── logs/
│
├── .env
├── requirements.txt
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

# GITLAB
GITLAB_TOKEN=your_gitlab_token
GITLAB_URL=https://gitlab.com/api/v4

# GITHUB
GITHUB_TOKEN=your_github_token
GITHUB_API_URL=https://api.github.com
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

## Stream de geração

```http
POST /api/stream
```

Body:

```json
{
  "prompt": "pipeline python pytest docker",
  "provider": "auto"
}
```

---

## Aplicar pipeline GitLab

```http
POST /api/gitlab/apply
```

Body:

```json
{
  "project_id": "123",
  "branch": "main",
  "yaml": "stages: ..."
}
```

---

## Aplicar workflow GitHub

```http
POST /api/github/apply
```

Body:

```json
{
  "owner": "usuario",
  "repo": "repositorio",
  "branch": "main",
  "yaml": "name: CI"
}
```

---

# 🧩 Funcionamento Interno

## Fluxo da aplicação

1. Usuário envia prompt
2. Backend escolhe provider
3. LLM gera pipeline YAML
4. YAML é validado
5. Frontend exibe GitLab e GitHub
6. Usuário pode:
   - editar
   - baixar
   - publicar

---

# 🛡️ Validações

A aplicação valida:

- YAML válido
- Campos obrigatórios
- Providers configurados
- Tokens de integração

---

# 🔄 Fallback Inteligente

No modo `auto`:

1. Tenta Groq
2. Se falhar → OpenAI
3. Se falhar → Template Local

---

# 📦 Templates Locais

Templates disponíveis:

- .NET 8
- .NET 9
- Java
- Python
- Terraform

Renderizados via Jinja2.

---

# 🚀 Melhorias Futuras

Sugestões para evolução:

- Monaco Editor
- Syntax Highlight
- Histórico de pipelines
- Login OAuth GitHub/GitLab
- Deploy Docker
- Kubernetes deployment
- Multi-workflow support
- Dark/Light Theme
- Banco de dados
- Pipeline templates marketplace

---

# 🐳 Docker

Exemplo de Dockerfile:

```dockerfile
FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
```

---

# 📋 Dependências Recomendadas

```txt
flask
openai
python-dotenv
pyyaml
jinja2
requests
```

---

# 🔥 Destaques Técnicos

## Backend

- Streaming SSE
- Logging rotativo
- Fallback inteligente
- Validação YAML
- Integração REST APIs

## Frontend

- Interface responsiva
- Conversão automática GitHub
- Validação client-side
- Download de arquivos
- Atualização dinâmica

---

# 📝 Observações

- O projeto já possui arquitetura muito bem organizada.
- O frontend está moderno e bem estruturado.
- A separação GitLab/GitHub ficou excelente.
- O fallback entre providers está muito bom.
- O uso de templates locais aumenta a resiliência.

---

# 📄 Licença

MIT License

---

# 👨‍💻 Autor

Thiago Liberati
