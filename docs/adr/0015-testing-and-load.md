# 0015. pytest + httpx for behaviour; k6 for latency

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design rounds 2–3 (Q7, Q13)

## Decision

Behaviour tests use plain pytest and httpx against real Postgres and Redis (fits, 429, idempotency replay and conflict). Coverage on `api/src/fitment` must stay at or above 80%. k6 tests `/v1/fitment/check` at 200 req/s for 60 seconds with a target p95 under 50 ms; the README reports the measured number and the hardware, whatever it is.

## Consequences

No schema fuzzing. Latency in CI is report-only (nightly), because shared runners are noisy.
