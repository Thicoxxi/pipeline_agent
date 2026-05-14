import requests

API_URL = "http://localhost:5000"


def chat():
    print("🤖 Simple VSCode Agent (Python)\n")

    mode = input("Mode (chat/github): ").strip()

    if mode == "chat":
        prompt = input("Prompt: ")

        res = requests.post(
            f"{API_URL}/api/stream",
            json={
                "prompt": prompt,
                "provider": "auto"
            }
        )

        print("\n🤖 Response:\n")
        print(res.text)

    elif mode == "github":
        owner = input("Owner: ")
        repo = input("Repo: ")
        yaml = input("Paste YAML:\n")

        res = requests.post(
            f"{API_URL}/api/github/apply",
            json={
                "owner": owner,
                "repo": repo,
                "branch": "main",
                "yaml": yaml
            }
        )

        print("\n🚀 Result:\n")
        print(res.json())


if __name__ == "__main__":
    chat()