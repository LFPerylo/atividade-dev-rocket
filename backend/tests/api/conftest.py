from collections.abc import AsyncIterator
from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.auth.application.use_cases import EnsureAdmin
from app.auth.infrastructure.admin_repository import SqlAlchemyAdminRepository
from app.auth.infrastructure.password_hasher import Argon2PasswordHasher
from app.db.session import get_db
from app.db.transaction import SqlAlchemyTransactionManager
from app.main import create_app
from app.movies.infrastructure.seed.loader import SeedLoader
from tests.integration.seed.sample_data import write_sample_data

ADMIN_EMAIL = "admin@rocketlab.dev"
ADMIN_PASSWORD = "s3nha-forte"


@pytest.fixture
def database_path(database_path: Path, tmp_path: Path) -> Path:
    engine = create_engine(f"sqlite:///{database_path}")
    SeedLoader(engine, write_sample_data(tmp_path / "seed")).load()
    engine.dispose()
    return database_path


@pytest.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[httpx.AsyncClient]:
    async with session_factory() as session:
        await EnsureAdmin(
            SqlAlchemyAdminRepository(session),
            Argon2PasswordHasher(),
            SqlAlchemyTransactionManager(session),
        ).execute(email=ADMIN_EMAIL, name="Admin", password=ADMIN_PASSWORD)

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test/api/v1") as http:
        yield http


@pytest.fixture
async def auth_headers(client: httpx.AsyncClient) -> dict[str, str]:
    response = await client.post(
        "/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_PASSWORD}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
