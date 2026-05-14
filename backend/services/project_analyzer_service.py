from services.stream_service import StreamService


class ProjectAnalyzerService:

    @staticmethod
    def analyze(
        files,
        provider="auto",
        platform="gitlab"
    ):

        summary = []

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

        prompt = f"""
Você é um arquiteto DevOps SRE especialista em CI/CD.

Analise COMPLETAMENTE o projeto abaixo.

Detecte corretamente:

- backend principal
- frontend web
- framework principal
- linguagem principal
- dependências
- testes
- docker
- kubernetes
- terraform
- build tools
- package managers

IMPORTANTE:

- HTML/CSS/JS em /static ou /templates NÃO significa Node.js
- só considere Node.js se existir package.json
- Flask usa frontend estático frequentemente
- detectar corretamente projetos Flask
- detectar corretamente frontend web simples

REGRAS:

- retornar SOMENTE YAML
- NÃO retornar JSON
- NÃO retornar markdown
- NÃO usar ```
- NÃO explicar nada
- gerar pipeline REAL baseado nos arquivos
- usar boas práticas CI/CD

PROJETO:

{joined}
"""

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

        return result.strip()