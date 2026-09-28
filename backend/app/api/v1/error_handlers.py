from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.auth.domain.errors import (
    AuthError,
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidToken,
    InvalidUserData,
    PermissionDenied,
)
from app.movies.domain.errors import DomainError, MovieNotFound

UNAUTHORIZED_ERRORS = (InvalidCredentials, InvalidToken)


def _status_for(error: Exception) -> int:
    if isinstance(error, MovieNotFound):
        return status.HTTP_404_NOT_FOUND
    if isinstance(error, UNAUTHORIZED_ERRORS):
        return status.HTTP_401_UNAUTHORIZED
    if isinstance(error, PermissionDenied):
        return status.HTTP_403_FORBIDDEN
    if isinstance(error, EmailAlreadyRegistered):
        return status.HTTP_409_CONFLICT
    if isinstance(error, InvalidUserData | DomainError):
        return status.HTTP_422_UNPROCESSABLE_CONTENT
    return status.HTTP_400_BAD_REQUEST


async def _handle(request: Request, error: Exception) -> JSONResponse:
    del request
    headers = {"WWW-Authenticate": "Bearer"} if isinstance(error, UNAUTHORIZED_ERRORS) else None
    return JSONResponse({"detail": str(error)}, status_code=_status_for(error), headers=headers)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _handle)
    app.add_exception_handler(AuthError, _handle)
