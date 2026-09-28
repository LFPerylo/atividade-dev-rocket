from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.domain.entities import Role
from app.auth.domain.errors import InvalidToken
from app.auth.infrastructure.jwt_token_service import JwtTokenService
from app.auth.infrastructure.password_hasher import Argon2PasswordHasher
from app.auth.infrastructure.user_repository import SqlAlchemyUserRepository

SECRET = "segredo-de-teste-com-tamanho-suficiente-32"


def test_argon2_hasher_verifies_only_original_password() -> None:
    hasher = Argon2PasswordHasher()

    password_hash = hasher.hash("s3nha-forte")

    assert password_hash != "s3nha-forte"
    assert hasher.verify("s3nha-forte", password_hash) is True
    assert hasher.verify("errada", password_hash) is False


def test_jwt_round_trip_returns_subject() -> None:
    service = JwtTokenService(secret=SECRET, expires_minutes=5)

    token = service.issue("admin-1")

    assert token.expires_in_seconds == 300
    assert service.subject_of(token.value) == "admin-1"


def test_jwt_rejects_expired_token() -> None:
    past = datetime.now(UTC) - timedelta(hours=1)
    issuer = JwtTokenService(secret=SECRET, expires_minutes=5, clock=lambda: past)

    token = issuer.issue("admin-1")

    with pytest.raises(InvalidToken):
        JwtTokenService(secret=SECRET, expires_minutes=5).subject_of(token.value)


def test_jwt_rejects_token_signed_with_other_secret() -> None:
    token = JwtTokenService(secret="outro-segredo-com-tamanho-suficiente-32", expires_minutes=5)

    with pytest.raises(InvalidToken):
        JwtTokenService(secret=SECRET, expires_minutes=5).subject_of(token.issue("a").value)


async def test_user_repository_adds_and_finds_users_with_role(session: AsyncSession) -> None:
    repository = SqlAlchemyUserRepository(session)

    created = await repository.add("ana@exemplo.com", "Ana", "hash", Role.REVIEWER)
    await session.commit()

    assert created.role is Role.REVIEWER
    assert await repository.find_by_email("ana@exemplo.com") == created
    assert await repository.get(created.id) == created
    assert await repository.get("inexistente") is None
