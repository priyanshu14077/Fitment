# 0004. Fitment as ranges with NULL wildcards and three outcomes

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design rounds 1 and 3 (Q2, Q11)

## Context

A part fits a vehicle specification, not one car. Most fitment rules span years and apply to every trim or engine of a model.

## Decision

A fitment row is `(part_id, make_id, model_id, year_from, year_to, trim NULL, engine_id NULL, position NULL, notes)`. NULL means "any". `POST /v1/fitment/check` accepts a `vehicle_id` or a `vin` and returns `fits`, `does_not_fit` or `fits_with_conditions`, with `conditions` naming the detail the caller did not supply (for example `engine` must be one of a list) and the matched fitment ids.

## Consequences

Rules stay compact and match how the industry writes them. The wildcard `OR ... IS NULL` filters cannot use the trim and engine columns in an index; this is acceptable because `model_id` and year narrow the rows first.
