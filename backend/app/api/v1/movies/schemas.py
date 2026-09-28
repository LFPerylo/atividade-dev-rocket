from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.auth.domain.entities import User
from app.movies.domain.entities import (
    Genre,
    MovieDetails,
    MovieDraft,
    MovieSummary,
    NewReview,
    Performance,
    PersonRole,
    Review,
)
from app.movies.domain.rating import Stars


class GenreOut(BaseModel):
    id: str
    nome: str

    @classmethod
    def from_genre(cls, genre: Genre) -> "GenreOut":
        return cls(id=genre.id, nome=genre.name)


class MovieSummaryOut(BaseModel):
    id: str
    titulo: str
    ano_lancamento: int | None
    url_poster: str | None
    generos: list[GenreOut]
    diretores: list[str]
    media_estrelas: float | None
    total_avaliacoes: int

    @classmethod
    def from_summary(cls, movie: MovieSummary) -> "MovieSummaryOut":
        return cls(
            id=movie.id,
            titulo=movie.title,
            ano_lancamento=movie.release_year,
            url_poster=movie.poster_url,
            generos=[GenreOut.from_genre(genre) for genre in movie.genres],
            diretores=list(movie.directors),
            media_estrelas=movie.rating.average_stars,
            total_avaliacoes=movie.rating.count,
        )


class PerformanceOut(BaseModel):
    orcamento_usd: Decimal | None
    receita_usd: Decimal | None
    lucro_usd: Decimal | None
    popularidade: float | None
    nota_tmdb: float | None
    votos_tmdb: int | None
    nota_imdb: float | None
    votos_imdb: int | None

    @classmethod
    def from_performance(cls, performance: Performance) -> "PerformanceOut":
        return cls(
            orcamento_usd=performance.budget_usd,
            receita_usd=performance.revenue_usd,
            lucro_usd=performance.profit_usd,
            popularidade=performance.popularity,
            nota_tmdb=performance.tmdb_score,
            votos_tmdb=performance.tmdb_votes,
            nota_imdb=performance.imdb_score,
            votos_imdb=performance.imdb_votes,
        )


class MovieDetailsOut(BaseModel):
    id: str
    id_externo: str
    titulo: str
    data_lancamento: date | None
    ano_lancamento: int | None
    duracao_minutos: int | None
    status: str | None
    sinopse: str | None
    url_poster: str | None
    url_backdrop: str | None
    generos: list[GenreOut]
    diretores: list[str]
    roteiristas: list[str]
    elenco: list[str]
    produtoras: list[str]
    desempenho: PerformanceOut | None
    media_estrelas: float | None
    total_avaliacoes: int

    @classmethod
    def from_details(cls, movie: MovieDetails) -> "MovieDetailsOut":
        def names(role: PersonRole) -> list[str]:
            return [person.name for person in movie.people_with_role(role)]

        return cls(
            id=movie.id,
            id_externo=movie.external_id,
            titulo=movie.title,
            data_lancamento=movie.release_date,
            ano_lancamento=movie.release_year,
            duracao_minutos=movie.runtime_minutes,
            status=movie.status,
            sinopse=movie.synopsis,
            url_poster=movie.poster_url,
            url_backdrop=movie.backdrop_url,
            generos=[GenreOut.from_genre(genre) for genre in movie.genres],
            diretores=names(PersonRole.DIRECTOR),
            roteiristas=names(PersonRole.WRITER),
            elenco=names(PersonRole.ACTOR),
            produtoras=list(movie.companies),
            desempenho=(
                PerformanceOut.from_performance(movie.performance) if movie.performance else None
            ),
            media_estrelas=movie.rating.average_stars,
            total_avaliacoes=movie.rating.count,
        )


class MovieIn(BaseModel):
    titulo: str = Field(max_length=500)
    diretores: list[str] = Field(default_factory=list, max_length=20)
    generos: list[str] = Field(default_factory=list, max_length=19)
    ano_lancamento: int | None = None
    data_lancamento: date | None = None
    duracao_minutos: int | None = None
    sinopse: str | None = Field(default=None, max_length=4000)
    url_poster: str | None = Field(default=None, max_length=2048)
    url_backdrop: str | None = Field(default=None, max_length=2048)
    status: str | None = Field(default=None, max_length=50)

    def to_draft(self) -> MovieDraft:
        return MovieDraft(
            title=self.titulo,
            directors=tuple(self.diretores),
            genre_ids=tuple(self.generos),
            release_year=self.ano_lancamento,
            release_date=self.data_lancamento,
            runtime_minutes=self.duracao_minutos,
            synopsis=self.sinopse,
            poster_url=self.url_poster,
            backdrop_url=self.url_backdrop,
            status=self.status,
        )


class ReviewIn(BaseModel):
    estrelas: float
    comentario: str = Field(max_length=4000)

    def to_new_review(self, author: User) -> NewReview:
        return NewReview(
            author=author.name,
            author_id=author.id,
            stars=Stars.from_value(self.estrelas),
            comment=self.comentario,
        )


class ReviewOut(BaseModel):
    id: str
    nome: str
    estrelas: float
    nota: float
    comentario: str
    criado_em: datetime

    @classmethod
    def from_review(cls, review: Review) -> "ReviewOut":
        return cls(
            id=review.id,
            nome=review.author,
            estrelas=review.stars,
            nota=review.score,
            comentario=review.comment,
            criado_em=review.created_at,
        )
