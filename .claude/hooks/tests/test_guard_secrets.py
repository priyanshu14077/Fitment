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
        tool("Bash", command="source .env && env"),
        tool("Bash", command="docker run --env-file=.env x"),
        tool("Bash", command="python x.py <.env"),
        tool("Bash", command="cat certs/server.pem | head"),
        tool("Bash", command='bash -c "cat .env"'),
        tool("Bash", command="sh -c 'grep X .env'"),
        tool("Bash", command='cat "/path with space/.env"'),
        tool("Bash", command="echo hi && bash -c 'cat .env'"),
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
        tool(
            "Bash",
            command='git commit -m "feat(api): load settings from the repo-root .env"',
        ),
        tool("Bash", command="echo 'never commit .env files'"),
    ],
)
def test_allows(payload):
    assert check(payload) is None
