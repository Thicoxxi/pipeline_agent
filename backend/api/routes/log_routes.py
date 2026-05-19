from flask import Blueprint, request, jsonify
from core.logger import get_logger

log_bp = Blueprint(
    "logs",
    __name__
)


@log_bp.route("/api/log", methods=["POST"])
def receive_log():
    """Recebe logs enviados por clientes (ex: VS Code extension) e grava no logger do app."""
    try:
        data = request.get_json(force=True) or {}
        level = (data.get("level") or "info").lower()
        message = data.get("message") or ""
        name = data.get("name") or "extension"
        meta = data.get("meta") or {}

        logger = get_logger("app")

        log_msg = f"[remote:{name}] {message}"
        if meta:
            log_msg = f"{log_msg} | meta={meta}"

        if level == "debug":
            logger.debug(log_msg)
        elif level == "warning" or level == "warn":
            logger.warning(log_msg)
        elif level == "error":
            logger.error(log_msg)
        else:
            logger.info(log_msg)

        return jsonify({"ok": True}), 200

    except Exception as e:
        logger = get_logger("app")
        logger.exception("Failed to receive remote log: %s", str(e))
        return jsonify({"ok": False, "error": str(e)}), 500
