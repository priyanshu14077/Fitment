import subprocess

import pytest
from conftest import run_hook
from guard_master import check


@pytest.mark.parametrize(
    "command",
    [
        "git commit -m x",
        "git add . && git commit -m x",
        "git -C . commit -m x",
        "git push",
        "git push origin HEAD",
    ],
)
def test_blocks_on_master(command):
    assert check(command, "master")


@pytest.mark.parametrize(
    "command", ["git push origin master", "git push origin feat/x:master"]
)
def test_blocks_push_to_master_from_any_branch(command):
    assert check(command, "feat/x")


@pytest.mark.parametrize(
    "command",
    ["git commit -m x", "git push -u origin feat/x", "git status", "echo git commit"],
)
def test_allows_on_feature_branch(command):
    assert check(command, "feat/x") is None


def test_hook_exit_codes(repo):
    payload = {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"}}
    assert run_hook("guard_master.py", payload, repo).returncode == 2
    subprocess.run(
        ["git", "switch", "-c", "feat/x"], cwd=repo, check=True, capture_output=True
    )
    assert run_hook("guard_master.py", payload, repo).returncode == 0
