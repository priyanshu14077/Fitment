# 0002. One monorepo for API, SDK and demo

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design round 2 (Q1)

## Context

The project spans a Python service, a generated TypeScript client and a React demo. The SDK drift check must compare the spec and the generated client in one commit.

## Decision

One repository: `api/` (uv project), `packages/sdk/`, `apps/demo/`, `loadtest/`, `scripts/`, `data/`, with a pnpm workspace for the TypeScript parts and `docker-compose.yml` at the root.

## Consequences

One clone and one `docker compose up` for a reviewer. CI must run Python and Node toolchains side by side.
