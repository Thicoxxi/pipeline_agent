from flask import (
    Blueprint,
    request
)

from core.config import Config

from services.yaml_service import (
    YamlService
)

from providers.scm.github_client import (
    create_or_update_workflow
)

github_bp = Blueprint(
    "github",
    __name__
)

# =========================================================
# APPLY GITHUB
# =========================================================
@github_bp.route(
    "/api/github/apply",
    methods=["POST"]
)
def apply_github_pipeline():

    data = request.get_json(
        force=True
    )

    owner = data.get("owner")

    repo = data.get("repo")

    branch = data.get(
        "branch",
        "main"
    )

    yaml_content = data.get(
        "yaml",
        ""
    )

    # =====================================================
    # CONFIG
    # =====================================================
    if not Config.has_github():

        return {

            "success": False,

            "error": (
                "GITHUB_TOKEN nao configurado"
            )

        }, 500

    # =====================================================
    # VALIDATION
    # =====================================================
    valid, validation_msg = (
        YamlService.validate(
            yaml_content
        )
    )

    if not valid:

        return {

            "success": False,

            "error": validation_msg

        }, 400

    # =====================================================
    # APPLY
    # =====================================================
    response = create_or_update_workflow(

        owner=owner,

        repo=repo,

        branch=branch,

        yaml_content=yaml_content
    )

    if response.ok:

        return {

            "success": True
        }

    return {

        "success": False,

        "error": response.text

    }, response.status_code