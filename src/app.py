import os
import json
import yaml
import logging

from logging.handlers import RotatingFileHandler

from flask import (
    Flask,
    render_template,
    request,
    Response
)

from config import Config
from llm_agent import stream_llm
from gitlab_client import create_or_update_pipeline

# NOVO
from github_client import (
    create_or_update_workflow
)

# =========================================================
# LOGS
# =========================================================
LOG_DIR = "logs"

os.makedirs(
    LOG_DIR,
    exist_ok=True
)

logger = logging.getLogger()

logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# ---------------------------------------------------------
# APP LOG
# ---------------------------------------------------------
app_handler = RotatingFileHandler(
    f"{LOG_DIR}/app.log",
    maxBytes=1_000_000,
    backupCount=3,
    encoding="utf-8"
)

app_handler.setFormatter(
    formatter
)

# ---------------------------------------------------------
# ERROR LOG
# ---------------------------------------------------------
error_handler = RotatingFileHandler(
    f"{LOG_DIR}/error.log",
    maxBytes=1_000_000,
    backupCount=3,
    encoding="utf-8"
)

error_handler.setLevel(
    logging.ERROR
)

error_handler.setFormatter(
    formatter
)

# ---------------------------------------------------------
# CONSOLE LOG
# ---------------------------------------------------------
console_handler = logging.StreamHandler()

console_handler.setFormatter(
    formatter
)

logger.handlers.clear()

logger.addHandler(app_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)

# =========================================================
# APP
# =========================================================
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

# =========================================================
# HELPERS
# =========================================================
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


def validate_yaml(
    yaml_text: str
):

    try:

        parsed = yaml.safe_load(
            yaml_text
        )

        if not isinstance(
            parsed,
            dict
        ):

            return (
                False,
                "YAML nao e um objeto valido"
            )

        return (
            True,
            "YAML valido"
        )

    except yaml.YAMLError as e:

        return (
            False,
            f"YAML invalido: {str(e)}"
        )


def detect_type(
    yaml_text: str
) -> str:

    if (
        "jobs:" in yaml_text
        and
        "runs-on" in yaml_text
    ):
        return "github"

    if "stages:" in yaml_text:
        return "gitlab"

    return "unknown"


# =========================================================
# ROUTES
# =========================================================
@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# STREAM
# =========================================================
@app.route(
    "/api/stream",
    methods=["POST"]
)
def stream():

    data = request.get_json(
        force=True
    )

    prompt = data.get(
        "prompt",
        ""
    ).strip()

    provider = data.get(
        "provider",
        "auto"
    )

    logger.info(
        f"[REQUEST] provider={provider}"
    )

    if not prompt:

        return {
            "error": "Prompt vazio"
        }, 400

    # -----------------------------------------------------
    # GENERATOR
    # -----------------------------------------------------
    def generate():

        full = ""

        last_provider = None

        try:

            for chunk, prov in stream_llm(
                prompt,
                provider
            ):

                full += chunk

                # -----------------------------------------
                # PROVIDER CHANGED
                # -----------------------------------------
                if prov != last_provider:

                    logger.info(
                        f"Provider alterado para: {prov}"
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
                f"[STREAM ERROR] {str(e)}"
            )

            yield (
                f"data: "
                f"{json.dumps({'error': 'Erro inesperado'})}\n\n"
            )

            return

        # -------------------------------------------------
        # POST PROCESS
        # -------------------------------------------------
        cleaned = clean_yaml(
            full
        )

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


# =========================================================
# APPLY GITLAB
# =========================================================
@app.route(
    "/api/gitlab/apply",
    methods=["POST"]
)
def apply_gitlab_pipeline():

    data = request.get_json(
        force=True
    )

    project_id = data.get(
        "project_id"
    )

    branch = data.get(
        "branch",
        "main"
    )

    yaml_content = data.get(
        "yaml",
        ""
    )

    # -----------------------------------------------------
    # CONFIG
    # -----------------------------------------------------
    if not Config.has_gitlab():

        return {

            "success": False,

            "error": (
                "GITLAB_TOKEN nao configurado"
            )

        }, 500

    # -----------------------------------------------------
    # VALIDATIONS
    # -----------------------------------------------------
    if not project_id:

        return {

            "success": False,

            "error": (
                "project_id obrigatorio"
            )

        }, 400

    if not yaml_content.strip():

        return {

            "success": False,

            "error": "yaml vazio"

        }, 400

    # -----------------------------------------------------
    # YAML VALIDATION
    # -----------------------------------------------------
    valid, validation_msg = validate_yaml(
        yaml_content
    )

    if not valid:

        return {

            "success": False,

            "error": validation_msg

        }, 400

    # -----------------------------------------------------
    # APPLY
    # -----------------------------------------------------
    try:

        logger.info(
            f"[GITLAB] aplicando pipeline "
            f"project={project_id} "
            f"branch={branch}"
        )

        response = create_or_update_pipeline(

            project_id=project_id,

            branch=branch,

            yaml_content=yaml_content
        )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------
        if response.ok:

            logger.info(
                f"[OK] pipeline aplicado "
                f"project={project_id}"
            )

            return {

                "success": True,

                "message": (
                    "Pipeline aplicado com sucesso"
                )
            }

        # -------------------------------------------------
        # GITLAB ERROR
        # -------------------------------------------------
        logger.error(
            f"[GITLAB ERROR] "
            f"{response.text}"
        )

        return {

            "success": False,

            "error": response.text

        }, response.status_code

    except Exception as e:

        logger.exception(
            "[GITLAB EXCEPTION]"
        )

        return {

            "success": False,

            "error": str(e)

        }, 500


# =========================================================
# APPLY GITHUB
# =========================================================
@app.route(
    "/api/github/apply",
    methods=["POST"]
)
def apply_github_pipeline():

    data = request.get_json(
        force=True
    )

    owner = data.get(
        "owner"
    )

    repo = data.get(
        "repo"
    )

    branch = data.get(
        "branch",
        "main"
    )

    yaml_content = data.get(
        "yaml",
        ""
    )

    # -----------------------------------------------------
    # CONFIG
    # -----------------------------------------------------
    if not Config.has_github():

        return {

            "success": False,

            "error": (
                "GITHUB_TOKEN nao configurado"
            )

        }, 500

    # -----------------------------------------------------
    # VALIDATIONS
    # -----------------------------------------------------
    if not owner:

        return {

            "success": False,

            "error": (
                "owner obrigatorio"
            )

        }, 400

    if not repo:

        return {

            "success": False,

            "error": (
                "repo obrigatorio"
            )

        }, 400

    if not yaml_content.strip():

        return {

            "success": False,

            "error": "yaml vazio"

        }, 400

    # -----------------------------------------------------
    # YAML VALIDATION
    # -----------------------------------------------------
    valid, validation_msg = validate_yaml(
        yaml_content
    )

    if not valid:

        return {

            "success": False,

            "error": validation_msg

        }, 400

    # -----------------------------------------------------
    # APPLY
    # -----------------------------------------------------
    try:

        logger.info(
            f"[GITHUB] aplicando workflow "
            f"repo={owner}/{repo} "
            f"branch={branch}"
        )

        response = create_or_update_workflow(

            owner=owner,

            repo=repo,

            branch=branch,

            yaml_content=yaml_content
        )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------
        if response.ok:

            logger.info(
                f"[OK] workflow aplicado "
                f"repo={owner}/{repo}"
            )

            return {

                "success": True,

                "message": (
                    "Workflow aplicado com sucesso"
                )
            }

        # -------------------------------------------------
        # GITHUB ERROR
        # -------------------------------------------------
        logger.error(
            f"[GITHUB ERROR] "
            f"{response.text}"
        )

        return {

            "success": False,

            "error": response.text

        }, response.status_code

    except Exception as e:

        logger.exception(
            "[GITHUB EXCEPTION]"
        )

        return {

            "success": False,

            "error": str(e)

        }, 500


# =========================================================
# START
# =========================================================
if __name__ == "__main__":

    try:

        Config.validate()

    except Exception as e:

        logger.error(
            str(e)
        )

    logger.info(
        f"[START] Providers: {Config.summary()}"
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )