# rapid.codes — Decision log

Every decision made after the design was written goes here, newest last. D1–D12 live in [design.md section 5](design.md#5-decisions-and-reasons) and are not repeated.

Status is **Proposed** until Denis confirms it, then **Accepted** (or **Rejected**, with the reason kept). Significant ones also get an ADR in `docs/adr/` (tasks.md T20).

Format per entry: context, decision, alternatives rejected, why, consequences.

---

## D13. uv as the package manager, with a committed lockfile

- **Date:** 2026-10-21 · **Task:** T1 · **Status:** Proposed
- **Context:** T1 needs a way to declare dependencies that works the same on Denis's machine, in CI (T2) and on Heroku. Python isn't installed on the dev machine yet.
- **Decision:** Use [uv](https://docs.astral.sh/uv/). Dependencies are declared in `pyproject.toml`; `uv.lock` (a lockfile: the exact version of every package, direct and indirect) is committed. `.python-version` pins 3.12.
- **Alternatives rejected:**
  - `pip` + `requirements.txt`: no real lockfile unless you add `pip-tools`; two files to keep in sync.
  - Poetry: works, but slower and a second tool to learn for no gain here.
- **Why:** one tool installs Python itself (`uv python install 3.12`), creates the virtual environment and locks versions. Heroku's Python buildpack supports `uv.lock` natively, and GitHub Actions has an official `setup-uv` action, so all three environments install the exact same versions.
- **Consequences:** commands become `uv run pytest`, `uv run uvicorn …`, etc. CLAUDE.md's command list was updated in T2.

## D14. Strict checks and CI triggers

- **Date:** 2026-10-21 · **Task:** T2 · **Status:** Proposed
- **Context:** T2 sets up lint, type checking and tests. Each tool has settings that are cheap to choose now and painful to tighten later, once there's code that breaks them.
- **Decision:**
  - **mypy `strict = true`**, run on `app` *and* `tests`. Strict mode means every function needs type hints and nothing silently becomes `Any` (the "could be anything" type that turns checking off).
  - **ruff rule set** `E, W, F, I, UP, B, SIM, ASYNC, S`, line length 100. Beyond the defaults this adds import sorting, modern-syntax upgrades, common-bug patterns, blocking calls inside `async` code, and bandit security rules (`S`: e.g. string-built SQL, `random` used for secrets). `assert` is allowed in tests only.
  - **Async tests use anyio's pytest plugin** (`@pytest.mark.anyio`), which already ships with FastAPI, instead of adding `pytest-asyncio`.
  - **CI runs on every PR and every push to `main`**, not on every push to every branch.
  - **GitHub Actions are pinned to a full commit SHA** (with the version in a comment), not a tag like `@v10`. A tag can be moved to different code by whoever controls the action's repo; a SHA can't. Also, `setup-uv` doesn't publish a floating `v10` tag at all, which broke the first CI run.
- **Alternatives rejected:** mypy non-strict (lets untyped code in, which then has to be fixed later); ruff defaults only (misses `ASYNC` and `S`, which match this project's async DB code and its "no string SQL, `secrets` not `random`" rules); `pytest-asyncio` (one more dependency for the same job); CI on all pushes (each push to an open PR's branch would run CI twice).
- **Why:** the `ASYNC` and `S` rules check, in CI, two things CLAUDE.md asks for by hand. Strict typing is easiest when the codebase is 20 lines long.
- **Consequences:** a branch without a PR gets no CI run. tasks.md T2 wording was adjusted to match.

## D15. Serve the app with `uvicorn --factory`, no module-level `app`

- **Date:** 2026-10-28 · **Task:** T4 · **Status:** Proposed
- **Context:** With settings and a DB pool, building the app now reads `DATABASE_URL`. A module-level `app = create_app()` would run that on every `import app.main`, including in unit tests that have no database and no `.env`.
- **Decision:** `app/main.py` exposes only `create_app(settings=None)`. uvicorn builds the app with `uvicorn app.main:create_app --factory`. Tests call `create_app(Settings(...))` with their own settings.
- **Alternatives rejected:** keep `app = create_app()` and give `Settings` a default `DATABASE_URL` (a wrong default that silently "works" is worse than a clear startup error); a cached global `get_settings()` (a module-level global, which CLAUDE.md rules out for state).
- **Why:** importing a module has no side effects; tests control their own config; matches the "no globals, wire through `create_app`" rule.
- **Consequences:** Procfile, launch config, README, CLAUDE.md and design.md use `create_app --factory`.

## D16. Get everything working on localhost before Heroku (T4 before T3 and T5)

- **Date:** 2026-10-28 · **Task:** T4 · **Status:** Accepted (Denis, 2026-10-28)
- **Context:** Heroku account activation takes ~24 h; T3 (custom domain + HTTPS) and T5 (migration + Heroku Postgres) both need it.
- **Decision:** Do T4 now; T3 and T5 follow once the app runs locally against Postgres.
- **Why:** nothing in T4 depends on Heroku, and a working local setup makes T5 a deploy step instead of a debugging session.
- **Consequences:** tasks.md order is unchanged; only the execution order differs.

## D17. Integration tests skip locally without a DB, fail in CI

- **Date:** 2026-10-28 · **Task:** T4 · **Status:** Proposed
- **Context:** Integration tests need Postgres. Locally it may not be running; in CI it always is (a `postgres:16` service container).
- **Decision:** The `settings` fixture in `tests/integration/conftest.py` skips the test when `DATABASE_URL` isn't configured, unless `CI=true` (set by GitHub Actions), where it fails.
- **Alternatives rejected:** always fail (`uv run pytest` is red on a machine without Docker running, so people stop running it); always skip (CI could go green without ever touching a database).
- **Why:** local runs stay useful; CI can never silently skip the DB.
- **Consequences:** a local "skipped" is visible in pytest's summary (`-ra`), not hidden.
