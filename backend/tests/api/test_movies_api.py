import httpx
import pytest

NEW_MOVIE = {
    "titulo": "O Jardineiro Fiel",
    "diretores": ["Fernando Meirelles"],
    "generos": ["g-drama"],
    "ano_lancamento": 2005,
    "sinopse": "Um diplomata investiga a morte da esposa.",
    "duracao_minutos": 129,
    "url_poster": "https://image.tmdb.org/t/p/w500/poster.jpg",
}


async def test_list_movies_returns_paginated_summaries(client: httpx.AsyncClient) -> None:
    response = await client.get(
        "/movies", params={"tamanho": 1, "ordenar": "titulo", "ordem": "asc"}
    )

    assert response.status_code == 200
    body = response.json()
    assert (body["total"], body["pagina"], body["tamanho"], body["paginas"]) == (2, 1, 1, 2)
    movie = body["itens"][0]
    assert movie == {
        "id": "m-cdd",
        "titulo": "Cidade de Deus",
        "ano_lancamento": 2002,
        "url_poster": None,
        "generos": [{"id": "g-crime", "nome": "Crime"}, {"id": "g-drama", "nome": "Drama"}],
        "diretores": ["Fernando Meirelles", 'Kátia ""K"" Lund', 'Kátia ""K"" Lund"'],
        "media_estrelas": 4.5,
        "total_avaliacoes": 2,
    }


@pytest.mark.parametrize(
    ("params", "titles"),
    [
        ({"busca": "cegueira"}, ["Ensaio sobre a Cegueira"]),
        ({"genero": "g-crime"}, ["Cidade de Deus"]),
        ({"ano_de": 2005}, ["Ensaio sobre a Cegueira"]),
        ({"estrelas_min": 4}, ["Cidade de Deus"]),
    ],
)
async def test_list_movies_applies_filters(
    client: httpx.AsyncClient, params: dict[str, object], titles: list[str]
) -> None:
    response = await client.get("/movies", params=params)

    assert [movie["titulo"] for movie in response.json()["itens"]] == titles


@pytest.mark.parametrize(
    "params", [{"pagina": 0}, {"tamanho": 500}, {"ano_de": 2010, "ano_ate": 2000}, {"ordenar": "x"}]
)
async def test_list_movies_rejects_invalid_query(
    client: httpx.AsyncClient, params: dict[str, object]
) -> None:
    response = await client.get("/movies", params=params)

    assert response.status_code == 422


async def test_get_movie_returns_details(client: httpx.AsyncClient) -> None:
    response = await client.get("/movies/m-cdd")

    assert response.status_code == 200
    body = response.json()
    assert body["sinopse"] == '"Buscapé" "cresce"."'
    assert body["diretores"] == ["Fernando Meirelles", 'Kátia ""K"" Lund', 'Kátia ""K"" Lund"']
    assert body["produtoras"] == ["O2 Filmes"]
    assert body["desempenho"]["nota_imdb"] == 8.6
    assert (body["media_estrelas"], body["total_avaliacoes"]) == (4.5, 2)


async def test_get_movie_returns_404_for_unknown_movie(client: httpx.AsyncClient) -> None:
    response = await client.get("/movies/inexistente")

    assert response.status_code == 404
    assert response.json() == {"detail": "Filme inexistente não encontrado"}


async def test_create_movie_requires_authentication(client: httpx.AsyncClient) -> None:
    response = await client.post("/movies", json=NEW_MOVIE)

    assert response.status_code == 401


async def test_create_movie_returns_created_details(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.post("/movies", json=NEW_MOVIE, headers=auth_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["titulo"] == "O Jardineiro Fiel"
    assert body["generos"] == [{"id": "g-drama", "nome": "Drama"}]
    assert body["diretores"] == ["Fernando Meirelles"]
    assert response.headers["location"].endswith(f"/movies/{body['id']}")


@pytest.mark.parametrize(
    "overrides",
    [
        {"titulo": " "},
        {"generos": ["g-inexistente"]},
        {"ano_lancamento": 1500},
        {"duracao_minutos": -1},
    ],
)
async def test_create_movie_rejects_invalid_data(
    client: httpx.AsyncClient, auth_headers: dict[str, str], overrides: dict[str, object]
) -> None:
    response = await client.post("/movies", json=NEW_MOVIE | overrides, headers=auth_headers)

    assert response.status_code == 422


async def test_update_movie_replaces_data(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.put("/movies/m-blind", json=NEW_MOVIE, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["titulo"] == "O Jardineiro Fiel"
    assert response.json()["elenco"] == ["Alice Braga"]


async def test_update_movie_returns_404_for_unknown_movie(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.put("/movies/x", json=NEW_MOVIE, headers=auth_headers)

    assert response.status_code == 404


async def test_delete_movie_removes_it(
    client: httpx.AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.delete("/movies/m-cdd", headers=auth_headers)

    assert response.status_code == 204
    assert (await client.get("/movies/m-cdd")).status_code == 404


async def test_delete_movie_requires_authentication(client: httpx.AsyncClient) -> None:
    assert (await client.delete("/movies/m-cdd")).status_code == 401
