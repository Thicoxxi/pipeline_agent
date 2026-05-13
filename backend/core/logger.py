import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger():

    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger()

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    app_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8"
    )

    app_handler.setFormatter(formatter)

    console = logging.StreamHandler()

    console.setFormatter(formatter)

    logger.handlers.clear()

    logger.addHandler(app_handler)
    logger.addHandler(console)

    return logger