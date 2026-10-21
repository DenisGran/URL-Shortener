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
- **Consequences:** commands become `uv run pytest`, `uv run uvicorn …`, etc. CLAUDE.md's command list will be updated in T2 when the dev tools are added.
