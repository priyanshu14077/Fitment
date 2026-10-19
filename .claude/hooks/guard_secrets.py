"""PreToolUse(Read|Edit|Write|MultiEdit|Bash): keep secret files out of the
agent's context. .env.example is allowed; it holds names, not values."""

import re
from pathlib import Path

from _common import bash_command, block, edited_path, read_input

ALLOWED = {".env.example"}
SECRET_FILE = re.compile(r"(^|/)(\.env(\.[\w-]+)?|[\w.-]+\.(pem|key|p12))$")
SECRET_IN_COMMAND = re.compile(
    r"(^|[\s/'\"=<])(\.env(\.[\w-]+)?|[\w.-]+\.(pem|key|p12))(?=$|[\s'\";|&>)])"
)


def is_secret(path: str) -> bool:
    return Path(path).name not in ALLOWED and bool(SECRET_FILE.search(path))


def check(payload: dict) -> str | None:
    path = edited_path(payload)
    if path and is_secret(str(path)):
        return f"Blocked: {path.name} holds secrets. Agents never read or write it; add names to .env.example."
    command = bash_command(payload)
    for match in SECRET_IN_COMMAND.finditer(command):
        if match.group(2) not in ALLOWED:
            return f"Blocked: command touches {match.group(2)}. Agents never read secret files."
    return None


if __name__ == "__main__":
    reason = check(read_input())
    if reason:
        block(reason)
