# Fitment API

A developer API for automotive parts fitment: decode a VIN, search parts, check whether a part fits a vehicle. Platform layer: hashed API keys, Redis token-bucket rate limits, usage metering, idempotent batch calls, versioned OpenAPI spec, generated TypeScript SDK. This file is the single source of truth for agents. Skills, the contract reviewer and `CONTRIBUTING.md` link here instead of repeating it.

```
client (curl, k6, demo via packages/sdk)
        │  HTTP + X-API-Key
        ▼
  api  FastAPI :8000  ──SQL (asyncpg)──►  db     Postgres 17 :5432   catalog, keys, usage_daily, idempotency
                      ──RESP──────────►  redis  Redis 7.4  :6379   token buckets, per-minute usage counters
```

## Roles

The user designs the architecture and data flow. The agent implements. Decisions are recorded as ADRs in `docs/adr/`; read the relevant ADR before changing an area.

**Stop and ask the user before deciding any of these:**

- a new or changed table, column, index or constraint
- a new endpoint, or any change to a request or response shape
- a new error `code` value
- a new dependency (`uv add`, `pnpm add`)
- a new service, container, cache or queue
- any change to data ingestion or seeding logic
- rate limits, plans or retention periods

Put the question in the grilling format (numbered, with a recommended answer). When the user answers, write or update the ADR, then implement. Everything else (module structure inside the agreed layout, names, helpers, tests, log messages) the agent decides.

## Autonomy

| Action | Who |
|---|---|
| Edit code; run tests, ruff, pyright | agent |
| Scratch DB `fitment_check`: create, migrate, drop | agent |
| `alembic upgrade` on the real `fitment` DB | agent |
| `docker compose up / ps / logs / restart / exec` | agent |
| `git add` / `git commit` on a non-master branch | agent |
| `git push`, `gh pr create`, `uv add`, `pnpm add`, `alembic downgrade`, vPIC snapshot | user approves |
| Merge to `master`, tag a release, `docker compose down -v`, delete a branch | user |
| Commit or push on `master`, force-push, `reset --hard`, autogenerate, read `.env` | blocked |

`.claude/settings.json` and `.claude/hooks/` enforce the table.

## Commands

Run from the repo root unless noted.

```sh
cp .env.example .env                      # once; .env is git-ignored and agents never read it
docker compose up -d && docker compose ps # db + redis, wait for "healthy"
uv sync --project api                     # install the API and dev tools into api/.venv
uv run --project api alembic -c api/alembic.ini upgrade head
uv run --project api alembic -c api/alembic.ini current
uv run --project api pytest               # API tests (api/tests, from day 2)
uv run --project api pytest .claude/hooks/tests   # hook tests
docker exec -it fitment-db psql -U fitment   # \dt tables, \d <table>, \q quit
```

Planned, not built yet: `scripts/snapshot_vpic.py` and `scripts/seed.py` (day 1), `uvicorn` app (day 2), `pnpm gen` SDK generation (day 4), `loadtest/` k6 (day 5).

## Layout

```
api/src/fitment/       package: config.py now; routes/, schemas/, repo/, services/ from day 2
api/migrations/        Alembic, hand-written SQL
api/tests/             pytest + httpx
packages/sdk/          generated TypeScript client (day 4)
apps/demo/             Vite + React shop with a developer panel (day 4)
scripts/, data/        vPIC snapshot and seed (day 1)
docs/adr/              architecture decision records
.claude/               settings, hooks, skills, contract-reviewer agent
```

## Hard rules

1. **SQL lives only in `api/src/fitment/repo/`**, as SQLAlchemy Core `text()` with bind parameters. No ORM models, no string formatting into SQL. (ADR 0006)
2. **Migrations are hand-written and immutable.** Never `alembic revision --autogenerate`. Every migration has a working `downgrade()` and passes up → down → up on the scratch DB before commit. A migration on `master` is never edited; fix it with a new one. (ADR 0007)
3. **Errors are RFC 9457** `application/problem+json` with a stable `code` and `request_id`, declared in the OpenAPI spec. (ADR 0013)
4. **`/v1` is a contract.** Additive changes only. Breaking changes need a new major version and an ADR. The committed spec `api/openapi/v1.json` must match the code. (ADR 0012)
5. **API keys:** store SHA-256 of the secret half only, look up by the public `key_id`, compare with `hmac.compare_digest`. Say "hashing", never "encryption". (ADR 0008)
6. **Rate limiting** is a Redis token bucket updated by one Lua script; **metering** is Redis counters flushed to `usage_daily`. Never write to Postgres per request for either. (ADR 0009, 0010)
7. **Data:** vPIC is called only by `scripts/snapshot_vpic.py`, which the user runs by hand. There is no scheduled refresh. Tests, CI and seeding never touch the network. The seed is deterministic. Synthetic SKUs start with `SYN-`. (ADR 0003)
8. **Secrets:** never read `.env` or `*.pem`. Put new config names in `.env.example` with an empty value.
9. **Never state a latency, coverage or row-count number that was not measured in this repo.**

## Git

Branches `day-N/`, `feat/`, `fix/`, `hotfix/`, `chore/`, `docs/`, `data/`. Granular conventional commits (`feat(api): ...`), one logical step each. PRs are rebase-merged. Full workflow, release tags and branch protection: `CONTRIBUTING.md`. PR descriptions follow `.github/pull_request_template.md`, including a mermaid diagram of the changed flow.

## Teaching format

The user is learning the codebase while building it. End every step with the `explain-step` skill's format: what changed and why, the commands for the user to run, and the output they should expect.

## Skills and agents

- `run-stack`: bring the stack up and verify it
- `new-migration`: write, round-trip and explain a migration
- `new-endpoint`: route, schemas, errors, repo query, tests, spec, SDK
- `regen-sdk`: export the spec and regenerate the TypeScript client
- `refresh-vpic`: user-run snapshot refresh and diff
- `loadtest`: k6 run and recording the result
- `explain-step`: the teaching hand-off
- `contract-reviewer` agent: checks a change against rules 1–6 and reports. It never edits files.

## Plugins

`ponytail` (enabled in `.claude/settings.json`) pushes for the simplest solution: stdlib first, no unrequested abstractions. Follow it when choosing *how* to implement. It never overrides this file: ADRs, tests, `downgrade()` functions, problem+json errors and the stop-and-ask list are required even when they look like extra work. (ADR 0019)
