# 0020. Schema details from the day-1 contract review

- Status: Accepted. Supersedes the "engine fields reuse vPIC's vocabulary" line of ADR 0003 and the "every foreign key column has an explicit index" line of ADR 0005.
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, questions E1–E8 after the contract review of `day-1/schema`

## Context

The contract reviewer found schema choices with no ADR behind them, and one wrong claim: vPIC has no "aspiration" field. Its engine fields are `DisplacementL`, `EngineCylinders`, `FuelTypePrimary` and a yes/no `Turbo`.

## Decision

- **Engine vocabulary (E1):** our own closed sets. `fuel` is one of `gasoline`, `diesel`, `hybrid`, `plug_in_hybrid`, `electric`. `aspiration` is one of `naturally_aspirated`, `turbo`, `supercharged`, and NULL for electric. One function maps vPIC values onto these for both the seed and VIN decode. The values are part of `/v1`: they can be added, never removed.
- **Keys are never deleted (E2):** `DELETE /v1/admin/keys` sets `revoked_at`. `usage_daily` references `api_key` with `ON DELETE RESTRICT`, so billing history cannot disappear. `idempotency` keeps `ON DELETE CASCADE`; its rows live 24 hours.
- **Foreign key indexes (E3):** a foreign key column is covered when it is the leading column of any index. `fitment_part_id_idx` was dropped because `part_id` leads the fitment UNIQUE index.
- **Years (E4):** `vehicle.year`, `fitment.year_from` and `fitment.year_to` are CHECKed to 1981–2100 (17-character VINs start in 1981). Overlapping fitment ranges are allowed, as in real catalogues; the check returns every matching rule. The seed does not generate overlaps.
- **Idempotency integrity (E5):** `request_hash` is exactly 32 bytes (SHA-256 of the request body), and a `completed` row must have `response` and `response_status`.
- **Synthetic SKUs (E6):** the `SYN-` prefix is enforced by the seed and a seed test, not the schema, because real SKUs are planned.
- **pg_trgm (E7):** downgrade of 0001 leaves the extension installed; upgrade used `IF NOT EXISTS`, so it may predate the migration.
- **Build backend (E8):** hatchling packages `fitment` (build time only).

## Consequences

Mapping vPIC values is explicit code that tests can cover. Hard-deleting a key with usage fails at the database. Overlapping rules can appear in later real data; the API already returns all matches.
