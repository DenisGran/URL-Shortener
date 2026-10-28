# rapid.codes

A URL shortener: paste a long URL, get `https://rapid.codes/<code>`, which redirects with a 302.

> Work in progress. Live at https://rapid.codes once T3 (custom domain) is done.

- Requirements: [docs/SPEC.md](docs/SPEC.md)
- Design: [docs/design.md](docs/design.md)
- Decisions: [docs/decisions.md](docs/decisions.md)
- Task list: [docs/tasks.md](docs/tasks.md)

## Run locally

Requires [uv](https://docs.astral.sh/uv/) (it installs Python 3.12 for you) and Docker (for Postgres).

```bash
cp .env.example .env
docker compose up -d db
uv sync
uv run uvicorn app.main:create_app --factory --reload
```

Then open http://localhost:8000/.

> **Windows:** keep `--reload`. Without it, uvicorn uses Windows' `ProactorEventLoop`, which psycopg's async mode can't use, and startup fails. With `--reload` uvicorn runs the app in a subprocess on a compatible loop. Linux (CI, Heroku) is unaffected.

## Checks

The same four checks run in CI on every PR and every push to `main`:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy app tests
uv run pytest
```
