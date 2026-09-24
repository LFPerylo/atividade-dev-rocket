from app.movies.domain.entities import (
    Genre,
    MovieDetails,
    Performance,
    Person,
    PersonRole,
    Review,
)
from app.movies.domain.rating import RatingSummary
from app.movies.models import (
    DimGenre,
    DimMovie,
    DimPerson,
    DimReview,
    FactMoviePerformance,
    MovieReview,
)


def to_genre(model: DimGenre) -> Genre:
    return Genre(id=model.sk_genre_id, name=model.nome_genero)


def to_person(model: DimPerson) -> Person:
    return Person(id=model.sk_person_id, name=model.nome_pessoa, role=PersonRole(model.tipo_pessoa))


def to_rating(model: DimReview | None) -> RatingSummary:
    if model is None:
        return RatingSummary(count=0, average_score=None)
    return RatingSummary(
        count=model.qtd_avaliacoes_usuarios, average_score=model.nota_media_usuarios
    )


def to_performance(model: FactMoviePerformance | None) -> Performance | None:
    if model is None:
        return None
    return Performance(
        budget_usd=model.orcamento_usd,
        revenue_usd=model.receita_usd,
        profit_usd=model.lucro_usd,
        popularity=model.popularidade,
        tmdb_score=model.nota_tmdb,
        tmdb_votes=model.qtd_tmdb,
        imdb_score=model.nota_imdb,
        imdb_votes=model.qtd_imdb,
    )


def to_movie_details(model: DimMovie) -> MovieDetails:
    return MovieDetails(
        id=model.sk_movie_id,
        external_id=model.id_filme,
        title=model.titulo,
        release_date=model.data_lancamento,
        release_year=model.ano_lancamento,
        runtime_minutes=model.duracao_minutos,
        status=model.status_filme,
        synopsis=model.sinopse,
        poster_url=model.url_poster,
        backdrop_url=model.url_backdrop,
        genres=tuple(to_genre(genre) for genre in model.genres),
        people=tuple(
            to_person(person) for person in sorted(model.people, key=lambda p: p.nome_pessoa)
        ),
        companies=tuple(company.nome_produtora for company in model.companies),
        performance=to_performance(model.performance),
        rating=to_rating(model.reviews_summary),
    )


def to_review(model: MovieReview) -> Review:
    return Review(
        id=model.sk_movie_review_id,
        movie_id=model.sk_movie_id,
        author=model.nome,
        score=model.nota,
        comment=model.comentario,
        created_at=model.created_at,
    )
