from services.stream_service import StreamService


class ProjectAnalyzerService:

    @staticmethod
    def analyze(
        files,
        provider="auto",
        platform="gitlab"
    ):

        # =====================================================
        # BUILD PROJECT SUMMARY
        # =====================================================
        summary = []

        for file in files:

            name = file.get(
                "name",
                "unknown"
            )

            stack = file.get(
                "stack",
                "unknown"
            )

            content = file.get(
                "content",
                ""
            )[:4000]

            summary.append(

                f"""
FILE: {name}
STACK: {stack}

CONTENT:
{content}
"""
            )

        joined = "\n".join(summary)

        # =====================================================
        # PROMPT
        # =====================================================
        prompt = f"""
Você é um especialista sênior em DevOps, CI/CD e arquitetura de software.

Analise os arquivos do projeto abaixo e gere um pipeline COMPLETO e PROFISSIONAL para {platform}.

REGRAS OBRIGATÓRIAS:

- Retorne SOMENTE YAML puro
- NÃO retorne JSON
- NÃO retorne markdown
- NÃO use ```yaml
- NÃO explique nada
- NÃO escreva comentários fora do YAML
- NÃO escreva "data:"
- NÃO escreva "gitlab:"
- NÃO escreva "github:"
- Gere apenas o conteúdo final do pipeline

REQUISITOS:

- detectar stack automaticamente
- adicionar stages/jobs corretos
- incluir install/build/test/lint se aplicável
- usar imagens modernas
- otimizar cache quando possível
- usar boas práticas de CI/CD
- evitar configurações inseguras
- pipeline deve funcionar em produção

ARQUIVOS DO PROJETO:

{joined}
"""

        # =====================================================
        # STREAM CAPTURE
        # =====================================================
        chunks = []

        for chunk in StreamService.generate(
            prompt,
            provider
        ):

            # =================================================
            # IGNORA SSE PREFIX
            # =================================================
            if isinstance(chunk, str):

                chunk = chunk.replace(
                    "data:",
                    ""
                )

            chunks.append(chunk)

        # =====================================================
        # FINAL RESPONSE
        # =====================================================
        response = "".join(chunks).strip()

        # =====================================================
        # REMOVE MARKDOWN
        # =====================================================
        response = response.replace(
            "```yaml",
            ""
        )

        response = response.replace(
            "```yml",
            ""
        )

        response = response.replace(
            "```",
            ""
        )

        response = response.strip()

        # =====================================================
        # REMOVE JSON WRAPPER
        # =====================================================
        if response.startswith("{"):

            try:

                import json

                data = json.loads(response)

                response = (

                    data.get("pipeline")

                    or data.get("gitlab")

                    or data.get("github")

                    or response
                )

            except Exception:
                pass

        return response.strip()