from flask import (
    Blueprint,
    request,
    Response
)

from services.stream_service import (
    StreamService
)

stream_bp = Blueprint(
    "stream",
    __name__
)

# =========================================================
# STREAM
# =========================================================
@stream_bp.route(
    "/api/stream",
    methods=["POST"]
)
def stream():

    data = request.get_json(
        force=True
    )

    prompt = data.get(
        "prompt",
        ""
    ).strip()

    provider = data.get(
        "provider",
        "auto"
    )

    if not prompt:

        return {
            "error": "Prompt vazio"
        }, 400

    return Response(

        StreamService.generate(
            prompt,
            provider
        ),

        mimetype="text/event-stream"
    )