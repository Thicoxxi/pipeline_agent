import json
import logging

from llm_agent import stream_llm

logger = logging.getLogger(__name__)

# =========================================================
# STREAM SERVICE
# =========================================================
class StreamService:

    # =====================================================
    # GENERATE
    # =====================================================
    @staticmethod
    def generate(
        prompt: str,
        provider: str = "auto"
    ):

        try:

            logger.info(
                "[STREAM] iniciando geração"
            )

            # =================================================
            # STREAM LLM
            # =================================================
            for event in stream_llm(
                prompt,
                provider
            ):

                logger.info(
                    f"[STREAM EVENT] {event}"
                )

                # =============================================
                # SSE FORMAT
                # =============================================
                payload = json.dumps(event)

                yield (
                    f"data: {payload}\n\n"
                )

            logger.info(
                "[STREAM] finalizado"
            )

        except Exception as e:

            logger.exception(
                "[STREAM ERROR]"
            )

            error_payload = json.dumps({
                "error": str(e)
            })

            yield (
                f"data: {error_payload}\n\n"
            )