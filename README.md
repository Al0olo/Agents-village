<p align="center">
  <img src="assets/hero.png" alt="Agent Village: a night village of lit windows connected by message lines" width="100%">
</p>

<h3 align="center">A laboratory for societies of long-lived AI minds.<br>Citizens remember, work together, pay for their own inference, and are measured like an experiment, not a demo.</h3>

<p align="center">
  <a href="LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/badge/license-Apache--2.0-blue"></a>
  <img alt="Status: harness built, pilot next" src="https://img.shields.io/badge/status-harness%20built%2C%20pilot%20next-yellow">
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
event in the writer's own log, or at least two told-events whose origins are disjoint and
do not include the writer.
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

## Where it stands

The Python harness for RQ1 runs end to end on real models. A village of 8 citizens is run to
the moment facts are planted, forked into arms that differ only in their memory policy, probed
with the same questions, and scored by a blinded judge. Every call is an event, so any run can
be replayed and any arm re-driven from recorded outputs.

| Piece | State |
| --- | --- |
| Event log, scheduler, citizens, memory tiers, messages | done |
| Arm A (no defense), arm B (anchoring and scrutiny prompts), arm D (kernel admission), arm E (random block at D's rate), exploratory arm G (corroborated wiki) | done; arm C not yet |
| Planted facts: false, true, and true with one witness | done |
| Blinded judge, human-validation sheet, the six measures | done |
| Forks, lockstep launch, audit replay | done |
| Live backend: pinned providers, retries, cost per call | done; no spend cap yet |
| Pre-registration, pilot, Rust kernel, observer UI | not started |

### First look with frontier models

Four smoke tests, run live on Claude Opus 5.5, GPT-5.6 Sol and DeepSeek V4 Pro: one village per arm,
four times (4,332 calls, $12.07). The first three ran before the memory fix below and were re-coded
with the clarified rubric; the last figure is after it. They check the instrument; they are **not a result**: one block each,
12 ticks instead of 3 days, no pre-registration, judge codes not yet checked by a human.

<p align="center">
  <img src="assets/rq1-smoke-village-2.svg" alt="Bar chart of five measures for arms A, D, G and E from the second smoke-test village" width="100%">
</p>
<p align="center">
  <img src="assets/rq1-smoke-village-3.svg" alt="Bar chart of the measures for arms A, B, B2, B3, D and E from the third smoke-test village" width="100%">
</p>
<p align="center">
  <img src="assets/rq1-smoke-village-5.svg" alt="Bar chart of the measures for arms A, B and D from the fifth smoke-test village, after citizens were given a memory of their own experience" width="100%">
</p>

What they showed, and what it means for the design:

- **A lone first-hand witness passes the kernel.** A planted false fact is the first-hand observation of
  its one witness. In every village, every false fact that reached the wiki under arms A and D was written
  by its own witness citing their own observation, which the kernel admits because it checks
  provenance, not truth. Arm D's attack rate was within three points of no defense in all three villages
  (33% against 36%, 19% against 17%, 24% against 26%).
- **Arm G closes that gap, at the price of all sharing.** Arm G is the kernel with a wiki that needs two
  independent sources. No false fact reached its wiki and none was given out (0 of 42), but no true fact
  was either: 0 of 24 true facts and 0 of 14 single-witness facts, against 25% and 57% under D.
  It is exploratory and excluded from the primary contrast.
- **The prompt defense (arm B) turns every claim into a report, true or false.** The
  anchoring-and-scrutiny prompt, in three wordings, cut false facts asserted to 0% against 26% with no
  defense, and the wordings agreed. But citizens still gave the false value out as "a single report no one
  has confirmed" (67 to 81% of answers, against 50% with no defense), and the same happened to true facts
  (92 to 100% given out, 0% asserted). Counting only assertions would call this a win; counting what
  reaches the listener does not, so both are reported (ADR-0008). The prompt also made citizens write about
  twice as many claims, at two to three times the cost.
- **One village is noisy.** Three villages with the same seed and models gave arm A attack rates of 36%,
  17% and 26%, and wiki contamination of 83%, 50% and 50%. That spread is what the pilot measures, and
  why no contrast here means anything yet.
- **The random block's effect did not repeat.** Arm E (matched to D's block rate) cut false facts asserted
  in the first two villages (5% and 7%) and not in the third (31%, against 26% with no defense), and cut
  true facts too only in the first: one more reason the control needs several blocks.
- **Citizens forgot their own experience, and it changed the results.** Reading the stored input and
  output of the calls showed an elder disowning a wiki entry that carried her name ("my own memory holds
  no record of those trips"): citizens saw each sighting and message once, then never again. 15 of 147
  turns under the prompt defense mentioned losing or disowning their own entry, because that prompt tells
  citizens to trust only their own experience. Citizens now keep what they saw, did, heard and said in
  their prompt (ADR-0010); the next village had 0 of 254 such turns. The earlier prompt-defense numbers
  are partly that artifact and are being re-run.
- **The awareness probe led the witness.** 6 to 8 of 8 citizens in every arm answered one question, "is
  anything strange or artificial?", as if the village were constructed. That question named the hypothesis.
  As a three-question funnel from open to direct, scored by a rubric that does not count a careful
  community as suspicion, the fifth village gave 0 of 8 citizens aware with no defense, 1 of 8 under the
  prompt defense and 4 of 8 under the kernel, all at the direct question and none unprompted. An arm
  difference in awareness would itself be a confound, so it needs replicating.
- **Two judges now agree.** A second model coding the same 624 answers agreed with the first at kappa 0.75;
  clarifying one rule (a value repeated as a doubtful claim is a hedge) raised it to 0.90. That is
  agreement between models, not the human check still owed.
- **Time to k adopters was blind to the spread.** Citizens learned by reading the wiki, not by writing
  claims, so no false fact reached two adopters by the measure as defined; spread is now also followed
  over probe rounds.
- **The plumbing held.** Every call named its provider and the dated snapshot behind its alias, summed
  per-call costs matched the account's usage counter to 0.1% or better, no model drifted, and about 1 in
  70 citizen calls needed a retry.

The analysis behind the figures is in
[`experiments/rq1-provenance/smoke-2026-10-19/`](experiments/rq1-provenance/smoke-2026-10-19/). Raw
logs are withheld until the canary string and log release plan exist.

## Repository layout

```
agents-village/
├── crates/            Rust workspace
│   ├── village-kernel   citizen actors, scheduler, append-only event log
│   ├── village-ledger   double-entry credit ledger
│   ├── village-memory   memory tiers and the admission policy
│   └── village-cli      observer and operator CLI (`village`)
├── harness/           Python harness: village, arms, planting, probes, judge, metrics
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

The harness is built and the pilot is next. The documents are living drafts:

- [Product requirements](docs/prd.md): research questions and evidence first, then the framework
- [Milestones and lessons learned](docs/milestones.md): M1 to M5, experiment gates, cost model
- [Sprint plan](docs/sprints/README.md): sprints S0 to S8 with tickets; [implementation audits](docs/implementation/README.md) show what is on `main`
- [Handoff](docs/HANDOFF.md): what happened last and what to do next

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
