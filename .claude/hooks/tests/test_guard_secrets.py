import pytest
from guard_secrets import check


def tool(name, **tool_input):
    return {"tool_name": name, "tool_input": tool_input}


@pytest.mark.parametrize(
    "payload",
    [
        tool("Read", file_path="/repo/.env"),
        tool("Write", file_path="/repo/.env.local"),
        tool("Read", file_path="/repo/certs/server.pem"),
        tool("Bash", command="cat .env"),
        tool("Bash", command="grep ADMIN /repo/.env"),
        tool("Bash", command="cp .env.example .env"),
    ],
)
def test_blocks(payload):
    assert check(payload)


@pytest.mark.parametrize(
    "payload",
    [
        tool("Read", file_path="/repo/.env.example"),
        tool("Read", file_path="/repo/api/.venv/lib/x.py"),
        tool("Read", file_path="/repo/.gitignore"),
        tool("Bash", command="cat .env.example"),
        tool("Bash", command="uv sync --project api"),
    ],
)
def test_allows(payload):
    assert check(payload) is None
