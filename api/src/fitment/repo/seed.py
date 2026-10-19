"""Catalog reload for the seed (ADR 0022). Rows are inserted in list order
straight after RESTART IDENTITY, so row N of each table gets id N; the
generator relies on that for foreign keys and `load` checks it."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

TABLES = ("make", "model", "engine", "vehicle", "part_category", "part", "fitment")

TRUNCATE = "TRUNCATE make, model, engine, vehicle, part_category, part, fitment RESTART IDENTITY"

COUNTS = """
    SELECT 'make', count(*), coalesce(max(id), 0) FROM make
    UNION ALL SELECT 'model', count(*), coalesce(max(id), 0) FROM model
    UNION ALL SELECT 'engine', count(*), coalesce(max(id), 0) FROM engine
    UNION ALL SELECT 'vehicle', count(*), coalesce(max(id), 0) FROM vehicle
    UNION ALL SELECT 'part_category', count(*), coalesce(max(id), 0) FROM part_category
    UNION ALL SELECT 'part', count(*), coalesce(max(id), 0) FROM part
    UNION ALL SELECT 'fitment', count(*), coalesce(max(id), 0) FROM fitment
"""

INSERTS = {
    "make": "INSERT INTO make (vpic_make_id, name, source_version)"
    " VALUES (:vpic_make_id, :name, :source_version)",
    "model": "INSERT INTO model (make_id, vpic_model_id, name, source_version)"
    " VALUES (:make_id, :vpic_model_id, :name, :source_version)",
    "engine": "INSERT INTO engine (code, displacement_l, cylinders, fuel, aspiration)"
    " VALUES (:code, :displacement_l, :cylinders, :fuel, :aspiration)",
    "vehicle": "INSERT INTO vehicle (model_id, year, trim, engine_id)"
    " VALUES (:model_id, :year, :trim, :engine_id)",
    "part_category": "INSERT INTO part_category (slug, name) VALUES (:slug, :name)",
    "part": "INSERT INTO part (sku, brand, name, category_id, price_cents, attrs)"
    " VALUES (:sku, :brand, :name, :category_id, :price_cents, CAST(:attrs AS jsonb))",
    "fitment": "INSERT INTO fitment"
    " (part_id, make_id, model_id, year_from, year_to, trim, engine_id, position, notes)"
    " VALUES (:part_id, :make_id, :model_id, :year_from, :year_to, :trim, :engine_id,"
    " :position, :notes)",
}


async def load(conn: AsyncConnection, rows: dict[str, list[dict]]) -> dict[str, int]:
    """Replace the catalog with `rows` and return the row count per table."""
    await conn.execute(text(TRUNCATE))
    for table in TABLES:
        if rows[table]:
            await conn.execute(text(INSERTS[table]), rows[table])
    counts = {}
    for table, count, max_id in await conn.execute(text(COUNTS)):
        if count != max_id or count != len(rows[table]):
            raise RuntimeError(
                f"{table}: {count} rows, max id {max_id}, expected {len(rows[table])}"
            )
        counts[table] = count
    return counts
