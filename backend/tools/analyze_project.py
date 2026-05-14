from pathlib import Path
import json

import requests

# =========================================================
# CONFIG
# =========================================================
API_URL = "http://localhost:5000"

# =========================================================
# PROJECT ROOT
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent

print("\n=================================================")
print("📁 PROJECT ROOT:", BASE_DIR)
print("=================================================\n")

# =========================================================
# IGNORE DIRECTORIES
# =========================================================
IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".idea",
    ".vscode",
    "coverage",
    "bin",
    "obj"
}

# =========================================================
# FILE RULES
# =========================================================
STACK_RULES = {

    # =====================================================
    # PYTHON
    # =====================================================
    "python": {

        "files": {
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-prod.txt",
            "pyproject.toml",
            "poetry.lock",
            "pytest.ini",
            "Pipfile",
            "manage.py",
            "app.py",
            "main.py",
            "wsgi.py"
        },

        "extensions": {
            ".py"
        },

        "important_dirs": {
            "services",
            "providers",
            "api",
            "core",
            "tests"
        }
    },

    # =====================================================
    # NODE
    # =====================================================
    "node": {

        "files": {
            "package.json",
            "package-lock.json",
            "yarn.lock",
            "tsconfig.json",
            "vite.config.js",
            "next.config.js"
        },

        "extensions": {
            ".js",
            ".ts"
        },

        "important_dirs": {
            "src",
            "pages",
            "components",
            "server",
            "api"
        }
    },

    # =====================================================
    # JAVA
    # =====================================================
    "java": {

        "files": {
            "pom.xml",
            "build.gradle",
            "gradlew"
        },

        "extensions": {
            ".java"
        },

        "important_dirs": {
            "src"
        }
    },

    # =====================================================
    # DOTNET
    # =====================================================
    "dotnet": {

        "files": {
            "*.csproj",
            "*.sln",
            "NuGet.config"
        },

        "extensions": {
            ".cs"
        },

        "important_dirs": {
            "Controllers",
            "Services",
            "Models"
        }
    },

    # =====================================================
    # DOCKER
    # =====================================================
    "docker": {

        "files": {
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml"
        },

        "extensions": set(),

        "important_dirs": set()
    },

    # =====================================================
    # TERRAFORM
    # =====================================================
    "terraform": {

        "files": {
            "main.tf",
            "variables.tf",
            "outputs.tf"
        },

        "extensions": {
            ".tf"
        },

        "important_dirs": {
            "terraform"
        }
    },

    # =====================================================
    # KUBERNETES
    # =====================================================
    "kubernetes": {

        "files": {
            "deployment.yml",
            "deployment.yaml",
            "service.yml",
            "service.yaml",
            "ingress.yml",
            "ingress.yaml"
        },

        "extensions": {
            ".yaml",
            ".yml"
        },

        "important_dirs": {
            "k8s",
            "kubernetes"
        }
    }
}

# =========================================================
# LIMITS
# =========================================================
MAX_FILES = 25
MAX_FILE_SIZE = 4000


# =========================================================
# IGNORE CHECK
# =========================================================
def should_ignore(path: Path):

    return any(
        ignored in path.parts
        for ignored in IGNORE_DIRS
    )


# =========================================================
# STACK MATCHER
# =========================================================
def match_stack(path: Path):

    for stack, rules in STACK_RULES.items():

        # =================================================
        # EXACT FILES
        # =================================================
        if path.name in rules["files"]:
            return stack

        # =================================================
        # WILDCARDS
        # =================================================
        if "*.csproj" in rules["files"]:
            if path.name.endswith(".csproj"):
                return stack

        if "*.sln" in rules["files"]:
            if path.name.endswith(".sln"):
                return stack

        # =================================================
        # EXTENSIONS
        # =================================================
        if path.suffix in rules["extensions"]:
            return stack

        # =================================================
        # IMPORTANT DIRS
        # =================================================
        if any(
            directory in path.parts
            for directory in rules["important_dirs"]
        ):
            return stack

    return None


