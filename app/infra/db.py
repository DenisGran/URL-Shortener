"""Postgres connection pool: one per worker process, opened and closed by the app lifespan."""

from fastapi import Request
from psycopg_pool import AsyncConnectionPool

# 2 uvicorn workers x 5 = 10 connections, half of Heroku Essential-0's limit of 20,
# leaving room for psql and the release-phase migration. Check before raising.
POOL_MIN_SIZE = 1
POOL_MAX_SIZE = 5
OPEN_TIMEOUT_SECONDS = 10.0


def create_pool(conninfo: str) -> AsyncConnectionPool:
    # open=False: opening is async and belongs in the lifespan, not in a constructor.
    return AsyncConnectionPool(
        conninfo,
        min_size=POOL_MIN_SIZE,
        max_size=POOL_MAX_SIZE,
        open=False,
    )


async def open_pool(pool: AsyncConnectionPool) -> None:
    # wait=True fails startup if the DB is unreachable, instead of failing the first request.
    await pool.open(wait=True, timeout=OPEN_TIMEOUT_SECONDS)


def get_pool(request: Request) -> AsyncConnectionPool:
    """FastAPI dependency: the pool the lifespan stored on app.state."""
    pool: AsyncConnectionPool = request.app.state.pool
    return pool
