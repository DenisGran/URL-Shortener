# rapid.codes — v1 Tasks

Last updated: 2026-10-20 · Each task is at most half a day (~4 h). Do them in order; each one ends deployable.

**Owner key** (agreed work split):
- **You**: you write the core logic and its tests; Claude explains, guides and reviews.
- **Claude**: boilerplate, config and doc drafts; you review and merge.
- **Together**: setup steps that need your accounts or your machine.

"Done when" is the acceptance check. A task isn't done until CI is green and it's deployed.

---

## Phase 0 — Walking skeleton (live on the internet first)

### T1. Walking skeleton deployed to Heroku — Together
- [ ] Claim the Heroku offer in the GitHub Student Pack; create the app; set the dyno to **Basic** (not Eco, which sleeps).
- [ ] Claude scaffolds: `pyproject.toml` (Python 3.12, FastAPI, uvicorn), `app/main.py` app factory with `docs_url=None, redoc_url=None, openapi_url=None`, `GET /` returning "rapid.codes — coming soon", `Procfile` (`web: uvicorn app.main:create_app --factory --host 0.0.0.0 --port $PORT --workers 2 --proxy-headers --forwarded-allow-ips='*'`), `.python-version`, `.gitignore`, `README.md` stub.
- [ ] First commit on `main`, push, deploy (`git push heroku main` or GitHub integration).
- **Done when:** `https://<app>.herokuapp.com/` shows the page, and `/docs` and `/openapi.json` both return 404.

### T2. CI pipeline — Claude
- [x] GitHub Actions: on every PR and every push to `main` run `ruff check`, `ruff format --check`, `mypy app tests`, `pytest` (D14).
- [x] One trivial test (`GET /` returns 200) so the pipeline has something to run.
- [ ] Branch protection on `main`: CI must pass.
- **Done when:** a PR shows a green check, and a deliberately broken lint fails it.

