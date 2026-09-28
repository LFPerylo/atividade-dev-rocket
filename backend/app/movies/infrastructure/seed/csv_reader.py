import csv
import gzip
from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import IO


def blank_to_none(raw: str) -> str | None:
    return raw or None


def to_int(raw: str | None) -> int | None:
    return int(float(raw)) if raw else None


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
            yield {column: blank_to_none(value or "") for column, value in row.items()}
