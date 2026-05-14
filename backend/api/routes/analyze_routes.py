from flask import Blueprint, request, jsonify

from services.project_analyzer_service import (
    ProjectAnalyzerService
)

analyze_bp = Blueprint(
    "analyze",
    __name__
)


# =========================================================
# ANALYZE PROJECT
# =========================================================
@analyze_bp.route(
    "/api/analyze-project",
    methods=["POST"]
)
def analyze_project():

    try:

        data = request.get_json(force=True) or {}

        files = data.get("files", [])

        provider = data.get(
            "provider",
            "auto"
        )

        platform = data.get(
            "platform",
            "gitlab"
        )

        if not files:

            return jsonify({
                "success": False,
                "error": "Nenhum arquivo enviado"
            }), 400

        pipeline = ProjectAnalyzerService.analyze(
            files=files,
            provider=provider,
            platform=platform
        )

        return jsonify({
            "success": True,
            "pipeline": pipeline
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500