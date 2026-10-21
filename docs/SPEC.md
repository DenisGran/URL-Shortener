# rapid.codes — v1 Spec

Last updated: 2026-10-20

## Goal and context

rapid.codes takes a long URL and returns a short link of the form `https://rapid.codes/<code>`, which redirects to the target with a 302. It is a portfolio project: code quality, tests, documentation and measurement matter more than feature count.

- Language: Python. Stack: FastAPI + PostgreSQL
- Hosting: Heroku Basic dyno + Heroku Postgres Essential-0, paid by the GitHub Student Pack credit (see docs/design.md)
- v1: shorten and redirect only — no alias, expiration, stats or users

## Functional requirements

| ID | Requirement | Behavior |
| --- | --- | --- |
| FR1 | Create link | `POST /api/v1/links` with `{"url": "..."}` returns `201` with `code`, `short_url`, `long_url`, `created_at` |
| FR2 | Same URL, same code | If the normalized URL already exists, return the existing code with `200` |
| FR3 | Normalization | Lowercase scheme and host, drop default port (`:443`, `:80`); keep path, query and `#fragment` as-is |
| FR4 | Validation | `http`/`https` only, host required, max 2,048 chars, reject links to rapid.codes itself (loops). Failure returns `422` |
| FR5 | Redirect | `GET /{code}` for an active link returns `302` with `Location` set to the target. This is the only case that redirects |
| FR6 | Unknown code | `404` with a short HTML page, no redirect |
| FR7 | Disabled link | `410 Gone` with a short HTML page, no redirect |
| FR8 | Disabling | Manual SQL against the DB, e.g. `UPDATE links SET status = 'disabled' WHERE code = 'aB3xK9q';`. No endpoint, no script |
| FR9 | Code format | 7 base62 chars, case-sensitive, generated randomly with a uniqueness check. 62⁷ ≈ 3.5 trillion combinations |
| FR10 | Blocked codes | A generated code that matches any 7-letter English dictionary word, case-insensitively, is discarded and regenerated |
| FR11 | Errors | All API errors use one format, `application/problem+json` (RFC 9457) |
| FR12 | Home page | `GET /` serves a minimal shorten form so a recruiter can try it without curl |

## Non-functional requirements

Every target here is measured and documented in the repo. A number without a measurement does not go in the README.

| Area | Target |
| --- | --- |
| Read:write ratio | 100:1. The redirect is the hot path |
| Redirect latency | Server-side p95 < 50ms and p99 < 150ms, excluding network and cold start |
| Create latency | Server-side p95 < 200ms |
| Throughput | 500 redirect RPS on a single instance, proven by a load test (k6 or Locust) with the report in the repo |
| Availability | Best effort, no SLA. Free-tier cold starts are acceptable |
| Capacity | Up to 100,000 links, ~0.5KB per row including indexes |
| Durability and consistency | After `201` the link is stored (transaction commit). `UNIQUE` on `code` and on the SHA-256 hash of the normalized URL, so two concurrent requests for the same URL never create two codes |
| Security | HTTPS only. Rate limit on create: 10 per minute per IP. Untrusted input never reaches HTML without escaping |
| Logging | Structured JSON per request: `request_id`, path, status, duration. No full IP and no long URL at INFO level |
| Monitoring | The app pushes metrics via OpenTelemetry (OTLP) to Grafana Cloud free: RPS, latency histogram, error rate by status, links created. No public metrics route |
| Code structure | Layers API → service → repository, with the repository as an interface so the DB can be swapped or a cache added without touching logic (SOLID: SRP, DIP) |
| Tests and CI | ≥ 80% coverage on core logic. GitHub Actions runs lint, type check and tests on every PR |
| Documentation | On GitHub only: README with architecture and local run instructions, an exported `openapi.json` in the repo, and a short ADR per significant decision (302, code format, DB). The service exposes no docs route |

## Out of scope for v1

- Custom alias
- Link expiration
- Stats and click counting
- Users, login, API keys
- Editing or deleting a link by its creator
- Cache (Redis etc.) until the basic version works and has been measured
- Bulk create, QR codes, target preview
- Custom domains, multi-region, failover
- `301` redirects

## Risks and honest notes

- **"High RPS" on a free tier is not a claim you can hold in production.** What you can do: a load test, locally or on the instance, with numbers and a graph in the README. A technical recruiter will respect a measured 500 RPS more than "scalable" with no evidence.
- **Abuse is the real risk.** A public anonymous shortener attracts phishing links, and the domain can get blocked by browsers. The rate limit and manual disabling in the DB are a minimum, not a solution.
- **Disabling (FR7 disabled link returns 410, FR8 manual SQL) depends on you noticing.** Nobody reports bad links, so a phishing link stays live until you find it.
- **Dedup (FR2, same URL returns the same code) will clash with users later.** Once there are users, the same URL will probably need a separate code per user. Fine for v1, but worth an ADR now.
- **302 costs load.** Browsers don't cache it, so every click hits the server. That is right for future stats, and it is exactly why the cache comes next.
