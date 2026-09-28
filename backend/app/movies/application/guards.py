from app.movies.domain.entities import MovieDraft
from app.movies.domain.errors import GenreNotFound, MovieNotFound
from app.movies.domain.ports import GenreRepository, MovieRepository


async def ensure_genres_exist(genres: GenreRepository, draft: MovieDraft) -> None:
    missing = await genres.find_missing(draft.genre_ids)
    if missing:
        raise GenreNotFound(missing)


async def ensure_movie_exists(movies: MovieRepository, movie_id: str) -> None:
    if not await movies.exists(movie_id):
        raise MovieNotFound(movie_id)
