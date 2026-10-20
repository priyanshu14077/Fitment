"""Shared helpers for Claude Code hooks. Standard library only.

A hook reads one JSON object from stdin. Exit 0 lets the tool call proceed;
exit 2 blocks it (PreToolUse) or reports a problem (PostToolUse, Stop), and
stderr is shown to the agent.
"""

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path


def read_input() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def project_dir(payload: dict) -> Path:
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    return Path(root)


def block(reason: str) -> None:
    print(reason, file=sys.stderr)
    sys.exit(2)


def warn(message: str) -> None:
    """Report to the agent after a tool ran, without undoing anything."""
    print(message, file=sys.stderr)
    sys.exit(2)


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=root, check=False, capture_output=True, text=True
    )


def current_branch(root: Path) -> str:
    return git(root, "branch", "--show-current").stdout.strip()


def bash_command(payload: dict) -> str:
    return payload.get("tool_input", {}).get("command", "") or ""


def edited_path(payload: dict) -> Path | None:
    tool_input = payload.get("tool_input", {})
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    return Path(path) if path else None


def segments(command: str) -> list[list[str]]:
    """Split a shell command on && || ; | into token lists, so that each
    simple command can be checked on its own."""
    parts = re.split(r"&&|\|\||;|\|", command)
    result = []
    for part in parts:
        try:
            tokens = shlex.split(part)
        except ValueError:
            tokens = part.split()
        # Drop leading VAR=value assignments.
        while tokens and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
            tokens.pop(0)
        if tokens:
            result.append(tokens)
    return result


def git_subcommand(tokens: list[str]) -> tuple[str, list[str]] | None:
    """Return (subcommand, rest) for a git invocation, skipping global
    options such as -C <dir> or -c key=value."""
    if not tokens or Path(tokens[0]).name != "git":
        return None
    i = 1
    while i < len(tokens) and tokens[i].startswith("-"):
        i += 2 if tokens[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
    if i >= len(tokens):
        return None
    return tokens[i], tokens[i + 1 :]
