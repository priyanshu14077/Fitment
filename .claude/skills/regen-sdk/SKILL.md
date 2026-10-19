---
name: regen-sdk
description: Export the OpenAPI spec and regenerate the TypeScript SDK in packages/sdk. Use after any change to api/openapi/v1.json.
---

# regen-sdk

Rules: ADR 0012 and ADR 0014. Available from day 4, when `packages/sdk` exists.

1. `uv run --project api python -m fitment.openapi` writes `api/openapi/v1.json`.
2. `pnpm gen` regenerates `packages/sdk/src` with `@hey-api/openapi-ts`.
3. `pnpm --filter sdk exec tsc --noEmit` and `pnpm --filter demo build`.
4. `git diff --stat packages/sdk` and summarise what changed in the client for the user (new methods, new fields, new error types).
5. Commit generated code on its own: `build(sdk): regenerate from v1 spec`.

Never edit files under `packages/sdk/src` by hand; CI regenerates and fails on any difference.
