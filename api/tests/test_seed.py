"""Seed generation against the committed snapshot. Offline; no database."""

import json
from collections import defaultdict

import pytest
from fitment import seed

FUELS = {"gasoline", "diesel", "hybrid", "plug_in_hybrid", "electric"}
ASPIRATIONS = {"naturally_aspirated", "turbo", "supercharged"}


@pytest.fixture(scope="module")
def snapshot() -> dict:
    return json.loads(seed.SNAPSHOT.read_text())


@pytest.fixture(scope="module")
def rows(snapshot: dict) -> dict:
    return seed.build(snapshot)


def by_id(table: list[dict]) -> dict[int, dict]:
    return dict(enumerate(table, start=1))


def test_build_is_deterministic(snapshot: dict, rows: dict) -> None:
    assert seed.build(snapshot) == rows


def test_powertrain_lists_name_real_distinct_models(snapshot: dict) -> None:
    ids = {m["vpic_model_id"] for m in snapshot["models"]}
    lists = [
        seed.ELECTRIC,
        seed.HYBRID,
        seed.PLUG_IN_HYBRID,
        seed.GASOLINE_AND_HYBRID,
        set(seed.EXCLUDED),
    ]
    for listed in lists:
        assert listed <= ids, listed - ids
    assert sum(map(len, lists)) == len(set().union(*lists)), "a model is in two lists"


def test_excluded_models_and_empty_makes_are_skipped(rows: dict) -> None:
    vpic_ids = {m["vpic_model_id"] for m in rows["model"]}
    assert not vpic_ids & set(seed.EXCLUDED)
    names = {m["name"] for m in rows["make"]}
    assert not names & {"Gmc", "GMC", "Jeep", "Land Rover", "Ram"}
    assert {"BMW", "MINI", "Mercedes-Benz", "Toyota"} <= names
    made = {m["make_id"] for m in rows["model"]}
    assert made == set(range(1, len(rows["make"]) + 1))


def test_engines_match_schema_vocabulary(rows: dict) -> None:
    for e in rows["engine"]:
        assert e["fuel"] in FUELS
        if e["fuel"] == "electric":
            assert e["displacement_l"] is e["cylinders"] is e["aspiration"] is None
        else:
            assert e["aspiration"] in ASPIRATIONS and e["displacement_l"] > 0


def test_vehicles_only_for_listed_years_and_unique(snapshot: dict, rows: dict) -> None:
    years = {m["vpic_model_id"]: set(m["years"]) for m in snapshot["models"]}
    models = by_id(rows["model"])
    keys = set()
    for v in rows["vehicle"]:
        assert v["year"] in years[models[v["model_id"]]["vpic_model_id"]]
        keys.add((v["model_id"], v["year"], v["trim"], v["engine_id"]))
    assert len(keys) == len(rows["vehicle"])


def test_electric_models_have_only_electric_engines(rows: dict) -> None:
    models, engines = by_id(rows["model"]), by_id(rows["engine"])
    for v in rows["vehicle"]:
        fuel = engines[v["engine_id"]]["fuel"]
        if models[v["model_id"]]["vpic_model_id"] in seed.ELECTRIC:
            assert fuel == "electric"
        if models[v["model_id"]]["name"] == "335d":
            assert fuel == "diesel"


def test_parts_have_synthetic_skus(rows: dict) -> None:
    skus = [p["sku"] for p in rows["part"]]
    assert all(s.startswith("SYN-") for s in skus)
    assert len(set(skus)) == len(skus)
    assert len(skus) == seed.PARTS_PER_CATEGORY * len(seed.CATEGORIES)


def test_fitment_rules_match_real_vehicles(rows: dict) -> None:
    models = by_id(rows["model"])
    vehicles = defaultdict(list)
    for v in rows["vehicle"]:
        vehicles[v["model_id"]].append(v)
    for f in rows["fitment"]:
        assert models[f["model_id"]]["make_id"] == f["make_id"]
        assert f["year_from"] <= f["year_to"]
        matching = [
            v
            for v in vehicles[f["model_id"]]
            if f["year_from"] <= v["year"] <= f["year_to"]
            and f["trim"] in (None, v["trim"])
            and f["engine_id"] in (None, v["engine_id"])
        ]
        assert matching, f"rule matches no vehicle: {f}"


def test_no_overlapping_rules(rows: dict) -> None:
    pairs = [(f["part_id"], f["model_id"]) for f in rows["fitment"]]
    assert len(set(pairs)) == len(pairs)


def test_spark_plugs_never_fit_electric_engines(rows: dict) -> None:
    categories = {c["slug"]: i for i, c in by_id(rows["part_category"]).items()}
    parts, models, engines = (
        by_id(rows["part"]),
        by_id(rows["model"]),
        by_id(rows["engine"]),
    )
    for f in rows["fitment"]:
        if parts[f["part_id"]]["category_id"] != categories["spark-plugs"]:
            continue
        assert models[f["model_id"]]["vpic_model_id"] not in seed.ELECTRIC
        if f["engine_id"]:
            assert engines[f["engine_id"]]["fuel"] != "electric"


def test_rule_mix_exercises_every_kind(rows: dict) -> None:
    kinds = {
        "trim" if f["trim"] else "engine" if f["engine_id"] else "broad"
        for f in rows["fitment"]
    }
    assert kinds == {"broad", "trim", "engine"}
    assert any(f["position"] for f in rows["fitment"])
    assert any(f["notes"] for f in rows["fitment"])
