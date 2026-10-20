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


def downgrade() -> None:
    for table in ("vehicle", "engine", "model", "make"):
        op.execute(f"DROP TABLE {table}")
