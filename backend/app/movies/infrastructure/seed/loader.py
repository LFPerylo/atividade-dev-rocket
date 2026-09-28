from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path
from typing import Any

from sqlalchemy import Connection, Engine, Table, delete, func, select

from app.db.base import Base
from app.movies.infrastructure.seed.csv_reader import (
    read_csv,
    to_date,
    to_decimal,
    to_float,
    to_int,
)
from app.movies.models import DimMovie

BATCH_SIZE = 5_000

Converter = Callable[[str | None], Any]


@dataclass(frozen=True, slots=True)
class TableSource:
    table: str
    file_name: str
    converters: Mapping[str, Converter] = field(default_factory=dict)


MONEY_COLUMNS = (
    "orcamento_usd",
    "receita_usd",
    "lucro_usd",
    "orcamento_brl",
    "receita_brl",
    "lucro_brl",
)

SOURCES = (
    TableSource("dim_genres", "dim_genres.csv.gz"),
    TableSource("dim_companies", "dim_companies.csv.gz"),
    TableSource("dim_people", "dim_people.csv.gz"),
    TableSource(
        "dim_movies",
        "dim_movies.csv.gz",
        {
            "data_lancamento": to_date,
            "ano_lancamento": to_int,
            "duracao_minutos": to_int,
        },
    ),
    TableSource("bridge_movie_genre", "bridge_movie_genre.csv.gz"),
    TableSource("bridge_movie_company", "bridge_movie_company.csv.gz"),
    TableSource("bridge_movie_person", "bridge_movie_person.csv.gz"),
    TableSource(
        "fact_movies_performance",
        "fact_movies_performance.csv.gz",
        {
            **dict.fromkeys(MONEY_COLUMNS, to_decimal),
            "popularidade": to_float,
            "nota_tmdb": to_float,
            "qtd_tmdb": to_int,
            "nota_imdb": to_float,
            "qtd_imdb": to_int,
        },
    ),
    TableSource("movie_reviews", "movies_reviews.csv.gz", {"nota": to_float}),
    TableSource(
        "dim_reviews",
        "dim_reviews.csv.gz",
        {"qtd_avaliacoes_usuarios": to_int, "nota_media_usuarios": to_float},
    ),
)


@dataclass(frozen=True, slots=True)
class SeedReport:
    skipped: bool
    inserted: dict[str, int] = field(default_factory=dict)


def _unchanged(value: str | None) -> str | None:
    return value


def _batches(rows: Iterable[dict[str, Any]], size: int) -> Iterator[list[dict[str, Any]]]:
    iterator = iter(rows)
    while batch := list(islice(iterator, size)):
        yield batch


class SeedLoader:
    def __init__(self, engine: Engine, data_dir: Path) -> None:
        self._engine = engine
        self._data_dir = data_dir

    def load(self, reset: bool = False) -> SeedReport:
        with self._engine.begin() as connection:
            if reset:
                self._clear(connection)
            elif self._has_movies(connection):
                return SeedReport(skipped=True)
            inserted = {source.table: self._load_source(connection, source) for source in SOURCES}
        return SeedReport(skipped=False, inserted=inserted)

    def _has_movies(self, connection: Connection) -> bool:
        return connection.execute(select(func.count()).select_from(DimMovie)).scalar_one() > 0

    def _clear(self, connection: Connection) -> None:
        for table in reversed(Base.metadata.sorted_tables):
            if table.name != "users":
                connection.execute(delete(table))

    def _load_source(self, connection: Connection, source: TableSource) -> int:
        table: Table = Base.metadata.tables[source.table]
        raw_rows = read_csv(self._data_dir / source.file_name)
        rows = (self._convert(row, source) for row in raw_rows)
        inserted = 0
        for batch in _batches(rows, BATCH_SIZE):
            connection.execute(table.insert(), batch)
            inserted += len(batch)
        return inserted

    @staticmethod
    def _convert(row: dict[str, str | None], source: TableSource) -> dict[str, Any]:
        return {
            column: source.converters.get(column, _unchanged)(value)
            for column, value in row.items()
        }
