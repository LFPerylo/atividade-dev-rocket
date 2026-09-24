from pydantic import BaseModel, Field

from app.auth.domain.entities import AccessToken, AdminUser


class LoginIn(BaseModel):
    email: str = Field(max_length=255)
    senha: str = Field(max_length=255)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

    @classmethod
    def from_token(cls, token: AccessToken) -> "TokenOut":
        return cls(access_token=token.value, expires_in=token.expires_in_seconds)


class AdminOut(BaseModel):
    id: str
    email: str
    nome: str

    @classmethod
    def from_admin(cls, admin: AdminUser) -> "AdminOut":
        return cls(id=admin.id, email=admin.email, nome=admin.name)
