import requests

from core.config import Config


# =========================================================
# CREATE OR UPDATE PIPELINE
# =========================================================
def create_or_update_pipeline(

    project_id: str,

    branch: str,

    yaml_content: str
):

    base_url = Config.GITLAB_URL.rstrip("/")

    token = Config.GITLAB_TOKEN

    url = (
        f"{base_url}"
        f"/api/v4/projects/{project_id}"
        f"/repository/files/.gitlab-ci.yml"
    )

    headers = {

        "PRIVATE-TOKEN": token
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

    # =====================================================
    # UPDATE
    # =====================================================
    if check.status_code == 200:

        payload = {

            "branch": branch,

            "content": yaml_content,

            "commit_message":
                "update pipeline"
        }

        response = requests.put(

            url,

            headers=headers,

            json=payload
        )

    # =====================================================
    # CREATE
    # =====================================================
    else:

        payload = {

            "branch": branch,

            "content": yaml_content,

            "commit_message":
                "create pipeline"
        }

        response = requests.post(

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

        f"GitLab Error: "
        f"{response.status_code} - "
        f"{response.text}"
    )