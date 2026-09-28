from datetime import datetime

from sqlalchemy import CheckConstraint, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.movies.models import generate_surrogate_key

ROLE_CHECK = "papel IN ('admin', 'avaliador')"


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint(ROLE_CHECK, name="papel_valido"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_surrogate_key)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    papel: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
