import httpx

from tests.api.conftest import ADMIN_EMAIL, ADMIN_PASSWORD


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
