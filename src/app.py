from flask import Flask, render_template, request, Response
from llm_agent import stream_llm
import yaml
import json
import os

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
    data = request.json
    prompt = data.get("prompt")
    provider = data.get("provider", "auto")

    def generate():
        full = ""

        for chunk, prov in stream_llm(prompt, provider):
            if "ERROR:" in chunk:
                yield f"data: {json.dumps({'error': chunk})}\n\n"
                return

            full += chunk

            yield f"data: {json.dumps({'chunk': chunk, 'provider': prov})}\n\n"

        try:
            yaml.safe_load(full)
            validation = "✅ YAML válido"
        except Exception as e:
            validation = f"❌ YAML inválido: {str(e)}"

        yield f"data: {json.dumps({'validation': validation})}\n\n"

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)