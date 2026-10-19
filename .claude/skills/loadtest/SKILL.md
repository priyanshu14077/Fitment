---
name: loadtest
description: Run the k6 load test against the local API and record the measured p95 with the hardware. Use when the user asks for latency numbers or before updating the README's performance section.
---

# loadtest

Rules: ADR 0015 and `CLAUDE.md` § Hard rules 9. Available from day 5.

1. `run-stack`, a seeded database, and the API running in its container (not `--reload`).
2. Create a `pro` key for the run so the rate limit does not cap the test.
3. `docker run --rm -i --network host grafana/k6 run - < loadtest/fitment_check.js` (200 req/s for 60 s against `/v1/fitment/check`).
4. Record p50, p95, p99, error rate and throughput, plus the machine (`sysctl -n machdep.cpu.brand_string`, memory) and the row counts.
5. Put the numbers in the README exactly as measured, with the date. If p95 is above 50 ms, say so and propose causes from `EXPLAIN ANALYZE`; do not tune the test to pass.
