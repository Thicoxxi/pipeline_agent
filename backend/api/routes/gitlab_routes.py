from flask import (
    Blueprint,
    request,
    jsonify
)

from core.config import Config

from providers.scm.gitlab_client import (
    create_or_update_pipeline
)

gitlab_bp = Blueprint(
    "gitlab",
    __name__
)

# =========================================================
# APPLY GITLAB PIPELINE
# =========================================================
@gitlab_bp.route(
    "/api/gitlab/apply",
    methods=["POST"]
)
def apply_gitlab_pipeline():

    try:

        data = request.get_json(force=True)

        project_id = (
            data.get("project_id", "")
            .strip()
        )

        branch = (
            data.get("branch", "main")
            .strip()
        )

        yaml_content = data.get(
            "yaml",
            ""
        )

        # =================================================
        # VALIDATION
        # =================================================
        if not project_id:

            return jsonify({
                "error":
                    "GitLab Project ID é obrigatório"
            }), 400

        if not yaml_content:

            return jsonify({
                "error":
                    "YAML vazio"
            }), 400

        # =================================================
        # TOKEN
        # =================================================
        if not getattr(Config, "GITLAB_TOKEN", None):

            return jsonify({
                "error":
                    "GITLAB_TOKEN não configurado"
            }), 500

        # =================================================
        # APPLY
        # =================================================
        result = create_or_update_pipeline(
            project_id=project_id,
            branch=branch,
            yaml_content=yaml_content
        )

        return jsonify({
            "success": True,
            "message":
                "✅ Pipeline aplicada com sucesso no GitLab",
            "data": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500