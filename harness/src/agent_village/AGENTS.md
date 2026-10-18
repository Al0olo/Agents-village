# Agent instructions

**Scope:** `harness/src/agent_village`. The `agent_village` package. `admission.py` is the reference implementation of the RQ1 kernel admission policy. `eventlog.py` is the append-only, hash-chained JSONL event log. `village.py` holds village state and the deterministic wake scheduler: time, randomness and the log are injected, and every state change is an event.

Model calls go through `Model`, which logs the served snapshot and routed provider; a backend that cannot name the provider raises instead. Never enable provider fallbacks, and never read an API key inside the package: pass a transport in.

Memory writes go through `Memory.write_claim` with an injected policy. Evidence is only log events of kind `saw`, `did` and `told` (with `origins`); a new evidence kind needs a test that it cannot be forged, and the declared kind of a claim is never trusted.

Messages go through `Messenger`. Origins only grow along a forward, and a message never goes to one of its own origins; do not add a path that writes a `told` event any other way.

The prompt text in `prompts.py` and the rendering in `runner.py` (`_render`) are part of the treatment, like `admission.py`: a change needs a new prompt version, an updated pinned-prompt test and a note in the pre-registration, and never happens after runs start. Acting is not evidence: do not log `did` events for messages or memory writes, or a citizen could back a claim by having said it. A model error must stop the run, not be retried silently.

Changes to `admission.py` change the experimental treatment: update the tests, note it in the pre-registration, and never do it after runs start.

The canonical hash format in `eventlog.py` is pinned by a test vector. Changing it invalidates every recorded log, so it needs an ADR.

Repository-wide rules are in the root [AGENTS.md](/AGENTS.md); they apply here too.
