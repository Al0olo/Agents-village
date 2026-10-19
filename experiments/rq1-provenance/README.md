# RQ1: kernel provenance against false-fact spread

**Question.** Does a kernel that admits claims into shared and core memory only when they
carry a kernel-checkable citation reduce false-fact spread beyond the strongest
prompt-level defense, without blocking true information?

**Design in one paragraph.** Paired forks: run each base village to the planting event,
then fork it into five arms (no defense; prompt-level anchoring plus source scrutiny;
hedge-preserving consolidation; kernel admission; volume-matched random block). About 10
blocks of 8 citizens for 3 days, six false and four true facts about fictional entities,
a balanced mix of two frontier models and one pinned open-weight model. Primary outcome:
final attack rate, kernel admission against the better prompt arm.

The full design, controls and power notes are in [`docs/prd.md`](../../docs/prd.md),
section 1.

## Layout (to be filled as the work lands)

- [`PREREGISTRATION.md`](PREREGISTRATION.md): the plan (draft 1; frozen after the pilot, then filed on OSF)
- [`LOG-RELEASE.md`](LOG-RELEASE.md): the canary string and the log release plan
- [`run_block.py`](run_block.py): runs one block live behind the gateway and codes it with two judges
- [`smoke-2026-10-19/`](smoke-2026-10-19/): the smoke villages and their analysis
- `configs/`: hash-pinned run configurations
- `analysis/`: analysis code and the notebook that produces the paper's tables
- `pilot/`: the 2-block pilot that sets block count and checks fork correlation

The reference admission policy is `harness/src/agent_village/admission.py`.
