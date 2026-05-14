import logging

from flask import Blueprint, request, jsonify

from core.config import Config
from providers.scm.gitlab_client import create_or_update_pipeline

logger = logging.getLogger(__name__)

gitlab_bp = Blueprint("gitlab", __name__)


# =========================================================
# APPLY GITLAB PIPELINE
# =========================================================
@gitlab_bp.route("/api/gitlab/apply", methods=["POST"])
def apply_gitlab_pipeline():
    try:
        data = request.get_json(force=True) or {}

        project_id = (data.get("project_id") or "").strip()
        branch = (data.get("branch") or "main").strip()
        yaml_content = data.get("yaml") or ""

        # =====================================================
        # VALIDATION
        # =====================================================
        if not project_id:
            return jsonify({
                "success": False,
                "error": "GitLab project_id é obrigatório"
            }), 400

        if not yaml_content.strip():
            return jsonify({
                "success": False,
                "error": "YAML vazio"
            }), 400

        # =====================================================
        # CONFIG CHECK
        # =====================================================
        if not getattr(Config, "GITLAB_TOKEN", None):
            return jsonify({
                "success": False,
                "error": "GITLAB_TOKEN não configurado"
            }), 500

        # =====================================================
        # APPLY
        # =====================================================
        result = create_or_update_pipeline(
            project_id=project_id,
            branch=branch,
            yaml_content=yaml_content
        )

        return jsonify({
            "success": True,
            "message": "Pipeline aplicada com sucesso no GitLab",
            "data": result
        }), 200

    except Exception as e:
        logger.exception("Erro no apply_gitlab_pipeline")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500