from app.auth.domain.entities import AccessToken, AdminUser
from app.auth.domain.errors import InvalidToken


class PlainTextHasher:
    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == f"hashed:{password}"


class FakeTokenService:
    def issue(self, subject: str) -> AccessToken:
        return AccessToken(value=f"token:{subject}", expires_in_seconds=3600)

    def subject_of(self, token: str) -> str:
        if not token.startswith("token:"):
            raise InvalidToken()
        return token.removeprefix("token:")


class InMemoryAdminRepository:
    def __init__(self) -> None:
        self.admins: dict[str, AdminUser] = {}

    async def find_by_email(self, email: str) -> AdminUser | None:
        return next((admin for admin in self.admins.values() if admin.email == email), None)

    async def get(self, admin_id: str) -> AdminUser | None:
        return self.admins.get(admin_id)

    async def add(self, email: str, name: str, password_hash: str) -> AdminUser:
        admin = AdminUser(
            id=f"a{len(self.admins) + 1}", email=email, name=name, password_hash=password_hash
        )
        self.admins[admin.id] = admin
        return admin
