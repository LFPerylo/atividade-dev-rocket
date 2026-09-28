import pytest

from app.movies.application.movie_use_cases import (
    CreateMovie,
    DeleteMovie,
    GetMovieDetails,
    ListMovies,
    UpdateMovie,
)
from app.movies.domain.entities import Genre, MovieDraft
from app.movies.domain.errors import GenreNotFound, MovieNotFound
from app.movies.domain.queries import MovieFilters, PageRequest
from tests.unit.movies.fakes import (
    InMemoryGenreRepository,
    InMemoryMovieRepository,
    SpyTransactionManager,
)

DRAMA = Genre(id="g-drama", name="Drama")


@pytest.fixture
def movies() -> InMemoryMovieRepository:
    return InMemoryMovieRepository()


@pytest.fixture
def genres() -> InMemoryGenreRepository:
    return InMemoryGenreRepository([DRAMA])


@pytest.fixture
def transaction() -> SpyTransactionManager:
    return SpyTransactionManager()


async def test_list_movies_returns_repository_page(movies: InMemoryMovieRepository) -> None:
    await movies.add(MovieDraft(title="Central do Brasil"))

    page = await ListMovies(movies).execute(MovieFilters(), PageRequest())

    assert [movie.title for movie in page.items] == ["Central do Brasil"]


async def test_get_movie_details_raises_when_missing(movies: InMemoryMovieRepository) -> None:
    with pytest.raises(MovieNotFound):
        await GetMovieDetails(movies).execute("inexistente")


async def test_create_movie_persists_and_commits(
    movies: InMemoryMovieRepository,
    genres: InMemoryGenreRepository,
    transaction: SpyTransactionManager,
) -> None:
    draft = MovieDraft(title="Central do Brasil", genre_ids=("g-drama",))

    created = await CreateMovie(movies, genres, transaction).execute(draft)

    assert created.title == "Central do Brasil"
    assert await movies.exists(created.id)
    assert transaction.commits == 1


async def test_create_movie_rejects_unknown_genres(
    movies: InMemoryMovieRepository,
    genres: InMemoryGenreRepository,
    transaction: SpyTransactionManager,
) -> None:
    draft = MovieDraft(title="Central do Brasil", genre_ids=("g-drama", "g-x"))

    with pytest.raises(GenreNotFound) as error:
        await CreateMovie(movies, genres, transaction).execute(draft)

    assert error.value.genre_ids == {"g-x"}
    assert movies.movies == {}
    assert transaction.commits == 0


async def test_update_movie_replaces_data(
    movies: InMemoryMovieRepository,
    genres: InMemoryGenreRepository,
    transaction: SpyTransactionManager,
) -> None:
    movie_id = await movies.add(MovieDraft(title="Central"))

    updated = await UpdateMovie(movies, genres, transaction).execute(
        movie_id, MovieDraft(title="Central do Brasil", release_year=1998)
    )

    assert (updated.title, updated.release_year) == ("Central do Brasil", 1998)
    assert transaction.commits == 1


async def test_update_movie_raises_when_missing(
    movies: InMemoryMovieRepository,
    genres: InMemoryGenreRepository,
    transaction: SpyTransactionManager,
) -> None:
    with pytest.raises(MovieNotFound):
        await UpdateMovie(movies, genres, transaction).execute("x", MovieDraft(title="X"))


async def test_update_movie_rejects_unknown_genres(
    movies: InMemoryMovieRepository,
    genres: InMemoryGenreRepository,
    transaction: SpyTransactionManager,
) -> None:
    movie_id = await movies.add(MovieDraft(title="Central"))

    with pytest.raises(GenreNotFound):
        await UpdateMovie(movies, genres, transaction).execute(
            movie_id, MovieDraft(title="Central", genre_ids=("g-x",))
        )


async def test_delete_movie_removes_and_commits(
    movies: InMemoryMovieRepository, transaction: SpyTransactionManager
) -> None:
    movie_id = await movies.add(MovieDraft(title="Central"))

    await DeleteMovie(movies, transaction).execute(movie_id)

    assert not await movies.exists(movie_id)
    assert transaction.commits == 1


async def test_delete_movie_raises_when_missing(
    movies: InMemoryMovieRepository, transaction: SpyTransactionManager
) -> None:
    with pytest.raises(MovieNotFound):
        await DeleteMovie(movies, transaction).execute("x")
