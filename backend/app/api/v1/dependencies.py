from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.application.use_cases import DECOY_PASSWORD, AuthenticateAdmin, GetCurrentAdmin
from app.auth.domain.entities import AdminUser
from app.auth.domain.errors import InvalidToken
from app.auth.infrastructure.admin_repository import SqlAlchemyAdminRepository
from app.auth.infrastructure.jwt_token_service import JwtTokenService
from app.auth.infrastructure.password_hasher import Argon2PasswordHasher
from app.core.config import get_settings
from app.db.session import get_db
from app.db.transaction import SqlAlchemyTransactionManager
from app.movies.infrastructure.genre_repository import SqlAlchemyGenreRepository
from app.movies.infrastructure.movie_repository import SqlAlchemyMovieRepository
from app.movies.infrastructure.review_repository import SqlAlchemyReviewRepository

SessionDep = Annotated[AsyncSession, Depends(get_db)]

bearer_scheme = HTTPBearer(auto_error=False)
password_hasher = Argon2PasswordHasher()
decoy_hash = password_hasher.hash(DECOY_PASSWORD)


def get_token_service() -> JwtTokenService:
    settings = get_settings()
    return JwtTokenService(
        secret=settings.jwt_secret_key, expires_minutes=settings.jwt_expires_minutes
    )


TokenServiceDep = Annotated[JwtTokenService, Depends(get_token_service)]


def get_movie_repository(session: SessionDep) -> SqlAlchemyMovieRepository:
    return SqlAlchemyMovieRepository(session)


def get_genre_repository(session: SessionDep) -> SqlAlchemyGenreRepository:
    return SqlAlchemyGenreRepository(session)


def get_review_repository(session: SessionDep) -> SqlAlchemyReviewRepository:
    return SqlAlchemyReviewRepository(session)


def get_transaction(session: SessionDep) -> SqlAlchemyTransactionManager:
    return SqlAlchemyTransactionManager(session)


MovieRepositoryDep = Annotated[SqlAlchemyMovieRepository, Depends(get_movie_repository)]
GenreRepositoryDep = Annotated[SqlAlchemyGenreRepository, Depends(get_genre_repository)]
ReviewRepositoryDep = Annotated[SqlAlchemyReviewRepository, Depends(get_review_repository)]
TransactionDep = Annotated[SqlAlchemyTransactionManager, Depends(get_transaction)]


def get_authenticate_admin(session: SessionDep, tokens: TokenServiceDep) -> AuthenticateAdmin:
    return AuthenticateAdmin(
        SqlAlchemyAdminRepository(session), password_hasher, tokens, decoy_hash
    )


async def get_current_admin(
    session: SessionDep,
    tokens: TokenServiceDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AdminUser:
    if credentials is None:
        raise InvalidToken()
    use_case = GetCurrentAdmin(SqlAlchemyAdminRepository(session), tokens)
    return await use_case.execute(credentials.credentials)


CurrentAdmin = Annotated[AdminUser, Depends(get_current_admin)]
