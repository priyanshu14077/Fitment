"""PostToolUse(Edit|Write|MultiEdit): after a route or schema edit, regenerate
the OpenAPI spec and report whether the committed file changed (ADR 0012).
Skips until the spec exporter exists (day 2)."""

import subprocess

from _common import edited_path, git, project_dir, read_input, warn

WATCHED = ("api/src/fitment/routes/", "api/src/fitment/schemas/")
EXPORTER = "api/src/fitment/openapi.py"
SPEC = "api/openapi/v1.json"


def main() -> None:
    payload = read_input()
    path = edited_path(payload)
    root = project_dir(payload)
    if not path or not (root / EXPORTER).exists():
        return
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return
    if not rel.startswith(WATCHED):
        return
    result = subprocess.run(
        [
            "uv",
            "run",
            "--quiet",
            "--project",
            str(root / "api"),
            "python",
            "-m",
            "fitment.openapi",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        warn(
            f"OpenAPI export failed after editing {rel}:\n{result.stderr.strip()[-2000:]}"
        )
    if git(root, "diff", "--quiet", "--", SPEC).returncode != 0:
        warn(
            f"{SPEC} changed after editing {rel}. Review the diff: an additive change is fine on /v1, "
            "a removed or renamed field is a breaking change and needs an ADR. Regenerate the SDK (skill regen-sdk)."
        )


if __name__ == "__main__":
    main()
