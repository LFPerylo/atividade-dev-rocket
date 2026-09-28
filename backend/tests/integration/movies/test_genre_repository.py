from sqlalchemy.ext.asyncio import AsyncSession

from app.movies.infrastructure.genre_repository import SqlAlchemyGenreRepository


async def test_list_all_returns_genres_sorted_by_name(session: AsyncSession) -> None:
    genres = await SqlAlchemyGenreRepository(session).list_all()

    assert [genre.name for genre in genres] == ["Crime", "Drama"]


async def test_find_missing_returns_unknown_ids(session: AsyncSession) -> None:
    missing = await SqlAlchemyGenreRepository(session).find_missing(["g-drama", "g-x", "g-y"])

    assert missing == {"g-x", "g-y"}
