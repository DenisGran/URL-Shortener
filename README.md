# rapid.codes

A URL shortener: paste a long URL, get `https://rapid.codes/<code>`, which redirects with a 302.

> Work in progress. Live at https://rapid.codes once T3 (custom domain) is done.

- Requirements: [docs/SPEC.md](docs/SPEC.md)
- Design: [docs/design.md](docs/design.md)
- Decisions: [docs/decisions.md](docs/decisions.md)
- Task list: [docs/tasks.md](docs/tasks.md)

## Run locally

Requires [uv](https://docs.astral.sh/uv/) (it installs Python 3.12 for you).

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Then open http://localhost:8000/.
