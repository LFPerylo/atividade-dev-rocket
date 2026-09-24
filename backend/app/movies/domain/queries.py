import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from app.movies.domain.errors import InvalidQuery

MAX_PAGE_SIZE = 100
MAX_FILTER_STARS = 5


class SortField(StrEnum):
    TITLE = "titulo"
    YEAR = "ano"
    RATING = "media"
    POPULARITY = "popularidade"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True, slots=True)
class PageRequest:
    page: int = 1
    size: int = 20

    def __post_init__(self) -> None:
        if self.page < 1:
            raise InvalidQuery("Página deve ser maior ou igual a 1")
        if not 1 <= self.size <= MAX_PAGE_SIZE:
            raise InvalidQuery(f"Tamanho da página deve estar entre 1 e {MAX_PAGE_SIZE}")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


@dataclass(frozen=True, slots=True)
class Page[T]:
    items: Sequence[T]
    total: int
    request: PageRequest

    @property
    def pages(self) -> int:
        return math.ceil(self.total / self.request.size)


@dataclass(frozen=True, slots=True)
class MovieFilters:
    search: str | None = None
    genre_id: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    min_stars: float | None = None
    sort: SortField = SortField.POPULARITY
    order: SortOrder = SortOrder.DESC

    def __post_init__(self) -> None:
        normalized_search = self.search.strip() if self.search else None
        object.__setattr__(self, "search", normalized_search or None)
        if (
            self.year_from is not None
            and self.year_to is not None
            and self.year_from > self.year_to
        ):
            raise InvalidQuery("Ano inicial não pode ser maior que o ano final")
        if self.min_stars is not None and not 0 <= self.min_stars <= MAX_FILTER_STARS:
            raise InvalidQuery(f"Nota mínima deve estar entre 0 e {MAX_FILTER_STARS} estrelas")
