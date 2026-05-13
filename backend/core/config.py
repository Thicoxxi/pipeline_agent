import os

from dotenv import load_dotenv

# =========================================================
# LOAD ENV
# =========================================================
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)

# =========================================================
# CONFIG
# =========================================================
class Config:

    # =====================================================
    # LLM
    # =====================================================
    OPENAI_API_KEY = os.getenv(
        "OPENAI_API_KEY",
        ""
    ).strip()

    GROQ_API_KEY = os.getenv(
        "GROQ_API_KEY",
        ""
    ).strip()

    # =====================================================
    # GITHUB
    # =====================================================
    GITHUB_TOKEN = os.getenv(
        "GITHUB_TOKEN",
        ""
    ).strip()

    GITHUB_URL = os.getenv(
        "GITHUB_URL",
        "https://api.github.com"
    ).strip()

    # =====================================================
    # GITLAB
    # =====================================================
    GITLAB_TOKEN = os.getenv(
        "GITLAB_TOKEN",
        ""
    ).strip()

    GITLAB_URL = os.getenv(
        "GITLAB_URL",
        "https://gitlab.com/api/v4"
    ).strip()

    # =====================================================
    # PROVIDERS
    # =====================================================
    @classmethod
    def has_openai(cls):

        return bool(
            cls.OPENAI_API_KEY
        )

    @classmethod
    def has_groq(cls):

        return bool(
            cls.GROQ_API_KEY
        )

    @classmethod
    def has_github(cls):

        return bool(
            cls.GITHUB_TOKEN
        )

    @classmethod
    def has_gitlab(cls):

        return bool(
            cls.GITLAB_TOKEN
        )

    # =====================================================
    # VALIDATE
    # =====================================================
    @classmethod
    def validate(cls):

        if not (
            cls.has_openai()
            or cls.has_groq()
        ):

            raise Exception(
                "Nenhum provider configurado"
            )

    # =====================================================
    # SUMMARY
    # =====================================================
    @classmethod
    def summary(cls):

        return {
            "openai": cls.has_openai(),
            "groq": cls.has_groq(),
            "github": cls.has_github(),
            "gitlab": cls.has_gitlab()
        }