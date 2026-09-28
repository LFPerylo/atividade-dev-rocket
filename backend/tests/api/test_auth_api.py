import httpx

from tests.api.conftest import ADMIN_EMAIL, ADMIN_PASSWORD, REVIEWER, bearer


async def test_login_returns_bearer_token(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_PASSWORD}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0
    assert body["access_token"]


async def test_login_rejects_wrong_password(client: httpx.AsyncClient) -> None:
    response = await client.post("/auth/login", json={"email": ADMIN_EMAIL, "senha": "errada123"})

    assert response.status_code == 401
    assert response.json() == {"detail": "E-mail ou senha inválidos"}


async def test_me_returns_authenticated_admin(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["email"] == ADMIN_EMAIL


async def test_me_requires_token(client: httpx.AsyncClient) -> None:
    response = await client.get("/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_me_rejects_invalid_token(client: httpx.AsyncClient) -> None:
    response = await client.get("/auth/me", headers={"Authorization": "Bearer lixo"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Sessão inválida ou expirada"}


async def test_me_exposes_admin_role(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.get("/auth/me", headers=auth_headers)

    assert response.json()["papel"] == "admin"


async def test_register_creates_reviewer_and_returns_token(client: httpx.AsyncClient) -> None:
    response = await client.post("/auth/register", json=REVIEWER)

    assert response.status_code == 201
    me = await client.get("/auth/me", headers=bearer(response.json()["access_token"]))
    assert me.json() | {"id": "x"} == {
        "id": "x",
        "email": "bia@exemplo.com",
        "nome": "Bia Lima",
        "papel": "avaliador",
    }


async def test_register_rejects_duplicated_email(client: httpx.AsyncClient) -> None:
    await client.post("/auth/register", json=REVIEWER)

    response = await client.post("/auth/register", json=REVIEWER | {"nome": "Outra"})

    assert response.status_code == 409
    assert response.json() == {"detail": "Já existe uma conta com este e-mail"}


async def test_register_validates_password_length(client: httpx.AsyncClient) -> None:
    response = await client.post("/auth/register", json=REVIEWER | {"senha": "curta"})

    assert response.status_code == 422
    assert response.json() == {"detail": "Senha deve ter ao menos 8 caracteres"}


async def test_registered_reviewer_can_log_in(client: httpx.AsyncClient) -> None:
    await client.post("/auth/register", json=REVIEWER)

    response = await client.post(
        "/auth/login", json={"email": REVIEWER["email"], "senha": REVIEWER["senha"]}
    )

    assert response.status_code == 200
