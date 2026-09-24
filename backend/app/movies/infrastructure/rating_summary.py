from sqlalchemy import Delete, Insert, Select, delete, func, insert, literal_column, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.movies.models import DimReview, MovieReview

SUMMARY_COLUMNS = (
    "sk_review_id",
    "sk_movie_id",
    "qtd_avaliacoes_usuarios",
    "nota_media_usuarios",
)


def _aggregate_reviews() -> Select[tuple[str, str, int, float]]:
    return select(
        MovieReview.sk_movie_id,
        MovieReview.sk_movie_id,
        func.count(),
        func.avg(MovieReview.nota),
    ).group_by(MovieReview.sk_movie_id)


def clear_all_summaries() -> Delete:
    return delete(DimReview)


def rebuild_all_summaries() -> Insert:
    return insert(DimReview).from_select(SUMMARY_COLUMNS, _aggregate_reviews())


def refresh_movie_summary(movie_id: str) -> Insert:
    aggregate = _aggregate_reviews().where(MovieReview.sk_movie_id == movie_id)
    statement = sqlite_insert(DimReview).from_select(SUMMARY_COLUMNS, aggregate)
    return statement.on_conflict_do_update(
        index_elements=[DimReview.sk_movie_id],
        set_={
            "qtd_avaliacoes_usuarios": literal_column("excluded.qtd_avaliacoes_usuarios"),
            "nota_media_usuarios": literal_column("excluded.nota_media_usuarios"),
        },
    )
