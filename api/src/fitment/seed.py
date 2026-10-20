"""Build the catalog from data/vpic_snapshot.json and load it (ADR 0022).

`build` is pure and deterministic: the same snapshot always gives the same
rows. IDs are list positions (1-based) because `repo.seed.load` inserts
straight after RESTART IDENTITY.

    uv run --project api python scripts/seed.py
"""

import asyncio
import json
import random
import sys
from decimal import Decimal
from pathlib import Path

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from fitment.config import REPO_ROOT, get_settings
from fitment.repo import seed as repo

SNAPSHOT = REPO_ROOT / "data" / "vpic_snapshot.json"
RNG_SEED = 20261019
PARTS_PER_CATEGORY = 25
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}

EXCLUDED = {
    14930: "Ford '34: a replica builder's registration",
    3155: "Toyota FCHV-adv: fuel-cell test fleet",
    28490: "Volvo 'C70 / C30': one record for two models",
    4047: "Chevrolet Matiz: not sold in the US",
    27445: "Chevrolet Onix: not sold in the US",
}
UPPERCASE_MAKES = {"BMW", "MINI"}

# Powertrain class per vpic_model_id. Unlisted models are gasoline, except
# BMW names ending in "d", which are diesel. Fuel cells count as electric.
ELECTRIC = {
    17834, 1685, 10199, 27027, 2071,  # Tesla Model 3, S, X, Y, Roadster
    30005, 13672,  # Chevrolet Bolt EUV, Bolt EV
    1905, 30884,  # Nissan Leaf, Ariya
    28090,  # Porsche Taycan
    29994, 28998,  # Audi e-tron GT, RS e-tron GT
    30229, 29045,  # Mercedes-Benz EQE, EQS
    31360,  # Hyundai Ioniq 6
    2339,  # Mitsubishi i-MiEV
    8118,  # Volkswagen e-Golf
    29125,  # Mazda MX-30
    2178, 29579, 32328, 30512, 1971,  # BMW i3, i4, i5, i7, ActiveE
    10198, 1875, 14249,  # fuel cell: Toyota Mirai, Honda FCX Clarity, Clarity
}  # fmt: skip
HYBRID = {
    2209, 13823, 13822,  # Toyota Prius, Prius C, Prius V
    1870, 2128,  # Honda Insight, CR-Z
    3154, 3185,  # Lexus CT, HS
    2368,  # Infiniti M35h
    2219, 2240, 31534,  # BMW ActiveHybrid 3, 5, 7
}  # fmt: skip
PLUG_IN_HYBRID = {
    21950,  # Toyota Prius Prime
    1838,  # Chevrolet Volt
    34061, 27122, 34062,  # Audi A7 e, A8 e, A8 L e
    9569, 20813, 13835, 26482, 29051, 32327, 2179,  # BMW 330e .. 750e, i8
    8022,  # Porsche 918
}  # fmt: skip
GASOLINE_AND_HYBRID = {
    2469, 1861, 2459, 1780, 2475, 21961,  # Camry, Accord, Sonata, Fusion, ES, Ioniq
}  # fmt: skip

ENGINES = [
    # code, displacement_l, cylinders, fuel, aspiration
    ("1.5L-I4-T", 1.5, 4, "gasoline", "turbo"),
    ("2.0L-I4", 2.0, 4, "gasoline", "naturally_aspirated"),
    ("2.0L-I4-T", 2.0, 4, "gasoline", "turbo"),
    ("2.5L-I4", 2.5, 4, "gasoline", "naturally_aspirated"),
    ("3.0L-I6-T", 3.0, 6, "gasoline", "turbo"),
    ("3.5L-V6", 3.5, 6, "gasoline", "naturally_aspirated"),
    ("3.0L-V6-T", 3.0, 6, "gasoline", "turbo"),
    ("5.0L-V8", 5.0, 8, "gasoline", "naturally_aspirated"),
    ("6.2L-V8-S", 6.2, 8, "gasoline", "supercharged"),
    ("2.0L-I4-T-DIESEL", 2.0, 4, "diesel", "turbo"),
    ("1.8L-I4-HEV", 1.8, 4, "hybrid", "naturally_aspirated"),
    ("2.5L-I4-HEV", 2.5, 4, "hybrid", "naturally_aspirated"),
    ("2.0L-I4-T-PHEV", 2.0, 4, "plug_in_hybrid", "turbo"),
    ("EV-1M", None, None, "electric", None),
    ("EV-2M", None, None, "electric", None),
]
TRIMS = ["Base", "Sport", "Touring", "Limited"]
BRANDS = [
    "Kestrel Auto",
    "Ironbark",
    "Tidewater",
    "Quillon",
    "Harrow & Finch",
    "Northvale",
]

