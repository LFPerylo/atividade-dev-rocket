import shutil
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.session import enable_sqlite_foreign_keys
from tests.support import migrate


@pytest.fixture(scope="session")
def migrated_template(tmp_path_factory: pytest.TempPathFactory) -> Path:
    template = tmp_path_factory.mktemp("template") / "template.db"
    migrate(f"sqlite:///{template}")
    return template


@pytest.fixture
def database_path(migrated_template: Path, tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    shutil.copy(migrated_template, path)
    return path


@pytest.fixture
async def async_engine(database_path: Path) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
    enable_sqlite_foreign_keys(engine)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory(async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=async_engine, expire_on_commit=False, autoflush=False)


@pytest.fixture
async def session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as db_session:
        yield db_session
