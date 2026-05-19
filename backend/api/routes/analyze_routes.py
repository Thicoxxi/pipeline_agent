from flask import Blueprint, request

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

        data = request.get_json(
            force=True
        ) or {}

        files = data.get(
            "files",
            []
        )

        provider = data.get(
            "provider",
            "auto"
        )

        platform = data.get(
            "platform",
            "gitlab"
        )

        entry = data.get(
            "entry",
            None
        )

        if not files:

            return (
                "No files provided",
                400,
                {
                    "Content-Type": "text/plain"
                }
            )

        result = ProjectAnalyzerService.analyze(
            files=files,
            provider=provider,
            platform=platform,
            entry_file=entry
        )

        # =====================================================
        # RETURN PURE YAML
        # =====================================================
        return (
            result,
            200,
            {
                "Content-Type": "text/plain"
            }
        )

    except Exception as e:

        return (
            str(e),
            500,
            {
                "Content-Type": "text/plain"
            }
        )