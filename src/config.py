import os
from pathlib import Path
from dotenv import load_dotenv

# =========================
# LOAD .env
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# carrega apenas se existir
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)


# =========================
# HELPERS
# =========================
def get_env(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key, default)

    # evita string vazia ser considerada válida
    if value is not None and value.strip() == "":
        return None

    return value


# =========================
# CONFIG CLASS
# =========================
class Config:

    @staticmethod
    def openai_key():
        return get_env("OPENAI_API_KEY")

    @staticmethod
    def groq_key():
        return get_env("GROQ_API_KEY")

    @staticmethod
    def has_openai():
        return Config.openai_key() is not None

    @staticmethod
    def has_groq():
        return Config.groq_key() is not None

    @staticmethod
    def validate():
        """
        Valida se ao menos um provider está configurado.
        NÃO expõe nenhuma chave.
        """
        if not Config.has_openai() and not Config.has_groq():
            raise RuntimeError(
                "Nenhuma API configurada. Defina OPENAI_API_KEY ou GROQ_API_KEY no .env"
            )

    @staticmethod
    def gitlab_token():
        return get_env("GITLAB_TOKEN")

    @staticmethod
    def gitlab_url():
        return get_env(
            "GITLAB_URL",
            "https://gitlab.com/api/v4"
        )

    @staticmethod
    def has_gitlab():
        return Config.gitlab_token() is not None

    @staticmethod
    def github_token():
        return get_env("GITHUB_TOKEN")


    @staticmethod
    def github_url():
        return get_env(
            "GITHUB_API_URL",
            "https://api.github.com"
    )


    @staticmethod
    def has_github():
        return Config.github_token() is not None    

    @staticmethod
    def summary():
        """
        Retorna status seguro (sem expor secrets)
        """
        return {
            "openai": "OK" if Config.has_openai() else "MISSING",
            "groq": "OK" if Config.has_groq() else "MISSING",
            "gitlab": "OK" if Config.has_gitlab() else "MISSING",
            "github": "OK" if Config.has_github() else "MISSING",
        }