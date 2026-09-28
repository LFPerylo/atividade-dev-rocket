from app.auth.domain.entities import AccessToken, Role, User
from app.auth.domain.errors import InvalidToken


class PlainTextHasher:
    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == f"hashed:{password}"


class CountingHasher(PlainTextHasher):
    def __init__(self) -> None:
        self.verifications = 0

    def verify(self, password: str, password_hash: str) -> bool:
        self.verifications += 1
        return super().verify(password, password_hash)


class FakeTokenService:
    def issue(self, subject: str) -> AccessToken:
        return AccessToken(value=f"token:{subject}", expires_in_seconds=3600)

    def subject_of(self, token: str) -> str:
        if not token.startswith("token:"):
            raise InvalidToken()
        return token.removeprefix("token:")


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    async def find_by_email(self, email: str) -> User | None:
        return next((user for user in self.users.values() if user.email == email), None)

    async def get(self, user_id: str) -> User | None:
        return self.users.get(user_id)

    async def add(self, email: str, name: str, password_hash: str, role: Role) -> User:
        user = User(
            id=f"u{len(self.users) + 1}",
            email=email,
            name=name,
            role=role,
            password_hash=password_hash,
        )
        self.users[user.id] = user
        return user
