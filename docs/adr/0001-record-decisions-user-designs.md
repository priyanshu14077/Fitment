# 0001. Record decisions as ADRs; the user designs, the agent implements

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, harness planning rounds 1–3 (Q3, R1, S3, S4)

## Context

The project is built with Claude Code. The user wants to own the architecture and data flow, learn the codebase while it is built, and be able to show which decisions were theirs.

## Decision

The user makes every architecture and data-flow decision. The agent implements, and stops to ask before deciding anything on the list in `CLAUDE.md` § Roles. Each decision is recorded here as an ADR, committed, and linked from the PR that implements it. The planning rounds of 2026-10-19 are recorded as ADRs 0002–0018.

## Consequences

Design changes are slower to start, because they wait on the user. In exchange, the reasoning behind each choice survives and is reviewable. ADRs are never edited after acceptance except to mark them superseded.
