from sqlalchemy import func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.movies.domain.entities import NewReview, Review
from app.movies.domain.queries import Page, PageRequest
from app.movies.infrastructure.mappers import to_review
from app.movies.infrastructure.rating_summary import refresh_movie_summary
from app.movies.models import MovieReview

INSERTION_ORDER = literal_column("movie_reviews.rowid")


class SqlAlchemyReviewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_movie(self, movie_id: str, page: PageRequest) -> Page[Review]:
        belongs_to_movie = MovieReview.sk_movie_id == movie_id
        total = await self._session.scalar(
            select(func.count()).select_from(MovieReview).where(belongs_to_movie)
        )
        reviews = await self._session.scalars(
            select(MovieReview)
            .where(belongs_to_movie)
            .order_by(MovieReview.created_at.desc(), INSERTION_ORDER.desc())
            .limit(page.size)
            .offset(page.offset)
        )
        return Page(items=[to_review(review) for review in reviews], total=total or 0, request=page)

    async def add(self, movie_id: str, review: NewReview) -> Review:
        model = MovieReview(
            sk_movie_id=movie_id,
            nome=review.author,
            nota=review.stars.to_score(),
            comentario=review.comment,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        await self._session.execute(refresh_movie_summary(movie_id))
        return to_review(model)
