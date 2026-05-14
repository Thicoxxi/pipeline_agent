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

    if not token:
        return {
            "success": False,
            "error": "GITHUB_TOKEN não configurado",
            "status_code": 500
        }

    workflow_path = ".github/workflows/pipeline.yml"

    url = (
        f"{base_url}/repos/"
        f"{owner}/{repo}/contents/"
        f"{workflow_path}"
    )

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    # =====================================================
    # CHECK FILE EXISTS
    # =====================================================
    check = requests.get(
        url,
        headers=headers,
        params={"ref": branch}
    )

    sha = None
    if check.status_code == 200:
        sha = check.json().get("sha")

    # =====================================================
    # PAYLOAD
    # =====================================================
    payload = {
        "message": "update github actions workflow",
        "content": base64.b64encode(
            yaml_content.encode("utf-8")
        ).decode("utf-8"),
        "branch": branch
    }

    if sha:
        payload["sha"] = sha

    # =====================================================
    # REQUEST
    # =====================================================
    try:
        response = requests.put(
            url,
            headers=headers,
            json=payload
        )

        if response.ok:
            return {
                "success": True,
                "data": response.json(),
                "status_code": 200
            }

        return {
            "success": False,
            "error": response.text,
            "status_code": response.status_code
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": 500
        }