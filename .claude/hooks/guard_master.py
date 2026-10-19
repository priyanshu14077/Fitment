"""PreToolUse(Bash): no commits or pushes on master. Changes reach master
through a pull request (CONTRIBUTING.md)."""

from _common import (
    bash_command,
    block,
    current_branch,
    git_subcommand,
    project_dir,
    read_input,
    segments,
)

PROTECTED = "master"


def check(command: str, branch: str) -> str | None:
    for tokens in segments(command):
        parsed = git_subcommand(tokens)
        if not parsed:
            continue
        sub, rest = parsed
        if sub == "commit" and branch == PROTECTED:
            return f"Blocked: committing on {PROTECTED}. Create a branch (day-N/, feat/, fix/, chore/ ...) first."
        if sub == "push":
            targets = [arg.split(":")[-1] for arg in rest if not arg.startswith("-")][
                1:
            ]
            if PROTECTED in targets or f"refs/heads/{PROTECTED}" in targets:
                return (
                    f"Blocked: pushing to {PROTECTED}. Push your branch and open a PR."
                )
            if branch == PROTECTED and (not targets or "HEAD" in targets):
                return f"Blocked: pushing from {PROTECTED}. Push your branch and open a PR."
    return None


if __name__ == "__main__":
    payload = read_input()
    reason = check(bash_command(payload), current_branch(project_dir(payload)))
    if reason:
        block(reason)
