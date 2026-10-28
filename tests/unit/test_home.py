import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_home_returns_200(client: AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
async def test_docs_routes_are_not_exposed(client: AsyncClient, path: str) -> None:
    # D12: docs live on GitHub only.
    response = await client.get(path)

    assert response.status_code == 404
