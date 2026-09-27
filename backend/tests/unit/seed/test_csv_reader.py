import gzip
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.movies.infrastructure.seed.csv_reader import (
    blank_to_none,
    read_csv,
    to_date,
    to_decimal,
    to_float,
    to_int,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("", None),
        ("Rings", "Rings"),
        ('"A ""movie within the movie"" appears."', '"A ""movie within the movie"" appears."'),
        (" com espaços ", " com espaços "),
    ],
)
def test_blank_to_none_keeps_every_value_except_empty_cells(raw: str, expected: str | None) -> None:
    assert blank_to_none(raw) == expected


def test_numeric_converters_accept_float_notation_and_blank() -> None:
    assert to_int("2375.0") == 2375
    assert to_int("0") == 0
    assert to_int("") is None
    assert to_float("7.064") == 7.064
    assert to_decimal("25000000.0") == Decimal("25000000.0")
    assert to_decimal("") is None


def test_to_date_parses_iso_dates() -> None:
    assert to_date("2017-02-01") == date(2017, 2, 1)
    assert to_date("") is None


def test_read_csv_reads_gzip_rows_as_provided(tmp_path: Path) -> None:
    path = tmp_path / "dim_genres.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8") as file:
        file.write('nome_genero,sk_genre_id\nHorror,g1\n,g2\n"Tv ""Movie""",g3\n')

    assert list(read_csv(path)) == [
        {"nome_genero": "Horror", "sk_genre_id": "g1"},
        {"nome_genero": None, "sk_genre_id": "g2"},
        {"nome_genero": 'Tv "Movie"', "sk_genre_id": "g3"},
    ]
