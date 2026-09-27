import httpx
import pytest

REVIEW = {"nome": "Diego", "estrelas": 3.5, "comentario": "Tenso e bem filmado."}


async def test_list_reviews_returns_paginated_reviews(client: httpx.AsyncClient) -> None:
    response = await client.get("/movies/m-cdd/reviews", params={"tamanho": 1})

    assert response.status_code == 200
    body = response.json()
    assert (body["total"], body["paginas"]) == (2, 2)
    assert set(body["itens"][0]) == {"id", "nome", "estrelas", "nota", "comentario", "criado_em"}


async def test_list_reviews_returns_404_for_unknown_movie(client: httpx.AsyncClient) -> None:
    assert (await client.get("/movies/x/reviews")).status_code == 404


async def test_add_review_updates_movie_average(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.post("/movies/m-blind/reviews", json=REVIEW, headers=auth_headers)

    assert response.status_code == 201
    assert (response.json()["estrelas"], response.json()["nota"]) == (3.5, 7.0)
    movie = (await client.get("/movies/m-blind")).json()
    assert (movie["media_estrelas"], movie["total_avaliacoes"]) == (3.5, 1)


@pytest.mark.parametrize(
    "overrides", [{"estrelas": 0.5}, {"estrelas": 4.2}, {"nome": " "}, {"comentario": ""}]
)
async def test_add_review_rejects_invalid_data(
    client: httpx.AsyncClient, auth_headers: dict[str, str], overrides: dict[str, object]
) -> None:
    response = await client.post(
        "/movies/m-cdd/reviews", json=REVIEW | overrides, headers=auth_headers
    )

    assert response.status_code == 422


async def test_add_review_requires_authentication(client: httpx.AsyncClient) -> None:
    assert (await client.post("/movies/m-cdd/reviews", json=REVIEW)).status_code == 401


async def test_add_review_returns_404_for_unknown_movie(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.post("/movies/x/reviews", json=REVIEW, headers=auth_headers)

    assert response.status_code == 404
