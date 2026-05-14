import os

from dotenv import load_dotenv

# =========================================================
# BASE DIR
# =========================================================
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# =========================================================
# ENV
# =========================================================
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
    # SCM
    # =====================================================
    GITHUB_TOKEN = os.getenv(
        "GITHUB_TOKEN",
        ""
    ).strip()

    GITHUB_URL = os.getenv(
        "GITHUB_URL",
        "https://api.github.com"
    ).strip()

    GITLAB_TOKEN = os.getenv(
        "GITLAB_TOKEN",
        ""
    ).strip()

    GITLAB_URL = os.getenv(
        "GITLAB_URL",
        "https://gitlab.com/api/v4"
    ).strip()

    # =====================================================
    # OPENAI
    # =====================================================
    @classmethod
    def has_openai(cls):

        return bool(
            cls.OPENAI_API_KEY
        )

    @classmethod
    def openai_key(cls):

        return cls.OPENAI_API_KEY

    # =====================================================
    # GROQ
    # =====================================================
    @classmethod
    def has_groq(cls):

        return bool(
            cls.GROQ_API_KEY
        )

    @classmethod
    def groq_key(cls):

        return cls.GROQ_API_KEY

    # =====================================================
    # GITHUB
    # =====================================================
    @classmethod
    def has_github(cls):

        return bool(
            cls.GITHUB_TOKEN
        )

    @classmethod
    def github_token(cls):

        return cls.GITHUB_TOKEN

    @classmethod
    def github_url(cls):

        return cls.GITHUB_URL

    # =====================================================
    # GITLAB
    # =====================================================
    @classmethod
    def has_gitlab(cls):

        return bool(
            cls.GITLAB_TOKEN
        )

    @classmethod
    def gitlab_token(cls):

        return cls.GITLAB_TOKEN

    @classmethod
    def gitlab_url(cls):

        return cls.GITLAB_URL

    # =====================================================
    # DEFAULT PROVIDER
    # =====================================================
    @classmethod
    def default_provider(cls):

        if cls.has_groq():
            return "groq"

        if cls.has_openai():
            return "openai"

        return "local"

    # =====================================================
    # VALIDATE
    # =====================================================
    @classmethod
    def validate(cls):

        if not (
            cls.has_groq()
            or cls.has_openai()
        ):

            print(
                "[WARNING] Nenhum provider LLM configurado"
            )

    # =====================================================
    # SUMMARY
    # =====================================================
    @classmethod
    def summary(cls):

        return {

            "openai":
                "OK"
                if cls.has_openai()
                else "MISSING",

            "groq":
                "OK"
                if cls.has_groq()
                else "MISSING",

            "github":
                "OK"
                if cls.has_github()
                else "MISSING",

            "gitlab":
                "OK"
                if cls.has_gitlab()
                else "MISSING",
        }