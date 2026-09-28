from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.domain.entities import Role, User
from app.auth.infrastructure.models import UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        name=model.name,
        role=Role(model.papel),
        password_hash=model.password_hash,
    )


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_email(self, email: str) -> User | None:
        model = await self._session.scalar(select(UserModel).where(UserModel.email == email))
        return _to_entity(model) if model else None

    async def get(self, user_id: str) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return _to_entity(model) if model else None

    async def add(self, email: str, name: str, password_hash: str, role: Role) -> User:
        model = UserModel(email=email, name=name, papel=role.value, password_hash=password_hash)
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)
