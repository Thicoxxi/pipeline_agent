import base64

import requests

from core.config import Config


# =========================================================
# CREATE OR UPDATE WORKFLOW
# =========================================================
def create_or_update_workflow(

    owner: str,

    repo: str,

    branch: str,

    yaml_content: str
):

    base_url = Config.GITHUB_API_URL.rstrip("/")

    token = Config.GITHUB_TOKEN

    workflow_path = (
        ".github/workflows/"
        "pipeline.yml"
    )

    url = (
        f"{base_url}/repos/"
        f"{owner}/{repo}/contents/"
        f"{workflow_path}"
    )

    headers = {

        "Authorization":
            f"Bearer {token}",

        "Accept":
            "application/vnd.github+json"
    }

    # =====================================================
    # CHECK FILE
    # =====================================================
    check = requests.get(

        url,

        headers=headers,

        params={
            "ref": branch
        }
    )

    sha = None

    if check.status_code == 200:

        sha = check.json().get("sha")

    # =====================================================
    # PAYLOAD
    # =====================================================
    payload = {

        "message":
            "update github actions workflow",

        "content":
            base64.b64encode(
                yaml_content.encode()
            ).decode(),

        "branch":
            branch
    }

    # =====================================================
    # UPDATE
    # =====================================================
    if sha:

        payload["sha"] = sha

    # =====================================================
    # CREATE/UPDATE
    # =====================================================
    response = requests.put(

        url,

        headers=headers,

        json=payload
    )

    # =====================================================
    # RESULT
    # =====================================================
    if response.ok:

        return response.json()

    raise Exception(

        f"GitHub Error: "
        f"{response.status_code} - "
        f"{response.text}"
    )