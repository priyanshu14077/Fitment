"""Snapshot real makes and models from NHTSA vPIC into data/vpic_snapshot.json.

The only code in the repo that calls vPIC (ADR 0003). The user runs it by
hand; scope and shape are fixed by ADR 0021:

    uv run --project api python scripts/snapshot_vpic.py

Names are stored exactly as vPIC returns them; the seed cleans them up.
"""

import argparse
import asyncio
import json
import sys
from datetime import date
from pathlib import Path

import httpx

BASE = "https://vpic.nhtsa.dot.gov/api/vehicles"
MAKES = [
    "TOYOTA", "LEXUS", "HONDA", "ACURA", "NISSAN", "INFINITI", "MAZDA", "SUBARU",
    "MITSUBISHI", "SUZUKI", "HYUNDAI", "KIA", "GENESIS", "FORD", "CHEVROLET", "GMC",
    "DODGE", "RAM", "JEEP", "CHRYSLER", "TESLA", "VOLKSWAGEN", "AUDI", "BMW", "MINI",
    "MERCEDES-BENZ", "PORSCHE", "VOLVO", "LAND ROVER", "JAGUAR",
]  # fmt: skip
YEARS = range(2010, 2025)
VEHICLE_TYPE = "car"
CONCURRENCY = 4
RETRIES = 3
USER_AGENT = "fitment-snapshot/1 (+https://github.com/priyanshu14077/Fitment)"
OUT = Path(__file__).resolve().parents[1] / "data" / "vpic_snapshot.json"


async def get(
    client: httpx.AsyncClient, limit: asyncio.Semaphore, path: str
) -> list[dict]:
    for attempt in range(RETRIES + 1):
        try:
            async with limit:
                response = await client.get(f"{BASE}/{path}", params={"format": "json"})
            response.raise_for_status()
            return response.json()["Results"]
        except (httpx.HTTPError, ValueError, KeyError):
            if attempt == RETRIES:
                raise
            await asyncio.sleep(2**attempt)
    raise AssertionError("unreachable")


def resolve_make_ids(all_makes: list[dict]) -> dict[str, int]:
    """Exact, case-insensitive name match. vPIC's by-name endpoints match
    partially, so the snapshot queries by ID instead."""
    by_name: dict[str, list[int]] = {}
    for row in all_makes:
        by_name.setdefault(row["Make_Name"].strip().upper(), []).append(row["Make_ID"])
    problems = {
        name: by_name.get(name, []) for name in MAKES if len(by_name.get(name, [])) != 1
    }
    if problems:
        sys.exit(f"Make names that do not match exactly one vPIC make: {problems}")
    return {name: by_name[name][0] for name in MAKES}


def build(
    make_ids: dict[str, int], rows_by_year: dict[tuple[int, int], list[dict]]
) -> dict:
    makes = {}
    models: dict[int, dict] = {}
    for (make_id, year), rows in rows_by_year.items():
        for row in rows:
            makes[row["Make_ID"]] = row["Make_Name"]
            model = models.setdefault(
                row["Model_ID"],
                {
                    "vpic_model_id": row["Model_ID"],
                    "vpic_make_id": row["Make_ID"],
                    "name": row["Model_Name"],
                    "vehicle_type": row.get("VehicleTypeName"),
                    "years": [],
                },
            )
            model["years"].append(year)
    for name, make_id in make_ids.items():
        makes.setdefault(make_id, name)
    today = date.today().isoformat()
    return {
        "source": "vpic-api",
        "fetched_at": today,
        "source_version": f"vpic-api-{today}",
        "query": {
            "makes": MAKES,
            "years": [YEARS.start, YEARS.stop - 1],
            "vehicle_types": [VEHICLE_TYPE],
        },
        "makes": sorted(
            ({"vpic_make_id": i, "name": n} for i, n in makes.items()),
            key=lambda m: m["name"],
        ),
        "models": sorted(
            ({**m, "years": sorted(set(m["years"]))} for m in models.values()),
            key=lambda m: (m["vpic_make_id"], m["name"], m["vpic_model_id"]),
        ),
    }


async def snapshot(transport: httpx.AsyncBaseTransport | None = None) -> dict:
    limit = asyncio.Semaphore(CONCURRENCY)
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(
        headers=headers, timeout=30, transport=transport
    ) as client:
        make_ids = resolve_make_ids(await get(client, limit, "GetAllMakes"))
        keys = [(make_id, year) for make_id in make_ids.values() for year in YEARS]
        results = await asyncio.gather(
            *(
                get(
                    client,
                    limit,
                    f"GetModelsForMakeIdYear/makeId/{m}/modelyear/{y}/vehicletype/{VEHICLE_TYPE}",
                )
                for m, y in keys
            )
        )
    return build(make_ids, dict(zip(keys, results, strict=True)))


def report(data: dict) -> str:
    names = {m["vpic_make_id"]: m["name"] for m in data["makes"]}
    counts = {make_id: 0 for make_id in names}
    for model in data["models"]:
        counts[model["vpic_make_id"]] += 1
    lines = [
        f"{names[i]:<15} {n:>3} models"
        for i, n in sorted(counts.items(), key=lambda c: names[c[0]])
    ]
    empty = [names[i] for i, n in counts.items() if n == 0]
    lines.append(f"\n{len(data['makes'])} makes, {len(data['models'])} models")
    if empty:
        lines.append(f"No {VEHICLE_TYPE} models: {', '.join(sorted(empty))}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    data = asyncio.run(snapshot())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2) + "\n")
    print(report(data))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
