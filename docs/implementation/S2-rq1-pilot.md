# S2 — RQ1 pilot and pre-registration (implementation audit)

**Source of intent:** [`docs/sprints/S2-rq1-pilot.md`](../sprints/S2-rq1-pilot.md)  
**Status:** 🚧 Preparation under way: the pre-registration draft, the analysis library, the gateway and the block runner exist; the pilot has not run.

## Ticket status

Legend: ✅ done · 🟡 partial · 🚧 in progress or blocked · ⏸ deferred · ⏳ not started

| # | Title | Status | Notes |
| --- | --- | --- | --- |
| T1 | Draft `experiments/rq1-provenance/PREREGISTRATION.md` from the experiment-design checklist | 🟡 | Draft 1 is committed. Parameters the pilot sets (blocks, margin, the prompt arm, arm E's rate, kappa threshold) are marked *pilot*, with the rule for each. Not frozen and not filed on OSF (needs an account). |
| T2 | Analysis code: paired within-block differences, exact permutation test, effect sizes with intervals, Holm correction | 🟡 | `harness/src/agent_village/analysis.py`, tests `test_analysis.py`: `paired_differences`, `sign_flip_test` (exact up to 40 blocks by meeting in the middle, two-sided), `p_value` (Monte Carlo beyond that), `cohens_dz`, `bootstrap_interval`, `holm`, `contrast`. `experiments/rq1-provenance/analyze_blocks.py` applies it to finished blocks (per-block table and paired differences from a reference arm, offline from the judge log); the notebook is not written. |
| T3 | Power simulation script parameterized by pilot estimates | 🟡 | `harness/src/agent_village/power.py` (`power`, `blocks_needed`, `sign_flip_p`) and `experiments/rq1-provenance/power_table.py`; tests `test_power.py`. The table in `smoke-2026-10-19/power-table.txt` uses the spread of four exploratory blocks (0.34 for D minus A: about 45 blocks for 15 points); the rule that sets the main run's block count from the pilot and the first eight blocks is in ADR-0014. |
| T4 | Decide and pin the model mix (two frontier, one open-weight); record in the handoff | ✅ | ADR-0009: Opus 5.5, GPT-5.6 Sol, DeepSeek V4 Pro, each pinned to one provider (`anthropic`, `openai`, `deepinfra/fp8`) after an unpinned DeepSeek drifted between providers and the drift check killed three blocks. |
| T5 | Gateway config: OpenRouter routing, snapshot pinning, provider logging, fallback off, hard spend cap and kill switch | 🟡 | `harness/src/agent_village/gateway.py`, tests `test_gateway.py`: cost, per-model and call caps counting calls in flight, a kill file that latches, wrapped in `Retrying`; `experiments/rq1-provenance/run_block.py` checks the credit left on the key and the account before it starts. The infrastructure-level budget alarm and kill switch are T14. A live run was cut off by an exhausted account (HTTP 402), which no cap in the harness can prevent. |
| T6 | Run the pilot: 2 blocks, 5 arms, 8 citizens, 3 days | ⏳ | |
| T7 | Judge reliability: blinded judge against human-coded sample | 🟡 | Two judge models agree at kappa 0.83 on 612 answers of one block. A stratified blind sample of 85 answers was coded by Claude, not a human: kappa 0.82 against the primary judge and 0.80 against the second on 80 fact answers (the awareness sample was five answers). Disagreement was between hedges and denies when an answer relays a claim and calls it implausible. A human sample is still owed. |
| T8 | Estimate variance and fork correlation; recompute power; set block count | ⏳ | |
| T9 | Pilot report in `experiments/rq1-provenance/pilot/` | ⏳ | |
| T10 | Owner review, then OSF registration | ⏳ | |
| T11 | Canary string and log release plan | 🟡 | `experiments/rq1-provenance/LOG-RELEASE.md` holds the canary string and the plan; no archive has been made. |
| T12 | Awareness probe calibration | 🟡 | The funnel and `judge-awareness-2` are in (ADR-0008); the replication across blocks was cut off by a credit limit. |
| T13 | Confirm ADR-0002; infra skeleton and remote state | ⏳ | |
| T14 | Object storage, secrets, budget alarms, spend kill switch | ⏳ | |
| T15 | Batch runner for all arms of a block | ⏳ | |
| T16 | OIDC deploys; egress allow-list | ⏳ | |
| T17 | Harness Dockerfile and image | ⏳ | |
