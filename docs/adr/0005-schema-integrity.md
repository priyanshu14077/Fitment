# 0005. Schema integrity and indexing

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design round 3 (Q10)

## Context

The schema review raised several ways bad rows could get in and several slow paths.

## Decision

- `fitment (model_id, make_id)` references `model (id, make_id)`, so a row cannot say make = Ford, model = Camry.
- Uniqueness on `vehicle` and `fitment` uses `UNIQUE NULLS NOT DISTINCT` (Postgres 15+); a plain unique constraint treats NULLs as distinct and lets duplicates through.
- CHECK constraints: `year_from <= year_to`, `price_cents >= 0`, `octet_length(key_hash) = 32`.
- Every foreign key column has an explicit index; Postgres does not create them.
- Hot path index `fitment_lookup (model_id, year_from, year_to) INCLUDE (part_id, trim, engine_id, position)` for index-only scans.
- `pg_trgm` GIN index on `part.name` for search; GIN `jsonb_path_ops` on `part.attrs`.
- No assemblies table: category plus `position` covers the demo.
- B-tree, not `int4range` + GiST, for years at this scale.

## Consequences

The database rejects inconsistent data instead of the application. Next steps at millions of rows, not taken now: range types, partitioning by `make_id`, or a flattened `vehicle_part` table.
