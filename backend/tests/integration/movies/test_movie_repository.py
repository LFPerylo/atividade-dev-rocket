from datetime import date
from typing import Any

import pytest
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.movies.domain.entities import MovieDraft, PersonRole
from app.movies.domain.queries import MovieFilters, PageRequest, SortField, SortOrder
from app.movies.infrastructure.movie_repository import SqlAlchemyMovieRepository
from app.movies.models import DimPerson, DimReview, MovieReview


@pytest.fixture
def repository(session: AsyncSession) -> SqlAlchemyMovieRepository:
    return SqlAlchemyMovieRepository(session)


async def search_titles(repository: SqlAlchemyMovieRepository, **filters: Any) -> list[str]:
    page = await repository.search(MovieFilters(**filters), PageRequest())
    return [movie.title for movie in page.items]


async def test_search_paginates_catalog(repository: SqlAlchemyMovieRepository) -> None:
    page = await repository.search(MovieFilters(), PageRequest(page=2, size=1))

    assert page.total == 2
    assert page.pages == 2
    assert len(page.items) == 1


async def test_search_summary_includes_genres_directors_and_rating(
    repository: SqlAlchemyMovieRepository,
) -> None:
    page = await repository.search(MovieFilters(search="cidade"), PageRequest())

    movie = page.items[0]
    assert movie.title == "Cidade de Deus"
    assert movie.release_year == 2002
    assert [genre.name for genre in movie.genres] == ["Crime", "Drama"]
    assert movie.directors == ("Fernando Meirelles", 'Kátia "K" Lund')
    assert (movie.rating.count, movie.rating.average_stars) == (2, 4.5)


async def test_search_matches_title_case_insensitively(
    repository: SqlAlchemyMovieRepository,
) -> None:
    assert await search_titles(repository, search="CEGUEIRA") == ["Ensaio sobre a Cegueira"]


async def test_search_matches_director_name(repository: SqlAlchemyMovieRepository) -> None:
    titles = await search_titles(
        repository, search="meirelles", sort=SortField.TITLE, order=SortOrder.ASC
    )

    assert titles == ["Cidade de Deus", "Ensaio sobre a Cegueira"]


async def test_search_ignores_actor_names(repository: SqlAlchemyMovieRepository) -> None:
    assert await search_titles(repository, search="Alice Braga") == []


async def test_search_filters_by_genre(repository: SqlAlchemyMovieRepository) -> None:
    assert await search_titles(repository, genre_id="g-crime") == ["Cidade de Deus"]


async def test_search_filters_by_year_range(repository: SqlAlchemyMovieRepository) -> None:
    assert await search_titles(repository, year_from=2005) == ["Ensaio sobre a Cegueira"]
    assert await search_titles(repository, year_to=2005) == ["Cidade de Deus"]


async def test_search_filters_by_minimum_stars(repository: SqlAlchemyMovieRepository) -> None:
    assert await search_titles(repository, min_stars=4) == ["Cidade de Deus"]


@pytest.mark.parametrize(
    ("sort", "order", "expected"),
    [
        (SortField.TITLE, SortOrder.ASC, ["Cidade de Deus", "Ensaio sobre a Cegueira"]),
        (SortField.YEAR, SortOrder.DESC, ["Ensaio sobre a Cegueira", "Cidade de Deus"]),
        (SortField.RATING, SortOrder.ASC, ["Ensaio sobre a Cegueira", "Cidade de Deus"]),
        (SortField.POPULARITY, SortOrder.ASC, ["Cidade de Deus", "Ensaio sobre a Cegueira"]),
    ],
)
async def test_search_sorts_with_missing_values_last(
    repository: SqlAlchemyMovieRepository,
    sort: SortField,
    order: SortOrder,
    expected: list[str],
) -> None:
    assert await search_titles(repository, sort=sort, order=order) == expected


