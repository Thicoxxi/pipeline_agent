import json
import logging

from llm_agent import stream_llm

logger = logging.getLogger(__name__)


class StreamService:

    @staticmethod
    def generate(
        prompt: str,
        provider: str = "auto",
        sse: bool = True
    ):

        try:

            logger.info(
                "[STREAM] iniciando geração"
            )

            for event in stream_llm(
                prompt,
                provider
            ):

                # =====================================
                # FRONTEND SSE
                # =====================================
                if sse:

                    payload = json.dumps(event)

                    yield f"data: {payload}\n\n"

                # =====================================
                # INTERNAL RAW
                # =====================================
                else:

                    if isinstance(event, dict):

                        if event.get("gitlab"):
                            yield event["gitlab"]

                        elif event.get("github"):
                            yield event["github"]

                        elif event.get("content"):
                            yield event["content"]

                    else:
                        yield str(event)

            logger.info(
                "[STREAM] finalizado"
            )

        except Exception as e:

            logger.exception(
                "[STREAM ERROR]"
            )

            if sse:

                error_payload = json.dumps({
                    "error": str(e)
                })

                yield (
                    f"data: {error_payload}\n\n"
                )

            else:

                raise