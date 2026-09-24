import httpx


async def test_list_genres(client: httpx.AsyncClient) -> None:
    response = await client.get("/genres")

    assert response.status_code == 200
    assert response.json() == [
        {"id": "g-crime", "nome": "Crime"},
        {"id": "g-drama", "nome": "Drama"},
    ]
