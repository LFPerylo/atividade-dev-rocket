from collections.abc import Sequence
from dataclasses import replace
from datetime import datetime

from app.movies.domain.entities import (
    Genre,
    MovieDetails,
    MovieDraft,
    MovieSummary,
    NewReview,
    Review,
)
from app.movies.domain.queries import MovieFilters, Page, PageRequest
from app.movies.domain.rating import RatingSummary


def make_details(movie_id: str, draft: MovieDraft) -> MovieDetails:
    return MovieDetails(
        id=movie_id,
        external_id=f"ext-{movie_id}",
        title=draft.title,
        release_date=draft.release_date,
        release_year=draft.release_year,
        runtime_minutes=draft.runtime_minutes,
        status=draft.status,
        synopsis=draft.synopsis,
        poster_url=draft.poster_url,
        backdrop_url=draft.backdrop_url,
        genres=(),
        people=(),
        companies=(),
        performance=None,
        rating=RatingSummary(count=0, average_score=None),
    )


class InMemoryMovieRepository:
    def __init__(self) -> None:
        self.movies: dict[str, MovieDetails] = {}

    async def search(self, filters: MovieFilters, page: PageRequest) -> Page[MovieSummary]:
        items = [
            MovieSummary(
                id=movie.id,
                title=movie.title,
                release_year=movie.release_year,
                poster_url=movie.poster_url,
                genres=movie.genres,
                directors=(),
                rating=movie.rating,
            )
            for movie in self.movies.values()
        ]
        return Page(items=items, total=len(items), request=page)

    async def get(self, movie_id: str) -> MovieDetails | None:
        return self.movies.get(movie_id)

    async def exists(self, movie_id: str) -> bool:
        return movie_id in self.movies

    async def add(self, draft: MovieDraft) -> str:
        movie_id = f"m{len(self.movies) + 1}"
        self.movies[movie_id] = make_details(movie_id, draft)
        return movie_id

    async def update(self, movie_id: str, draft: MovieDraft) -> None:
        current = self.movies[movie_id]
        self.movies[movie_id] = replace(make_details(movie_id, draft), rating=current.rating)

    async def delete(self, movie_id: str) -> None:
        del self.movies[movie_id]


class InMemoryGenreRepository:
    def __init__(self, genres: Sequence[Genre] = ()) -> None:
        self.genres = list(genres)

    async def list_all(self) -> Sequence[Genre]:
        return sorted(self.genres, key=lambda genre: genre.name)

    async def find_missing(self, genre_ids: Sequence[str]) -> set[str]:
        return set(genre_ids) - {genre.id for genre in self.genres}


class InMemoryReviewRepository:
    def __init__(self) -> None:
        self.reviews: list[Review] = []

    async def list_for_movie(self, movie_id: str, page: PageRequest) -> Page[Review]:
        items = [review for review in self.reviews if review.movie_id == movie_id]
        return Page(items=items, total=len(items), request=page)

    async def add(self, movie_id: str, review: NewReview) -> Review:
        created = Review(
            id=f"r{len(self.reviews) + 1}",
            movie_id=movie_id,
            author=review.author,
            score=review.stars.to_score(),
            comment=review.comment,
            created_at=datetime(2026, 9, 24),
        )
        self.reviews.append(created)
        return created


class SpyTransactionManager:
    def __init__(self) -> None:
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        pass
