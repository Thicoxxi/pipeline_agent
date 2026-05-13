import yaml


class YamlService:

    # =====================================================
    # VALIDATE YAML
    # =====================================================
    @staticmethod
    def validate(yaml_text: str):

        try:

            yaml.safe_load(
                yaml_text
            )

            return (
                True,
                "YAML válido"
            )

        except yaml.YAMLError as e:

            return (
                False,
                str(e)
            )

    # =====================================================
    # CLEAN YAML
    # =====================================================
    @staticmethod
    def clean(text: str):

        if not text:

            return ""

        # remove markdown
        text = text.replace(
            "```yaml",
            ""
        )

        text = text.replace(
            "```yml",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        return text.strip()

    # =====================================================
    # DETECT TYPE
    # =====================================================
    @staticmethod
    def detect_type(yaml_text: str):

        text = yaml_text.lower()

        if "stages:" in text:

            return "gitlab"

        if "jobs:" in text:

            return "github"

        return "unknown"