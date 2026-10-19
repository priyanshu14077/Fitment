# 0014. Generated TypeScript SDK with a drift check; Vite demo

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design round 1 (Q8)

## Decision

`@hey-api/openapi-ts` generates `packages/sdk` from the committed spec via one `pnpm gen` script. CI fails if regenerating produces a diff, and type-checks the result. The demo is Vite + React with a developer panel showing response headers (rate limits, idempotency replay) for the walkthrough video.

## Consequences

The SDK can never silently fall behind the API. The demo has no server rendering, which it does not need.
