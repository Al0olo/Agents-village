# Agent instructions

**Scope:** `crates/village-kernel`. Citizen actors, mailboxes, the scheduler and the append-only event log. Scaffold; milestone M1 fills it in.

The event log is the single source of truth. Every perception, tool call and payment is an event. Do not add state that cannot be rebuilt by replaying the log.

Repository-wide rules are in the root [AGENTS.md](/AGENTS.md); they apply here too.
