from flask import (
    Blueprint,
    request,
    jsonify
)

from services.project_analyzer_service import (
    ProjectAnalyzerService
)

from core.logger import (
    setup_logger
)

# =========================================================
# LOGGER
# =========================================================
logger = setup_logger(__name__)

# =========================================================
# BLUEPRINT
# =========================================================
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

        detected_stacks = data.get(
            "detected_stacks",
            []
        )

        # =================================================
        # VALIDATION
        # =================================================
        if not files:

            return jsonify({

                "success": False,

                "error":
                    "Nenhum arquivo enviado"

            }), 400

        logger.info(
            (
                "PROJECT ANALYSIS START | "
                "platform=%s | "
                "provider=%s | "
                "files=%s | "
                "stacks=%s"
            ),
            platform,
            provider,
            len(files),
            detected_stacks
        )

        # =================================================
        # ANALYZE
        # =================================================
        pipeline = (
            ProjectAnalyzerService.analyze(
                files=files,
                provider=provider,
                platform=platform
            )
        )

        # =================================================
        # PIPELINE CLEANUP
        # =================================================
        if isinstance(
            pipeline,
            dict
        ):

            pipeline = (

                pipeline.get("pipeline")

                or pipeline.get("gitlab")

                or pipeline.get("github")

                or ""
            )

        if not isinstance(
            pipeline,
            str
        ):

            pipeline = str(pipeline)

        pipeline = pipeline.strip()

        # remove markdown
        pipeline = pipeline.replace(
            "```yaml",
            ""
        )

        pipeline = pipeline.replace(
            "```yml",
            ""
        )

        pipeline = pipeline.replace(
            "```",
            ""
        )

        pipeline = pipeline.strip()

        # =================================================
        # EMPTY PIPELINE
        # =================================================
        if not pipeline:

            logger.error(
                "EMPTY PIPELINE GENERATED"
            )

            return jsonify({

                "success": False,

                "error":
                    "Pipeline vazia"

            }), 500

        logger.info(
            (
                "PROJECT ANALYSIS SUCCESS | "
                "platform=%s | "
                "pipeline_size=%s"
            ),
            platform,
            len(pipeline)
        )

        # =================================================
        # SUCCESS
        # =================================================
        return jsonify({

            "success": True,

            "platform": platform,

            "pipeline": pipeline

        }), 200

    except Exception as e:

        logger.exception(
            "PROJECT ANALYSIS ERROR"
        )

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500