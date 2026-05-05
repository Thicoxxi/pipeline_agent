import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)


def get_env(key: str):
    return os.getenv(key)


class Config:
    @staticmethod
    def openai_key():
        return get_env("OPENAI_API_KEY")

    @staticmethod
    def groq_key():
        return get_env("GROQ_API_KEY")

    @staticmethod
    def has_openai():
        return bool(get_env("OPENAI_API_KEY"))

    @staticmethod
    def has_groq():
        return bool(get_env("GROQ_API_KEY"))