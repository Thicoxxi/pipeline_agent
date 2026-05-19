import json

from services.stream_service import StreamService


class ProjectAnalyzerService:

    @staticmethod
    def analyze(
        files,
        provider="auto",
        platform="gitlab",
        entry_file: str | None = None
    ):

        summary = []

        # =====================================================
        # BUILD PROJECT CONTEXT
        # =====================================================
        for file in files:

            name = file.get("name")

            stack = file.get(
                "stack",
                "unknown"
            )

            content = file.get(
                "content",
                ""
            )[:4000]

            summary.append(
                (
                    f"\nFILE: {name}"
                    f"\nSTACK: {stack}"
                    f"\nCONTENT:\n{content}"
                )
            )

        joined = "\n".join(summary)

        # =====================================================
        # PROMPT
        # =====================================================
        extra_instruction = ""

        if entry_file:
            import os

            _, ext = os.path.splitext(entry_file)
            ext = ext.lower()

            tool_hint = None

            if ext == ".py":
                tool_hint = f"Para este projeto, gere passos usando `pyinstaller` para construir um executável a partir do arquivo {entry_file}. Inclua instalação das dependências (venv/pip) e um passo de build com pyinstaller."
            elif ext == ".go":
                tool_hint = f"Para este projeto, gere passos usando `go build` para compilar {entry_file} e produzir o binário."
            elif ext in (".java", ".jar"):
                tool_hint = f"Para este projeto, gere passos para compilar e empacotar usando Maven/Gradle apropriado para {entry_file}."
            elif ext in (".cs",):
                tool_hint = f"Para este projeto, gere passos usando `dotnet publish` para produzir o artefato a partir de {entry_file}."
            elif ext in (".js", ".ts"):
                tool_hint = f"Para este projeto, gere passos de build com npm/yarn (ex.: `npm ci` e `npm run build`) para produzir o artefato a partir do código que inclui {entry_file}."

            if tool_hint:
                extra_instruction = (
                    "USUARIO ESPECIFICOU ARQUIVO DE ENTRADA: "
                    f"{entry_file}. {tool_hint} "
                    "Detecte a linguagem e adapte as etapas de build para produzir o artefato a partir deste arquivo."
                )

        prompt = f"""
Você é um arquiteto DevOps SRE especialista em CI/CD.

Analise COMPLETAMENTE o projeto abaixo.

OBJETIVO:
Gerar EXCLUSIVAMENTE um pipeline {platform}.

IMPORTANTE:
- Gere SOMENTE pipeline para {platform}
- NÃO gere múltiplas plataformas
- NÃO gere JSON
- NÃO gere objetos
- NÃO retorne campos "gitlab" ou "github"
- NÃO use markdown
- NÃO use ```
- NÃO explique nada
- Retorne APENAS YAML puro

ANALISE:
- backend
- frontend
- framework principal
- linguagem principal
- dependências
- testes
- docker
- terraform
- kubernetes

Detecte automaticamente:
- Flask
- FastAPI
- Django
- React
- Vue
- Node.js
- Java
- Maven
- Gradle
- .NET

Use boas práticas:
- cache
- install
- lint
- test
- build
- deploy

PROJETO:

{joined}

{extra_instruction}
"""

        # =====================================================
        # STREAM RESULT
        # =====================================================
        chunks = []

        for chunk in StreamService.generate(
            prompt=prompt,
            provider=provider,
            sse=False
        ):

            if not chunk:
                continue

            chunks.append(chunk)

        result = "".join(chunks).strip()

        # =====================================================
        # CLEAN MARKDOWN
        # =====================================================
        result = result.replace(
            "```yaml",
            ""
        )

        result = result.replace(
            "```yml",
            ""
        )

        result = result.replace(
            "```",
            ""
        )

        # =====================================================
        # JSON RESPONSE FIX
        # =====================================================
        if result.startswith("{"):

            try:

                parsed = json.loads(result)

                # pega somente plataforma solicitada
                result = parsed.get(
                    platform,
                    ""
                )

            except Exception:
                pass

        # =====================================================
        # FINAL CLEAN
        # =====================================================
        result = result.encode().decode(
            "unicode_escape"
        )

        result = result.strip()

        # remove lixo comum
        if result.startswith("yaml"):
            result = result[4:].strip()

        return result