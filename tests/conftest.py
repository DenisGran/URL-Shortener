from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.fixture
def anyio_backend() -> str:
    # anyio's pytest plugin runs @pytest.mark.anyio tests; asyncio only, no trio.
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    # Calls the app in-process through ASGI: no server, no network.
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
