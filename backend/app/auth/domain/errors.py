class AuthError(Exception):
    pass


class InvalidCredentials(AuthError):
    def __init__(self) -> None:
        super().__init__("E-mail ou senha inválidos")


class InvalidToken(AuthError):
    def __init__(self) -> None:
        super().__init__("Sessão inválida ou expirada")


class InvalidUserData(AuthError):
    pass


class EmailAlreadyRegistered(AuthError):
    def __init__(self) -> None:
        super().__init__("Já existe uma conta com este e-mail")


class PermissionDenied(AuthError):
    def __init__(self) -> None:
        super().__init__("Apenas administradores podem realizar esta ação")
