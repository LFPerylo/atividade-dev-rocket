from collections.abc import Sequence

from alembic import op

revision: str = "0003_sort_indexes"
down_revision: str | Sequence[str] | None = "0002_admin_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_fact_movies_performance_popularidade", "fact_movies_performance", ["popularidade"]
    )
    op.create_index("ix_dim_reviews_nota_media_usuarios", "dim_reviews", ["nota_media_usuarios"])


def downgrade() -> None:
    op.drop_index("ix_dim_reviews_nota_media_usuarios", table_name="dim_reviews")
    op.drop_index("ix_fact_movies_performance_popularidade", table_name="fact_movies_performance")
