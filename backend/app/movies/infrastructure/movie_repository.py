from collections import defaultdict
from collections.abc import Sequence
from typing import Any
from uuid import uuid4

from sqlalchemy import ColumnElement, Select, delete, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.movies.domain.entities import Genre, MovieDetails, MovieDraft, MovieSummary, PersonRole
from app.movies.domain.queries import MovieFilters, Page, PageRequest, SortField, SortOrder
from app.movies.domain.rating import SCORE_PER_STAR, RatingSummary
from app.movies.infrastructure.mappers import to_genre, to_movie_details
from app.movies.models import (
    DimGenre,
    DimMovie,
    DimPerson,
    DimReview,
    FactMoviePerformance,
    bridge_movie_genre,
    bridge_movie_person,
)

SORT_COLUMNS: dict[SortField, ColumnElement[object]] = {
    SortField.TITLE: DimMovie.titulo,  # type: ignore[dict-item]
    SortField.YEAR: DimMovie.ano_lancamento,  # type: ignore[dict-item]
    SortField.RATING: DimReview.nota_media_usuarios,  # type: ignore[dict-item]
    SortField.POPULARITY: FactMoviePerformance.popularidade,  # type: ignore[dict-item]
}


def _new_external_id() -> str:
    return f"adm-{uuid4().hex[:12]}"


class SqlAlchemyMovieRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(self, filters: MovieFilters, page: PageRequest) -> Page[MovieSummary]:
        conditions = self._conditions(filters)
        total = await self._session.scalar(self._count(conditions)) or 0
        rows = (await self._session.execute(self._page(conditions, filters, page))).all()
        movie_ids = [row.sk_movie_id for row in rows]
        genres = await self._genres_by_movie(movie_ids)
        directors = await self._directors_by_movie(movie_ids)
        items = [
            MovieSummary(
                id=row.sk_movie_id,
                title=row.titulo,
                release_year=row.ano_lancamento,
                poster_url=row.url_poster,
                genres=genres.get(row.sk_movie_id, ()),
                directors=directors.get(row.sk_movie_id, ()),
                rating=RatingSummary(
                    count=row.qtd_avaliacoes_usuarios or 0,
                    average_score=row.nota_media_usuarios,
                ),
            )
            for row in rows
        ]
        return Page(items=items, total=total, request=page)

    async def get(self, movie_id: str) -> MovieDetails | None:
        movie = await self._load(movie_id)
        return to_movie_details(movie) if movie else None

    async def exists(self, movie_id: str) -> bool:
        statement = select(exists().where(DimMovie.sk_movie_id == movie_id))
        return bool(await self._session.scalar(statement))

    async def add(self, draft: MovieDraft) -> str:
        movie = DimMovie(id_filme=_new_external_id(), genres=[], people=[])
        await self._apply(movie, draft)
        self._session.add(movie)
        await self._session.flush()
        return movie.sk_movie_id

    async def update(self, movie_id: str, draft: MovieDraft) -> None:
        movie = await self._load(movie_id)
        if movie is not None:
            await self._apply(movie, draft)
            await self._session.flush()

    async def delete(self, movie_id: str) -> None:
        await self._session.execute(delete(DimMovie).where(DimMovie.sk_movie_id == movie_id))

    async def _load(self, movie_id: str) -> DimMovie | None:
        statement = (
            select(DimMovie)
            .where(DimMovie.sk_movie_id == movie_id)
            .options(
                selectinload(DimMovie.genres),
                selectinload(DimMovie.people),
                selectinload(DimMovie.companies),
                selectinload(DimMovie.performance),
                selectinload(DimMovie.reviews_summary),
            )
            .execution_options(populate_existing=True)
        )
        movie: DimMovie | None = await self._session.scalar(statement)
        return movie

    async def _apply(self, movie: DimMovie, draft: MovieDraft) -> None:
        movie.titulo = draft.title
        movie.data_lancamento = draft.release_date
        movie.ano_lancamento = draft.release_year
        movie.duracao_minutos = draft.runtime_minutes
        movie.sinopse = draft.synopsis
        movie.url_poster = draft.poster_url
        movie.url_backdrop = draft.backdrop_url
        movie.status_filme = draft.status or movie.status_filme
        movie.genres = await self._genres(draft.genre_ids)
        others = [
            person for person in movie.people if person.tipo_pessoa != PersonRole.DIRECTOR.value
        ]
        movie.people = others + await self._directors(draft.directors)

    async def _genres(self, genre_ids: Sequence[str]) -> list[DimGenre]:
        if not genre_ids:
            return []
        result = await self._session.scalars(
            select(DimGenre).where(DimGenre.sk_genre_id.in_(genre_ids))
        )
        return list(result)

    async def _directors(self, names: Sequence[str]) -> list[DimPerson]:
        if not names:
            return []
        existing = {
            person.nome_pessoa: person
            for person in await self._session.scalars(
                select(DimPerson).where(
                    DimPerson.tipo_pessoa == PersonRole.DIRECTOR,
                    DimPerson.nome_pessoa.in_(names),
                )
            )
        }
        return [
            existing.get(name) or DimPerson(nome_pessoa=name, tipo_pessoa=PersonRole.DIRECTOR.value)
            for name in names
        ]

    def _conditions(self, filters: MovieFilters) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if filters.search:
            conditions.append(self._matches_search(filters.search))
        if filters.genre_id:
            conditions.append(
                DimMovie.sk_movie_id.in_(
                    select(bridge_movie_genre.c.sk_movie_id).where(
                        bridge_movie_genre.c.sk_genre_id == filters.genre_id
                    )
                )
            )
        if filters.year_from is not None:
            conditions.append(DimMovie.ano_lancamento >= filters.year_from)
        if filters.year_to is not None:
            conditions.append(DimMovie.ano_lancamento <= filters.year_to)
        if filters.min_stars is not None:
            conditions.append(DimReview.nota_media_usuarios >= filters.min_stars * SCORE_PER_STAR)
        return conditions

    @staticmethod
    def _matches_search(term: str) -> ColumnElement[bool]:
        pattern = f"%{term}%"
        directed_by = (
            select(bridge_movie_person.c.sk_movie_id)
            .join(DimPerson, DimPerson.sk_person_id == bridge_movie_person.c.sk_person_id)
            .where(
                DimPerson.tipo_pessoa == PersonRole.DIRECTOR,
                DimPerson.nome_pessoa.ilike(pattern),
            )
        )
        return or_(DimMovie.titulo.ilike(pattern), DimMovie.sk_movie_id.in_(directed_by))

    @staticmethod
    def _base[T: tuple[Any, ...]](statement: Select[T]) -> Select[T]:
        return statement.outerjoin(
            DimReview, DimReview.sk_movie_id == DimMovie.sk_movie_id
        ).outerjoin(FactMoviePerformance, FactMoviePerformance.sk_movie_id == DimMovie.sk_movie_id)

    def _count(self, conditions: list[ColumnElement[bool]]) -> Select[tuple[int]]:
        return self._base(select(func.count(DimMovie.sk_movie_id))).where(*conditions)

    def _page(
        self, conditions: list[ColumnElement[bool]], filters: MovieFilters, page: PageRequest
    ) -> Select[tuple[str, str, int | None, str | None, int, float | None]]:
        column = SORT_COLUMNS[filters.sort]
        ordering = column.asc() if filters.order is SortOrder.ASC else column.desc()
        statement = select(
            DimMovie.sk_movie_id,
            DimMovie.titulo,
            DimMovie.ano_lancamento,
            DimMovie.url_poster,
            DimReview.qtd_avaliacoes_usuarios,
            DimReview.nota_media_usuarios,
        )
        return (
            self._base(statement)
            .where(*conditions)
            .order_by(ordering.nulls_last(), DimMovie.sk_movie_id)
            .limit(page.size)
            .offset(page.offset)
        )

    async def _genres_by_movie(self, movie_ids: list[str]) -> dict[str, tuple[Genre, ...]]:
        statement = (
            select(bridge_movie_genre.c.sk_movie_id, DimGenre)
            .join(DimGenre, DimGenre.sk_genre_id == bridge_movie_genre.c.sk_genre_id)
            .where(bridge_movie_genre.c.sk_movie_id.in_(movie_ids))
            .order_by(DimGenre.nome_genero)
        )
        grouped: defaultdict[str, list[Genre]] = defaultdict(list)
        for movie_id, genre in (await self._session.execute(statement)).all():
            grouped[movie_id].append(to_genre(genre))
        return {movie_id: tuple(genres) for movie_id, genres in grouped.items()}

    async def _directors_by_movie(self, movie_ids: list[str]) -> dict[str, tuple[str, ...]]:
        statement = (
            select(bridge_movie_person.c.sk_movie_id, DimPerson.nome_pessoa)
            .join(DimPerson, DimPerson.sk_person_id == bridge_movie_person.c.sk_person_id)
            .where(
                bridge_movie_person.c.sk_movie_id.in_(movie_ids),
                DimPerson.tipo_pessoa == PersonRole.DIRECTOR,
            )
            .order_by(DimPerson.nome_pessoa)
        )
        grouped: defaultdict[str, list[str]] = defaultdict(list)
        for movie_id, name in (await self._session.execute(statement)).all():
            grouped[movie_id].append(name)
        return {movie_id: tuple(names) for movie_id, names in grouped.items()}
