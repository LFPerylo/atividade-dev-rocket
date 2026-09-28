from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.domain.errors import InvalidToken
from app.auth.infrastructure.admin_repository import SqlAlchemyAdminRepository
from app.auth.infrastructure.jwt_token_service import JwtTokenService
from app.auth.infrastructure.password_hasher import Argon2PasswordHasher

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


async def test_admin_repository_adds_and_finds_admin(session: AsyncSession) -> None:
    repository = SqlAlchemyAdminRepository(session)

    created = await repository.add("admin@rocketlab.dev", "Admin", "hash")
    await session.commit()

    assert await repository.find_by_email("admin@rocketlab.dev") == created
    assert await repository.get(created.id) == created
    assert await repository.get("inexistente") is None
