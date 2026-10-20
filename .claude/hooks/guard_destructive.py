"""PreToolUse(Bash): block commands that destroy uncommitted work, history
or data. The user runs these by hand when they are really wanted."""

import re

from _common import bash_command, block, git_subcommand, read_input, segments


def check(command: str) -> str | None:
    for tokens in segments(command):
        name = tokens[0].rsplit("/", 1)[-1]
        flags = "".join(t for t in tokens[1:] if re.match(r"^-[A-Za-z]+$", t))
        if name == "rm" and "r" in flags.lower() and "f" in flags:
            return "Blocked: rm -rf. Delete specific files, or ask the user."
        parsed = git_subcommand(tokens)
        if parsed:
            sub, rest = parsed
            if sub == "push" and any(
                r in ("-f", "--force") or r.startswith("--force") for r in rest
            ):
                return "Blocked: force-push rewrites shared history."
            if sub == "reset" and "--hard" in rest:
                return "Blocked: git reset --hard discards uncommitted work."
            if sub == "clean" and any(r.startswith("-") and "f" in r for r in rest):
                return "Blocked: git clean -f deletes untracked files."
            if (
                sub in ("checkout", "restore")
                and "--staged" not in rest
                and ("." in rest or "--" in rest)
            ):
                return f"Blocked: git {sub} on paths discards uncommitted changes."
            if sub == "stash" and rest[:1] and rest[0] in ("drop", "clear"):
                return "Blocked: dropping a stash loses the work in it."
            if sub == "branch" and any(
                r in ("-D", "--delete") or r == "-d" for r in rest
            ):
                return "Blocked: deleting branches is the user's call."
        if (
            name == "docker"
            and "compose" in tokens
            and "down" in tokens
            and ("-v" in tokens or "--volumes" in tokens)
        ):
            return "Blocked: docker compose down -v deletes the database volume."
        if (
            name == "docker"
            and "volume" in tokens
            and ("rm" in tokens or "prune" in tokens)
        ):
            return "Blocked: removing Docker volumes deletes data."
        if "alembic" in tokens and "downgrade" in tokens and not _scratch(command):
            return "Blocked: alembic downgrade on the real database. Use the scratch DB, or ask the user."
    return None


def _scratch(command: str) -> bool:
    return "fitment_check" in command


if __name__ == "__main__":
    reason = check(bash_command(read_input()))
    if reason:
        block(reason)
