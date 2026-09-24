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


def test_load_inserts_every_table(loader: SeedLoader, sync_engine: Engine) -> None:
    report = loader.load()

    assert report.skipped is False
    assert report.inserted["dim_movies"] == 2
    assert count(sync_engine, "bridge_movie_person") == 5
    assert count(sync_engine, "movie_reviews") == 3
    assert count(sync_engine, "fact_movies_performance") == 1


def test_load_recomputes_rating_summaries_from_reviews(
    loader: SeedLoader, sync_engine: Engine
) -> None:
    loader.load()

    with sync_engine.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT sk_movie_id, qtd_avaliacoes_usuarios, nota_media_usuarios "
                "FROM dim_reviews ORDER BY sk_movie_id"
            )
        ).all()
    assert [tuple(row) for row in rows] == [("m-blind", 1, 6.0), ("m-cdd", 2, 9.0)]


def test_load_normalizes_values(loader: SeedLoader, sync_engine: Engine) -> None:
    loader.load()

    with sync_engine.connect() as connection:
        synopsis, runtime = connection.execute(
            text("SELECT sinopse, duracao_minutos FROM dim_movies WHERE sk_movie_id = 'm-cdd'")
        ).one()
        blind_runtime = connection.execute(
            text("SELECT duracao_minutos FROM dim_movies WHERE sk_movie_id = 'm-blind'")
        ).scalar_one()
    assert synopsis == '"Buscapé" cresce.'
    assert runtime == 130
    assert blind_runtime is None


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


def test_load_merges_people_duplicated_after_normalization(
    loader: SeedLoader, sync_engine: Engine
) -> None:
    loader.load()

    with sync_engine.connect() as connection:
        people = connection.execute(
            text("SELECT sk_person_id, nome_pessoa FROM dim_people WHERE tipo_pessoa = 'Diretor'")
        ).all()
        credited_movies = (
            connection.execute(
                text(
                    "SELECT sk_movie_id FROM bridge_movie_person "
                    "WHERE sk_person_id = 'p-kl' ORDER BY sk_movie_id"
                )
            )
            .scalars()
            .all()
        )
    assert sorted(tuple(row) for row in people) == [
        ("p-fm", "Fernando Meirelles"),
        ("p-kl", 'Kátia "K" Lund'),
    ]
    assert credited_movies == ["m-blind", "m-cdd"]
