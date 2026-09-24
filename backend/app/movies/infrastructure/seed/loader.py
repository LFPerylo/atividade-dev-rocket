from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path
from typing import Any

from sqlalchemy import Connection, Engine, Table, delete, func, select

from app.db.base import Base
from app.movies.infrastructure.rating_summary import clear_all_summaries, rebuild_all_summaries
from app.movies.infrastructure.seed.csv_reader import (
    read_csv,
    to_date,
    to_decimal,
    to_float,
    to_int,
    to_positive_int,
)
from app.movies.models import DimMovie

BATCH_SIZE = 5_000

Converter = Callable[[str | None], Any]


@dataclass(frozen=True, slots=True)
class TableSource:
    table: str
    file_name: str
    converters: Mapping[str, Converter] = field(default_factory=dict)
    natural_key: tuple[str, ...] = ()
    references: Mapping[str, str] = field(default_factory=dict)

    @property
    def id_column(self) -> str:
        return next(iter(Base.metadata.tables[self.table].primary_key.columns)).name


MONEY_COLUMNS = (
    "orcamento_usd",
    "receita_usd",
    "lucro_usd",
    "orcamento_brl",
    "receita_brl",
    "lucro_brl",
)

SOURCES = (
    TableSource("dim_genres", "dim_genres.csv.gz", natural_key=("nome_genero",)),
    TableSource("dim_companies", "dim_companies.csv.gz", natural_key=("nome_produtora",)),
    TableSource("dim_people", "dim_people.csv.gz", natural_key=("nome_pessoa", "tipo_pessoa")),
    TableSource(
        "dim_movies",
        "dim_movies.csv.gz",
        {
            "data_lancamento": to_date,
            "ano_lancamento": to_int,
            "duracao_minutos": to_positive_int,
        },
    ),
    TableSource(
        "bridge_movie_genre", "bridge_movie_genre.csv.gz", references={"sk_genre_id": "dim_genres"}
    ),
    TableSource(
        "bridge_movie_company",
        "bridge_movie_company.csv.gz",
        references={"sk_company_id": "dim_companies"},
    ),
    TableSource(
        "bridge_movie_person",
        "bridge_movie_person.csv.gz",
        references={"sk_person_id": "dim_people"},
    ),
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
        self._aliases: dict[str, dict[str, str]] = {}

    def load(self, reset: bool = False) -> SeedReport:
        with self._engine.begin() as connection:
            if reset:
                self._clear(connection)
            elif self._has_movies(connection):
                return SeedReport(skipped=True)
            self._aliases = {}
            inserted = {source.table: self._load_source(connection, source) for source in SOURCES}
            connection.execute(clear_all_summaries())
            connection.execute(rebuild_all_summaries())
        return SeedReport(skipped=False, inserted=inserted)

    def _has_movies(self, connection: Connection) -> bool:
        return connection.execute(select(func.count()).select_from(DimMovie)).scalar_one() > 0

    def _clear(self, connection: Connection) -> None:
        for table in reversed(Base.metadata.sorted_tables):
            if table.name != "admin_users":
                connection.execute(delete(table))

    def _load_source(self, connection: Connection, source: TableSource) -> int:
        table: Table = Base.metadata.tables[source.table]
        raw_rows = read_csv(self._data_dir / source.file_name)
        converted = (self._convert(row, source) for row in raw_rows)
        rows = self._unique_rows(self._remap_references(converted, source), source)
        inserted = 0
        for batch in _batches(rows, BATCH_SIZE):
            connection.execute(table.insert(), batch)
            inserted += len(batch)
        return inserted

    def _remap_references(
        self, rows: Iterable[dict[str, Any]], source: TableSource
    ) -> Iterator[dict[str, Any]]:
        for row in rows:
            for column, referenced_table in source.references.items():
                aliases = self._aliases.get(referenced_table, {})
                row[column] = aliases.get(row[column], row[column])
            yield row

    def _unique_rows(
        self, rows: Iterable[dict[str, Any]], source: TableSource
    ) -> Iterator[dict[str, Any]]:
        if source.natural_key:
            return self._merge_duplicated_dimensions(rows, source)
        if source.references:
            return self._drop_repeated_links(rows)
        return iter(rows)

    def _merge_duplicated_dimensions(
        self, rows: Iterable[dict[str, Any]], source: TableSource
    ) -> Iterator[dict[str, Any]]:
        aliases = self._aliases.setdefault(source.table, {})
        canonical_ids: dict[tuple[Any, ...], str] = {}
        for row in rows:
            key = tuple(row[column] for column in source.natural_key)
            row_id = row[source.id_column]
            if key in canonical_ids:
                aliases[row_id] = canonical_ids[key]
                continue
            canonical_ids[key] = row_id
            yield row

    @staticmethod
    def _drop_repeated_links(rows: Iterable[dict[str, Any]]) -> Iterator[dict[str, Any]]:
        seen: set[tuple[Any, ...]] = set()
        for row in rows:
            link = tuple(row.values())
            if link not in seen:
                seen.add(link)
                yield row

    @staticmethod
    def _convert(row: dict[str, str | None], source: TableSource) -> dict[str, Any]:
        return {
            column: source.converters.get(column, _unchanged)(value)
            for column, value in row.items()
        }
