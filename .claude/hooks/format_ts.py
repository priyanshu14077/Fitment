"""PostToolUse(Edit|Write|MultiEdit): Biome format on edited TypeScript and
JavaScript. Skips quietly until Biome is installed in the pnpm workspace."""

import subprocess

from _common import edited_path, project_dir, read_input, warn

SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}


def main() -> None:
    payload = read_input()
    path = edited_path(payload)
    if not path or path.suffix not in SUFFIXES or not path.exists():
        return
    root = project_dir(payload)
    biome = root / "node_modules" / ".bin" / "biome"
    if not biome.exists():
        return
    result = subprocess.run(
        [str(biome), "check", "--write", str(path)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        warn(
            f"Biome found issues in {path.name}:\n{(result.stdout or result.stderr).strip()[-2000:]}"
        )


if __name__ == "__main__":
    main()