async def test_get_returns_full_details(repository: SqlAlchemyMovieRepository) -> None:
    movie = await repository.get("m-cdd")

    assert movie is not None
    assert movie.external_id == "598"
    assert movie.release_date == date(2002, 8, 30)
    assert movie.runtime_minutes == 130
    assert movie.synopsis == '"Buscapé" cresce.'
    assert movie.companies == ("O2 Filmes",)
    assert [p.name for p in movie.people_with_role(PersonRole.DIRECTOR)] == [
        "Fernando Meirelles",
        'Kátia "K" Lund',
    ]
    assert movie.performance is not None
    assert movie.performance.imdb_score == 8.6
    assert movie.rating.average_stars == 4.5


async def test_get_returns_none_for_unknown_movie(repository: SqlAlchemyMovieRepository) -> None:
    assert await repository.get("desconhecido") is None


async def test_exists(repository: SqlAlchemyMovieRepository) -> None:
    assert await repository.exists("m-cdd") is True
    assert await repository.exists("desconhecido") is False


async def test_add_creates_movie_reusing_existing_directors(
    repository: SqlAlchemyMovieRepository, session: AsyncSession
) -> None:
    draft = MovieDraft(
        title="O Jardineiro Fiel",
        directors=("Fernando Meirelles", "Nova Diretora"),
        genre_ids=("g-drama",),
        release_date=date(2005, 8, 31),
        synopsis="Um diplomata investiga.",
        runtime_minutes=129,
    )

    movie_id = await repository.add(draft)
    await session.commit()

    movie = await repository.get(movie_id)
    assert movie is not None
    assert movie.external_id.startswith("adm-")
    assert movie.release_year == 2005
    assert [genre.name for genre in movie.genres] == ["Drama"]
    assert {p.name for p in movie.people_with_role(PersonRole.DIRECTOR)} == {
        "Fernando Meirelles",
        "Nova Diretora",
    }
    directors = await session.scalar(
        select(func.count()).select_from(DimPerson).where(DimPerson.tipo_pessoa == "Diretor")
    )
    assert directors == 3


async def test_update_replaces_fields_genres_and_directors_keeping_cast(
    repository: SqlAlchemyMovieRepository, session: AsyncSession
) -> None:
    draft = MovieDraft(
        title="Blindness",
        directors=("Outro Diretor",),
        genre_ids=("g-crime",),
        release_year=2008,
    )

    await repository.update("m-blind", draft)
    await session.commit()

    movie = await repository.get("m-blind")
    assert movie is not None
    assert movie.title == "Blindness"
    assert [genre.name for genre in movie.genres] == ["Crime"]
    assert [p.name for p in movie.people_with_role(PersonRole.DIRECTOR)] == ["Outro Diretor"]
    assert [p.name for p in movie.people_with_role(PersonRole.ACTOR)] == ["Alice Braga"]


async def test_delete_removes_movie_and_its_reviews(
    repository: SqlAlchemyMovieRepository, session: AsyncSession
) -> None:
    await repository.delete("m-cdd")
    await session.commit()

    assert await repository.get("m-cdd") is None
    reviews = await session.scalar(
        select(func.count()).select_from(MovieReview).where(MovieReview.sk_movie_id == "m-cdd")
    )
    assert reviews == 0


async def test_search_treats_like_wildcards_literally(
    repository: SqlAlchemyMovieRepository,
) -> None:
    assert await search_titles(repository, search="_") == []
    assert await search_titles(repository, search="%") == []


async def test_min_stars_filter_uses_displayed_rounded_stars(
    repository: SqlAlchemyMovieRepository, session: AsyncSession
) -> None:
    await session.execute(
        update(DimReview).where(DimReview.sk_movie_id == "m-blind").values(nota_media_usuarios=7.95)
    )

    assert await search_titles(
        repository, min_stars=4, sort=SortField.TITLE, order=SortOrder.ASC
    ) == [
        "Cidade de Deus",
        "Ensaio sobre a Cegueira",
    ]