### T3. Custom domain + HTTPS — Together
- [ ] `heroku domains:add rapid.codes`, then point DNS at the Heroku DNS target (ALIAS/CNAME-flattened record at the root; no AAAA record).
- [ ] `heroku certs:auto:enable` (ACM).
- [ ] Consider moving the domain to the cheapest registrar for renewal (decide, don't block on it).
- **Done when:** `https://rapid.codes/` shows the page with a valid certificate. (DNS can take hours; start this early, and move on to T4 while it propagates.)

## Phase 1 — Database

### T4. Local Postgres + config + connection pool — Claude
- [x] `docker-compose.yml` with Postgres 16; `.env.example`.
- [x] `app/config.py` (pydantic-settings): `DATABASE_URL`, `BASE_URL`. **Gotcha:** Heroku gives `postgres://…`; convert it to `postgresql://…` in config.
- [x] `app/infra/db.py`: `AsyncConnectionPool(min_size=1, max_size=5)` opened and closed in the FastAPI lifespan.
- **Done when:** the app starts locally against Docker Postgres, and a test opens and closes the pool.

### T5. Schema migration + Heroku Postgres — Together
- [ ] Alembic set up; first migration = the `links` table from design.md section 2.1, written as raw SQL with a working `downgrade()`.
- [ ] Add Heroku Postgres Essential-0; `Procfile` gets `release: alembic upgrade head`.
- [ ] You review the migration line by line (Claude explains every constraint).
- **Done when:** a deploy runs the migration in the release phase, and `heroku pg:psql -c '\d links'` shows both unique constraints.

## Phase 2 — Core logic (yours)

### T6. URL validation + normalization + hash — You
- [ ] `domain/normalize.py`: FR4 (http/https only, host required, max 2,048 chars, reject rapid.codes and the herokuapp.com host) and FR3 (lowercase scheme and host, drop `:80`/`:443`, keep path, query and `#fragment`). Return the normalized URL and its SHA-256.
- [ ] Table-driven unit tests: at least 15 cases, including `HTTPS://EXAMPLE.com:443/A?b=C#d`, `ftp://…`, `javascript:…`, no host, 2,049 chars, `https://rapid.codes/x`, IDN host.
- **Done when:** 100% branch coverage on this module.

### T7. Code generator + word blocklist — You
- [ ] Pick a 7-letter English word list, check its license, save it to `app/data/words7.txt`, load it once into a `frozenset`.
- [ ] `domain/codes.py`: `generate_code(rng)` uses `secrets` (not `random`), 7 base62 chars, regenerates while the lowercased code is in the blocklist (FR10).
- [ ] Tests: correct length and alphabet; a blocked word is never returned (inject a fake RNG that yields a word first); 10,000 codes have no obvious bias.
- **Done when:** tests pass and the RNG is injectable.

### T8. Repository interface + in-memory fake — You
- [ ] `repositories/base.py`: `LinkRepository` Protocol with `insert_if_absent(code, long_url, url_hash) -> Link | None`, `get_by_hash(url_hash)`, `get_by_code(code)`.
- [ ] `repositories/in_memory.py` with the same conflict behavior as Postgres.
- [ ] `domain/models.py`: `Link` dataclass, `LinkStatus` enum.
- **Done when:** a contract test suite exists that any implementation must pass, and the fake passes it.

### T9. Postgres repository — You
- [ ] `repositories/postgres.py`: the `INSERT … ON CONFLICT DO NOTHING RETURNING` from design.md section 2.2, plus the two lookups, with parameterized queries only.
- [ ] Run the **same contract tests** against real Postgres (CI uses a Postgres service container).
- [ ] A concurrency test: 20 parallel inserts of the same URL end up as exactly 1 row.
- **Done when:** the contract tests pass on both implementations.

### T10. Link service — You
- [ ] `services/link_service.py`: `create_link(url)` → `(Link, created: bool)`, with the collision retry (max 5) and FR2 (same URL, same code) handling; `resolve(code)` → `Link | None`.
- [ ] Unit tests with the in-memory repo and a fake RNG: new link, existing URL, forced code collision, 5 collisions raise an error.
- **Done when:** every branch in the service is tested.

## Phase 3 — HTTP layer

### T11. Error format — Claude
- [ ] `api/errors.py`: problem+json handlers (FR11 one error format) for validation errors, `RequestValidationError`, rate limit and unexpected errors (no stack traces in responses).
- **Done when:** a test checks the `Content-Type` and body shape for each error type.

### T12. `POST /api/v1/links` — You (Claude reviews)
- [ ] Pydantic request and response models; returns `201` or `200` (FR1 create link, FR2 same URL, same code), `422` (FR4 validation).
- [ ] API tests with `httpx.AsyncClient`, using the in-memory repo through `Depends` overrides.
- **Done when:** deployed, and `curl -X POST https://rapid.codes/api/v1/links -d '{"url":"…"}'` works live.

### T13. `GET /{code}` redirect — You
- [ ] FR5 (302 for an active link) with `Cache-Control: no-store`; FR6 (404 page for unknown or malformed codes, without hitting the DB); FR7 (410 page for disabled links).
- [ ] Tests for all three, plus a malformed code (`abc`, `aB3xK9q!`).
- [ ] Disable a link live with SQL (FR8) and watch it switch to 410.
- **Done when:** a full round trip works on rapid.codes. **This is the first real end-to-end version.**

### T14. Home page form — Claude
- [ ] `static/index.html` (FR12 home page): one input, one button, `fetch` to the API, result written with `textContent`, copy-to-clipboard button. No framework.
- **Done when:** a link can be shortened from a phone browser.

## Phase 4 — Protection and observability

### T15. Rate limiting + client IP — You
- [ ] `infra/ratelimit.py`: sliding window, 10 creates per minute per IP, `429` + `Retry-After`.
- [ ] Client IP = rightmost `X-Forwarded-For` entry (Heroku appends the real IP last).
- [ ] Tests: the 11th request in a minute is blocked; a faked leftmost `X-Forwarded-For` value doesn't bypass the limit.
- **Done when:** deployed; document the per-worker gap in design.md.

### T16. Structured logging — Claude
- [ ] JSON log lines with `request_id` (from Heroku's `X-Request-ID`, or a generated one locally), method, path, status, `duration_ms`. No IPs, no long URLs at INFO level.
- **Done when:** `heroku logs --tail` shows one JSON line per request.

### T17. Metrics to Grafana Cloud — Together
- [ ] Grafana Cloud free account; OTLP endpoint and token as Heroku config vars.
- [ ] `infra/telemetry.py`: OpenTelemetry FastAPI instrumentation + `links_created_total` counter, exported every 60 s.
- [ ] Dashboard: RPS, p50/p95/p99 latency, error rate by status, links created. Screenshot it for the README.
- **Done when:** live traffic shows up on the dashboard within 2 minutes.

## Phase 5 — Proof and polish

### T18. Load test (local 500 RPS proof) — Together
- [ ] `loadtest/redirect.js` (k6): seed 10,000 links, then hit `GET /{code}` at a constant 500 RPS for 5 minutes against `docker compose`.
- [ ] Record p50/p95/p99, error rate and CPU; write `docs/load-test.md` with machine specs and exact commands, so anyone can reproduce it.
- [ ] If the target is missed: profile first, then tune (workers, pool size). No cache yet; the cache is a later, measured change.
- **Done when:** the report shows ≥ 500 RPS with < 1% errors, or explains honestly why not.

### T19. Coverage gate + OpenAPI export — Claude
- [ ] `pytest --cov` with an 80% minimum on `app/domain` and `app/services` in CI.
- [ ] `scripts/export_openapi.py` → `docs/openapi.json`; CI fails if the committed file is out of date.
- **Done when:** both gates fail on purpose once, then pass.

### T20. ADRs — Claude drafts, you edit
- [ ] `docs/adr/0001`–`0008` for D1–D8 in design.md section 5 (302, FastAPI, code format, word list, Postgres, SHA-256 dedup, psycopg raw SQL, Heroku). Each ADR covers context, decision, consequences, and no more than one page.
- **Done when:** each is in your own words — interviewers will ask about them.

### T21. README — Claude drafts, you edit
- [ ] What it is, live link, architecture diagram, API examples, how to run locally (3 commands), how to test, load test results, dashboard screenshot, links to the spec, the design doc and the ADRs.
- **Done when:** someone new can run it locally in under 10 minutes.

### T22. Release v1.0 — Together
- [ ] Security review pass (Claude lists, you fix): headers (`X-Content-Type-Options`, `Referrer-Policy`), SQL parameterization, no secrets in the repo, dependency audit (`pip-audit`).
- [ ] Tag `v1.0.0`, write the GitHub release notes.
- **Done when:** the tag is live and every item in SPEC.md is checked off.

---

## Backlog (after v1, not ordered yet)

- v1.1 Google login (required to shorten links; redirects stay public).
- v1.2 In-process cache with TTL, measured with the same k6 script before and after.
