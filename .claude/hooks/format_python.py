"""PostToolUse(Edit|Write|MultiEdit): ruff format and ruff check --fix on an
edited Python file. Reports only what ruff could not fix."""

import subprocess

from _common import edited_path, project_dir, read_input, warn


def main() -> None:
    payload = read_input()
    path = edited_path(payload)
    if not path or path.suffix != ".py" or not path.exists():
        return
    root = project_dir(payload)
    if not (root / "api" / "pyproject.toml").exists():
        return
    ruff = ["uv", "run", "--quiet", "--project", str(root / "api"), "ruff"]
    subprocess.run(
        [*ruff, "format", str(path)], cwd=root, check=False, capture_output=True
    )
    result = subprocess.run(
        [*ruff, "check", "--fix", "--quiet", str(path)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and result.stdout.strip():
        warn(
            f"ruff found issues it could not fix in {path.name}:\n{result.stdout.strip()}"
        )


if __name__ == "__main__":
    main()
