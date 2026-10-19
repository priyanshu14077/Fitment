# Architecture decision records

One file per decision: context, decision, consequences. Accepted ADRs are not edited; a change of mind is a new ADR that supersedes the old one. Start from [`template.md`](template.md).

| # | Decision |
|---|---|
| [0001](0001-record-decisions-user-designs.md) | Record decisions as ADRs; the user designs, the agent implements |
| [0002](0002-monorepo-layout.md) | One monorepo for API, SDK and demo |
| [0003](0003-vehicle-data-source.md) | Real makes and models from vPIC; synthetic trims, engines and parts |
| [0004](0004-fitment-model.md) | Fitment as ranges with NULL wildcards and three outcomes |
| [0005](0005-schema-integrity.md) | Schema integrity and indexing |
| [0006](0006-sql-in-repo-layer.md) | SQLAlchemy Core `text()` queries in a repo layer, no ORM |
| [0007](0007-migrations.md) | Hand-written, reversible, immutable migrations |
| [0008](0008-api-key-hashing.md) | API keys stored as SHA-256 hashes |
| [0009](0009-rate-limiting.md) | Token-bucket rate limits in Redis via one Lua script |
| [0010](0010-usage-metering.md) | Usage metering via Redis counters flushed to daily rollups |
| [0011](0011-idempotency.md) | Idempotency keys for the batch endpoint, stored in Postgres |
| [0012](0012-versioning.md) | URL path versioning with a committed spec per version |
| [0013](0013-errors.md) | RFC 9457 problem details for every error |
| [0014](0014-sdk-and-demo.md) | Generated TypeScript SDK with a drift check; Vite demo |
| [0015](0015-testing-and-load.md) | pytest + httpx for behaviour; k6 for latency |
| [0016](0016-git-workflow.md) | Branch prefixes, granular conventional commits, rebase-merge |
| [0017](0017-ci-cd.md) | CI gates and tag-triggered delivery |
| [0018](0018-agent-harness.md) | Claude Code harness: rules, permissions, hooks, skills, reviewer |
| [0019](0019-ponytail-plugin.md) | Enable the ponytail plugin; CLAUDE.md takes precedence |
