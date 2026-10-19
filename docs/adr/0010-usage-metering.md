# 0010. Usage metering via Redis counters flushed to daily rollups

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design round 2 (Q4)

## Context

One row per request adds a write to every call, puts the database in the request path and creates hot rows. Billing and dashboards only ask aggregate questions.

## Decision

Each request runs `INCR` on a Redis counter per (key, endpoint, minute). A background task flushes every 30 seconds into `usage_daily (api_key_id, day, endpoint, requests, errors_4xx, errors_5xx)` with `requests = usage_daily.requests + EXCLUDED.requests`. `GET /v1/usage` returns the caller's own rows. The same task deletes expired idempotency rows. Enforcement (ADR 0009) and accounting are separate systems.

## Consequences

A crash can lose up to 30 seconds of counts; the system undercounts rather than overbills. Production would add a durable event log and reconciliation (see CONTRIBUTING § Horizon).
