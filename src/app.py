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

# log geral
app_handler = RotatingFileHandler(
    f"{LOG_DIR}/app.log", maxBytes=1_000_000, backupCount=3
)
app_handler.setLevel(logging.INFO)
app_handler.setFormatter(formatter)

# log erro
error_handler = RotatingFileHandler(
    f"{LOG_DIR}/error.log", maxBytes=1_000_000, backupCount=3
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

logger.addHandler(app_handler)
logger.addHandler(error_handler)

# silenciar libs externas
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

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

    if not prompt:
        return {"error": "Prompt vazio"}, 400

    def generate():
        full = ""

        try:
            for chunk, prov in stream_llm(prompt):
                full += chunk

                payload = {
                    "chunk": chunk,
                    "provider": prov
                }

                yield f"data: {json.dumps(payload)}\n\n"

        except Exception:
            logger.exception("Erro durante streaming")

            payload = {
                "error": "Erro ao gerar resposta"
            }

            yield f"data: {json.dumps(payload)}\n\n"
            return

        cleaned = clean_yaml(full)

        # validação YAML
        try:
            yaml.safe_load(cleaned)
            validation = "✅ YAML válido"
        except Exception as e:
            validation = f"❌ YAML inválido: {str(e)}"

        pipeline_type = detect_type(cleaned)

        payload = {
            "validation": validation,
            "yaml": cleaned,
            "type": pipeline_type
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