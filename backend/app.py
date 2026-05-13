import os

from dotenv import load_dotenv

from flask import (
    Flask,
    render_template
)

# =========================================================
# LOAD ENV
# =========================================================
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_PATH)

# =========================================================
# IMPORTS
# =========================================================
from core.config import Config

from core.logger import (
    setup_logger
)

from api.routes.stream_routes import (
    stream_bp
)

from api.routes.github_routes import (
    github_bp
)

from api.routes.gitlab_routes import (
    gitlab_bp
)

# =========================================================
# LOGGER
# =========================================================
logger = setup_logger()

logger.info(
    "[BOOT] iniciando aplicação..."
)

# =========================================================
# DEBUG ENV
# =========================================================
logger.info(
    f"[ENV] OPENAI={bool(os.getenv('OPENAI_API_KEY'))}"
)

logger.info(
    f"[ENV] GROQ={bool(os.getenv('GROQ_API_KEY'))}"
)

logger.info(
    f"[ENV] GITHUB={bool(os.getenv('GITHUB_TOKEN'))}"
)

logger.info(
    f"[ENV] GITLAB={bool(os.getenv('GITLAB_TOKEN'))}"
)

# =========================================================
# APP
# =========================================================
app = Flask(

    __name__,

    template_folder=os.path.join(
        BASE_DIR,
        "templates"
    ),

    static_folder=os.path.join(
        BASE_DIR,
        "static"
    )
)

# =========================================================
# BLUEPRINTS
# =========================================================
app.register_blueprint(
    stream_bp
)

app.register_blueprint(
    github_bp
)

app.register_blueprint(
    gitlab_bp
)

# =========================================================
# HOME
# =========================================================
@app.route("/")
def home():

    return render_template(
        "index.html"
    )

# =========================================================
# START
# =========================================================
if __name__ == "__main__":

    try:

        Config.validate()

        logger.info(
            f"[CONFIG] {Config.summary()}"
        )

    except Exception as e:

        logger.exception(
            "[CONFIG ERROR]"
        )

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True
    )