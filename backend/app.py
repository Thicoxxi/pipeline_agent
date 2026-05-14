import os
import uuid
import logging

from dotenv import load_dotenv
from flask import Flask, render_template, request, g

# =========================================================
# LOAD ENV
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)


# =========================================================
# CORE IMPORTS
# =========================================================
from core.config import Config
from core.logger import setup_logger

from api.routes.stream_routes import stream_bp
from api.routes.github_routes import github_bp
from api.routes.gitlab_routes import gitlab_bp


# =========================================================
# LOGGER
# =========================================================
logger = setup_logger()


# =========================================================
# REDUZ RUÍDO DO FLASK/WERKZEUG
# =========================================================
logging.getLogger("werkzeug").setLevel(logging.WARNING)


# =========================================================
# APP INIT
# =========================================================
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)


# =========================================================
# REQUEST ID (BÁSICO MAS MUITO ÚTIL)
# =========================================================
@app.before_request
def start_request():

    g.request_id = str(uuid.uuid4())[:8]

    logger.info(
        "REQUEST START | id=%s method=%s path=%s ip=%s",
        g.request_id,
        request.method,
        request.path,
        request.remote_addr
    )


@app.after_request
def end_request(response):

    logger.info(
        "REQUEST END   | id=%s status=%s",
        getattr(g, "request_id", "-"),
        response.status_code
    )

    return response


# =========================================================
# BLUEPRINTS
# =========================================================
app.register_blueprint(stream_bp)
app.register_blueprint(github_bp)
app.register_blueprint(gitlab_bp)


# =========================================================
# HOME
# =========================================================
@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# BOOT LOG (LIMPO)
# =========================================================
logger.info("=================================================")
logger.info("APP STARTING")
logger.info("=================================================")

logger.info(
    "ENV | openai=%s groq=%s github=%s gitlab=%s",
    bool(os.getenv("OPENAI_API_KEY")),
    bool(os.getenv("GROQ_API_KEY")),
    bool(os.getenv("GITHUB_TOKEN")),
    bool(os.getenv("GITLAB_TOKEN"))
)


# =========================================================
# START
# =========================================================
if __name__ == "__main__":

    try:
        Config.validate()
        logger.info("CONFIG | %s", Config.summary())

    except Exception:
        logger.exception("CONFIG ERROR")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )