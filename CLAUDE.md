# CLAUDE.md — rapid.codes

A URL shortener (bitly-like) at https://rapid.codes. Portfolio project for Denis's CV: judged on code quality, tests, docs and measured performance, not on feature count.

Read these before changing anything:
- `docs/SPEC.md`: requirements (FR1–FR12) and what's out of scope
- `docs/design.md`: architecture, data model, API, decisions D1–D12
- `docs/tasks.md`: the ordered task list; work on the next unchecked task only

## How we work

- **Denis writes the core logic and its tests** (`app/domain`, `app/services`, `app/repositories`, the endpoints and their tests). Claude guides, explains and reviews; Claude does **not** write that code for him unless he explicitly asks. Give hints, point to the line, explain the concept, suggest a test case.
- **Claude handles boilerplate and doc drafts**: config, CI, Docker, Procfile, logging and telemetry wiring, the HTML page, README and ADR drafts.
- **Denis makes the final decisions.** Propose options with trade-offs; don't decide silently.
- **Be brutally honest.** Point out bugs, weak designs and wrong assumptions directly, including in your own earlier advice.
- **Explain every technical term** the first time it comes up (e.g. "connection pool", "release phase", "ON CONFLICT").
- **When referring to a requirement or decision ID, always say what it means**, e.g. "FR2 (same URL returns the same code)", never a bare "FR2".
- Keep `docs/SPEC.md`, `docs/design.md` and `docs/tasks.md` in sync with the code. If a change contradicts them, flag it and update the doc in the same PR.

## Stack

Python 3.12 (via uv, D13) · FastAPI · uvicorn (2 workers) · PostgreSQL 16 · psycopg 3 + psycopg_pool (raw SQL, no ORM) · Alembic · pytest + httpx · ruff · mypy · OpenTelemetry (OTLP push) · k6 · Heroku Basic dyno + Heroku Postgres Essential-0 · GitHub Actions.

## Commands

```bash
uv sync                                          # install deps (incl. dev) from uv.lock
docker compose up -d db                          # local Postgres
uv run alembic upgrade head                      # apply migrations
uv run uvicorn app.main:create_app --factory --reload   # run locally on :8000
uv run pytest                                    # all tests (integration tests need Docker Postgres)
uv run pytest tests/unit                         # fast tests only
uv run ruff check . && uv run ruff format --check .   # lint + format check
uv run mypy app tests                            # type check (strict)
uv run python -m scripts.export_openapi          # regenerate docs/openapi.json
k6 run loadtest/redirect.js                      # load test (local only)
```

## Architecture rules

- Layers: `api` (HTTP only) → `services` (rules) → `repositories` (SQL). `domain` is pure: no I/O, no FastAPI imports.
- Services depend on the `LinkRepository` Protocol, never on `postgres.py` directly (DIP, dependency inversion). Wire dependencies with FastAPI `Depends` in `main.py`; no module-level globals for state.
- FR2 (same URL, same code) and code uniqueness are enforced by the DB's `UNIQUE` constraints with `INSERT … ON CONFLICT DO NOTHING`. Never replace that with "SELECT, then INSERT" (race condition).
- SQL is always parameterized. No string-formatted SQL, ever.
- Codes come from `secrets`, never `random`.

## Hard "don'ts" (decided; ask Denis before changing)

- No `/docs`, `/redoc`, `/openapi.json`, `/healthz` or `/metrics` routes (D10 metrics are pushed, D12 docs live on GitHub). Keep `docs_url=None, redoc_url=None, openapi_url=None`.
- No 301 redirects (D1: 302 only).
- No cache, Redis or second dyno in v1 (D9: measure first; a second dyno is over budget).
- No admin endpoint or disable script: disabling is manual SQL (FR8).
- Nothing listed in SPEC.md's "Out of scope for v1": no alias, expiration, stats or users. Google login is a v1.1 idea, not v1.

## Gotchas

- Heroku sets `DATABASE_URL` as `postgres://…`; convert it to `postgresql://…` in `app/config.py`.
- Client IP = the **rightmost** `X-Forwarded-For` value. Earlier values are client-controlled.
- Heroku Postgres Essential-0 allows 20 connections in total: 2 workers × pool max 5 = 10. Don't raise either without checking.
- The rate limit is per worker (in-process), so the real limit is up to 2× the configured one. Known and documented.
- `code` uses `COLLATE "C"`: case-sensitive by bytes. Don't lowercase codes anywhere except for the word-blocklist check.
- The dyno filesystem is wiped on restart. Never write state to disk.
- Windows dev: psycopg async can't run on the `ProactorEventLoop`. Run uvicorn with `--reload` (it then uses a selector loop); tests get one via the `anyio_backend` fixture in `tests/conftest.py`.
- The app is built by `create_app()` and served with `--factory`; there is no module-level `app` (D15).
- Integration tests skip locally when `DATABASE_URL` isn't set, but fail in CI (D17).

## Commits and PRs

- Small PRs, one task from `docs/tasks.md` each; reference the task (e.g. "T9 Postgres repository").
- Conventional commits: `feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:`.
- CI must be green before merging to `main`.
