import os
import json
import yaml
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, Response

from config import Config
from llm_agent import stream_llm
from gitlab_client import create_or_update_pipeline

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

app_handler = RotatingFileHandler(
    f"{LOG_DIR}/app.log",
    maxBytes=1_000_000,
    backupCount=3
)

app_handler.setFormatter(formatter)

error_handler = RotatingFileHandler(
    f"{LOG_DIR}/error.log",
    maxBytes=1_000_000,
    backupCount=3
)

error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

logger.addHandler(app_handler)
logger.addHandler(error_handler)

# -----------------------------
# APP
# -----------------------------
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

app = Flask(
    __name__,
    template_folder=os.path.join(
        BASE_DIR,
        "..",
        "templates"
    ),
    static_folder=os.path.join(
        BASE_DIR,
        "..",
        "static"
    )
)

# -----------------------------
# HELPERS
# -----------------------------
def clean_yaml(text: str) -> str:

    if "```" in text:

        parts = text.split("```")

        if len(parts) >= 3:

            return (
                parts[1]
                .replace("yaml", "")
                .replace("yml", "")
                .strip()
            )

    return text.strip()


def validate_yaml(yaml_text: str):

    try:

        parsed = yaml.safe_load(yaml_text)

        if not isinstance(parsed, dict):

            return (
                False,
                "YAML não é um objeto válido"
            )

        return (
            True,
            "✅ YAML válido"
        )

    except yaml.YAMLError as e:

        return (
            False,
            f"❌ YAML inválido: {str(e)}"
        )


def detect_type(yaml_text: str) -> str:

    if (
        "jobs:" in yaml_text and
        "runs-on" in yaml_text
    ):
        return "github"

    if "stages:" in yaml_text:
        return "gitlab"

    return "unknown"


# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# -----------------------------
# STREAM
# -----------------------------
@app.route(
    "/api/stream",
    methods=["POST"]
)
def stream():

    data = request.get_json(force=True)

    prompt = data.get(
        "prompt",
        ""
    ).strip()

    provider = data.get(
        "provider",
        "auto"
    )

    logger.info(
        f"Prompt recebido | provider={provider}"
    )

    if not prompt:

        return {
            "error": "Prompt vazio"
        }, 400

    def generate():

        full = ""
        last_provider = None

        try:

            for chunk, prov in stream_llm(
                prompt,
                provider
            ):

                full += chunk

                # troca provider
                if prov != last_provider:

                    logger.info(
                        f"Mudou provider → {prov}"
                    )

                    last_provider = prov

                payload = {
                    "chunk": chunk,
                    "provider": prov
                }

                yield (
                    f"data: "
                    f"{json.dumps(payload)}\n\n"
                )

        except Exception as e:

            logger.exception(
                f"Erro crítico no streaming: {str(e)}"
            )

            yield (
                f"data: "
                f"{json.dumps({'error': 'Erro inesperado'})}\n\n"
            )

            return

        # -----------------------------
        # PÓS PROCESSAMENTO
        # -----------------------------
        cleaned = clean_yaml(full)

        valid, validation_msg = validate_yaml(
            cleaned
        )

        pipeline_type = detect_type(
            cleaned
        )

        payload = {
            "validation": validation_msg,
            "valid": valid,
            "type": pipeline_type,
            "yaml": cleaned
        }

        yield (
            f"data: "
            f"{json.dumps(payload)}\n\n"
        )

    return Response(
        generate(),
        mimetype="text/event-stream"
    )


# -----------------------------
# APPLY GITLAB
# -----------------------------
@app.route(
    "/api/gitlab/apply",
    methods=["POST"]
)
def apply_gitlab_pipeline():

    data = request.get_json(force=True)

    project_id = data.get("project_id")

    branch = data.get(
        "branch",
        "main"
    )

    yaml_content = data.get(
        "yaml",
        ""
    )

    # =====================================
    # GITLAB CONFIG
    # =====================================
    if not Config.has_gitlab():

        return {
            "success": False,
            "error": (
                "GITLAB_TOKEN "
                "não configurado"
            )
        }, 500

    # =====================================
    # VALIDATIONS
    # =====================================
    if not project_id:

        return {
            "success": False,
            "error": (
                "project_id obrigatório"
            )
        }, 400

    if not yaml_content.strip():

        return {
            "success": False,
            "error": "yaml vazio"
        }, 400

    # =====================================
    # YAML VALIDATION
    # =====================================
    valid, validation_msg = validate_yaml(
        yaml_content
    )

    if not valid:

        return {
            "success": False,
            "error": validation_msg
        }, 400

    try:

        logger.info(
            f"Aplicando pipeline | "
            f"project={project_id} "
            f"branch={branch}"
        )

        response = create_or_update_pipeline(
            project_id=project_id,
            branch=branch,
            yaml_content=yaml_content
        )

        # =====================================
        # SUCCESS
        # =====================================
        if response.ok:

            logger.info(
                f"Pipeline aplicado "
                f"com sucesso | "
                f"project={project_id}"
            )

            return {
                "success": True,
                "message": (
                    "Pipeline aplicado "
                    "com sucesso"
                )
            }

        # =====================================
        # GITLAB ERROR
        # =====================================
        logger.error(
            f"Erro GitLab API: "
            f"{response.text}"
        )

        return {
            "success": False,
            "error": response.text
        }, response.status_code

    except Exception as e:

        logger.exception(
            "Erro GitLab"
        )

        return {
            "success": False,
            "error": str(e)
        }, 500


# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":

    try:

        Config.validate()

    except Exception as e:

        logger.error(str(e))

    logger.info(
        f"Providers: {Config.summary()}"
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )