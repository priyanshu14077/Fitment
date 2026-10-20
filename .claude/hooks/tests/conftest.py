import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HOOKS))


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A throwaway git repo with one commit on master."""

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-b", "master")
    git("config", "user.email", "test@example.com")
    git("config", "user.name", "test")
    (tmp_path / "README.md").write_text("x\n")
    git("add", ".")
    git("commit", "-m", "init")
    return tmp_path


def run_hook(name: str, payload: dict, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOKS / name)],
        input=json.dumps(payload),
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
        env={"PATH": "/usr/bin:/bin:/opt/homebrew/bin", "CLAUDE_PROJECT_DIR": str(cwd)},
    )
