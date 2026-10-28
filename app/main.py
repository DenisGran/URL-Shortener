"""Application factory: builds the FastAPI app and wires routers and dependencies.

Run with `uvicorn app.main:create_app --factory` (D15): there is no module-level `app`,
so importing this module never reads settings or touches the database.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import home
from app.config import Settings
from app.infra.db import create_pool, open_pool


def create_app(settings: Settings | None = None) -> FastAPI:
    # Tests pass their own Settings; in production they come from the environment.
    resolved = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # Runs once per worker: open the pool before serving, close it on shutdown.
        pool = create_pool(resolved.database_url)
        await open_pool(pool)
        app.state.pool = pool
        try:
            yield
        finally:
            await pool.close()

    # D12 (docs live on GitHub only): no /docs, /redoc or /openapi.json routes.
    # The schema is still available in code via app.openapi() for the export script (T19).
    app = FastAPI(
        title="rapid.codes",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.state.settings = resolved
    app.include_router(home.router)
    return app
