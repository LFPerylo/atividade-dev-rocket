from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.domain.entities import AdminUser
from app.auth.infrastructure.models import AdminUserModel


def _to_entity(model: AdminUserModel) -> AdminUser:
    return AdminUser(
        id=model.id, email=model.email, name=model.name, password_hash=model.password_hash
    )


class SqlAlchemyAdminRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_email(self, email: str) -> AdminUser | None:
        model = await self._session.scalar(
            select(AdminUserModel).where(AdminUserModel.email == email)
        )
        return _to_entity(model) if model else None

    async def get(self, admin_id: str) -> AdminUser | None:
        model = await self._session.get(AdminUserModel, admin_id)
        return _to_entity(model) if model else None

    async def add(self, email: str, name: str, password_hash: str) -> AdminUser:
        model = AdminUserModel(email=email, name=name, password_hash=password_hash)
        self._session.add(model)
        await self._session.flush()
        return _to_entity(model)
