import logging

from flask import Blueprint, request, jsonify

from core.config import Config
from services.yaml_service import YamlService
from providers.scm.github_client import create_or_update_workflow

logger = logging.getLogger(__name__)

github_bp = Blueprint("github", __name__)


# =========================================================
# APPLY GITHUB PIPELINE
# =========================================================
@github_bp.route("/api/github/apply", methods=["POST"])
def apply_github_pipeline():
    try:
        data = request.get_json(force=True) or {}

        owner = (data.get("owner") or "").strip()
        repo = (data.get("repo") or "").strip()
        branch = (data.get("branch") or "main").strip()
        yaml_content = data.get("yaml") or ""

        # =====================================================
        # VALIDATION BASIC
        # =====================================================
        if not owner or not repo:
            return jsonify({
                "success": False,
                "error": "owner e repo são obrigatórios"
            }), 400

        if not yaml_content.strip():
            return jsonify({
                "success": False,
                "error": "YAML vazio"
            }), 400

        # =====================================================
        # CONFIG CHECK
        # =====================================================
        if not Config.has_github():
            return jsonify({
                "success": False,
                "error": "GITHUB_TOKEN não configurado"
            }), 500

        # =====================================================
        # YAML VALIDATION
        # =====================================================
        valid, validation_msg = YamlService.validate(yaml_content)

        if not valid:
            return jsonify({
                "success": False,
                "error": validation_msg
            }), 400

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
            return jsonify({
                "success": True,
                "message": "Workflow aplicado com sucesso no GitHub"
            }), 200

        return jsonify({
            "success": False,
            "error": response.text
        }), response.status_code

    except Exception as e:
        logger.exception("Erro no apply_github_pipeline")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500