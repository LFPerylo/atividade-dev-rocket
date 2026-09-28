from collections.abc import Sequence
from typing import Protocol

from app.movies.domain.entities import (
    Genre,
    MovieDetails,
    MovieDraft,
    MovieSummary,
    NewReview,
    Review,
)
from app.movies.domain.queries import MovieFilters, Page, PageRequest


class MovieRepository(Protocol):
    async def search(self, filters: MovieFilters, page: PageRequest) -> Page[MovieSummary]: ...

    async def get(self, movie_id: str) -> MovieDetails | None: ...

    async def exists(self, movie_id: str) -> bool: ...

    async def add(self, draft: MovieDraft) -> str: ...

    async def update(self, movie_id: str, draft: MovieDraft) -> None: ...

    async def delete(self, movie_id: str) -> None: ...


class GenreRepository(Protocol):
    async def list_all(self) -> Sequence[Genre]: ...

    async def find_missing(self, genre_ids: Sequence[str]) -> set[str]: ...


class ReviewRepository(Protocol):
    async def list_for_movie(self, movie_id: str, page: PageRequest) -> Page[Review]: ...

    async def add(self, movie_id: str, review: NewReview) -> Review: ...
