"""PreToolUse(Edit|Write|MultiEdit): a migration already on master is
immutable. Fix it with a new migration (ADR 0007)."""

from _common import block, edited_path, git, project_dir, read_input

MIGRATIONS = "api/migrations/versions/"


def check(payload: dict) -> str | None:
    path = edited_path(payload)
    if not path or path.suffix != ".py":
        return None
    root = project_dir(payload)
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None
    if not rel.startswith(MIGRATIONS):
        return None
    if git(root, "cat-file", "-e", f"master:{rel}").returncode == 0:
        return (
            f"Blocked: {rel} is on master and immutable. Write a new migration instead."
        )
    return None


if __name__ == "__main__":
    reason = check(read_input())
    if reason:
        block(reason)
