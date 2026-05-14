import logging
import os
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path
import contextvars

# =========================================================
# CONTEXT (REQUEST ID GLOBAL)
# =========================================================
request_id_ctx = contextvars.ContextVar("request_id", default="-")


def set_request_id(value: str | None = None):
    request_id_ctx.set(value or str(uuid.uuid4())[:8])


def get_request_id():
    return request_id_ctx.get()


# =========================================================
# FORMATTER CUSTOM (com request_id)
# =========================================================
class ContextFormatter(logging.Formatter):

    def format(self, record):
        record.request_id = get_request_id()
        return super().format(record)


# =========================================================
# LOGGER FACTORY
# =========================================================
def setup_logger(
    name: str = "app",
    log_dir: str = "logs",
    log_file: str = "app.log",
    level: str | int = logging.INFO,
    max_bytes: int = 1_000_000,
    backup_count: int = 3,
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s [req=%(request_id)s]: %(message)s",
    disable_werkzeug: bool = True,
):
    """
    Logger global estruturado com suporte a request_id.
    """

    # -----------------------------
    # LOG DIR
    # -----------------------------
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # LOGGER BASE
    # -----------------------------
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        logger.handlers.clear()

    logger.propagate = False

    formatter = ContextFormatter(fmt)

    # -----------------------------
    # FILE HANDLER
    # -----------------------------
    file_handler = RotatingFileHandler(
        log_path / log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # -----------------------------
    # CONSOLE HANDLER
    # -----------------------------
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # -----------------------------
    # REDUZ RUÍDO DO FLASK (opcional)
    # -----------------------------
    if disable_werkzeug:
        logging.getLogger("werkzeug").setLevel(logging.WARNING)

    return logger


# =========================================================
# HELPER
# =========================================================
def get_logger(name: str = "app"):
    return logging.getLogger(name)