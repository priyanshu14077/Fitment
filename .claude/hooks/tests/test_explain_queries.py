from explain_queries import queries, seq_scans, to_positional


def test_finds_text_queries():
    source = (
        'from sqlalchemy import text\nQ = text("SELECT 1 FROM part WHERE id = :id")\n'
    )
    assert queries(source) == [(2, "SELECT 1 FROM part WHERE id = :id")]


def test_named_binds_become_positional_and_casts_survive():
    sql = "SELECT * FROM f WHERE model_id = :model AND :year BETWEEN a AND b AND x::int = :model"
    assert (
        to_positional(sql)
        == "SELECT * FROM f WHERE model_id = $1 AND $2 BETWEEN a AND b AND x::int = $1"
    )


def test_seq_scan_detection_walks_children():
    plan = {
        "Node Type": "Hash Join",
        "Plans": [{"Node Type": "Seq Scan", "Relation Name": "part"}],
    }
    assert seq_scans(plan) == ["part"]


def test_live_database_errors_are_reported():
    import shutil
    import subprocess

    import pytest
    from explain_queries import explain

    probe = ["docker", "exec", "fitment-db", "true"]
    if (
        not shutil.which("docker")
        or subprocess.run(probe, check=False, capture_output=True).returncode
    ):
        pytest.skip("fitment-db not running")
    assert explain("SELECT relname FROM pg_class WHERE oid = :oid") == []
    assert "no_such_table" in explain("SELECT * FROM no_such_table WHERE id = :id")
