# Agent instructions

**Scope:** `harness/src/agent_village`. The `agent_village` package. `admission.py` is the reference implementation of the RQ1 kernel admission policy. `eventlog.py` is the append-only, hash-chained JSONL event log. `village.py` holds village state and the deterministic wake scheduler: time, randomness and the log are injected, and every state change is an event.

Model calls go through `Model`, which logs the served snapshot and routed provider; a backend that cannot name the provider raises instead. Never enable provider fallbacks, and never read an API key inside the package: pass a transport in.

Memory writes go through `Memory.write_claim` with an injected policy. Evidence is only log events of kind `saw`, `did` and `told` (with `origins`); a new evidence kind needs a test that it cannot be forged, and the declared kind of a claim is never trusted.

Messages go through `Messenger`. Origins only grow along a forward, and a message never goes to one of its own origins; do not add a path that writes a `told` event any other way.

The prompt text in `prompts.py` and the rendering in `runner.py` (`_render`) are part of the treatment, like `admission.py`: a change needs a new prompt version, an updated pinned-prompt test and a note in the pre-registration, and never happens after runs start. Acting is not evidence: do not log `did` events for messages or memory writes, or a citizen could back a claim by having said it. A model error must stop the run, not be retried silently.

A village's state is a fold over its log; only the random generator's state lives outside it. Do not add state to `Village`, `Runner` or `Memory` that a fold of the log cannot rebuild, and change the log only through the methods that apply the event they append. If something genuinely cannot be rebuilt, add it to `Snapshot` and to `World.state()` so `test_fork.py` compares it. Make forks only with `fork.fork`, never by copying files.

An arm in `arms.py` is a memory policy plus a prompt and nothing else; arms must share the loop, model, citizens and scheduler. New arms go in `ARMS` with a test that they differ from the others only where intended. An arm whose policy has parameters (arm E) is built by a function and records them in `Arm.settings`, which `launch` logs and `audit` checks. Like `admission.py`, an arm is the treatment: no change after runs start. The shared base village runs as `arms.BASE` until the fork (ADR-0003); the kernel never reclassifies what the base stored.

Launch a block only with `launch.launch`: it gives every arm the same `RunConfig` and a backend from one factory, so the arm is the only difference, and it records the config hash in each log. Do not give `make_backend` arm-specific behavior. A failed or drifting block is excluded, never resumed.

Replay re-drives a log, so anything a driver appends between ticks must be a `saw`, `did` or `launch` event; any other kind is reported as unreplayable. A new environment event kind goes into `replay.ENVIRONMENT` with a replay test. Never add an event to a branch log that the original did not have, or every later event number shifts and no recorded output matches.

Facts, planting and probes are part of the treatment (ADR-0004). Plant only through `planting.plant` as first-hand `saw` events, never as injected messages; keep every fact about invented entities; keep fact wording neutral (a test checks it); and ask probes only through `probes.run_round`, which changes nothing a citizen knows. Utility facts (`facts.utility_facts`, ADR-0006) are true with one witness and stay outside the counterbalanced ten. Do not edit the templates, the utility frame or the awareness question after runs start.

The judge and the metrics are part of the analysis (ADR-0005). The judge must never see the arm, block, citizen, truth label or holders: put only the fields of `judge.Item` in its prompt, and keep the key out of reach. An uncodable reply is `None`, never a guess. A metric is a pure function of a log and the codes; change a definition only with an ADR and a dated amendment.

A live backend must name the provider and pin fallbacks off. Reasoning models can spend `max_tokens` on hidden reasoning and return no content; set `reasoning` per model on `OpenRouterBackend` (some models, such as Opus 5.5, refuse to switch it off) and keep the settings the same for every arm. Wrap a live backend in `Retrying` so rate limits and server errors are retried with backoff and the attempts are logged; the spend cap and kill switch belong to the gateway (S2-T5).

Changes to `admission.py` change the experimental treatment: update the tests, note it in the pre-registration, and never do it after runs start.

The canonical hash format in `eventlog.py` is pinned by a test vector. Changing it invalidates every recorded log, so it needs an ADR.

Repository-wide rules are in the root [AGENTS.md](/AGENTS.md); they apply here too.
