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
    return render_template("index.html")


@app.route("/api/stream", methods=["POST"])
def stream():
    data = request.get_json(force=True)

    prompt = data.get("prompt", "").strip()
    provider = data.get("provider", "auto")

    if not prompt:
        return {"error": "Prompt vazio"}, 400

    def generate():
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
    app.run(host="0.0.0.0", port=5000, debug=True)