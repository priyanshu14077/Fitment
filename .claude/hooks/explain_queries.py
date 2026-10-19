"""PostToolUse(Edit|Write|MultiEdit): after a repo/ edit, EXPLAIN each text()
query against the local database and warn on sequential scans. Warns only;
a small or empty table can make a seq scan the right plan."""

import ast
import json
import re
import subprocess

from _common import edited_path, project_dir, read_input, warn

REPO = "api/src/fitment/repo/"
CONTAINER = "fitment-db"


def queries(source: str) -> list[tuple[int, str]]:
    found = []
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Call)
            and getattr(node.func, "id", getattr(node.func, "attr", None)) == "text"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            found.append((node.lineno, node.args[0].value))
    return found


def to_positional(sql: str) -> str:
    """:name binds become $1, $2 ... so Postgres 16+ can plan with GENERIC_PLAN."""
    names: dict[str, int] = {}

    def sub(match: re.Match) -> str:
        return f"${names.setdefault(match.group(1), len(names) + 1)}"

    return re.sub(r"(?<!:):([A-Za-z_]\w*)", sub, sql)


def seq_scans(plan: dict) -> list[str]:
    hits = []
    if plan.get("Node Type") == "Seq Scan":
        hits.append(plan.get("Relation Name", "?"))
    for child in plan.get("Plans", []):
        hits.extend(seq_scans(child))
    return hits


def explain(sql: str) -> list[str] | str:
    statement = (
        f"EXPLAIN (GENERIC_PLAN, FORMAT JSON) {to_positional(sql).strip().rstrip(';')}"
    )
    result = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            CONTAINER,
            "psql",
            "-U",
            "fitment",
            "-d",
            "fitment",
            "-XAt",
            "-v",
            "ON_ERROR_STOP=1",
        ],
        input=statement,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        return (
            result.stderr.strip().splitlines()[0]
            if result.stderr.strip()
            else "EXPLAIN failed"
        )
    return seq_scans(json.loads(result.stdout)[0]["Plan"])


def main() -> None:
    payload = read_input()
    path = edited_path(payload)
    root = project_dir(payload)
    if not path or path.suffix != ".py" or not path.exists():
        return
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return
    if not rel.startswith(REPO):
        return
    try:
        found = queries(path.read_text())
    except SyntaxError:
        return
    notes = []
    for line, sql in found:
        if not sql.lstrip().upper().startswith(("SELECT", "WITH", "UPDATE", "DELETE")):
            continue
        try:
            outcome = explain(sql)
        except (subprocess.SubprocessError, FileNotFoundError, ValueError, KeyError):
            return  # database not running; nothing to report
        if isinstance(outcome, str):
            notes.append(f"line {line}: EXPLAIN error: {outcome}")
        elif outcome:
            notes.append(f"line {line}: sequential scan on {', '.join(outcome)}")
    if notes:
        warn(
            f"EXPLAIN on {rel} (warning only; check row counts before acting):\n"
            + "\n".join(notes)
        )


if __name__ == "__main__":
    main()
