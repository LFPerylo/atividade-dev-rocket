import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.movies.domain.entities import MovieDraft, NewReview
from app.movies.domain.queries import PageRequest
from app.movies.domain.rating import Stars
from app.movies.infrastructure.movie_repository import SqlAlchemyMovieRepository
from app.movies.infrastructure.review_repository import SqlAlchemyReviewRepository


@pytest.fixture
def repository(session: AsyncSession) -> SqlAlchemyReviewRepository:
    return SqlAlchemyReviewRepository(session)


async def test_list_for_movie_paginates_reviews(repository: SqlAlchemyReviewRepository) -> None:
    page = await repository.list_for_movie("m-cdd", PageRequest(page=1, size=1))

    assert page.total == 2
    assert len(page.items) == 1
    assert page.items[0].movie_id == "m-cdd"


async def test_add_persists_review_in_score_scale(
    repository: SqlAlchemyReviewRepository, session: AsyncSession
) -> None:
    review = await repository.add(
        "m-blind", NewReview(author="Diego", stars=Stars.from_value(3.5), comment="Tenso.")
    )
    await session.commit()

    assert review.score == 7.0
    assert review.stars == 3.5
    assert review.created_at is not None


async def test_add_lists_newest_review_first(
    repository: SqlAlchemyReviewRepository, session: AsyncSession
) -> None:
    await repository.add(
        "m-cdd", NewReview(author="Diego", stars=Stars.from_value(1), comment="Não gostei.")
    )
    await session.commit()

    page = await repository.list_for_movie("m-cdd", PageRequest())

    assert page.items[0].author == "Diego"


async def test_add_refreshes_movie_rating_summary(
    repository: SqlAlchemyReviewRepository, session: AsyncSession
) -> None:
    await repository.add(
        "m-cdd", NewReview(author="Diego", stars=Stars.from_value(1), comment="Não gostei.")
    )
    await session.commit()

    movie = await SqlAlchemyMovieRepository(session).get("m-cdd")

    assert movie is not None
    assert movie.rating.count == 3
    assert movie.rating.average_score == pytest.approx(20 / 3)


async def test_add_creates_summary_for_movie_without_reviews(
    repository: SqlAlchemyReviewRepository, session: AsyncSession
) -> None:
    movies = SqlAlchemyMovieRepository(session)
    movie_id = await movies.add(MovieDraft(title="Sem avaliações"))
    await repository.add(
        movie_id, NewReview(author="Eva", stars=Stars.from_value(5), comment="Perfeito.")
    )
    await session.commit()

    movie = await movies.get(movie_id)

    assert movie is not None
    assert (movie.rating.count, movie.rating.average_stars) == (1, 5.0)
