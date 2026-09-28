from pathlib import Path

import pytest
from sqlalchemy import create_engine

from app.movies.infrastructure.seed.loader import SeedLoader
from tests.integration.seed.sample_data import write_sample_data


@pytest.fixture
def database_path(database_path: Path, tmp_path: Path) -> Path:
    engine = create_engine(f"sqlite:///{database_path}")
    SeedLoader(engine, write_sample_data(tmp_path / "seed")).load()
    engine.dispose()
    return database_path
