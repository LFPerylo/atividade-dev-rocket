from fastapi import APIRouter

from app.api.v1.dependencies import GenreRepositoryDep
from app.api.v1.movies.schemas import GenreOut
from app.movies.application.genre_use_cases import ListGenres

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("")
async def list_genres(genres: GenreRepositoryDep) -> list[GenreOut]:
    return [GenreOut.from_genre(genre) for genre in await ListGenres(genres).execute()]
