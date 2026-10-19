"""SessionStart: tell the agent where things stand before it assumes
anything: branch, uncommitted work, stack health, migration version, and the
progress note saved before the last compaction."""

import subprocess

from _common import current_branch, git, project_dir, read_input

PROGRESS = ".claude/state/progress.md"


def run(args: list[str]) -> str:
    try:
        result = subprocess.run(
            args, check=False, capture_output=True, text=True, timeout=8
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def main() -> None:
    root = project_dir(read_input())
    lines = [f"Branch: {current_branch(root) or '(detached)'}"]
    status = git(root, "status", "--short").stdout.splitlines()
    lines.append(f"Uncommitted files: {len(status)}")
    stashes = git(root, "stash", "list").stdout.strip()
    if stashes:
        lines.append(f"Stashes:\n{stashes}")
    services = run(
        [
            "docker",
            "compose",
            "--project-directory",
            str(root),
            "ps",
            "--format",
            "{{.Service}}: {{.Status}}",
        ]
    )
    lines.append(
        f"Services:\n{services}"
        if services
        else "Services: none running (docker compose up -d)"
    )
    if services:
        version = run(
            [
                "docker",
                "exec",
                "fitment-db",
                "psql",
                "-U",
                "fitment",
                "-XAtc",
                "select version_num from alembic_version",
            ]
        )
        lines.append(f"Migration: {version or 'none applied'}")
    progress = root / PROGRESS
    if progress.exists():
        lines.append(
            f"Saved progress ({PROGRESS}):\n{progress.read_text().strip()[-1500:]}"
        )
    print("\n".join(lines))


if __name__ == "__main__":
    main()
