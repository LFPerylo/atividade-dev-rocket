from app.auth.domain.entities import (
    AccessToken,
    Role,
    User,
    normalize_email,
    validate_new_user,
)
from app.auth.domain.errors import EmailAlreadyRegistered, InvalidCredentials, InvalidToken
from app.auth.domain.ports import PasswordHasher, TokenService, UserRepository
from app.shared.transaction import TransactionManager

DECOY_PASSWORD = "senha-inexistente-para-tempo-constante"


class AuthenticateUser:
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        tokens: TokenService,
        decoy_hash: str | None = None,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens
        self._decoy_hash = decoy_hash or hasher.hash(DECOY_PASSWORD)

    async def execute(self, email: str, password: str) -> AccessToken:
        user = await self._users.find_by_email(normalize_email(email))
        password_hash = user.password_hash if user else self._decoy_hash
        password_matches = self._hasher.verify(password, password_hash)
        if user is None or not password_matches:
            raise InvalidCredentials()
        return self._tokens.issue(user.id)


class GetCurrentUser:
    def __init__(self, users: UserRepository, tokens: TokenService) -> None:
        self._users = users
        self._tokens = tokens

    async def execute(self, token: str) -> User:
        user = await self._users.get(self._tokens.subject_of(token))
        if user is None:
            raise InvalidToken()
        return user


class EnsureAdmin:
    def __init__(
        self, users: UserRepository, hasher: PasswordHasher, transaction: TransactionManager
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._transaction = transaction

    async def execute(self, email: str, name: str, password: str) -> bool:
        normalized_email = normalize_email(email)
        if await self._users.find_by_email(normalized_email):
            return False
        validate_new_user(normalized_email, name.strip(), password)
        await self._users.add(
            normalized_email, name.strip(), self._hasher.hash(password), Role.ADMIN
        )
        await self._transaction.commit()
        return True


class RegisterReviewer:
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        tokens: TokenService,
        transaction: TransactionManager,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens
        self._transaction = transaction

    async def execute(self, name: str, email: str, password: str) -> AccessToken:
        normalized_email = normalize_email(email)
        clean_name = name.strip()
        validate_new_user(normalized_email, clean_name, password)
        if await self._users.find_by_email(normalized_email):
            raise EmailAlreadyRegistered()
        user = await self._users.add(
            normalized_email, clean_name, self._hasher.hash(password), Role.REVIEWER
        )
        await self._transaction.commit()
        return self._tokens.issue(user.id)
