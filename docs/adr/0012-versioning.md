# 0012. URL path versioning with a committed spec per version

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design round 2 (Q2)

## Context

Integrators need a stable contract and a clear signal before anything breaks.

## Decision

Version in the path: `/v1/...`. Additive changes stay on v1; only a breaking change starts v2. One schema and one engine sit behind thin per-version serialisers, as route groups in one app. Each version's OpenAPI spec is committed (`api/openapi/v1.json`), and CI runs oasdiff against `master` to fail on breaking changes. Retired versions get `Deprecation` and `Sunset` headers. Rows record their upstream `source_version` so upstream changes are absorbed without changing v1 output.

## Consequences

The spec is a reviewed artifact; changing the API means changing a committed file.
