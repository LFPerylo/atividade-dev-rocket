from sqlalchemy import MetaData

from app.auth.infrastructure.models import AdminUserModel
from app.db.base import Base
from app.movies.models import DimMovie

REGISTERED_MODELS = (AdminUserModel, DimMovie)


def registered_metadata() -> MetaData:
    return Base.metadata
