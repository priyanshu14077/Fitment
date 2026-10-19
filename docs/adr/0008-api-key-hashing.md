# 0008. API keys stored as SHA-256 hashes

- Status: Accepted
- Date: 2026-10-19
- Decided by: Priyanshu Kumar, design rounds 1–2 (Q4, Q5)

## Context

A leaked database must not yield usable keys, and key checks run on every request.

## Decision

Key format `fk_live_<key_id>_<secret>`. `key_id` is stored in plain text for an indexed lookup; only SHA-256 of the secret is stored, compared with `hmac.compare_digest`. SHA-256 rather than bcrypt or argon2: the secret is 32+ random bytes, so brute force is already infeasible and a slow hash would only add latency. The full key is shown once at creation. Keys are managed by admin endpoints (`POST/DELETE /v1/admin/keys`, admin token) and a CLI. Rotation issues a new key and keeps the old one valid for 24 hours. Plans: `free` 5 req/s burst 10, `pro` 50 req/s burst 100.

## Consequences

Lost keys cannot be recovered, only rotated. This is hashing, not encryption: it cannot be reversed.
