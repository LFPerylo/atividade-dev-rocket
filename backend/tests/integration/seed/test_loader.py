from pathlib import Path

import pytest
from sqlalchemy import Engine, create_engine, text

from app.movies.infrastructure.seed.loader import SeedLoader
from tests.integration.seed.sample_data import write_sample_data


@pytest.fixture
def sync_engine(database_path: Path) -> Engine:
    return create_engine(f"sqlite:///{database_path}")


@pytest.fixture
def loader(sync_engine: Engine, tmp_path: Path) -> SeedLoader:
    return SeedLoader(sync_engine, write_sample_data(tmp_path / "seed"))


def count(engine: Engine, table: str) -> int:
    with engine.connect() as connection:
        return connection.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()


def rows(engine: Engine, sql: str) -> list[tuple[object, ...]]:
    with engine.connect() as connection:
        return [tuple(row) for row in connection.execute(text(sql)).all()]


def test_load_inserts_every_table(loader: SeedLoader, sync_engine: Engine) -> None:
    report = loader.load()

    assert report.skipped is False
    assert report.inserted["dim_movies"] == 2
    assert report.inserted["dim_reviews"] == 2
    assert count(sync_engine, "bridge_movie_person") == 6
    assert count(sync_engine, "movie_reviews") == 3
    assert count(sync_engine, "fact_movies_performance") == 1


def test_load_keeps_rating_summaries_exactly_as_provided(
    loader: SeedLoader, sync_engine: Engine
) -> None:
    loader.load()

    assert rows(
        sync_engine,
        "SELECT sk_movie_id, qtd_avaliacoes_usuarios, nota_media_usuarios "
        "FROM dim_reviews ORDER BY sk_movie_id",
    ) == [("m-blind", 0, None), ("m-cdd", 2, 9.0)]


def test_load_keeps_text_and_numbers_as_provided(loader: SeedLoader, sync_engine: Engine) -> None:
    loader.load()

    assert rows(
        sync_engine, "SELECT sk_movie_id, sinopse, duracao_minutos FROM dim_movies ORDER BY 1"
    ) == [("m-blind", None, 0), ("m-cdd", '"Buscapé" "cresce"."', 130)]


def test_load_keeps_people_that_only_differ_by_quotes(
    loader: SeedLoader, sync_engine: Engine
) -> None:
    loader.load()

    assert rows(
        sync_engine,
        "SELECT sk_person_id, nome_pessoa FROM dim_people "
        "WHERE sk_person_id LIKE 'p-kl%' ORDER BY 1",
    ) == [("p-kl", 'Kátia ""K"" Lund'), ("p-kl-dup", 'Kátia ""K"" Lund"')]


def test_load_is_skipped_when_catalog_already_has_movies(
    loader: SeedLoader, sync_engine: Engine
) -> None:
    loader.load()

    report = loader.load()

    assert report.skipped is True
    assert count(sync_engine, "dim_movies") == 2


def test_load_with_reset_replaces_existing_data(loader: SeedLoader, sync_engine: Engine) -> None:
    loader.load()
    with sync_engine.begin() as connection:
        connection.execute(text("DELETE FROM movie_reviews WHERE sk_movie_review_id = 'r1'"))

    report = loader.load(reset=True)

    assert report.skipped is False
    assert count(sync_engine, "movie_reviews") == 3
    assert count(sync_engine, "dim_movies") == 2
