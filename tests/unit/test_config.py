import pytest

from app.config import Settings


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        # Heroku's format gets the scheme libpq-based and SQLAlchemy-based tools both accept.
        ("postgres://u:p@host:5432/db", "postgresql://u:p@host:5432/db"),
        ("postgresql://u:p@host:5432/db", "postgresql://u:p@host:5432/db"),
        # Only the scheme changes, never a "postgres://" later in the string.
        ("postgres://u:postgres://@host/db", "postgresql://u:postgres://@host/db"),
    ],
)
def test_database_url_uses_postgresql_scheme(given: str, expected: str) -> None:
    assert Settings(database_url=given).database_url == expected


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("https://rapid.codes/", "https://rapid.codes"),
        ("https://rapid.codes", "https://rapid.codes"),
    ],
)
def test_base_url_has_no_trailing_slash(given: str, expected: str) -> None:
    assert Settings(database_url="postgresql://x", base_url=given).base_url == expected
