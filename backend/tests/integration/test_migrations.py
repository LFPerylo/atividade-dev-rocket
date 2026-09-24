from pathlib import Path

from sqlalchemy import create_engine, inspect

from tests.support import migrate


def test_migrations_create_all_tables(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'test.db'}"

    migrate(url)

    tables = set(inspect(create_engine(url)).get_table_names())
    assert {"dim_movies", "movie_reviews", "dim_reviews", "alembic_version"} <= tables