# slug: (name, SKU code, positions, price range in cents, products, attrs choices)
CATEGORIES = {
    "brakes": ("Brakes", "BRK", ["front", "rear"], (3_500, 18_000),
               ["Ceramic brake pad set", "Semi-metallic brake pad set", "Vented brake rotor"],
               {"material": ["ceramic", "semi_metallic", "cast_iron"]}),
    "suspension": ("Suspension", "SUS", ["front_left", "front_right", "rear_left", "rear_right"],
                   (6_000, 35_000), ["Strut assembly", "Control arm", "Coil spring"],
                   {"type": ["strut", "control_arm", "coil_spring"]}),
    "lighting": ("Lighting", "LGT", ["left", "right"], (2_500, 60_000),
                 ["Headlight assembly", "Tail light assembly", "Fog light"],
                 {"bulb": ["H11", "H7", "LED"]}),
    "filters": ("Filters", "FLT", [], (900, 4_500),
                ["Cabin air filter", "Engine air filter"], {"media": ["paper", "carbon"]}),
    "wipers": ("Wipers", "WPR", [], (1_200, 4_000),
               ["Beam wiper blade", "Conventional wiper blade"],
               {"length_mm": [400, 450, 500, 550, 600, 650]}),
    "spark-plugs": ("Spark plugs", "SPK", [], (600, 2_500),
                    ["Iridium spark plug", "Platinum spark plug"],
                    {"electrode": ["iridium", "platinum"]}),
    "batteries": ("Batteries", "BAT", [], (9_000, 28_000),
                  ["12V AGM battery", "12V flooded battery"],
                  {"group_size": ["H5", "H6", "H7", "35", "48"]}),
    "cooling": ("Cooling", "COL", [], (1_500, 45_000),
                ["Radiator", "Thermostat", "Water pump"],
                {"type": ["radiator", "thermostat", "water_pump"]}),
}  # fmt: skip
CROSS_MAKE = {"wipers", "batteries"}
COMBUSTION_ONLY = {"spark-plugs"}
RULE_KINDS = (["broad", "trim", "engine"], [60, 20, 20])
NOTES = [
    "With sport package",
    "Not for models with adaptive headlights",
    "Requires hardware kit, sold separately",
    "Check part number on existing unit before ordering",
]
NOTES_RATE = 0.10


def make_name(vpic_name: str) -> str:
    name = vpic_name.strip()
    return name.upper() if name.upper() in UPPERCASE_MAKES else name.title()


def powertrain(make: str, model: dict) -> str:
    model_id = model["vpic_model_id"]
    for cls, ids in (
        ("electric", ELECTRIC),
        ("hybrid", HYBRID),
        ("plug_in_hybrid", PLUG_IN_HYBRID),
        ("gasoline_and_hybrid", GASOLINE_AND_HYBRID),
    ):
        if model_id in ids:
            return cls
    if make == "BMW" and model["name"].strip().endswith("d"):
        return "diesel"
    return "gasoline"


def pick_engines(rng: random.Random, cls: str) -> list[int]:
    """Engine ids (1-based positions in ENGINES) for one model."""
    by_fuel: dict[str, list[int]] = {}
    for i, engine in enumerate(ENGINES, start=1):
        by_fuel.setdefault(engine[3], []).append(i)
    if cls == "gasoline":
        return sorted(rng.sample(by_fuel["gasoline"], rng.randint(1, 2)))
    if cls == "gasoline_and_hybrid":
        return [rng.choice(by_fuel["gasoline"]), rng.choice(by_fuel["hybrid"])]
    if cls == "electric":
        return sorted(rng.sample(by_fuel["electric"], rng.randint(1, 2)))
    return [rng.choice(by_fuel[cls])]


