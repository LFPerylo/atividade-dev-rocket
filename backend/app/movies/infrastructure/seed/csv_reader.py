import csv
import gzip
from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import IO

QUOTE = '"'
ESCAPED_QUOTE = '""'


def clean_text(raw: str) -> str | None:
    value = raw.strip()
    if ESCAPED_QUOTE in value:
        value = _decode_double_encoded(value)
    return value or None


def _decode_double_encoded(value: str) -> str:
    unwrapped = value.removeprefix(QUOTE).removesuffix(QUOTE)
    return unwrapped.replace(ESCAPED_QUOTE, QUOTE).strip()


def to_int(raw: str | None) -> int | None:
    return int(float(raw)) if raw else None


def to_positive_int(raw: str | None) -> int | None:
    value = to_int(raw)
    return value if value else None


def to_float(raw: str | None) -> float | None:
    return float(raw) if raw else None


def to_decimal(raw: str | None) -> Decimal | None:
    return Decimal(raw) if raw else None


def to_date(raw: str | None) -> date | None:
    return date.fromisoformat(raw) if raw else None


def _open(path: Path) -> IO[str]:
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return path.open(encoding="utf-8", newline="")


def read_csv(path: Path) -> Iterator[dict[str, str | None]]:
    with _open(path) as file:
        for row in csv.DictReader(file):
            yield {column: clean_text(value or "") for column, value in row.items()}
