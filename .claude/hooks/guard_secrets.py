"""PreToolUse(Read|Edit|Write|MultiEdit|Bash): keep secret files out of the
agent's context. .env.example is allowed; it holds names, not values."""

import re
import shlex
from pathlib import Path

from _common import bash_command, block, edited_path, read_input

ALLOWED = {".env.example"}
SECRET_FILE = re.compile(r"(^|/)(\.env(\.[\w-]+)?|[\w.-]+\.(pem|key|p12))$")
PROSE_FLAGS = {"-m", "--message"}
PROSE_COMMANDS = {"echo", "printf"}
SEPARATORS = {"&&", "||", ";", "|", "&"}


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
    """Words the shell could treat as file paths. Quoted phrases are split and
    checked too (bash -c "cat <file>"), except prose: a commit message after
    -m/--message, or text given to echo/printf. --opt=<path> is split so the
    path is still checked."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        words = list(lexer)
    except ValueError:
        words = command.split()
    result = []
    for i, word in enumerate(words):
        if any(c.isspace() for c in word):
            previous = words[i - 1] if i else ""
            if previous in PROSE_FLAGS or _in_prose_command(words, i):
                continue
            result.extend(shell_words(word))
        else:
            result.append(word.rsplit("=", 1)[-1])
    return result


def _in_prose_command(words: list[str], i: int) -> bool:
    """True when words[i] is an argument of echo or printf."""
    for j in range(i - 1, -1, -1):
        if words[j] in SEPARATORS:
            return False
        if words[j] in PROSE_COMMANDS and (j == 0 or words[j - 1] in SEPARATORS):
            return True
    return False


if __name__ == "__main__":
    reason = check(read_input())
    if reason:
        block(reason)
