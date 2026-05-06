import os
import json
import yaml
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, Response

from config import Config
from llm_agent import stream_llm

# -----------------------------
# LOGS
# -----------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app_handler = RotatingFileHandler(f"{LOG_DIR}/app.log", maxBytes=1_000_000, backupCount=3)
app_handler.setFormatter(formatter)

error_handler = RotatingFileHandler(f"{LOG_DIR}/error.log", maxBytes=1_000_000, backupCount=3)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

logger.addHandler(app_handler)
logger.addHandler(error_handler)

# -----------------------------
# APP
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "..", "templates"),
    static_folder=os.path.join(BASE_DIR, "..", "static")
)

# -----------------------------
# HELPERS
# -----------------------------
def clean_yaml(text: str) -> str:
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            return parts[1].replace("yaml", "").replace("yml", "").strip()
    return text.strip()


def validate_yaml(yaml_text: str):
    try:
        parsed = yaml.safe_load(yaml_text)

        if not isinstance(parsed, dict):
            return False, "YAML não é um objeto válido"

        return True, "✅ YAML válido"

    except yaml.YAMLError as e:
        return False, f"❌ YAML inválido: {str(e)}"


def detect_type(yaml_text: str) -> str:
    if "jobs:" in yaml_text and "runs-on" in yaml_text:
        return "github"
    if "stages:" in yaml_text:
        return "gitlab"
    return "unknown"


# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/stream", methods=["POST"])
def stream():
    data = request.get_json(force=True)

    prompt = data.get("prompt", "").strip()
    provider = data.get("provider", "auto")  # 🔥 AQUI ESTÁ A CORREÇÃO

    logger.info(f" Prompt recebido | provider={provider}")

    if not prompt:
        return {"error": "Prompt vazio"}, 400

    def generate():
        full = ""
        last_provider = None

        try:
            # Passando provider
            for chunk, prov in stream_llm(prompt, provider):
                full += chunk

                # Detecta troca de provider
                if prov != last_provider:
                    logger.info(f" Mudou provider → {prov}")
                    last_provider = prov

                payload = {
                    "chunk": chunk,
                    "provider": prov
                }

                yield f"data: {json.dumps(payload)}\n\n"

        except Exception as e:
            logger.exception(f"Erro crítico no streaming: {str(e)}")

            yield f"data: {json.dumps({'error': 'Erro inesperado'})}\n\n"
            return

        # Pós-processamento
        cleaned = clean_yaml(full)

        valid, validation_msg = validate_yaml(cleaned)
        pipeline_type = detect_type(cleaned)

        payload = {
            "validation": validation_msg,
            "valid": valid,
            "type": pipeline_type,
            "yaml": cleaned
        }

        yield f"data: {json.dumps(payload)}\n\n"

    return Response(generate(), mimetype="text/event-stream")


# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    try:
        Config.validate()
    except Exception as e:
        logger.error(str(e))

    logger.info(f"Providers: {Config.summary()}")

    app.run(host="0.0.0.0", port=5000, debug=True)