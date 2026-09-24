from app.movies.application.guards import ensure_movie_exists
from app.movies.domain.entities import NewReview, Review
from app.movies.domain.ports import MovieRepository, ReviewRepository
from app.movies.domain.queries import Page, PageRequest
from app.shared.transaction import TransactionManager


class AddReview:
    def __init__(
        self,
        movies: MovieRepository,
        reviews: ReviewRepository,
        transaction: TransactionManager,
    ) -> None:
        self._movies = movies
        self._reviews = reviews
        self._transaction = transaction

    async def execute(self, movie_id: str, review: NewReview) -> Review:
        await ensure_movie_exists(self._movies, movie_id)
        created = await self._reviews.add(movie_id, review)
        await self._transaction.commit()
        return created


class ListReviews:
    def __init__(self, movies: MovieRepository, reviews: ReviewRepository) -> None:
        self._movies = movies
        self._reviews = reviews

    async def execute(self, movie_id: str, page: PageRequest) -> Page[Review]:
        await ensure_movie_exists(self._movies, movie_id)
        return await self._reviews.list_for_movie(movie_id, page)
