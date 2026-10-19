import pytest
from guard_destructive import check


@pytest.mark.parametrize(
    "command",
    [
        "rm -rf api",
        "rm -fr /tmp/x",
        "git push --force",
        "git push -f origin feat/x",
        "git push --force-with-lease",
        "git reset --hard HEAD~1",
        "git clean -fd",
        "git checkout -- api/main.py",
        "git checkout .",
        "git restore .",
        "git stash drop",
        "git branch -D feat/x",
        "docker compose down -v",
        "docker compose down --volumes",
        "docker volume rm fitment-pgdata",
        "cd api && uv run alembic downgrade base",
    ],
)
def test_blocks(command):
    assert check(command)


@pytest.mark.parametrize(
    "command",
    [
        "rm api/old.py",
        "git push -u origin feat/x",
        "git reset HEAD~1",
        "git checkout -b feat/x",
        "git switch master",
        "git restore --staged api/x.py",
        "git stash push -m wip",
        "docker compose down",
        "DATABASE_URL=postgresql+asyncpg://fitment:fitment@localhost:5432/fitment_check uv run alembic downgrade base",
    ],
)
def test_allows(command):
    assert check(command) is None
