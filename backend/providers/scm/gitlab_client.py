import requests

from core.config import Config


# =========================================================
# GITLAB API
# =========================================================
BASE_URL = (
    Config.GITLAB_API_URL.rstrip("/")
)

TOKEN = (
    Config.GITLAB_TOKEN
)


# =========================================================
# CREATE OR UPDATE PIPELINE
# =========================================================
def create_or_update_pipeline(
    project_id: str,
    branch: str,
    yaml_content: str
):

    # =====================================================
    # URL
    # =====================================================
    url = (
        f"{BASE_URL}/projects/"
        f"{project_id}/repository/files/"
        f".gitlab-ci.yml"
    )

    headers = {
        "PRIVATE-TOKEN": TOKEN
    }

    # =====================================================
    # CHECK FILE
    # =====================================================
    check_response = requests.get(
        url,
        headers=headers,
        params={
            "ref": branch
        }
    )

    # =====================================================
    # FILE EXISTS -> UPDATE
    # =====================================================
    if check_response.status_code == 200:

        payload = {
            "branch": branch,
            "content": yaml_content,
            "commit_message":
                "update gitlab pipeline"
        }

        response = requests.put(
            url,
            headers=headers,
            json=payload
        )

    # =====================================================
    # FILE DOES NOT EXIST -> CREATE
    # =====================================================
    elif check_response.status_code == 404:

        payload = {
            "branch": branch,
            "content": yaml_content,
            "commit_message":
                "create gitlab pipeline"
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

    # =====================================================
    # OTHER ERROR
    # =====================================================
    else:

        raise Exception(
            f"GitLab Error: "
            f"{check_response.status_code} - "
            f"{check_response.text}"
        )

    # =====================================================
    # RESULT
    # =====================================================
    if response.ok:

        return response.json()

    raise Exception(
        f"GitLab Error: "
        f"{response.status_code} - "
        f"{response.text}"
    )