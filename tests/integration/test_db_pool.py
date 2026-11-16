import pytest

from app.config import Settings
from app.infra.db import POOL_MAX_SIZE, create_pool, open_pool
from app.main import create_app

pytestmark = pytest.mark.anyio


async def test_pool_opens_runs_a_query_and_closes(settings: Settings) -> None:
    pool = create_pool(settings.database_url)

    await open_pool(pool)
    async with pool.connection() as conn:
        cursor = await conn.execute("SELECT 1")
        row = await cursor.fetchone()
    await pool.close()

    assert row == (1,)
    assert pool.max_size == POOL_MAX_SIZE
    assert pool.closed


async def test_lifespan_opens_pool_on_startup_and_closes_it_on_shutdown(
    settings: Settings,
) -> None:
    app = create_app(settings)

    async with app.router.lifespan_context(app):
        pool = app.state.pool
        assert not pool.closed

    assert pool.closed
