import subprocess

from guard_migrations import check


def test_blocks_merged_migration_allows_new(repo):
    versions = repo / "api" / "migrations" / "versions"
    versions.mkdir(parents=True)
    merged = versions / "0001_catalog.py"
    merged.write_text("x = 1\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "m"], cwd=repo, check=True)

    def payload(path):
        return {"cwd": str(repo), "tool_input": {"file_path": str(path)}}

    assert check(payload(merged))
    assert check(payload(versions / "0002_platform.py")) is None
    assert check(payload(repo / "api" / "src" / "x.py")) is None
