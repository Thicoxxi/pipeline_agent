from services.yaml_service import YamlService


class PipelineService:

    @staticmethod
    def build_response(full_text: str):

        cleaned = YamlService.clean(
            full_text
        )

        valid, validation_msg = (
            YamlService.validate(cleaned)
        )

        pipeline_type = (
            YamlService.detect_type(cleaned)
        )

        return {

            "validation": validation_msg,

            "valid": valid,

            "type": pipeline_type,

            "yaml": cleaned
        }