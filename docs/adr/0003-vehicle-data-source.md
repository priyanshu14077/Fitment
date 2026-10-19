# 0003. Real makes and models from vPIC; synthetic trims, engines and parts

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design rounds 1–2 (Q3, Q6, Q9) and harness round 1 (Q6, R4)

## Context

Live checks of the NHTSA vPIC API on 2026-10-19 found: makes and models are available (`GetModelsForMakeYear/.../vehicletype/car` filters out motorcycles), but no endpoint lists trims or engines per make, model and year. VIN decoding returns engine fields (displacement, cylinders, fuel) fairly reliably and trim rarely. vPIC also decodes VINs with a bad check digit, returning `ErrorCode 1`. NHTSA publishes a standalone Postgres dump (about 68 MB) whose contents we did not inspect.

## Decision

- `scripts/snapshot_vpic.py` pulls makes and models (about 30 makes, 2010–2024) into `data/vpic_snapshot.json`, which is committed with its `source_version` and fetch date.
- The user runs the snapshot by hand. There is no scheduled refresh. A refresh goes on a `data/vpic-<date>` branch.
- Tests, CI and seeding never call the network.
- Trims and engines are generated from per-model templates; parts are synthetic with `SYN-` SKUs. The seed is deterministic (fixed RNG seed).
- Engine fields reuse vPIC's vocabulary so decode output and fitment rows share terms.
- `/v1/vehicles/decode` validates the check digit itself and matches against the local snapshot.

## Consequences

Builds are reproducible and offline. Trim and engine data is not real, and the README says so. The production path is the vPIC standalone dump or a licensed catalogue (ACES/PIES, TecDoc).
