# 0019. Enable the ponytail plugin; CLAUDE.md takes precedence

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, after the harness merge

## Context

The user wants the agent to prefer the smallest working solution. `ponytail` (github.com/DietrichGebert/ponytail, MIT, v5.3.2 on 2026-10-19) does this by injecting instructions on SessionStart, SubagentStart and UserPromptSubmit. It registers no PreToolUse or PostToolUse hooks, so it does not interact with this repo's guards. It writes a per-task ledger to `~/.config/ponytail/`; its optional webhook is empty by default, so nothing leaves the machine.

## Decision

Register the marketplace and enable `ponytail@ponytail` in `.claude/settings.json` so everyone who opens the repo gets it. Where ponytail's "write less" guidance conflicts with `CLAUDE.md` (ADRs, tests, reversible migrations, declared error responses, stop-and-ask), `CLAUDE.md` wins.

## Consequences

Implementations lean smaller. The webhook stays unset; setting one is a decision for the user, because it sends task names and token counts to a third party.
