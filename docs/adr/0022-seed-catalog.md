# 0022. Seed catalog from the vPIC snapshot

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, questions S1–S14 after reviewing `vpic-api-2026-10-19`

## Context

The snapshot holds 353 Passenger Car models across 30 makes. vPIC lists BMW per trim (`328i`, `335i`), has gaps in some model years, includes a few non-production records, and returns no cars for GMC, Jeep, Land Rover and Ram. It has no trims, engines or parts. ADR 0003 makes the seed deterministic and offline; ADR 0020 fixes the engine vocabulary and forbids generated overlaps.

## Decision

- **Models (S1):** one `model` row per vPIC `Model_ID`, BMW included, so VIN decode matches on `vpic_model_id` directly.
- **Exclusions (S2, S5):** an explicit list of `vpic_model_id`s with a reason each: Ford `'34` (14930), Toyota `FCHV-adv` (3155), Volvo `C70 / C30` (28490), Chevrolet `Matiz` (4047) and `Onix` (27445).
- **Empty makes (S3):** makes with no models after exclusion are not seeded.
- **Years (S4):** vehicles exist only for the years vPIC lists; gaps stay gaps.
- **Names (S6):** make names in title case (`Mercedes-Benz`), except `BMW` and `MINI`. Model names as vPIC returns them, trimmed. Matching uses vPIC IDs, never names.
- **Engines (S7, S14):** a fixed catalog of 15 engines (nine gasoline, one diesel, two hybrid, one plug-in hybrid, two electric). Each model has one powertrain class from explicit `vpic_model_id` lists: electric, hybrid, plug-in hybrid, gasoline plus hybrid, or diesel (BMW names ending in `d`). Every other model is gasoline with 1–2 engines from the seeded RNG.
- **Fuel cells (S13):** Mirai, FCX Clarity and Clarity are electric; no `fuel_cell` value is added.
- **Trims (S8):** each model gets 1–3 trims from `Base`, `Sport`, `Touring`, `Limited`, the same for every year. A vehicle row is model × listed year × trim × engine.
- **Categories (S9):** brakes (position front/rear), suspension (front/rear × left/right), lighting (left/right), filters, wipers, spark-plugs (combustion engines only), batteries, cooling. Position is NULL for the rest.
- **Parts (S10):** `PARTS_PER_CATEGORY` (25 to start) parts per category, invented brand names, SKU `SYN-<CAT>-<NNNNN>`, price from a per-category range, category-specific `attrs`.
- **Fitment (S11):** each part gets rules on 1–4 distinct models of one powertrain class, within one make except wipers and batteries. Rule kind: broad (NULL trim and engine) 60%, trim-specific 20%, engine-specific 20%. The year range is cut from the model's listed years. One rule per part and model, so there are no overlaps. About 10% of rules carry a `notes` line.
- **Re-runs (S12):** one transaction truncates the seven catalog tables with `RESTART IDENTITY` and inserts everything with a fixed RNG seed, so IDs are identical on every run. Platform tables (`api_key`, `usage_daily`, `idempotency`) are never touched. The seed refuses a non-local `DATABASE_URL`.

## Consequences

The catalog is reproducible and can be rebuilt in one command. Trims, engines and parts are synthetic and the README says so. The powertrain lists are hand-maintained: a snapshot refresh with new EVs needs the lists updated, and a test fails if a listed ID is missing from the snapshot.
