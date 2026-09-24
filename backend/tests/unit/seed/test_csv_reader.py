import gzip
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.movies.infrastructure.seed.csv_reader import (
    clean_text,
    read_csv,
    to_date,
    to_decimal,
    to_float,
    to_int,
    to_positive_int,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("", None),
        ("   ", None),
        ("Rings", "Rings"),
        ('"A ""movie within the movie"" appears."', 'A "movie within the movie" appears.'),
        ('"Truncated ""quote', 'Truncated "quote'),
        ('"Buscapé" cresce.', '"Buscapé" cresce.'),
    ],
)
def test_clean_text_normalizes_blank_and_double_encoded_quotes(
    raw: str, expected: str | None
) -> None:
    assert clean_text(raw) == expected


def test_numeric_converters_accept_float_notation_and_blank() -> None:
    assert to_int("2375.0") == 2375
    assert to_int("") is None
    assert to_float("7.064") == 7.064
    assert to_decimal("25000000.0") == Decimal("25000000.0")
    assert to_decimal("") is None


def test_to_positive_int_treats_zero_as_unknown() -> None:
    assert to_positive_int("0") is None
    assert to_positive_int("102") == 102


def test_to_date_parses_iso_dates() -> None:
    assert to_date("2017-02-01") == date(2017, 2, 1)
    assert to_date("") is None


def test_read_csv_reads_gzip_rows_with_clean_values(tmp_path: Path) -> None:
    path = tmp_path / "dim_genres.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8") as file:
        file.write("nome_genero,sk_genre_id\nHorror,g1\n,g2\n")

    assert list(read_csv(path)) == [
        {"nome_genero": "Horror", "sk_genre_id": "g1"},
        {"nome_genero": None, "sk_genre_id": "g2"},
    ]