# =========================================================
# SCAN PROJECT
# =========================================================
def scan_project():

    files = []

    detected_stacks = set()

    print("\n🔍 scanning project...\n")

    for path in BASE_DIR.rglob("*"):

        # =================================================
        # FILE ONLY
        # =================================================
        if not path.is_file():
            continue

        # =================================================
        # IGNORE
        # =================================================
        if should_ignore(path):
            continue

        # =================================================
        # STACK DETECTION
        # =================================================
        stack = match_stack(path)

        if not stack:
            continue

        detected_stacks.add(stack)

        # =================================================
        # FILE LIMIT
        # =================================================
        if len(files) >= MAX_FILES:
            continue

        try:

            relative_path = str(
                path.relative_to(BASE_DIR)
            )

            print(
                f"✔ [{stack.upper()}] {relative_path}"
            )

            content = path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            files.append({

                "name": relative_path,

                "stack": stack,

                "content": content[:MAX_FILE_SIZE]
            })

        except Exception as e:

            print(
                f"❌ failed reading {path}: {e}"
            )

    return files, detected_stacks


# =========================================================
# EXTRACT PIPELINE
# =========================================================
def extract_pipeline(response):

    raw = response.text.strip()

    # =====================================================
    # DEBUG
    # =====================================================
    print("\n[DEBUG] raw backend response:\n")
    print(raw)

    # =====================================================
    # REMOVE SSE PREFIX
    # =====================================================
    if raw.startswith("data:"):

        raw = raw[len("data:"):].strip()

    # =====================================================
    # TRY JSON
    # =====================================================
    try:

        data = json.loads(raw)

        pipeline = (
            data.get("pipeline")
            or data.get("gitlab")
            or data.get("github")
            or ""
        )

    except Exception:

        # fallback texto puro
        pipeline = raw

    # =====================================================
    # CLEAN MARKDOWN
    # =====================================================
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

    return pipeline.strip()


# =========================================================
# ANALYZE PROJECT
# =========================================================
def analyze_project(
    platform="gitlab"
):

    files, stacks = scan_project()

    # =====================================================
    # NO FILES
    # =====================================================
    if not files:

        print(
            "\n❌ no supported files found\n"
        )

        return

    # =====================================================
    # STACK SUMMARY
    # =====================================================
    print(
        "\n🧠 detected stacks:\n"
    )

    for stack in sorted(stacks):

        print(
            f" - {stack}"
        )

    print(
        "\n🚀 sending files to analyzer...\n"
    )

    try:

        response = requests.post(

            f"{API_URL}/api/analyze-project",

            json={

                "files": files,

                "platform": platform,

                "detected_stacks": list(stacks),

                "provider": "auto"
            },

            timeout=180
        )

        # =================================================
        # PIPELINE EXTRACTION
        # =================================================
        pipeline = extract_pipeline(response)

        # =================================================
        # ERROR
        # =================================================
        if not pipeline:

            print(
                "\n❌ analyzer error:\n"
            )

            print(
                response.text
            )

            return

        # =================================================
        # SUCCESS
        # =================================================
        print(
            "\n================================================="
        )

        print(
            f" GENERATED {platform.upper()} PIPELINE "
        )

        print(
            "=================================================\n"
        )

        print(
            pipeline
        )

        # =================================================
        # OUTPUT FILE
        # =================================================
        output_file = (

            ".gitlab-ci.yml"

            if platform == "gitlab"

            else ".github/workflows/pipeline.yml"
        )

        output_path = (
            BASE_DIR / output_file
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path.write_text(
            pipeline,
            encoding="utf-8"
        )

        print(
            f"\n💾 pipeline saved to:\n{output_path}\n"
        )

    except Exception as e:

        print(
            f"\n❌ request error: {e}\n"
        )


# =========================================================
# DIRECT EXECUTION
# =========================================================
if __name__ == "__main__":

    selected = input(
        "\nPlatform (gitlab/github): "
    ).strip().lower()

    if selected not in [
        "gitlab",
        "github"
    ]:

        print(
            "\n❌ invalid platform\n"
        )

    else:

        analyze_project(selected)