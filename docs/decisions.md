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
- **Alternatives rejected:** mypy non-strict (lets untyped code in, which then has to be fixed later); ruff defaults only (misses `ASYNC` and `S`, which match this project's async DB code and its "no string SQL, `secrets` not `random`" rules); `pytest-asyncio` (one more dependency for the same job); CI on all pushes (each push to an open PR's branch would run CI twice).
- **Why:** the `ASYNC` and `S` rules check, in CI, two things CLAUDE.md asks for by hand. Strict typing is easiest when the codebase is 20 lines long.
- **Consequences:** a branch without a PR gets no CI run. tasks.md T2 wording was adjusted to match.
