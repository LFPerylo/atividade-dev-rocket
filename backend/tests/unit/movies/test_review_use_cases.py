import pytest

from app.movies.application.genre_use_cases import ListGenres
from app.movies.application.review_use_cases import AddReview, ListReviews
from app.movies.domain.entities import Genre, MovieDraft, NewReview
from app.movies.domain.errors import MovieNotFound
from app.movies.domain.queries import PageRequest
from app.movies.domain.rating import Stars
from tests.unit.movies.fakes import (
    InMemoryGenreRepository,
    InMemoryMovieRepository,
    InMemoryReviewRepository,
    SpyTransactionManager,
)

REVIEW = NewReview(author="Ana", stars=Stars.from_value(4.5), comment="Lindo.")


@pytest.fixture
def movies() -> InMemoryMovieRepository:
    return InMemoryMovieRepository()


@pytest.fixture
def reviews() -> InMemoryReviewRepository:
    return InMemoryReviewRepository()


async def test_add_review_persists_and_commits(
    movies: InMemoryMovieRepository, reviews: InMemoryReviewRepository
) -> None:
    movie_id = await movies.add(MovieDraft(title="Central do Brasil"))
    transaction = SpyTransactionManager()

    review = await AddReview(movies, reviews, transaction).execute(movie_id, REVIEW)

    assert (review.movie_id, review.score) == (movie_id, 9.0)
    assert transaction.commits == 1


async def test_add_review_raises_for_unknown_movie(
    movies: InMemoryMovieRepository, reviews: InMemoryReviewRepository
) -> None:
    transaction = SpyTransactionManager()

    with pytest.raises(MovieNotFound):
        await AddReview(movies, reviews, transaction).execute("x", REVIEW)

    assert reviews.reviews == []
    assert transaction.commits == 0


async def test_list_reviews_returns_movie_reviews(
    movies: InMemoryMovieRepository, reviews: InMemoryReviewRepository
) -> None:
    movie_id = await movies.add(MovieDraft(title="Central do Brasil"))
    await reviews.add(movie_id, REVIEW)

    page = await ListReviews(movies, reviews).execute(movie_id, PageRequest())

    assert [review.author for review in page.items] == ["Ana"]


async def test_list_reviews_raises_for_unknown_movie(
    movies: InMemoryMovieRepository, reviews: InMemoryReviewRepository
) -> None:
    with pytest.raises(MovieNotFound):
        await ListReviews(movies, reviews).execute("x", PageRequest())


async def test_list_genres_returns_sorted_genres() -> None:
    genres = InMemoryGenreRepository([Genre("g2", "Drama"), Genre("g1", "Comédia")])

    result = await ListGenres(genres).execute()

    assert [genre.name for genre in result] == ["Comédia", "Drama"]
