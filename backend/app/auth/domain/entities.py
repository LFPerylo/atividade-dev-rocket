from dataclasses import dataclass
from enum import StrEnum

from app.auth.domain.errors import InvalidUserData, PermissionDenied

MIN_PASSWORD_LENGTH = 8
MAX_NAME_LENGTH = 120


class Role(StrEnum):
    ADMIN = "admin"
    REVIEWER = "avaliador"


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_new_user(email: str, name: str, password: str) -> None:
    local, _, domain = email.partition("@")
    if not local or "." not in domain:
        raise InvalidUserData("E-mail inválido")
    if not name or len(name) > MAX_NAME_LENGTH:
        raise InvalidUserData(f"Nome é obrigatório (máximo {MAX_NAME_LENGTH} caracteres)")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise InvalidUserData(f"Senha deve ter ao menos {MIN_PASSWORD_LENGTH} caracteres")


@dataclass(frozen=True, slots=True)
class User:
    id: str
    email: str
    name: str
    role: Role
    password_hash: str

    @property
    def is_admin(self) -> bool:
        return self.role is Role.ADMIN

    def require_admin(self) -> None:
        if not self.is_admin:
            raise PermissionDenied()


@dataclass(frozen=True, slots=True)
class AccessToken:
    value: str
    expires_in_seconds: int
