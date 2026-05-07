import requests

from config import Config

BASE_URL = Config.gitlab_url()

HEADERS = {
    "PRIVATE-TOKEN": Config.gitlab_token()
}


def create_or_update_pipeline(
    project_id: str,
    branch: str,
    yaml_content: str
):

    file_path = ".gitlab-ci.yml"

    url = (
        f"{BASE_URL}/projects/"
        f"{project_id}/repository/files/"
        f"{file_path.replace('/', '%2F')}"
    )

    payload = {
        "branch": branch,
        "content": yaml_content,
        "commit_message": "update pipeline via Pipeline Generator AI"
    }

    # tenta atualizar
    response = requests.put(
        url,
        headers=HEADERS,
        json=payload
    )

    # arquivo não existe → cria
    if response.status_code == 400:

        response = requests.post(
            url,
            headers=HEADERS,
            json=payload
        )

    return response