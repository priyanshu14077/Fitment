# 0018. Claude Code harness: rules, permissions, hooks, skills, reviewer

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, harness rounds 1–3

## Context

The harness is committed and mentioned in the README, so guardrails are part of the work being shown. A previous project drifted because the same facts were copied into several agent files.

## Decision

- `CLAUDE.md` is the single source of truth; `AGENTS.md`, skills and the reviewer point to it. Claude Code is the only agent targeted.
- `.claude/settings.json` holds allow, ask and deny lists matching CLAUDE.md § Autonomy.
- Hooks in `.claude/hooks/`, Python standard library, each tested:
  - PreToolUse: block commits and pushes on `master`, destructive commands, autogenerate, edits to merged migrations, and access to secret files.
  - PostToolUse: ruff on Python edits, Biome on TypeScript edits, secret scan on written files, OpenAPI drift after route edits, `EXPLAIN` warning after repo query edits.
  - Stop: tests for changed files, 30 second limit.
  - SessionStart: branch, stack status, migration version, saved progress.
  - PreCompact: save the current branch and step to `.claude/state/`.
- Skills: `run-stack`, `new-migration`, `new-endpoint`, `regen-sdk`, `refresh-vpic`, `loadtest`, `explain-step`.
- One subagent, `contract-reviewer`: reports violations and suggestions to the user or the main agent, never edits.

## Consequences

Hooks that depend on tools not installed yet (Biome, gitleaks) or code not written yet (spec export) skip quietly until those exist. Hooks are a second layer behind permissions, not a replacement.
