# 0007. Hand-written, reversible, immutable migrations

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design round 2 (Q7) and harness round 1 (Q6)

## Context

Alembic autogenerate compares against ORM metadata we do not have, and in a previous project it proposed dropping constraints that existed only in the database.

## Decision

Migrations are plain SQL via `op.execute`, numbered `0001`, `0002`, …. Each has a working `downgrade()` and is tested up → down → up on the scratch database `fitment_check` before commit. Autogenerate is blocked by a hook. A migration already on `master` is never edited; corrections go in a new migration.

## Consequences

More typing per migration, full control over constraints and indexes. CI repeats the round trip and the immutability check.
