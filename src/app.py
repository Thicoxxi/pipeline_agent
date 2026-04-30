import os
import json
import yaml
import logging
from flask import Flask, render_template, request, Response
from dotenv import load_dotenv
from llm_agent import stream_llm

load_dotenv()

logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "..", "templates"),
    static_folder=os.path.join(BASE_DIR, "..", "static")
)


@app.route("/")
def home():
    """
    Rota principal da aplicação.

    Returns:
        str: Renderiza o template HTML `index.html` localizado na pasta templates.
    """
    return render_template("index.html")


@app.route("/api/stream", methods=["POST"])
def stream():
    """
    Endpoint de streaming para geração de YAML via LLM.

    Recebe um JSON com os campos:
        - prompt (str): Texto fornecido pelo usuário.
        - provider (str, opcional): Provider específico ("openai", "groq", "local").
          Se não informado, usa "auto".

    Fluxo:
        1. Valida se o prompt não está vazio.
        2. Chama `stream_llm` para gerar YAML em streaming.
        3. Retorna os chunks em formato SSE (Server-Sent Events).
        4. Ao final, valida se o YAML completo é válido e envia resultado da validação.

    Returns:
        Response: Resposta HTTP em formato `text/event-stream` contendo os dados em tempo real.
    """
    data = request.get_json(force=True)

    prompt = data.get("prompt", "").strip()
    provider = data.get("provider", "auto")

    if not prompt:
        return {"error": "Prompt vazio"}, 400

    def generate():
        """
        Função geradora que produz eventos SSE em tempo real.

        Yields:
            str: Eventos SSE contendo:
                - chunk: fragmento do YAML gerado
                - provider: nome do provider utilizado
                - error: mensagem de erro (se ocorrer)
                - validation: resultado da validação do YAML
        """
        full = ""

        try:
            for chunk, prov in stream_llm(prompt, provider):
                full += chunk
                yield f"data: {json.dumps({'chunk': chunk, 'provider': prov})}\n\n"

        except Exception as e:
            logging.exception("Erro no streaming")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        # Validação YAML
        try:
            yaml.safe_load(full)
            validation = "✅ YAML válido"
        except Exception as e:
            validation = f"❌ YAML inválido: {str(e)}"

        yield f"data: {json.dumps({'validation': validation})}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # importante p/ nginx
        }
    )


if __name__ == "__main__":
    """
    Ponto de entrada da aplicação Flask.

    Executa o servidor na porta 5000, acessível em todas as interfaces
    (`host="0.0.0.0"`), com `debug=True` para facilitar o desenvolvimento.
    """
    app.run(host="0.0.0.0", port=5000, debug=True)
