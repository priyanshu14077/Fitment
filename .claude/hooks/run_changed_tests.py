"""Stop: run the tests that cover files changed in the working tree, with a
30 second limit. Failing tests are reported back so the agent fixes them
before handing over. CI runs the whole suite."""

import subprocess
from pathlib import Path

from _common import git, project_dir, read_input, warn

LIMIT_SECONDS = 30
TEST_ROOTS = {"api/": "api/tests", ".claude/hooks/": ".claude/hooks/tests"}


def changed_files(root: Path) -> list[str]:
    tracked = git(root, "diff", "--name-only", "HEAD").stdout.split()
    untracked = git(root, "ls-files", "--others", "--exclude-standard").stdout.split()
    return [f for f in tracked + untracked if f.endswith(".py")]


def tests_for(root: Path, files: list[str]) -> list[str]:
    selected: set[str] = set()
    for rel in files:
        for prefix, test_dir in TEST_ROOTS.items():
            if not rel.startswith(prefix) or not (root / test_dir).is_dir():
                continue
            name = Path(rel).name
            if name.startswith("test_"):
                selected.add(rel)
            else:
                stem = Path(rel).stem.lstrip("_")
                selected.update(
                    p.relative_to(root).as_posix()
                    for p in (root / test_dir).rglob(f"test_{stem}*.py")
                )
    return sorted(s for s in selected if (root / s).exists())


def main() -> None:
    payload = read_input()
    if payload.get("stop_hook_active"):
        return  # already reported once this turn; do not loop
    root = project_dir(payload)
    targets = tests_for(root, changed_files(root))
    if not targets:
        return
    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "--quiet",
                "--project",
                str(root / "api"),
                "pytest",
                "-q",
                "-x",
                *targets,
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=LIMIT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        print(
            f"Changed-file tests exceeded {LIMIT_SECONDS}s; skipped. CI runs the full suite."
        )
        return
    if result.returncode not in (0, 5):  # 5: no tests collected
        warn(
            f"Tests failing for changed files ({', '.join(targets)}):\n{result.stdout.strip()[-3000:]}"
        )


if __name__ == "__main__":
    main()
