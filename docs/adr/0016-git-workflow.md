# 0016. Branch prefixes, granular conventional commits, rebase-merge

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, harness rounds 1–3 (Q4, R2, S1, S2)

## Decision

Branch prefixes `day-N/`, `feat/`, `fix/`, `hotfix/`, `chore/`, `docs/`, `data/`. Granular conventional commits, tidied with lazygit before a PR. PRs are rebase-merged so `master`'s log is the build history. Releases are tagged `api-vX.Y.Z` and `sdk-vX.Y.Z` independently. PR descriptions follow the template with a mermaid diagram; coverage and the oasdiff result are posted by CI. Details in `CONTRIBUTING.md`.

## Consequences

Every commit on `master` must stand alone, so CI lints each commit message. Direct commits to `master` are blocked by a hook.
