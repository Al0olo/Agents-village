# Agent instructions

**Scope:** `harness/src/agent_village`. The `agent_village` package. `admission.py` is the reference implementation of the RQ1 kernel admission policy. `eventlog.py` is the append-only, hash-chained JSONL event log.

Changes to `admission.py` change the experimental treatment: update the tests, note it in the pre-registration, and never do it after runs start.

The canonical hash format in `eventlog.py` is pinned by a test vector. Changing it invalidates every recorded log, so it needs an ADR.

Repository-wide rules are in the root [AGENTS.md](/AGENTS.md); they apply here too.
