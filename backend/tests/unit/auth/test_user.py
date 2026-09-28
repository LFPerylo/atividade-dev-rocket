import pytest

from app.auth.domain.entities import Role, User
from app.auth.domain.errors import PermissionDenied


def make_user(role: Role) -> User:
    return User(id="u1", email="a@b.dev", name="Ana", role=role, password_hash="h")


def test_admin_passes_admin_requirement() -> None:
    make_user(Role.ADMIN).require_admin()


def test_reviewer_is_denied_admin_actions() -> None:
    with pytest.raises(PermissionDenied):
        make_user(Role.REVIEWER).require_admin()
