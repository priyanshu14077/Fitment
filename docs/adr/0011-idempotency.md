# 0011. Idempotency keys for the batch endpoint, stored in Postgres

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design round 1 (Q6)

## Context

Clients retry after network failures. A retry must not produce a different result or duplicate work.

## Decision

`POST /v1/fitment/check:batch` accepts `Idempotency-Key`. The server stores `(api_key_id, idem_key) → request_hash, status, response, expires_at` (24 hours) in Postgres. Same key and body: replay the stored response. Same key, different body: `422`. First request still running: `409`.

## Consequences

Stored in Postgres so it survives a Redis flush. A fitment check is a read and already naturally idempotent; the README says the pattern is there to demonstrate the technique.
