from flask import Blueprint, request, Response

from services.stream_service import StreamService

stream_bp = Blueprint(
    "stream",
    __name__
)


@stream_bp.route(
    "/api/stream",
    methods=["POST"]
)
def stream():

    data = request.get_json(force=True) or {}

    prompt = data.get("prompt", "")

    provider = data.get(
        "provider",
        "auto"
    )

    return Response(
        StreamService.generate(
            prompt=prompt,
            provider=provider,
            sse=True
        ),
        mimetype="text/event-stream"
    )