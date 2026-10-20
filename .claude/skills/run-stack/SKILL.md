---
name: run-stack
description: Bring up Postgres and Redis, apply migrations and confirm the stack is healthy. Use at the start of work, after a reboot, or when a test fails with a connection error.
---

# run-stack

Commands and ports: `CLAUDE.md` § Commands.

1. `docker compose up -d`, then poll `docker compose ps` until `db` and `redis` both report `healthy`. Do not continue on `starting` or `unhealthy`; read `docker compose logs <service>`.
2. `uv sync --project api`.
3. `uv run --project api alembic -c api/alembic.ini upgrade head`, then `... current` and confirm it shows `(head)`.
4. Smoke checks: `docker exec fitment-db psql -U fitment -XAtc 'select 1'` and `docker exec fitment-redis redis-cli ping`.
5. Once the seed exists (day 1): confirm row counts are non-zero. Once the API exists (day 2): start it and curl the health endpoint agreed on day 2.

If `.env` is missing, tell the user to run `cp .env.example .env`. Never read or create `.env` yourself.

Finish with the `explain-step` format, listing each service, its state and how to check it.
