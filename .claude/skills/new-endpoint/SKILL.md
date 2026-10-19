---
name: new-endpoint
description: Add or change an API endpoint end to end, from route to SDK. Use whenever a request or response shape is added or changed.
---

# new-endpoint

Rules: `CLAUDE.md` § Hard rules 1, 3, 4, ADRs 0006, 0012 and 0013. A new endpoint or shape change is the user's decision (§ Roles): agree the request, response and error codes first and record them in an ADR.

1. Schemas in `api/src/fitment/schemas/`: Pydantic models with field descriptions and an example per model.
2. Query in `api/src/fitment/repo/<area>.py` as `text()` with bind parameters. The EXPLAIN hook will warn on sequential scans; check row counts before acting on it.
3. Route in `api/src/fitment/routes/<area>.py` under `/v1`. Declare every error response as problem+json with its `code`.
4. Tests in `api/tests/`: the success case, every documented error code, and auth or rate-limit behaviour if the route is keyed.
5. Export the spec (the spec-drift hook does this after route edits) and review the diff of `api/openapi/v1.json`. Removing or renaming a field, or tightening validation, is breaking: stop and ask.
6. Run `regen-sdk`.
7. Run the `contract-reviewer` agent and pass its report to the user. Fix only what the user agrees to.
8. Commits: `feat(api): ...` for the route and tests, then `build(sdk): regenerate` for the SDK, as separate commits.

Finish with `explain-step`, including a `curl` example with a key and the expected response.
