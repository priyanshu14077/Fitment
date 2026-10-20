# 0009. Token-bucket rate limits in Redis via one Lua script

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design round 1 (Q5)

## Context

Fixed windows allow double the limit across a boundary. Several API instances share one limit per key.

## Decision

A token bucket per key in Redis (`tokens`, `last_refill_ts`). Read, refill and decrement happen in one Lua script so concurrent instances cannot both spend the last token. Responses carry `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`; an empty bucket returns `429` with `Retry-After`. Limits come from the key's plan (ADR 0008).

## Consequences

Redis is in the request path for every call. Redis persistence is off on purpose; a restart refills every bucket.
