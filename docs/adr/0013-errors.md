# 0013. RFC 9457 problem details for every error

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design round 2 (Q3)

## Decision

Errors are `application/problem+json` with `type`, `title`, `status`, `detail`, a stable machine-readable `code` (for example `rate_limited`, `invalid_vin`, `idempotency_conflict`) and the `request_id`. Error responses are declared in the OpenAPI spec so the generated SDK has typed errors. New `code` values are a design decision (CLAUDE.md § Roles).

## Consequences

Clients branch on `code`, never on message text. FastAPI's default `{"detail": ...}` is replaced by exception handlers.