def build(snapshot: dict, parts_per_category: int = PARTS_PER_CATEGORY) -> dict:
    rng = random.Random(RNG_SEED)
    source_version = snapshot["source_version"]
    vpic_makes = {m["vpic_make_id"]: m["name"] for m in snapshot["makes"]}
    kept = [m for m in snapshot["models"] if m["vpic_model_id"] not in EXCLUDED]

    make_rows, make_ids = [], {}
    for vpic_make_id in sorted({m["vpic_make_id"] for m in kept}):
        make_rows.append(
            {
                "vpic_make_id": vpic_make_id,
                "name": make_name(vpic_makes[vpic_make_id]),
                "source_version": source_version,
            }
        )
        make_ids[vpic_make_id] = len(make_rows)

    engine_rows = [
        {
            "code": code,
            "displacement_l": None if litres is None else Decimal(str(litres)),
            "cylinders": cylinders,
            "fuel": fuel,
            "aspiration": aspiration,
        }
        for code, litres, cylinders, fuel, aspiration in ENGINES
    ]

    model_rows, models, vehicle_rows = [], [], []
    for m in kept:
        make_id = make_ids[m["vpic_make_id"]]
        model_rows.append(
            {
                "make_id": make_id,
                "vpic_model_id": m["vpic_model_id"],
                "name": m["name"].strip(),
                "source_version": source_version,
            }
        )
        model_id = len(model_rows)
        cls = powertrain(make_name(vpic_makes[m["vpic_make_id"]]), m)
        picked = set(rng.sample(TRIMS, rng.randint(1, 3)))
        trims = [t for t in TRIMS if t in picked]
        engines = pick_engines(rng, cls)
        models.append(
            {
                "id": model_id,
                "make_id": make_id,
                "class": cls,
                "years": m["years"],
                "trims": trims,
                "engines": engines,
            }
        )
        vehicle_rows.extend(
            {"model_id": model_id, "year": y, "trim": t, "engine_id": e}
            for y in m["years"]
            for t in trims
            for e in engines
        )

    category_rows, part_rows, fitment_rows = [], [], []
    for slug, (
        name,
        code,
        positions,
        (low, high),
        products,
        attrs,
    ) in CATEGORIES.items():
        category_rows.append({"slug": slug, "name": name})
        category_id = len(category_rows)
        if slug in COMBUSTION_ONLY:
            eligible = [m for m in models if combustion_engines(m)]
        else:
            eligible = models
        for n in range(1, parts_per_category + 1):
            brand = rng.choice(BRANDS)
            product = rng.choice(products)
            position = rng.choice(positions) if positions else None
            label = f" ({position.replace('_', ' ')})" if position else ""
            part_rows.append(
                {
                    "sku": f"SYN-{code}-{n:05d}",
                    "brand": brand,
                    "name": f"{brand} {product}{label}",
                    "category_id": category_id,
                    "price_cents": rng.randrange(low, high, 50),
                    "attrs": json.dumps({k: rng.choice(v) for k, v in attrs.items()}),
                }
            )
            fitment_rows.extend(rules(rng, len(part_rows), slug, position, eligible))

    return {
        "make": make_rows,
        "model": model_rows,
        "engine": engine_rows,
        "vehicle": vehicle_rows,
        "part_category": category_rows,
        "part": part_rows,
        "fitment": fitment_rows,
    }


def combustion_engines(model: dict) -> list[int]:
    return [e for e in model["engines"] if ENGINES[e - 1][3] != "electric"]


def rules(
    rng: random.Random,
    part_id: int,
    slug: str,
    position: str | None,
    eligible: list[dict],
) -> list[dict]:
    """1-4 rules on distinct models of one powertrain class: one rule per
    part and model, so no two rules for a part can overlap."""
    anchor = rng.choice(eligible)
    pool = [
        m
        for m in eligible
        if m["class"] == anchor["class"]
        and (slug in CROSS_MAKE or m["make_id"] == anchor["make_id"])
    ]
    chosen = rng.sample(pool, min(rng.randint(1, 4), len(pool)))
    out = []
    for m in sorted(chosen, key=lambda m: m["id"]):
        years = m["years"]
        i, j = sorted(rng.sample(range(len(years)), 2)) if len(years) > 1 else (0, 0)
        kind = rng.choices(*RULE_KINDS)[0]
        engines = combustion_engines(m) if slug in COMBUSTION_ONLY else m["engines"]
        out.append(
            {
                "part_id": part_id,
                "make_id": m["make_id"],
                "model_id": m["id"],
                "year_from": years[i],
                "year_to": years[j],
                "trim": rng.choice(m["trims"]) if kind == "trim" else None,
                "engine_id": rng.choice(engines) if kind == "engine" else None,
                "position": position,
                "notes": rng.choice(NOTES) if rng.random() < NOTES_RATE else None,
            }
        )
    return out


async def seed(rows: dict) -> dict[str, int]:
    url = get_settings().database_url
    if make_url(url).host not in LOCAL_HOSTS:
        sys.exit(f"Refusing to seed a non-local database: {make_url(url).host}")
    engine = create_async_engine(url)
    try:
        async with engine.begin() as conn:
            return await repo.load(conn, rows)
    finally:
        await engine.dispose()


def main(snapshot_path: Path = SNAPSHOT) -> None:
    rows = build(json.loads(snapshot_path.read_text()))
    counts = asyncio.run(seed(rows))
    width = max(map(len, counts))
    for table, count in counts.items():
        print(f"{table:<{width}} {count:>7}")
