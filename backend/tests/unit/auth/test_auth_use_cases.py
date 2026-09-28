import pytest

from app.auth.application.use_cases import (
    AuthenticateUser,
    EnsureAdmin,
    GetCurrentUser,
    RegisterReviewer,
)
from app.auth.domain.entities import Role
from app.auth.domain.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidToken,
    InvalidUserData,
)
from tests.unit.auth.fakes import (
    CountingHasher,
    FakeTokenService,
    InMemoryUserRepository,
    PlainTextHasher,
)
from tests.unit.movies.fakes import SpyTransactionManager


@pytest.fixture
def users() -> InMemoryUserRepository:
    return InMemoryUserRepository()


async def create_admin(users: InMemoryUserRepository) -> None:
    await EnsureAdmin(users, PlainTextHasher(), SpyTransactionManager()).execute(
        email="Admin@RocketLab.dev", name="Admin", password="s3nha-forte"
    )


def register(users: InMemoryUserRepository, transaction: SpyTransactionManager) -> RegisterReviewer:
    return RegisterReviewer(users, PlainTextHasher(), FakeTokenService(), transaction)


async def test_ensure_admin_creates_admin_with_normalized_email_and_hash(
    users: InMemoryUserRepository,
) -> None:
    await create_admin(users)

    admin = await users.find_by_email("admin@rocketlab.dev")
    assert admin is not None
    assert admin.role is Role.ADMIN
    assert admin.password_hash == "hashed:s3nha-forte"


async def test_ensure_admin_is_idempotent(users: InMemoryUserRepository) -> None:
    await create_admin(users)
    transaction = SpyTransactionManager()

    created = await EnsureAdmin(users, PlainTextHasher(), transaction).execute(
        email="admin@rocketlab.dev", name="Admin", password="outra"
    )

    assert created is False
    assert len(users.users) == 1
    assert transaction.commits == 0


@pytest.mark.parametrize(
    ("name", "email", "password"),
    [
        ("Ana", "sem-arroba", "s3nha-forte"),
        ("Ana", "a@b.dev", "curta"),
        (" ", "a@b.dev", "s3nha-forte"),
        ("A" * 121, "a@b.dev", "s3nha-forte"),
    ],
)
async def test_register_validates_name_email_and_password(
    users: InMemoryUserRepository, name: str, email: str, password: str
) -> None:
    with pytest.raises(InvalidUserData):
        await register(users, SpyTransactionManager()).execute(
            name=name, email=email, password=password
        )


async def test_register_creates_reviewer_and_logs_in(users: InMemoryUserRepository) -> None:
    transaction = SpyTransactionManager()

    token = await register(users, transaction).execute(
        name=" Ana Souza ", email=" Ana@Exemplo.com ", password="s3nha-forte"
    )

    user = await users.find_by_email("ana@exemplo.com")
    assert user is not None
    assert (user.name, user.role, user.password_hash) == (
        "Ana Souza",
        Role.REVIEWER,
        "hashed:s3nha-forte",
    )
    assert token.value == f"token:{user.id}"
    assert transaction.commits == 1


async def test_register_rejects_email_already_in_use(users: InMemoryUserRepository) -> None:
    await create_admin(users)

    with pytest.raises(EmailAlreadyRegistered):
        await register(users, SpyTransactionManager()).execute(
            name="Outra", email="ADMIN@rocketlab.dev", password="s3nha-forte"
        )


async def test_authenticate_issues_token_for_valid_credentials(
    users: InMemoryUserRepository,
) -> None:
    await create_admin(users)

    token = await AuthenticateUser(users, PlainTextHasher(), FakeTokenService()).execute(
        email=" ADMIN@rocketlab.dev ", password="s3nha-forte"
    )

    assert token.value == "token:u1"


@pytest.mark.parametrize(
    ("email", "password"),
    [("admin@rocketlab.dev", "errada"), ("outro@rocketlab.dev", "s3nha-forte")],
)
async def test_authenticate_rejects_invalid_credentials(
    users: InMemoryUserRepository, email: str, password: str
) -> None:
    await create_admin(users)

    with pytest.raises(InvalidCredentials):
        await AuthenticateUser(users, PlainTextHasher(), FakeTokenService()).execute(
            email=email, password=password
        )


async def test_authenticate_verifies_a_hash_even_for_unknown_email(
    users: InMemoryUserRepository,
) -> None:
    hasher = CountingHasher()

    with pytest.raises(InvalidCredentials):
        await AuthenticateUser(users, hasher, FakeTokenService()).execute(
            email="ninguem@rocketlab.dev", password="qualquer-senha"
        )

    assert hasher.verifications == 1


async def test_get_current_user_resolves_token_subject(users: InMemoryUserRepository) -> None:
    await create_admin(users)

    user = await GetCurrentUser(users, FakeTokenService()).execute("token:u1")

    assert user.email == "admin@rocketlab.dev"


@pytest.mark.parametrize("token", ["lixo", "token:inexistente"])
async def test_get_current_user_rejects_invalid_or_orphan_tokens(
    users: InMemoryUserRepository, token: str
) -> None:
    with pytest.raises(InvalidToken):
        await GetCurrentUser(users, FakeTokenService()).execute(token)
