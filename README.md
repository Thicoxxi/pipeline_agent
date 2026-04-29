# 🚀 Pipeline Agent

Um **Agent de IA para geração automática de pipelines CI/CD (`.gitlab-ci.yml`)**, com streaming em tempo real, fallback inteligente entre LLMs e interface moderna estilo ChatGPT.

---

## ✨ Funcionalidades

* 🤖 Geração automática de pipelines GitLab CI
* ⚡ Streaming em tempo real (SSE)
* 🔄 Fallback automático entre LLMs:

  * OpenAI
  * Groq
  * Local (fallback)
* 🧠 Validação automática de YAML
* 🎨 Interface estilo ChatGPT
* ⌨️ Efeito de digitação (typing effect)
* 📋 Copiar YAML
* ⬇️ Download `.gitlab-ci.yml`
* 🎯 Sugestões inteligentes de pipelines
* 🌙 Dark mode

---

## 🏗️ Estrutura do Projeto

```
pipeline_agent/
│
├── src/
│   ├── app.py           # Backend Flask
│   └── llm_agent.py     # Lógica de LLM + fallback
│
├── templates/
│   └── index.html       # Frontend HTML
│
├── static/
│   ├── chat.js          # Lógica do chat
│   └── chat.css         # Estilo UI
│
├── .env
└── README.md
```

---

## ⚙️ Pré-requisitos

* Python 3.9+
* pip

---

## 🔧 Instalação

```bash
git clone https://github.com/Thicoxxi/pipeline_agent.git
cd pipeline-agent

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate

pip install flask openai pyyaml requests python-dotenv
```

---

## 🔑 Configuração (.env)

Crie um arquivo `.env` na raiz:

```env
OPENAI_API_KEY=sua_chave_openai
GROQ_API_KEY=sua_chave_groq
```

---

## ▶️ Executar

```bash
python src/app.py
```

Acesse no navegador:

```
http://localhost:5000
```

---

## 🔄 Fallback Inteligente de LLM

O sistema escolhe automaticamente o melhor provider:

1. 🤖 OpenAI
2. ⚡ Groq
3. 🧠 Local (fallback)

Se um falhar, o próximo é utilizado automaticamente.

---

## 📡 API

### POST `/api/stream`

Streaming da resposta em tempo real.

#### Request

```json
{
  "prompt": "pipeline node com test",
  "provider": "auto"
}
```

#### Response (SSE)

```
data: { "chunk": "stages:" }
data: { "provider": "groq" }
data: { "validation": "✅ YAML válido" }
```

---

## 🧩 Estrutura Interna (Detalhada)

---

### 🔹 `app.py` — Backend Flask

Responsável por:

* Servir o frontend
* Receber prompts do usuário
* Fazer streaming da resposta
* Validar YAML

---

### 🔁 Fluxo

```
Usuário → /api/stream → LLM → Streaming → Frontend
```

---

### 📌 Partes principais

#### Rota principal

```python
@app.route("/")
def home():
    return render_template("index.html")
```

---

#### Endpoint de streaming

```python
@app.route("/api/stream", methods=["POST"])
def stream():
```

---

#### Generator de resposta

```python
def generate():
    for chunk, prov in stream_llm(prompt, provider):
        yield f"data: ...\n\n"
```

---

#### Validação YAML

```python
yaml.safe_load(full)
```

---

#### Retorno SSE

```python
return Response(generate(), mimetype="text/event-stream")
```

---

### 🔹 `llm_agent.py` — Orquestração de LLMs

Responsável por:

* Escolher o modelo
* Fazer fallback automático
* Fazer streaming

---

### 🔄 Estratégia

```
OpenAI → Groq → Local
```

---

### 📌 Função principal

#### `stream_llm(prompt, provider)`

Retorna:

```python
yield chunk, provider
```

---

### Providers

#### OpenAI

* API oficial
* Pode falhar por quota

---

#### Groq

* Alternativa gratuita
* Necessita `GROQ_API_KEY`

---

#### Local

* Fallback final
* Garante funcionamento mesmo offline

---

## 🧠 Exemplos de uso

* criar pipeline dotnet core 10
* pipeline node com npm install e test
* pipeline python com pytest
* pipeline docker build e push
* pipeline terraform aws

---

## 🎨 UI Features

* Interface estilo ChatGPT
* Chips de sugestão
* Syntax Highlight YAML
* Spinner de carregamento
* Cursor piscando
* Streaming em tempo real

---

## 🛠️ Tecnologias

* Flask
* JavaScript (Vanilla)
* Prism.js
* PyYAML
* OpenAI API
* Groq API

---

## 🐛 Problemas comuns

---

### ❌ TemplateNotFound: index.html

Verifique se existe:

```
templates/index.html
```

---

### ❌ OpenAI quota exceeded

Solução:

* Ativar billing
* Ou usar Groq

---

### ❌ Groq model deprecated

Atualize modelo no `llm_agent.py`:

```python
model="mixtral-8x7b-32768"
```

---

### ❌ YAML inválido

Causa comum:

* LLM retornando texto + explicação

Solução:

```
"Retorne apenas YAML, sem explicações."
```

---

## 🚀 Melhorias futuras

* 💾 Histórico persistente
* 📂 Exportar múltiplos pipelines
* 🔐 Autenticação
* ☁️ Deploy com Docker
* 📊 Templates reutilizáveis

---

## 🤝 Contribuição

Pull requests são bem-vindos 🚀

---

## 📄 Licença

MIT

---

## ⭐ Se curtiu

Deixe uma estrela no repositório 😄
