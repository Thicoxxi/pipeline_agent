import logging

from flask import Blueprint, request, Response, jsonify

from services.stream_service import StreamService

logger = logging.getLogger(__name__)

stream_bp = Blueprint("stream", __name__)


# =========================================================
# STREAM LLM
# =========================================================
@stream_bp.route("/api/stream", methods=["POST"])
def stream():
    try:
        data = request.get_json(force=True) or {}

        prompt = (data.get("prompt") or "").strip()
        provider = (data.get("provider") or "auto").strip().lower()

        # =====================================================
        # VALIDATION
        # =====================================================
        if not prompt:
            return jsonify({
                "error": "Prompt vazio"
            }), 400

        # =====================================================
        # STREAM RESPONSE
        # =====================================================
        return Response(
            StreamService.generate(prompt, provider),
            mimetype="text/event-stream"
        )

    except Exception as e:
        logger.exception("Erro no stream endpoint")
        return jsonify({
            "error": str(e)
        }), 500