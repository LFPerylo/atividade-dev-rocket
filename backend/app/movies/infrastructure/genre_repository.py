from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.movies.domain.entities import Genre
from app.movies.infrastructure.mappers import to_genre
from app.movies.models import DimGenre


class SqlAlchemyGenreRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Sequence[Genre]:
        result = await self._session.scalars(select(DimGenre).order_by(DimGenre.nome_genero))
        return [to_genre(genre) for genre in result]

    async def find_missing(self, genre_ids: Sequence[str]) -> set[str]:
        found = await self._session.scalars(
            select(DimGenre.sk_genre_id).where(DimGenre.sk_genre_id.in_(genre_ids))
        )
        return set(genre_ids) - set(found)
