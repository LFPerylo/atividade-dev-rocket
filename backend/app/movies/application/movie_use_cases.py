from app.movies.application.guards import ensure_genres_exist, ensure_movie_exists
from app.movies.domain.entities import MovieDetails, MovieDraft, MovieSummary
from app.movies.domain.errors import MovieNotFound
from app.movies.domain.ports import GenreRepository, MovieRepository, TransactionManager
from app.movies.domain.queries import MovieFilters, Page, PageRequest


class ListMovies:
    def __init__(self, movies: MovieRepository) -> None:
        self._movies = movies

    async def execute(self, filters: MovieFilters, page: PageRequest) -> Page[MovieSummary]:
        return await self._movies.search(filters, page)


class GetMovieDetails:
    def __init__(self, movies: MovieRepository) -> None:
        self._movies = movies

    async def execute(self, movie_id: str) -> MovieDetails:
        movie = await self._movies.get(movie_id)
        if movie is None:
            raise MovieNotFound(movie_id)
        return movie


class CreateMovie:
    def __init__(
        self, movies: MovieRepository, genres: GenreRepository, transaction: TransactionManager
    ) -> None:
        self._movies = movies
        self._genres = genres
        self._transaction = transaction

    async def execute(self, draft: MovieDraft) -> MovieDetails:
        await ensure_genres_exist(self._genres, draft)
        movie_id = await self._movies.add(draft)
        await self._transaction.commit()
        return await GetMovieDetails(self._movies).execute(movie_id)


class UpdateMovie:
    def __init__(
        self, movies: MovieRepository, genres: GenreRepository, transaction: TransactionManager
    ) -> None:
        self._movies = movies
        self._genres = genres
        self._transaction = transaction

    async def execute(self, movie_id: str, draft: MovieDraft) -> MovieDetails:
        await ensure_movie_exists(self._movies, movie_id)
        await ensure_genres_exist(self._genres, draft)
        await self._movies.update(movie_id, draft)
        await self._transaction.commit()
        return await GetMovieDetails(self._movies).execute(movie_id)


class DeleteMovie:
    def __init__(self, movies: MovieRepository, transaction: TransactionManager) -> None:
        self._movies = movies
        self._transaction = transaction

    async def execute(self, movie_id: str) -> None:
        await ensure_movie_exists(self._movies, movie_id)
        await self._movies.delete(movie_id)
        await self._transaction.commit()
