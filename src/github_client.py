import requests
import base64

from config import Config


def create_or_update_workflow(
    owner: str,
    repo: str,
    branch: str,
    yaml_content: str
):
    base_url = Config.github_url()

    headers = {
        "Authorization": f"Bearer {Config.github_token()}",
        "Accept": "application/vnd.github+json"
    }

    path = ".github/workflows/pipeline.yml"

    url = (
        f"{base_url}/repos/"
        f"{owner}/{repo}/contents/{path}"
    )

    # pega SHA se arquivo existir
    current = requests.get(
        url,
        headers=headers,
        params={"ref": branch}
    )

    sha = None

    if current.status_code == 200:
        sha = current.json()["sha"]

    payload = {
        "message": "update workflow via Pipeline Generator AI",
        "content": base64.b64encode(
            yaml_content.encode()
        ).decode(),
        "branch": branch
    }

    if sha:
        payload["sha"] = sha

    response = requests.put(
        url,
        headers=headers,
        json=payload
    )

    return response