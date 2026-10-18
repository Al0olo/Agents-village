# agent_village

The `agent_village` package. `admission.py` is the reference implementation of the RQ1 kernel admission policy. `eventlog.py` is the append-only, hash-chained JSONL event log. `village.py` holds village state and the deterministic wake scheduler. `model.py` is the model interface with fake and recorded backends, and `openrouter.py` the live backend. `memory.py` holds the memory tiers and structured claim writes. `messages.py` delivers messages and forwards with origin tracking. `actions.py` parses a model reply into an action, `prompts.py` holds versioned system prompts, and `runner.py` is the citizen loop. `fork.py` takes snapshots between ticks and forks a village into arms. `arms.py` defines the arms: a memory policy plus a prompt. `launch.py` launches every arm from one snapshot and runs them in lockstep.

See the repository [README](/README.md) for the project overview.
