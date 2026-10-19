---
name: explain-step
description: Hand a finished step to the user in the teaching format. Use at the end of every implementation step.
---

# explain-step

The user is learning the codebase as it is built (`CLAUDE.md` § Teaching format). End each step with these sections, in this order:

1. **What changed**: files, one line each.
2. **Why**: the reason for each non-obvious line or choice, linked to its ADR. Explain terms the first time they appear.
3. **How it connects**: a small ASCII or mermaid diagram when the step adds or changes a flow between services or modules.
4. **Your turn**: the exact commands for the user to run, one per line, each with a comment saying what it shows.
5. **Expect**: the output each command should print, or its key line.
6. **Next**: the next step, and any decision the user needs to make before it.

Never report a number (latency, coverage, row count) you did not measure in this session.
