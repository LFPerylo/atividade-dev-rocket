from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text

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


def test_existing_admins_keep_admin_role_after_upgrade(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'test.db'}"
    migrate(url, "0003_sort_indexes")
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO admin_users (id, email, name, password_hash) "
                "VALUES ('a1', 'admin@rocketlab.dev', 'Admin', 'hash')"
            )
        )

    migrate(url)

    with engine.connect() as connection:
        role = connection.execute(text("SELECT papel FROM users WHERE id = 'a1'")).scalar_one()
    assert role == "admin"
