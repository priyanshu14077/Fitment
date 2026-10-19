---
name: refresh-vpic
description: Guide the user through refreshing the vPIC makes and models snapshot and judging the diff. Use only when the user asks to refresh vehicle data.
---

# refresh-vpic

Rules: ADR 0003 and `CLAUDE.md` § Hard rules 7. The snapshot calls an external API, so the user runs it. There is no scheduled refresh.

1. Branch: `git switch -c data/vpic-$(date +%F)`.
2. Ask the user to run `uv run --project api python scripts/snapshot_vpic.py` (the permission prompt will ask too).
3. Diff old and new: makes and models added and removed, and changed `source_version`. Show counts and a few examples.
4. Removed models matter: list the fitment rows and vehicles that reference them. Whether to keep, remap or drop them is the user's decision.
5. Reseed the scratch DB from the new snapshot and run the test suite.
6. Commit `chore(data): refresh vPIC snapshot <date>` with the diff summary in the body.
