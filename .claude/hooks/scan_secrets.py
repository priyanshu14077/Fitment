"""PostToolUse(Edit|Write|MultiEdit): look for secrets in a file the agent
just wrote. Uses gitleaks when installed, plus built-in patterns either way."""

import re
import shutil
import subprocess

from _common import edited_path, read_input, warn

PATTERNS = {
    "Fitment API key": re.compile(
        r"\bfk_(live|test)_[A-Za-z0-9]{6,}_[A-Za-z0-9_-]{16,}"
    ),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "Anthropic key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "credential URL": re.compile(r"\b[a-z+]+://[^\s:/@]+:(?!fitment@)[^\s@]{8,}@"),
}


def scan(text: str) -> list[str]:
    return [name for name, pattern in PATTERNS.items() if pattern.search(text)]


def main() -> None:
    path = edited_path(read_input())
    if not path or not path.is_file():
        return
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        return
    found = scan(text)
    if shutil.which("gitleaks"):
        result = subprocess.run(
            ["gitleaks", "detect", "--no-git", "--no-banner", "--source", str(path)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 1:
            found.append("gitleaks finding")
    if found:
        warn(
            f"Possible secret in {path.name}: {', '.join(found)}. Remove it, put the name in "
            ".env.example, and read the value from settings."
        )


if __name__ == "__main__":
    main()
