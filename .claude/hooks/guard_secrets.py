"""PreToolUse(Read|Edit|Write|MultiEdit|Bash): keep secret files out of the
agent's context. .env.example is allowed; it holds names, not values."""

import re
import shlex
from pathlib import Path

from _common import bash_command, block, edited_path, read_input

ALLOWED = {".env.example"}
SECRET_FILE = re.compile(r"(^|/)(\.env(\.[\w-]+)?|[\w.-]+\.(pem|key|p12))$")


def is_secret(path: str) -> bool:
    return Path(path).name not in ALLOWED and bool(SECRET_FILE.search(path))


def check(payload: dict) -> str | None:
    path = edited_path(payload)
    if path and is_secret(str(path)):
        return f"Blocked: {path.name} holds secrets. Agents never read or write it; add names to .env.example."
    for word in shell_words(bash_command(payload)):
        if is_secret(word):
            return f"Blocked: command touches {Path(word).name}. Agents never read secret files."
    return None


def shell_words(command: str) -> list[str]:
    """Words the shell would pass as arguments. A quoted phrase such as a
    commit message stays one word, so mentioning a secret file in prose is
    allowed; --opt=<path> is split so the path is still checked."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        words = list(lexer)
    except ValueError:
        words = command.split()
    return [
        word.rsplit("=", 1)[-1] for word in words if not any(c.isspace() for c in word)
    ]


if __name__ == "__main__":
    reason = check(read_input())
    if reason:
        block(reason)
