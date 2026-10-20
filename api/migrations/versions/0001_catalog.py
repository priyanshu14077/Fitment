"""Catalog: makes, models, engines, vehicles, parts, fitment.

Revision ID: 0001
Revises:
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.execute("""
        CREATE TABLE make (
            id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            vpic_make_id   integer NOT NULL UNIQUE,
            name           text    NOT NULL,
            source_version text    NOT NULL
        )
    """)

    # UNIQUE (id, make_id) exists only so fitment can reference the pair and
    # the database rejects a row that says make = Ford, model = Camry.
    op.execute("""
        CREATE TABLE model (
            id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            make_id        integer NOT NULL REFERENCES make (id),
            vpic_model_id  integer NOT NULL UNIQUE,
            name           text    NOT NULL,
            source_version text    NOT NULL,
            UNIQUE (id, make_id)
        )
    """)
    op.execute("CREATE INDEX model_make_id_idx ON model (make_id)")

    # Field names follow vPIC's DecodeVinValues output. Electric engines have
    # no displacement or cylinders, so both are nullable.
    op.execute("""
        CREATE TABLE engine (
            id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            code           text    NOT NULL UNIQUE,
            displacement_l numeric(3, 1) CHECK (displacement_l > 0),
            cylinders      smallint CHECK (cylinders > 0),
            fuel           text    NOT NULL,
            aspiration     text    NOT NULL
                CHECK (aspiration IN ('naturally_aspirated', 'turbo', 'supercharged', 'electric'))
        )
    """)

    op.execute("""
        CREATE TABLE vehicle (
            id        integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            model_id  integer  NOT NULL REFERENCES model (id),
            year      smallint NOT NULL CHECK (year BETWEEN 1981 AND 2100),
            trim      text,
            engine_id integer  NOT NULL REFERENCES engine (id),
            UNIQUE NULLS NOT DISTINCT (model_id, year, trim, engine_id)
        )
    """)
    op.execute("CREATE INDEX vehicle_engine_id_idx ON vehicle (engine_id)")

    op.execute("""
        CREATE TABLE part_category (
            id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            slug text NOT NULL UNIQUE,
            name text NOT NULL
        )
    """)

    op.execute("""
        CREATE TABLE part (
            id          bigint  GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            sku         text    NOT NULL UNIQUE,
            brand       text    NOT NULL,
            name        text    NOT NULL,
            category_id integer NOT NULL REFERENCES part_category (id),
            price_cents integer NOT NULL CHECK (price_cents >= 0),
            attrs       jsonb   NOT NULL DEFAULT '{}'
        )
    """)
    op.execute("CREATE INDEX part_category_id_idx ON part (category_id)")
    op.execute("CREATE INDEX part_attrs_idx ON part USING gin (attrs jsonb_path_ops)")
    op.execute("CREATE INDEX part_name_trgm_idx ON part USING gin (name gin_trgm_ops)")

    # A NULL trim or engine_id means the rule applies to every trim or engine.
    op.execute("""
        CREATE TABLE fitment (
            id        bigint   GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            part_id   bigint   NOT NULL REFERENCES part (id) ON DELETE CASCADE,
            make_id   integer  NOT NULL,
            model_id  integer  NOT NULL,
            year_from smallint NOT NULL,
            year_to   smallint NOT NULL,
            trim      text,
            engine_id integer  REFERENCES engine (id),
            position  text,
            notes     text,
            FOREIGN KEY (model_id, make_id) REFERENCES model (id, make_id),
            CHECK (year_from <= year_to),
            UNIQUE NULLS NOT DISTINCT
                (part_id, model_id, year_from, year_to, trim, engine_id, position)
        )
    """)
    # The hot path: "which parts fit model M in year Y?" INCLUDE lets the
    # wildcard filters run from the index without visiting the table.
    op.execute("""
        CREATE INDEX fitment_lookup ON fitment (model_id, year_from, year_to)
            INCLUDE (part_id, trim, engine_id, position)
    """)
    op.execute("CREATE INDEX fitment_part_id_idx ON fitment (part_id)")
    op.execute("CREATE INDEX fitment_make_id_idx ON fitment (make_id)")
    op.execute(
        "CREATE INDEX fitment_engine_id_idx ON fitment (engine_id) WHERE engine_id IS NOT NULL"
    )


def downgrade() -> None:
    for table in (
        "fitment",
        "part",
        "part_category",
        "vehicle",
        "engine",
        "model",
        "make",
    ):
        op.execute(f"DROP TABLE {table}")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
