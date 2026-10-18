# agent_village

The `agent_village` package. `admission.py` is the reference implementation of the RQ1 kernel admission policy. `eventlog.py` is the append-only, hash-chained JSONL event log. `village.py` holds village state and the deterministic wake scheduler. `model.py` is the model interface with fake and recorded backends, and `openrouter.py` the live backend. `memory.py` holds the memory tiers and structured claim writes.

See the repository [README](/README.md) for the project overview.
