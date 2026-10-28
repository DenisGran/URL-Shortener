"""Application factory: builds the FastAPI app and wires routers and dependencies."""

import os  # deliberate lint error (T2 proof), reverted next commit

from fastapi import FastAPI

from app.api import home


def create_app() -> FastAPI:
    # D12 (docs live on GitHub only): no /docs, /redoc or /openapi.json routes.
    # The schema is still available in code via app.openapi() for the export script (T19).
    app = FastAPI(title="rapid.codes", docs_url=None, redoc_url=None, openapi_url=None)
    app.include_router(home.router)
    return app


app = create_app()
