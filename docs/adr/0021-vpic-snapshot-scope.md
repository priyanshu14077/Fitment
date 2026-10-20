# 0021. vPIC snapshot scope and shape

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, questions D1–D6

## Decision

- **Vehicle type (D1):** Passenger Car only (`.../vehicletype/car`). SUVs (vPIC "Multipurpose Passenger Vehicle") and pickups ("Truck") are out of scope; the README says so. Adding them is a change to the query and a re-run.
- **Makes (D2):** Toyota, Lexus, Honda, Acura, Nissan, Infiniti, Mazda, Subaru, Mitsubishi, Suzuki, Hyundai, Kia, Genesis, Ford, Chevrolet, GMC, Dodge, Ram, Jeep, Chrysler, Tesla, Volkswagen, Audi, BMW, Mini, Mercedes-Benz, Porsche, Volvo, Land Rover, Jaguar. Makes that sell few passenger cars in the US (GMC, Ram, Jeep, Land Rover) may return none; the script reports per-make counts. vPIC covers the US market, so NZ/AU-only models are absent.
- **Years (D3):** 2010–2024.
- **Shape (D4):** `GetModelsForMakeYear` per make and year. Each model records the years it appeared, so the seed creates vehicles only for real model years. The file holds `source`, `fetched_at`, `source_version` (`vpic-api-<date>`, since the API reports no dataset version), the query, `makes` and `models`.
- **Names (D5):** the snapshot stores vPIC values exactly. The seed cleans names for display.
- **Politeness (D6):** 4 requests in flight, 3 retries with exponential backoff, a `User-Agent` naming the repository. httpx, already a dependency.

## Consequences

About 450 calls per refresh. The committed file is a faithful copy of the source and can be diffed between refreshes.
