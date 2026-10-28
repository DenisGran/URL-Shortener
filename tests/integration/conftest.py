import os

import pytest
from pydantic import ValidationError

from app.config import Settings


@pytest.fixture
def settings() -> Settings:
    # Reads DATABASE_URL from the environment or .env. Locally without a DB configured,
    # integration tests skip; in CI (GitHub sets CI=true) a missing DB is a failure.
    try:
        return Settings()
    except ValidationError:
        if os.environ.get("CI") == "true":
            raise
        pytest.skip("DATABASE_URL not set: run `docker compose up -d db` and create .env")
