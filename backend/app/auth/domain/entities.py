from dataclasses import dataclass

from app.auth.domain.errors import InvalidAdminData

MIN_PASSWORD_LENGTH = 8


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_new_admin(email: str, password: str) -> None:
    local, _, domain = email.partition("@")
    if not local or "." not in domain:
        raise InvalidAdminData("E-mail inválido")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise InvalidAdminData(f"Senha deve ter ao menos {MIN_PASSWORD_LENGTH} caracteres")


@dataclass(frozen=True, slots=True)
class AdminUser:
    id: str
    email: str
    name: str
    password_hash: str


@dataclass(frozen=True, slots=True)
class AccessToken:
    value: str
    expires_in_seconds: int
