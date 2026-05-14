from services.stream_service import StreamService


class ProjectAnalyzerService:

    @staticmethod
    def analyze(
        files,
        provider="auto",
        platform="gitlab"
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
        prompt = f"""
Você é um arquiteto DevOps SRE especialista em CI/CD.

Sua tarefa é analisar COMPLETAMENTE um projeto real
e gerar um pipeline profissional para {platform}.

ANÁLISE O PROJETO COMO UM TODO.

Detecte automaticamente:

- backend
- frontend
- framework principal
- linguagem principal
- testes
- docker
- terraform
- kubernetes
- build tools
- package managers
- dependências

EXEMPLOS:
- Flask
- FastAPI
- Django
- React
- Vue
- Next.js
- Node.js
- Java
- Maven
- Gradle
- .NET
- Terraform
- Docker

REGRAS OBRIGATÓRIAS:

- retornar SOMENTE YAML
- NÃO retornar JSON
- NÃO retornar markdown
- NÃO usar ```
- NÃO explicar nada
- NÃO adicionar comentários fora do YAML
- gerar pipeline REAL baseado nos arquivos
- usar boas práticas CI/CD
- usar cache quando apropriado
- usar install/test/build/deploy
- detectar corretamente o tipo do projeto

PROJETO:

{joined}
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
        # CLEAN JSON RESPONSE
        # =====================================================
        if result.startswith("{"):

            # remove wrapper json
            if '"gitlab":' in result:

                result = result.split(
                    '"gitlab":',
                    1
                )[1]

            elif '"github":' in result:

                result = result.split(
                    '"github":',
                    1
                )[1]

            result = result.strip()

            # remove aspas iniciais
            if result.startswith('"'):
                result = result[1:]

            # remove fechamento
            if result.endswith('"}'):
                result = result[:-2]

            # decode \n
            result = result.encode().decode(
                "unicode_escape"
            )

        # =====================================================
        # FINAL CLEAN
        # =====================================================
        result = result.strip()

        # remove lixo comum
        if result.startswith("yaml"):
            result = result[4:].strip()

        return result