# 0006. SQLAlchemy Core text() queries in a repo layer, no ORM

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, harness round 1 (Q7)

## Context

The schema lives in hand-written SQL migrations. ORM models or Core `Table` objects would be a second copy of it that can drift.

## Decision

Queries are SQLAlchemy Core `text()` with bind parameters, in `api/src/fitment/repo/`, one module per area, returning Pydantic models. No SQL anywhere else. Async engine with asyncpg.

## Consequences

The SQL in code is the SQL in `EXPLAIN` output. Mapping rows to models is manual. CI greps for SQL outside `repo/`; a hook runs `EXPLAIN` on edited repo queries and warns on sequential scans.
