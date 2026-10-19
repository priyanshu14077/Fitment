# Contributing

This covers the git workflow. Code rules and commands live in [`CLAUDE.md`](CLAUDE.md); design decisions live in [`docs/adr/`](docs/adr/).

## Branches

`master` is always green. Nothing is committed to it directly; every change arrives through a PR.

| Prefix | Use | Branches from | Example |
|---|---|---|---|
| `day-N/` | the five build days | `master` | `day-1/schema` |
| `feat/` | new capability after day 5 | `master` | `feat/part-images` |
| `fix/` | a bug fix on the normal schedule | `master` | `fix/ratelimit-reset-header` |
| `hotfix/` | an urgent fix to a released version | the latest `api-v*` tag | `hotfix/key-lookup-timing` |
| `chore/` | tooling, CI, dependencies | `master` | `chore/ci` |
| `docs/` | README, ADRs, diagrams | `master` | `docs/architecture-diagram` |
| `data/` | a vPIC snapshot refresh | `master` | `data/vpic-2026-11-02` |

Names are lowercase, hyphenated, and say what the branch does.

## Commits

Granular [Conventional Commits](https://www.conventionalcommits.org/): one logical step per commit, each one building and passing tests on its own.

```
<type>(<scope>): <imperative summary, under 72 characters>

<optional body: why, not what>
```

Types: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `chore`, `ci`, `build`. Scopes follow the area: `api`, `db`, `ratelimit`, `metering`, `keys`, `sdk`, `demo`, `data`, `ci`, `claude`. A breaking change adds `!` after the scope and a `BREAKING CHANGE:` footer.

Before opening a PR, tidy the branch: squash "fix typo" commits into the commit they fix (lazygit: select the commit, `f` to fixup, or `s` to squash). CI lints every commit message, not only the PR title.

## Pull requests

- Fill in [`.github/pull_request_template.md`](.github/pull_request_template.md), including a mermaid diagram of the changed flow. CI posts test coverage and the oasdiff contract result as comments.
- Link the ADR behind any design change in the "Why" section.
- The `contract-reviewer` agent runs before the PR is opened. Its report goes into the PR conversation.
- Merge with **rebase-merge** so every commit lands on `master` in order and `git log` reads as the build history.

## Releases

The API and the SDK are versioned separately with SemVer tags:

- `api-vMAJOR.MINOR.PATCH`: the service. A major bump means a new URL version (`/v2`) and an ADR.
- `sdk-vMAJOR.MINOR.PATCH`: the TypeScript client. Its major version tracks the API major it targets.

Tagging a release builds the Docker image and pushes it to GHCR, and attaches the SDK build to a GitHub Release. Nothing is published to npm.

## Hotfixes

1. `git switch -c hotfix/<topic> api-v1.4.0` from the tag in production.
2. Fix with a test that fails before the fix.
3. PR to `master`; after merge, tag `api-v1.4.1`.

## Branch protection on `master`

Enabled once CI exists (`chore/ci`):

- require a pull request
- require the CI checks listed in `CLAUDE.md` to pass
- require linear history (rebase-merge only)
- block force-pushes and deletion

## Horizon

Planned beyond the five days, in rough order. Each becomes an ADR before it becomes a branch.

- Load the vPIC standalone Postgres dump to source real trims and engines (replaces synthetic templates).
- `/v1/parts/{id}/vehicles`: reverse fitment, "what does this part fit?"
- Usage pipeline: durable event log and reconciled billing totals in place of Redis counter flushes.
- Partition `fitment` by `make_id`, or precompute a flattened `vehicle_part` table, once rows reach the millions.
- Key scopes (read-only, batch) and per-endpoint limits.
- Hosted demo.
