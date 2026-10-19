"""PreToolUse(Bash): migrations are hand-written (ADR 0007)."""

from _common import bash_command, block, read_input, segments


def check(command: str) -> str | None:
    for tokens in segments(command):
        if "alembic" in tokens and "revision" in tokens and "--autogenerate" in tokens:
            return "Blocked: alembic --autogenerate. Write the migration by hand (ADR 0007, skill new-migration)."
    return None


if __name__ == "__main__":
    reason = check(bash_command(read_input()))
    if reason:
        block(reason)
