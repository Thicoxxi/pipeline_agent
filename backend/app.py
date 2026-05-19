import os
import logging
import base64
from time import perf_counter

from dotenv import load_dotenv
from flask import Flask, render_template, request, g

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
# CORE IMPORTS
# =========================================================
from core.config import Config

from core.logger import (
    setup_logger,
    set_request_id,
    get_request_id
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

from api.routes.analyze_routes import (
    analyze_bp
)
from api.routes.log_routes import (
    log_bp
)

# =========================================================
# LOGGER
# =========================================================
# Ensure logs are written to the backend folder regardless of CWD
logger = setup_logger(log_dir=os.path.join(BASE_DIR, "logs"))

# =========================================================
# REDUZ RUÍDO DO FLASK/WERKZEUG
# =========================================================
logging.getLogger(
    "werkzeug"
).setLevel(logging.WARNING)

# =========================================================
# APP INIT
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
# REQUEST CONTEXT
# =========================================================
@app.before_request
def before_request():

    # request id global
    set_request_id()

    # timer request
    g.start_time = perf_counter()

    logger.info(
        "REQUEST START | id=%s | method=%s | path=%s | ip=%s",
        get_request_id(),
        request.method,
        request.path,
        request.remote_addr
    )


# =========================================================
# AFTER REQUEST
# =========================================================
@app.after_request
def after_request(response):

    duration_ms = (
        perf_counter() - g.start_time
    ) * 1000

    logger.info(
        (
            "REQUEST END   | "
            "id=%s | "
            "status=%s | "
            "duration=%.2fms"
        ),
        get_request_id(),
        response.status_code,
        duration_ms
    )

    return response


# =========================================================
# GLOBAL ERROR HANDLER
# =========================================================
@app.errorhandler(Exception)
def handle_exception(error):

    logger.exception(
        "UNHANDLED ERROR | %s",
        str(error)
    )

    return {
        "success": False,
        "error": "Internal server error"
    }, 500


# =========================================================
# NOT FOUND (404) - handle missing static files like favicon
# =========================================================
@app.errorhandler(404)
def handle_not_found(error):

    logger.info(
        "NOT FOUND | path=%s",
        request.path
    )

    return {
        "success": False,
        "error": "Not found"
    }, 404


# =========================================================
# FAVICON
# Serve a favicon if present in the static folder, otherwise
# return a 204 to avoid spamming logs with 404 errors.
# =========================================================
@app.route("/favicon.ico")
def favicon():

    try:
        return app.send_static_file("favicon.ico")
    except Exception:
        # Return a tiny 1x1 transparent PNG so browsers get a valid image
        png_base64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
        )

        png_bytes = base64.b64decode(png_base64)

        from flask import Response

        return Response(png_bytes, mimetype="image/png")


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

app.register_blueprint(
    analyze_bp
)

app.register_blueprint(
    log_bp
)

# =========================================================
# HOME
# =========================================================
@app.route("/")
def home():

    logger.info(
        "HOME PAGE ACCESSED"
    )

    return render_template(
        "index.html"
    )


# =========================================================
# BOOT LOG
# =========================================================
logger.info("=" * 60)
logger.info("APP STARTING")
logger.info("=" * 60)

logger.info(
    (
        "ENV | "
        "openai=%s | "
        "groq=%s | "
        "github=%s | "
        "gitlab=%s"
    ),
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

        logger.info(
            "CONFIG | %s",
            Config.summary()
        )

    except Exception:

        logger.exception(
            "CONFIG ERROR"
        )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )