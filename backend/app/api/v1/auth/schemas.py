from pydantic import BaseModel, Field

from app.auth.domain.entities import AccessToken, User


class LoginIn(BaseModel):
    email: str = Field(max_length=255)
    senha: str = Field(max_length=255)


class RegisterIn(BaseModel):
    nome: str = Field(max_length=255)
    email: str = Field(max_length=255)
    senha: str = Field(max_length=255)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

    @classmethod
    def from_token(cls, token: AccessToken) -> "TokenOut":
        return cls(access_token=token.value, expires_in=token.expires_in_seconds)


class UserOut(BaseModel):
    id: str
    email: str
    nome: str
    papel: str

    @classmethod
    def from_user(cls, user: User) -> "UserOut":
        return cls(id=user.id, email=user.email, nome=user.name, papel=user.role.value)
