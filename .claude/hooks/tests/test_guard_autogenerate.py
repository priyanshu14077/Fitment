from guard_autogenerate import check


def test_blocks_autogenerate():
    assert check('cd api && uv run alembic revision --autogenerate -m "x"')


def test_allows_hand_written_revision():
    assert check('uv run alembic revision -m "add index"') is None
