from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect

from app.db.registry import registered_metadata
from tests.support import migrate


def test_migrations_create_all_tables(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'test.db'}"

    migrate(url)

    tables = set(inspect(create_engine(url)).get_table_names())
    assert {"dim_movies", "movie_reviews", "dim_reviews", "alembic_version"} <= tables


def test_migrations_match_orm_models(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    migrate(url)

    with create_engine(url).connect() as connection:
        context = MigrationContext.configure(connection, opts={"render_as_batch": True})
        differences = compare_metadata(context, registered_metadata())

    assert differences == []
