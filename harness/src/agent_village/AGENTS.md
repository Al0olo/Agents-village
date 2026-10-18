# Agent instructions

**Scope:** `harness/src/agent_village`. The `agent_village` package. `admission.py` is the reference implementation of the RQ1 kernel admission policy. `eventlog.py` is the append-only, hash-chained JSONL event log. `village.py` holds village state and the deterministic wake scheduler: time, randomness and the log are injected, and every state change is an event.

Model calls go through `Model`, which logs the served snapshot and routed provider; a backend that cannot name the provider raises instead. Never enable provider fallbacks, and never read an API key inside the package: pass a transport in.

Memory writes go through `Memory.write_claim` with an injected policy. Evidence is only log events of kind `saw`, `did` and `told` (with `origins`); a new evidence kind needs a test that it cannot be forged, and the declared kind of a claim is never trusted.

Changes to `admission.py` change the experimental treatment: update the tests, note it in the pre-registration, and never do it after runs start.

The canonical hash format in `eventlog.py` is pinned by a test vector. Changing it invalidates every recorded log, so it needs an ADR.

Repository-wide rules are in the root [AGENTS.md](/AGENTS.md); they apply here too.
