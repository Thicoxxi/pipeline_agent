from flask import Blueprint, request, jsonify

from core.config import Config
from services.yaml_service import YamlService
from providers.scm.github_client import create_or_update_workflow

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
        yaml_content = (data.get("yaml") or "").strip()

        # =====================================================
        # DEBUG (REMOVE EM PRODUÇÃO SE QUISER)
        # =====================================================
        print("[DEBUG] payload:", data)
        print("[DEBUG] owner:", owner)
        print("[DEBUG] repo:", repo)
        print("[DEBUG] yaml length:", len(yaml_content))

        # =====================================================
        # VALIDATION DETAIL (MELHORADO)
        # =====================================================
        missing_fields = []

        if not owner:
            missing_fields.append("owner")

        if not repo:
            missing_fields.append("repo")

        if not yaml_content:
            missing_fields.append("yaml")

        if missing_fields:
            return jsonify({
                "success": False,
                "error": "Campos obrigatórios ausentes",
                "missing_fields": missing_fields
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
        result = create_or_update_workflow(
            owner=owner,
            repo=repo,
            branch=branch,
            yaml_content=yaml_content
        )

        # =====================================================
        # RESPONSE PATTERN (DICT STANDARD)
        # =====================================================
        if result.get("success"):
            return jsonify({
                "success": True,
                "message": "Workflow aplicado com sucesso no GitHub",
                "data": result.get("data")
            }), 200

        return jsonify({
            "success": False,
            "error": result.get("error", "Erro desconhecido no GitHub"),
            "data": result.get("data")
        }), result.get("status_code", 400)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500