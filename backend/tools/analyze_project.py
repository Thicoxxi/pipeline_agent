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
    "obj",
    "logs"
}

# =========================================================
# LIMITS
# =========================================================
MAX_FILES = 30
MAX_FILE_SIZE = 4000

# =========================================================
# IMPORTANT FILES
# =========================================================
IMPORTANT_FILES = {
    # python
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "Pipfile",
    "pytest.ini",

    # node
    "package.json",

    # java
    "pom.xml",
    "build.gradle",

    # dotnet
    "*.csproj",
    "*.sln",

    # docker
    "Dockerfile",
    "docker-compose.yml",

    # terraform
    "main.tf",

    # kubernetes
    "deployment.yml",
    "deployment.yaml",
}

# =========================================================
# IGNORE CHECK
# =========================================================
def should_ignore(path: Path):

    return any(
        ignored in path.parts
        for ignored in IGNORE_DIRS
    )

# =========================================================
# STACK DETECTION
# =========================================================
def detect_stack(path: Path):

    # =====================================================
    # PYTHON
    # =====================================================
    if path.suffix == ".py":
        return "python"

    if path.name in {
        "requirements.txt",
        "pyproject.toml",
        "poetry.lock",
        "Pipfile"
    }:
        return "python"

    # =====================================================
    # FRONTEND WEB
    # =====================================================
    if path.suffix in {
        ".html",
        ".css",
        ".js"
    }:

        if "static" in path.parts:
            return "frontend"

        if "templates" in path.parts:
            return "frontend"

    # =====================================================
    # NODE
    # =====================================================
    if path.name == "package.json":
        return "node"

    # =====================================================
    # JAVA
    # =====================================================
    if path.name in {
        "pom.xml",
        "build.gradle"
    }:
        return "java"

    # =====================================================
    # DOTNET
    # =====================================================
    if path.name.endswith(".csproj"):
        return "dotnet"

    if path.name.endswith(".sln"):
        return "dotnet"

    # =====================================================
    # DOCKER
    # =====================================================
    if path.name == "Dockerfile":
        return "docker"

    if path.name in {
        "docker-compose.yml",
        "docker-compose.yaml"
    }:
        return "docker"

    # =====================================================
    # TERRAFORM
    # =====================================================
    if path.name == "main.tf":
        return "terraform"

    # =====================================================
    # KUBERNETES
    # =====================================================
    if path.name in {
        "deployment.yml",
        "deployment.yaml"
    }:
        return "kubernetes"

    return None

# =========================================================
# FILE PRIORITY
# =========================================================
def is_important_file(path: Path):

    if path.name in IMPORTANT_FILES:
        return True

    if path.name.endswith(".csproj"):
        return True

    if path.name.endswith(".sln"):
        return True

    return False

# =========================================================
# SCAN PROJECT
# =========================================================
def scan_project():

    files = []

    detected_stacks = set()

    print("\n🔍 scanning project...\n")

    for path in BASE_DIR.rglob("*"):

        if not path.is_file():
            continue

        if should_ignore(path):
            continue

        stack = detect_stack(path)

        if not stack:
            continue

        detected_stacks.add(stack)

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

            # prioridade maior para arquivos importantes
            max_size = (
                8000
                if is_important_file(path)
                else MAX_FILE_SIZE
            )

            files.append({
                "name": relative_path,
                "stack": stack,
                "content": content[:max_size]
            })

        except Exception as e:

            print(
                f"❌ failed reading {path}: {e}"
            )

    return files[:MAX_FILES], detected_stacks

# =========================================================
# EXTRACT PIPELINE
# =========================================================
def extract_pipeline(response):

    raw = response.text.strip()

    print("\n[DEBUG] raw backend response:\n")
    print(raw)

    if raw.startswith("data:"):
        raw = raw.replace("data:", "").strip()

    try:

        data = json.loads(raw)

        pipeline = (
            data.get("pipeline")
            or data.get("gitlab")
            or data.get("github")
            or ""
        )

    except Exception:

        pipeline = raw

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
def analyze_project(platform="gitlab"):

    files, stacks = scan_project()

    if not files:

        print("\n❌ no supported files found\n")
        return

    print("\n🧠 detected stacks:\n")

    for stack in sorted(stacks):
        print(f" - {stack}")

    print("\n🚀 sending files to analyzer...\n")

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

        pipeline = extract_pipeline(response)

        if not pipeline:

            print("\n❌ analyzer error:\n")
            print(response.text)
            return

        print("\n=================================================")
        print(f" GENERATED {platform.upper()} PIPELINE ")
        print("=================================================\n")

        print(pipeline)

        output_file = (
            ".gitlab-ci.yml"
            if platform == "gitlab"
            else ".github/workflows/pipeline.yml"
        )

        output_path = BASE_DIR / output_file

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

        print(f"\n❌ request error: {e}\n")

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

        print("\n❌ invalid platform\n")

    else:

        analyze_project(selected)