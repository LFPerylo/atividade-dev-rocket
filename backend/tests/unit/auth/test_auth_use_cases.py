import pytest

from app.auth.application.use_cases import AuthenticateAdmin, EnsureAdmin, GetCurrentAdmin
from app.auth.domain.errors import InvalidAdminData, InvalidCredentials, InvalidToken
from tests.unit.auth.fakes import FakeTokenService, InMemoryAdminRepository, PlainTextHasher
from tests.unit.movies.fakes import SpyTransactionManager


@pytest.fixture
def admins() -> InMemoryAdminRepository:
    return InMemoryAdminRepository()


async def create_admin(admins: InMemoryAdminRepository) -> None:
    await EnsureAdmin(admins, PlainTextHasher(), SpyTransactionManager()).execute(
        email="Admin@RocketLab.dev", name="Admin", password="s3nha-forte"
    )


async def test_ensure_admin_creates_admin_with_normalized_email_and_hash(
    admins: InMemoryAdminRepository,
) -> None:
    await create_admin(admins)

    admin = await admins.find_by_email("admin@rocketlab.dev")
    assert admin is not None
    assert admin.password_hash == "hashed:s3nha-forte"


async def test_ensure_admin_is_idempotent(admins: InMemoryAdminRepository) -> None:
    await create_admin(admins)
    transaction = SpyTransactionManager()

    created = await EnsureAdmin(admins, PlainTextHasher(), transaction).execute(
        email="admin@rocketlab.dev", name="Admin", password="outra"
    )

    assert created is False
    assert len(admins.admins) == 1
    assert transaction.commits == 0


@pytest.mark.parametrize(
    ("email", "password"), [("sem-arroba", "s3nha-forte"), ("a@b.dev", "curta")]
)
async def test_ensure_admin_validates_email_and_password_length(
    admins: InMemoryAdminRepository, email: str, password: str
) -> None:
    with pytest.raises(InvalidAdminData):
        await EnsureAdmin(admins, PlainTextHasher(), SpyTransactionManager()).execute(
            email=email, name="Admin", password=password
        )


async def test_authenticate_issues_token_for_valid_credentials(
    admins: InMemoryAdminRepository,
) -> None:
    await create_admin(admins)

    token = await AuthenticateAdmin(admins, PlainTextHasher(), FakeTokenService()).execute(
        email=" ADMIN@rocketlab.dev ", password="s3nha-forte"
    )

    assert token.value == "token:a1"


@pytest.mark.parametrize(
    ("email", "password"),
    [("admin@rocketlab.dev", "errada"), ("outro@rocketlab.dev", "s3nha-forte")],
)
async def test_authenticate_rejects_invalid_credentials(
    admins: InMemoryAdminRepository, email: str, password: str
) -> None:
    await create_admin(admins)

    with pytest.raises(InvalidCredentials):
        await AuthenticateAdmin(admins, PlainTextHasher(), FakeTokenService()).execute(
            email=email, password=password
        )


async def test_get_current_admin_resolves_token_subject(
    admins: InMemoryAdminRepository,
) -> None:
    await create_admin(admins)

    admin = await GetCurrentAdmin(admins, FakeTokenService()).execute("token:a1")

    assert admin.email == "admin@rocketlab.dev"


@pytest.mark.parametrize("token", ["lixo", "token:inexistente"])
async def test_get_current_admin_rejects_invalid_or_orphan_tokens(
    admins: InMemoryAdminRepository, token: str
) -> None:
    with pytest.raises(InvalidToken):
        await GetCurrentAdmin(admins, FakeTokenService()).execute(token)
