from sqlalchemy import Insert, func
from sqlalchemy.dialects.sqlite import insert

from app.movies.models import DimReview


def add_score_to_summary(movie_id: str, score: float) -> Insert:
    count = DimReview.qtd_avaliacoes_usuarios
    average = func.coalesce(DimReview.nota_media_usuarios, 0)
    statement = insert(DimReview).values(
        sk_review_id=movie_id,
        sk_movie_id=movie_id,
        qtd_avaliacoes_usuarios=1,
        nota_media_usuarios=score,
    )
    return statement.on_conflict_do_update(
        index_elements=[DimReview.sk_movie_id],
        set_={
            "qtd_avaliacoes_usuarios": count + 1,
            "nota_media_usuarios": (average * count + score) / (count + 1),
        },
    )
