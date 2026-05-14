import requests

from analyze_project import analyze_project

API_URL = "http://localhost:5000"


# =========================================================
# CHAT
# =========================================================
def chat():

    prompt = input(
        "\n💬 Prompt: "
    ).strip()

    if not prompt:

        print(
            "❌ Prompt vazio"
        )

        return

    try:

        response = requests.post(

            f"{API_URL}/api/stream",

            json={
                "prompt": prompt,
                "provider": "auto"
            },

            timeout=120
        )

        print(
            "\n🤖 RESPONSE\n"
        )

        print(
            response.text
        )

    except Exception as e:

        print(
            f"\n❌ Chat error: {e}"
        )


# =========================================================
# APPLY GITHUB
# =========================================================
def github_apply():

    owner = input(
        "\n👤 Owner: "
    ).strip()

    repo = input(
        "📦 Repo: "
    ).strip()

    branch = input(
        "🌿 Branch (default main): "
    ).strip() or "main"

    print(
        "\n📄 Paste YAML "
        "(finish with CTRL+D):\n"
    )

    yaml_lines = []

    try:

        while True:

            yaml_lines.append(
                input()
            )

    except EOFError:
        pass

    yaml_content = "\n".join(
        yaml_lines
    )

    if not yaml_content.strip():

        print(
            "❌ YAML vazio"
        )

        return

    try:

        response = requests.post(

            f"{API_URL}/api/github/apply",

            json={
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "yaml": yaml_content
            },

            timeout=120
        )

        print(
            "\n🚀 GITHUB RESULT\n"
        )

        print(
            response.json()
        )

    except Exception as e:

        print(
            f"\n❌ GitHub apply error: {e}"
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
            "❌ Plataforma inválida"
        )

        return

    analyze_project(platform)


# =========================================================
# HELP
# =========================================================
def help_menu():

    print(
        """
=================================================
🤖 VSCode DevOps Agent
=================================================

Comandos disponíveis:

1. chat
   -> conversa com o LLM

2. github
   -> aplica workflow GitHub Actions

3. analyze
   -> analisa projeto e gera pipeline

4. exit
   -> sair

=================================================
"""
    )


# =========================================================
# MAIN LOOP
# =========================================================
def main():

    print(
        "\n🤖 VSCode DevOps Agent Started\n"
    )

    while True:

        help_menu()

        command = input(
            "\nCommand: "
        ).strip().lower()

        # =================================================
        # EXIT
        # =================================================
        if command == "exit":

            print(
                "\n👋 Bye\n"
            )

            break

        # =================================================
        # CHAT
        # =================================================
        elif command == "chat":

            chat()

        # =================================================
        # GITHUB
        # =================================================
        elif command == "github":

            github_apply()

        # =================================================
        # ANALYZE
        # =================================================
        elif command == "analyze":

            analyze()

        # =================================================
        # UNKNOWN
        # =================================================
        else:

            print(
                "\n❌ Unknown command\n"
            )


# =========================================================
# START
# =========================================================
if __name__ == "__main__":

    main()