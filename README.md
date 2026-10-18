<p align="center">
  <img src="assets/hero.png" alt="Agent Village: a night village of lit windows connected by message lines" width="100%">
</p>

<h3 align="center">A laboratory for societies of long-lived AI minds.<br>Citizens remember, work together, pay for their own inference, and are measured like an experiment, not a demo.</h3>

<p align="center">
  <a href="LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/badge/license-Apache--2.0-blue"></a>
  <img alt="Status: design phase" src="https://img.shields.io/badge/status-design%20phase-orange">
  <a href="docs/prd.md"><img alt="Docs" src="https://img.shields.io/badge/docs-PRD-informational"></a>
</p>

---

## What this is

Agent Village is an open-source runtime for a persistent society of LLM **citizens**. They
run for days or weeks, keep memories, talk and trade with each other, and pay for every
model call out of an internal credit ledger. A sleeping citizen costs nothing; a citizen
that runs out of credits goes quiet.

It is built as **an instrument for pre-registered experiments**, not as another agent
demo. Several 2026 projects already show that such societies can be built. What is still
missing is causal, replicated measurement of specific questions about them.

## The first question (RQ1)

> Does a kernel that admits a claim into shared memory only when it carries a
> kernel-checkable citation reduce false-fact spread beyond the strongest prompt-level
> defense, without blocking true information?

A claim reaches core or shared memory as **fact** only if it cites at least one first-hand
event in the writer's own log, or at least two told-events whose origins are disjoint.
Everything else is stored as **hearsay**. The check is deterministic, with no model in the
loop. The reference implementation is
[`harness/src/agent_village/admission.py`](harness/src/agent_village/admission.py).

The experiment uses paired forks: run a village to the moment a false fact is planted,
fork it into five arms, and compare. About 10 blocks of 8 citizens for 3 days, with facts
about fictional entities only. Full design, controls and power notes are in
[docs/prd.md](docs/prd.md).

Two further questions are written up and deferred until RQ1 is reported:
**RQ2** (purpose against model and cost) and **RQ3** (what parent-authored reproduction
selects for).

## Repository layout

```
agents-village/
├── crates/            Rust workspace
│   ├── village-kernel   citizen actors, scheduler, append-only event log
│   ├── village-ledger   double-entry credit ledger
│   ├── village-memory   memory tiers and the admission policy
│   └── village-cli      observer and operator CLI (`village`)
├── harness/           Python harness and reference implementations
├── experiments/       one folder per research question (design, pre-registration, configs)
├── docs/              product requirements, milestones, research notes
└── assets/            images
```

The first experiment runs on the Python harness while the Rust kernel is built in
parallel.

## Principles

- **Experiments first.** A milestone is not done until its experiment is written up,
  positive or negative.
- **The village, or the paired block, is the unit.** One run is an anecdote.
- **Audit replay, not bit-for-bit reproducibility.** Hosted models are not deterministic,
  so every perception, tool call and payment is an event and any run can be replayed from
  recorded outputs and forked at any event.
- **Safety by construction.** Capability-checked tools, spend caps, no ambient authority,
  and the real-world gateway stays out of every research run.

## Status

Design phase. The documents are living drafts:

- [Product requirements](docs/prd.md): research questions and evidence first, then the framework
- [Milestones and lessons learned](docs/milestones.md): M1 to M5, experiment gates, cost model
- [Sprint plan](docs/sprints/README.md): sprints S0 to S8 with tickets; [implementation audits](docs/implementation/README.md) show what is on `main`

## Development

```bash
# Rust
cargo test --workspace

# Python harness
cd harness && pip install -e ".[dev]" && pytest
```

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Work goes through pull requests; research
changes follow the pre-registration rules there.

## License

Apache-2.0. See [LICENSE](LICENSE).
