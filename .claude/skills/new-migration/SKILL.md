---
name: new-migration
description: Write a hand-written Alembic migration, round-trip it on the scratch database and explain it. Use for any table, column, index or constraint change.
---

# new-migration

Rules: `CLAUDE.md` § Hard rules 2, ADR 0005 and ADR 0007. Schema changes are the user's decision (§ Roles): have the design agreed and recorded in an ADR before writing anything.

1. Next number: highest in `api/migrations/versions/` plus one. File `NNNN_<slug>.py`, `revision = "NNNN"`, `down_revision` the previous number.
2. Write `upgrade()` as SQL in `op.execute`. Index every foreign key column. Use `UNIQUE NULLS NOT DISTINCT` where a nullable column is part of a uniqueness rule. Add CHECK constraints for invariants.
3. Write `downgrade()` that exactly reverses it.
4. Round trip on the scratch DB, never the real one:
   ```sh
   docker exec fitment-db psql -U fitment -qc 'create database fitment_check'
   export DATABASE_URL=postgresql+asyncpg://fitment:fitment@localhost:5432/fitment_check
   uv run --project api alembic -c api/alembic.ini upgrade head
   uv run --project api alembic -c api/alembic.ini downgrade base
   uv run --project api alembic -c api/alembic.ini upgrade head
   ```
5. Prove each new constraint rejects a bad row: insert one and show the error. Insert prerequisite rows in a separate `psql -c` call, because one failing statement rolls back the whole call.
6. `EXPLAIN` the query the new index exists for and confirm the planner uses it.
7. Drop the scratch DB: `docker exec fitment-db psql -U fitment -qc 'drop database fitment_check'`.
8. Apply to the real DB: `uv run --project api alembic -c api/alembic.ini upgrade head`.
9. Commit as `feat(db): ...` on a non-master branch.

Finish with `explain-step`: what each statement does, the constraint tests and their output, and `\d <table>` for the user to run.
