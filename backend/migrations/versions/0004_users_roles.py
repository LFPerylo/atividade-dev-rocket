from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_users_roles"
down_revision: str | Sequence[str] | None = "0003_sort_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.rename_table("admin_users", "users")
    with op.batch_alter_table("users", recreate="always") as batch:
        batch.add_column(
            sa.Column("papel", sa.String(20), nullable=False, server_default="admin")
        )
        batch.drop_constraint("uq_admin_users_email", type_="unique")
        batch.create_unique_constraint("uq_users_email", ["email"])
        batch.create_check_constraint("papel_valido", "papel IN ('admin', 'avaliador')")
    with op.batch_alter_table("users") as batch:
        batch.alter_column("papel", server_default=None, existing_type=sa.String(20))
    with op.batch_alter_table("movie_reviews", recreate="always") as batch:
        batch.add_column(sa.Column("sk_user_id", sa.String(64), nullable=True))
        batch.create_foreign_key(
            "fk_movie_reviews_sk_user_id_users",
            "users",
            ["sk_user_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch.create_index("ix_movie_reviews_sk_user_id", ["sk_user_id"])


def downgrade() -> None:
    with op.batch_alter_table("movie_reviews", recreate="always") as batch:
        batch.drop_index("ix_movie_reviews_sk_user_id")
        batch.drop_constraint("fk_movie_reviews_sk_user_id_users", type_="foreignkey")
        batch.drop_column("sk_user_id")
    with op.batch_alter_table("users", recreate="always") as batch:
        batch.drop_constraint(op.f("ck_users_papel_valido"), type_="check")
        batch.drop_constraint("uq_users_email", type_="unique")
        batch.create_unique_constraint("uq_admin_users_email", ["email"])
        batch.drop_column("papel")
    op.rename_table("users", "admin_users")
