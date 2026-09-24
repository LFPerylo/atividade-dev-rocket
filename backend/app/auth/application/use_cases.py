from app.auth.domain.entities import AccessToken, AdminUser, normalize_email, validate_new_admin
from app.auth.domain.errors import InvalidCredentials, InvalidToken
from app.auth.domain.ports import AdminRepository, PasswordHasher, TokenService
from app.shared.transaction import TransactionManager


class AuthenticateAdmin:
    def __init__(
        self, admins: AdminRepository, hasher: PasswordHasher, tokens: TokenService
    ) -> None:
        self._admins = admins
        self._hasher = hasher
        self._tokens = tokens

    async def execute(self, email: str, password: str) -> AccessToken:
        admin = await self._admins.find_by_email(normalize_email(email))
        if admin is None or not self._hasher.verify(password, admin.password_hash):
            raise InvalidCredentials()
        return self._tokens.issue(admin.id)


class GetCurrentAdmin:
    def __init__(self, admins: AdminRepository, tokens: TokenService) -> None:
        self._admins = admins
        self._tokens = tokens

    async def execute(self, token: str) -> AdminUser:
        admin = await self._admins.get(self._tokens.subject_of(token))
        if admin is None:
            raise InvalidToken()
        return admin


class EnsureAdmin:
    def __init__(
        self, admins: AdminRepository, hasher: PasswordHasher, transaction: TransactionManager
    ) -> None:
        self._admins = admins
        self._hasher = hasher
        self._transaction = transaction

    async def execute(self, email: str, name: str, password: str) -> bool:
        normalized_email = normalize_email(email)
        if await self._admins.find_by_email(normalized_email):
            return False
        validate_new_admin(normalized_email, password)
        await self._admins.add(normalized_email, name.strip(), self._hasher.hash(password))
        await self._transaction.commit()
        return True
