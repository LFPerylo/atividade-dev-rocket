from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from app.movies.domain.errors import InvalidMovieData, InvalidReview
from app.movies.domain.rating import RatingSummary, Stars, score_to_stars

MIN_RELEASE_YEAR = 1870
MAX_RELEASE_YEAR = 2100
MAX_TITLE_LENGTH = 500
MAX_SYNOPSIS_LENGTH = 4000
MAX_AUTHOR_LENGTH = 120
MAX_COMMENT_LENGTH = 4000


class PersonRole(StrEnum):
    ACTOR = "Ator"
    DIRECTOR = "Diretor"
    WRITER = "Roteirista"


@dataclass(frozen=True, slots=True)
class Genre:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class Person:
    id: str
    name: str
    role: PersonRole


@dataclass(frozen=True, slots=True)
class Performance:
    budget_usd: Decimal | None
    revenue_usd: Decimal | None
    profit_usd: Decimal | None
    popularity: float | None
    tmdb_score: float | None
    tmdb_votes: int | None
    imdb_score: float | None
    imdb_votes: int | None


@dataclass(frozen=True, slots=True)
class MovieSummary:
    id: str
    title: str
    release_year: int | None
    poster_url: str | None
    genres: tuple[Genre, ...]
    directors: tuple[str, ...]
    rating: RatingSummary


@dataclass(frozen=True, slots=True)
class MovieDetails:
    id: str
    external_id: str
    title: str
    release_date: date | None
    release_year: int | None
    runtime_minutes: int | None
    status: str | None
    synopsis: str | None
    poster_url: str | None
    backdrop_url: str | None
    genres: tuple[Genre, ...]
    people: tuple[Person, ...]
    companies: tuple[str, ...]
    performance: Performance | None
    rating: RatingSummary

    def people_with_role(self, role: PersonRole) -> tuple[Person, ...]:
        return tuple(person for person in self.people if person.role is role)


@dataclass(frozen=True, slots=True)
class Review:
    id: str
    movie_id: str
    author: str
    score: float
    comment: str
    created_at: datetime

    @property
    def stars(self) -> float:
        return score_to_stars(self.score)


def _clean_text(value: str | None) -> str | None:
    cleaned = value.strip() if value else None
    return cleaned or None


def _unique_names(names: tuple[str, ...]) -> tuple[str, ...]:
    cleaned = (_clean_text(name) for name in names)
    return tuple(dict.fromkeys(name for name in cleaned if name))


@dataclass(frozen=True, slots=True)
class MovieDraft:
    title: str
    directors: tuple[str, ...] = ()
    genre_ids: tuple[str, ...] = ()
    release_year: int | None = None
    release_date: date | None = None
    runtime_minutes: int | None = None
    synopsis: str | None = None
    poster_url: str | None = None
    backdrop_url: str | None = None
    status: str | None = None

    def __post_init__(self) -> None:
        title = _clean_text(self.title)
        if title is None:
            raise InvalidMovieData("Título é obrigatório")
        if len(title) > MAX_TITLE_LENGTH:
            raise InvalidMovieData(f"Título deve ter no máximo {MAX_TITLE_LENGTH} caracteres")
        synopsis = _clean_text(self.synopsis)
        if synopsis and len(synopsis) > MAX_SYNOPSIS_LENGTH:
            raise InvalidMovieData(f"Sinopse deve ter no máximo {MAX_SYNOPSIS_LENGTH} caracteres")
        if self.runtime_minutes is not None and self.runtime_minutes < 0:
            raise InvalidMovieData("Duração não pode ser negativa")
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "synopsis", synopsis)
        object.__setattr__(self, "directors", _unique_names(self.directors))
        object.__setattr__(self, "genre_ids", tuple(dict.fromkeys(self.genre_ids)))
        object.__setattr__(self, "poster_url", _clean_text(self.poster_url))
        object.__setattr__(self, "backdrop_url", _clean_text(self.backdrop_url))
        object.__setattr__(self, "release_year", self._resolve_release_year())

    def _resolve_release_year(self) -> int | None:
        year = self.release_year
        if self.release_date is not None:
            if year is not None and year != self.release_date.year:
                raise InvalidMovieData("Ano de lançamento difere da data de lançamento")
            year = self.release_date.year
        if year is not None and not MIN_RELEASE_YEAR <= year <= MAX_RELEASE_YEAR:
            raise InvalidMovieData(
                f"Ano de lançamento deve estar entre {MIN_RELEASE_YEAR} e {MAX_RELEASE_YEAR}"
            )
        return year


@dataclass(frozen=True, slots=True)
class NewReview:
    author: str
    stars: Stars
    comment: str

    def __post_init__(self) -> None:
        author = _clean_text(self.author)
        comment = _clean_text(self.comment)
        if author is None or len(author) > MAX_AUTHOR_LENGTH:
            raise InvalidReview(f"Nome é obrigatório (máximo {MAX_AUTHOR_LENGTH} caracteres)")
        if comment is None or len(comment) > MAX_COMMENT_LENGTH:
            raise InvalidReview(f"Resenha é obrigatória (máximo {MAX_COMMENT_LENGTH} caracteres)")
        object.__setattr__(self, "author", author)
        object.__setattr__(self, "comment", comment)
