from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import jwt

from app.auth.domain.entities import AccessToken
from app.auth.domain.errors import InvalidToken

ALGORITHM = "HS256"
SECONDS_PER_MINUTE = 60


def _utc_now() -> datetime:
    return datetime.now(UTC)


class JwtTokenService:
    def __init__(
        self,
        secret: str,
        expires_minutes: int,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._secret = secret
        self._expires_minutes = expires_minutes
        self._clock = clock

    def issue(self, subject: str) -> AccessToken:
        issued_at = self._clock()
        claims = {
            "sub": subject,
            "iat": issued_at,
            "exp": issued_at + timedelta(minutes=self._expires_minutes),
        }
        return AccessToken(
            value=jwt.encode(claims, self._secret, algorithm=ALGORITHM),
            expires_in_seconds=self._expires_minutes * SECONDS_PER_MINUTE,
        )

    def subject_of(self, token: str) -> str:
        try:
            claims = jwt.decode(
                token, self._secret, algorithms=[ALGORITHM], options={"require": ["sub", "exp"]}
            )
        except jwt.PyJWTError as error:
            raise InvalidToken() from error
        return str(claims["sub"])
