from collections.abc import Sequence

from app.movies.domain.entities import Genre
from app.movies.domain.ports import GenreRepository


class ListGenres:
    def __init__(self, genres: GenreRepository) -> None:
        self._genres = genres

    async def execute(self) -> Sequence[Genre]:
        return await self._genres.list_all()
