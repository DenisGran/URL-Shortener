import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import Settings
from app.main import create_app


@pytest.fixture
def anyio_backend() -> tuple[str, dict[str, Any]]:
    # anyio's pytest plugin runs @pytest.mark.anyio tests; asyncio only, no trio.
    # Selector loop: psycopg's async mode can't run on Windows' default ProactorEventLoop.
    # (It's already the default on Linux, so CI and Heroku are unaffected.)
    return ("asyncio", {"loop_factory": asyncio.SelectorEventLoop})


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    # Calls the app in-process through ASGI: no server, no network.
    # ASGITransport doesn't run the lifespan, so no DB is needed and the URL is never used.
    app = create_app(Settings(database_url="postgresql://unused@localhost/unused"))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
