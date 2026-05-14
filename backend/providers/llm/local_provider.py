import logging

from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateNotFound
)

from providers.llm.base import (
    BaseProvider
)

logger = logging.getLogger(__name__)

# =========================================================
# PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

TEMPLATES_DIR = (
    BASE_DIR / "templates" / "pipelines"
).resolve()

# =========================================================
# TEMPLATES
# =========================================================
TEMPLATES = {

    "dotnet8":
        TEMPLATES_DIR
        / "dotnet"
        / "dotnet8.yml.j2",

    "dotnet9":
        TEMPLATES_DIR
        / "dotnet"
        / "dotnet9.yml.j2",

    "java":
        TEMPLATES_DIR
        / "java"
        / "java21.yml.j2",

    "python":
        TEMPLATES_DIR
        / "python"
        / "python312.yml.j2",

    "terraform":
        TEMPLATES_DIR
        / "terraform"
        / "terraform.yml.j2",
}

# =========================================================
# JINJA
# =========================================================
env = Environment(

    loader=FileSystemLoader(
        str(TEMPLATES_DIR)
    ),

    trim_blocks=True,

    lstrip_blocks=True
)


class LocalProvider(BaseProvider):

    def detect_stack(
        self,
        prompt: str
    ) -> str:

        p = prompt.lower()

        if "dotnet 8" in p:
            return "dotnet8"

        if "dotnet 9" in p:
            return "dotnet9"

        if "java" in p:
            return "java"

        if "python" in p:
            return "python"

        if "terraform" in p:
            return "terraform"

        return "unknown"

    def render_template(
        self,
        path: Path
    ) -> str:

        try:

            rel = path.relative_to(
                TEMPLATES_DIR
            )

            template_name = rel.as_posix()

            logger.info(
                f"[LOAD] template "
                f"{template_name}"
            )

            return env.get_template(
                template_name
            ).render()

        except TemplateNotFound as e:

            logger.error(
                f"[ERROR] template: {e}"
            )

            raise

    def stream(
        self,
        prompt: str
    ):

        stack = self.detect_stack(
            prompt
        )

        logger.info(
            f"[STACK] detectada: {stack}"
        )

        if stack in TEMPLATES:

            try:

                content = self.render_template(
                    TEMPLATES[stack]
                )

            except Exception:

                content = """
stages:
  - build

build:
  stage: build
  script:
    - echo "fallback local"
"""

        else:

            content = """
stages:
  - build

build:
  stage: build
  script:
    - echo "fallback local"
"""

        for c in content:
            yield c