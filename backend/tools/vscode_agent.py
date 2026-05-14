from pathlib import Path
from datetime import datetime
import logging
import requests

from analyze_project import analyze_project

# =========================================================
# CONFIG
# =========================================================
API_URL = "http://localhost:5000"

# =========================================================
# LOGS
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(
    exist_ok=True
)

LOG_FILE = LOG_DIR / "vscode_agent_py.log"

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "[%(levelname)s] "
        "%(message)s"
    ),
    handlers=[
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(
    "vscode_agent_py"
)

# =========================================================
# HELPERS
# =========================================================
def separator():

    print(
        "\n" + "=" * 60 + "\n"
    )


def log_command(command):

    logger.info(
        "COMMAND | %s",
        command
    )


# =========================================================
# CHAT
# =========================================================
def chat():

    prompt = input(
        "\n💬 Prompt: "
    ).strip()

    if not prompt:

        print(
            "\n❌ empty prompt\n"
        )

        return

    logger.info(
        "CHAT START"
    )

    logger.info(
        "PROMPT | %s",
        prompt
    )

    try:

        response = requests.post(

            f"{API_URL}/api/stream",

            json={
                "prompt": prompt,
                "provider": "auto"
            },

            stream=True,
            timeout=180
        )

        separator()

        print(
            "🤖 RESPONSE:\n"
        )

        final_text = []

        for line in response.iter_lines():

            if not line:
                continue

            decoded = line.decode()

            logger.info(
                "RAW SSE | %s",
                decoded
            )

            if decoded.startswith("data:"):

                decoded = decoded.replace(
                    "data:",
                    ""
                ).strip()

            if not decoded:
                continue

            print(
                decoded,
                end="",
                flush=True
            )

            final_text.append(decoded)

        logger.info(
            "CHAT END"
        )

        separator()

    except Exception as e:

        logger.exception(
            "CHAT ERROR"
        )

        print(
            f"\n❌ error: {e}\n"
        )


# =========================================================
# ANALYZE PROJECT
# =========================================================
def analyze():

    platform = input(
        "\n🛠 Platform (gitlab/github): "
    ).strip().lower()

    if platform not in [
        "gitlab",
        "github"
    ]:

        print(
            "\n❌ invalid platform\n"
        )

        return

    logger.info(
        "ANALYZE START | platform=%s",
        platform
    )

    try:

        analyze_project(
            platform
        )

        logger.info(
            "ANALYZE END"
        )

    except Exception:

        logger.exception(
            "ANALYZE ERROR"
        )


# =========================================================
# GITHUB APPLY
# =========================================================
def github_apply():

    owner = input(
        "\nOwner: "
    ).strip()

    repo = input(
        "Repo: "
    ).strip()

    yaml_path = input(
        "YAML file path: "
    ).strip()

    file_path = Path(
        yaml_path
    )

    if not file_path.exists():

        print(
            "\n❌ file not found\n"
        )

        return

    yaml_content = file_path.read_text(
        encoding="utf-8"
    )

    logger.info(
        "GITHUB APPLY | owner=%s repo=%s file=%s",
        owner,
        repo,
        yaml_path
    )

    try:

        response = requests.post(

            f"{API_URL}/api/github/apply",

            json={
                "owner": owner,
                "repo": repo,
                "branch": "main",
                "yaml": yaml_content
            },

            timeout=180
        )

        data = response.json()

        separator()

        print(
            "🚀 RESULT:\n"
        )

        print(data)

        separator()

        logger.info(
            "GITHUB RESPONSE | %s",
            data
        )

    except Exception:

        logger.exception(
            "GITHUB APPLY ERROR"
        )


# =========================================================
# MENU
# =========================================================
def main():

    separator()

    print(
        "🤖 VSCode Agent (Python)"
    )

    print(
        f"📝 log file: {LOG_FILE}"
    )

    separator()

    while True:

        print(
            "Available commands:\n"
        )

        print(" - chat")
        print(" - analyze")
        print(" - github")
        print(" - exit")

        command = input(
            "\nCommand: "
        ).strip().lower()

        log_command(command)

        if command == "chat":

            chat()

        elif command == "analyze":

            analyze()

        elif command == "github":

            github_apply()

        elif command == "exit":

            logger.info(
                "APPLICATION CLOSED"
            )

            print(
                "\n👋 bye\n"
            )

            break

        else:

            print(
                "\n❌ invalid command\n"
            )


# =========================================================
# START
# =========================================================
if __name__ == "__main__":

    logger.info(
        "=" * 60
    )

    logger.info(
        "VSCODE AGENT PY STARTED"
    )

    logger.info(
        "=" * 60
    )

    main()