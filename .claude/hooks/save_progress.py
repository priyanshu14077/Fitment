"""PreCompact: write the branch, recent commits and working-tree state to
.claude/state/progress.md (git-ignored) so the step in progress survives
context compaction. SessionStart prints it back."""

from datetime import UTC, datetime

from _common import current_branch, git, project_dir, read_input

PROGRESS = ".claude/state/progress.md"


def main() -> None:
    payload = read_input()
    root = project_dir(payload)
    path = root / PROGRESS
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    log = git(root, "log", "--oneline", "-5").stdout.strip()
    status = git(root, "status", "--short").stdout.strip() or "(clean)"
    path.write_text(
        f"Saved {stamp} before {payload.get('trigger', 'compact')} compaction\n"
        f"Branch: {current_branch(root)}\n\nRecent commits:\n{log}\n\nWorking tree:\n{status}\n"
    )


if __name__ == "__main__":
    main()
