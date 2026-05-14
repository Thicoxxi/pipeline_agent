# =========================================================
# BASE
# =========================================================
class AppError(Exception):

    def __init__(
        self,
        message: str,
        status_code: int = 500
    ):

        super().__init__(message)

        self.message = message

        self.status_code = status_code

    def to_dict(self):

        return {
            "error": self.message,
            "status_code": self.status_code
        }


# =========================================================
# PIPELINE
# =========================================================
class PipelineError(AppError):

    def __init__(
        self,
        message="Erro ao gerar pipeline"
    ):

        super().__init__(
            message,
            500
        )


# =========================================================
# YAML VALIDATION
# =========================================================
class ValidationError(AppError):

    def __init__(
        self,
        message="YAML inválido"
    ):

        super().__init__(
            message,
            400
        )


# =========================================================
# PROVIDER
# =========================================================
class ProviderError(AppError):

    def __init__(
        self,
        message="Provider indisponível"
    ):

        super().__init__(
            message,
            503
        )


# =========================================================
# SCM
# =========================================================
class SCMError(AppError):

    def __init__(
        self,
        message="Erro SCM"
    ):

        super().__init__(
            message,
            500
        )


# =========================================================
# GITHUB
# =========================================================
class GitHubError(SCMError):

    def __init__(
        self,
        message="Erro GitHub"
    ):

        super().__init__(
            message
        )


# =========================================================
# GITLAB
# =========================================================
class GitLabError(SCMError):

    def __init__(
        self,
        message="Erro GitLab"
    ):

        super().__init__(
            message
        )