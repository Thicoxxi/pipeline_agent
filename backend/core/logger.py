import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(
    name: str = "app",
    log_dir: str = "logs",
    log_file: str = "app.log",
    level: str | int = logging.INFO,
    max_bytes: int = 1_000_000,
    backup_count: int = 3,
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s (%(threadName)s): %(message)s",
):
    """
    Configura logger global reutilizável e seguro para produção/dev.
    """

    # -----------------------------
    # Diretório seguro de logs
    # -----------------------------
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # Logger principal
    # -----------------------------
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evita duplicação de handlers
    if logger.handlers:
        logger.handlers.clear()

    logger.propagate = False  # evita duplicar logs no root logger

    formatter = logging.Formatter(fmt)

    # -----------------------------
    # File handler (rotativo)
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
    # Console handler
    # -----------------------------
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # -----------------------------
    # Attach handlers
    # -----------------------------
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger