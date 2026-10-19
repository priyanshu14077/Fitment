from conftest import run_hook


def test_session_status_reports_branch(repo):
    result = run_hook("session_status.py", {"cwd": str(repo)}, repo)
    assert result.returncode == 0
    assert "Branch: master" in result.stdout


def test_save_progress_writes_note(repo):
    result = run_hook("save_progress.py", {"cwd": str(repo), "trigger": "auto"}, repo)
    assert result.returncode == 0
    note = (repo / ".claude" / "state" / "progress.md").read_text()
    assert "Branch: master" in note and "auto compaction" in note
