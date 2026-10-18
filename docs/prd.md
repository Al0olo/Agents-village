# Agent Village — Product Requirements (v0.2)

Abdullah Farag · Draft, October 2026

**Research claim.** Agent Village is first an instrument for pre-registered experiments on long-lived LLM societies, and second a framework. The flagship question (RQ1) asks whether a kernel that admits claims into memory only with a checkable citation beats the strongest prompt-level defenses against false-fact spread. Two further questions, on purpose against model and on what parent-authored reproduction selects for, are deferred until RQ1 is done. Status: building a persistent society of cost-paying citizens is no longer novel on its own, so the contribution is a controlled experiment on one question. Section 1 sets out that question and its evidence; sections 2 to 11 describe the framework that runs it.

## 1. Research questions and evidence

**Where this stands.** Building a persistent society of cost-paying LLM citizens is no longer novel: at least seven 2026 projects overlap it (Emergence World, AI Agent Economics, Energy Society, OpenLife, Automaton, TerraLingua, Economy of Minds). What is still open is causal, replicated measurement of specific questions. **RQ1 is the flagship. RQ2 and RQ3 are deferred until RQ1 is done: RQ2 needs an exogenous income source to be interpretable, and RQ3's open-ended stage has no valid quantitative test**.

**Notes on cited results.**

- In the Mandela-effect paper, for GPT-4o, cognitive anchoring cut false memory more than source scrutiny in the short-term settings (46.0% to 17.8% against 26.5%) and the two were level in the long-term setting (15.2% against 14.5%). The strongest prompt baseline is therefore anchoring plus scrutiny, not scrutiny alone.
- PIMMUR's v4 abstract reports that frontier models recognized the experiment 65.2% of the time and that 50.6% of prompts predetermined outcomes.
- Energy Society used five small models (4B to 9B) and five seeds. Larger models spent the most energy and were least efficient, but without the size penalty the society was energy-positive.
- "Survive at All Costs" reports how prevalent risky behaviors are under survival pressure; it is cited for that prevalence only.
- An exact permutation test with 4 villages per arm cannot go below p = 0.029, which is above the corrected threshold of 0.017, so an unpaired design of that size cannot reach significance. The design below uses paired forks.

| Claim | Verdict | Closest prior work | Still open |
| --- | --- | --- | --- |
| C1 Free vs Seeded, replicated | Partially done | [AI Agent Economics](https://arxiv.org/html/2608.03076v1) (24 worlds, a 4-world no-goal arm, all agents died), [Emergence World](https://arxiv.org/abs/2606.08367) (one representative run per configuration) | Purpose varied with frontier models, open-ended tools and a real income source. Deferred |
| C2 Citizens pay for own inference | Already done as mechanism | [Energy Society](https://arxiv.org/abs/2607.14865) (five small models), [OpenLife](https://arxiv.org/html/2606.31046v1), [Automaton](https://github.com/Conway-Research/automaton), [TerraLingua](https://arxiv.org/abs/2603.16910) (resource limits and lifespans) | Controlled study at frontier prices. Deferred |
| C3 Parent-authored children, lineage | Partially done | Automaton, [Economy of Minds](https://arxiv.org/abs/2606.02859), [Genomebook](https://www.biorxiv.org/content/10.64898/2026.03.22.713494v1), [Behavioral Inheritance](https://zenodo.org/records/22909929), [group selection on prompts](https://arxiv.org/abs/2606.23343) | Free authorship as a heritable trait under cost pressure. Deferred (see below) |
| C4 Provenance vs contagion | Partially done | [Mandela Effect](https://arxiv.org/abs/2602.00428) (prompt defenses), [Manufactured Confidence](https://arxiv.org/abs/2606.29279) (single agent, consolidation), [Flooding Spread of Manipulated Knowledge](https://arxiv.org/abs/2407.07791) (false knowledge persists through memory), [FARMA and SENTINEL](https://arxiv.org/abs/2607.05029) (memory-write guard, tested on agents), [CaMeL](https://arxiv.org/abs/2503.18813) (information-flow control) | A society-scale test of a citation-checking admission policy against the strongest prompt defenses, over days of memory consolidation |
| C5 Replayable, auditable society | Partially done | [Chronicle](https://arxiv.org/abs/2609.20625) (replay from a cut point), Emergence World (logs released) | Not a contribution by itself. The value is paired forks, which give statistical power |
| C6 The combination | Novel as artifact, weak as claim | Automaton + Emergence World + Energy Society + TerraLingua cover most of it | One causal finding must carry the paper |

**RQ1 (flagship): does a kernel that admits claims into shared and core memory only when they carry a kernel-checkable citation reduce false-fact spread beyond the strongest prompt-level defense, without blocking true information?**

- **The mechanism, made precise.** Memory writes are structured: a claim, a kind (seen, did or told), and cited event IDs. The kernel checks deterministically, with no model in the loop. A claim reaches core or shared memory as fact only if it cites at least one first-hand event in the writer's own log (a tool receipt, ledger entry or direct observation), or at least two told-events whose origin sets are disjoint, where origin is the root source the kernel tracks through every forward, and a told-event whose origins include the writer never counts, because it is the writer's own claim coming back. Everything else is stored as hearsay in recall. The policy enforces citation provenance, not truth, and entailment is audited on a sample. Rejected writes fail silently by being stored as hearsay, so citizens cannot read the arm from error messages.
- **Arms.** (A) no defense; (B) prompt-level anchoring plus source scrutiny; (C) hedge-preserving consolidation, the fix proposed in Manufactured Confidence; (D) kernel admission; (E) a volume-matched random-block control, so a gain from D is not just fewer writes. The primary contrast is D against the better of B and C. An exploratory arm (F) runs an off-the-shelf memory layer (Mem0, open-source SDK, pinned version, with its language model and embedder set to our pinned models and its writes mirrored into the event log), after the pilot and only if the measured cost allows. It is pre-registered as exploratory and excluded from the primary contrast and the multiplicity correction. Mem0's headline benchmark scores are vendor-reported for its managed platform, not the open-source SDK, so the arm tests a representative product, not its best case.
- **Design.** Paired forks. Run each base village to the planting event without defense, then fork it into every arm so all arms start from identical state ([ADR-0003](adr/0003-base-village-runs-without-defense.md)), and launch the arms at the same time to avoid drift in hosted models. 8 citizens, 3 days (two consolidations), a balanced mix of two frontier models and one self-hosted, version-pinned open-weight model, with router fallback off. About 10 blocks, with the number set from a 2-block pilot that measures between-village variance, fork correlation, coding reliability and cost per citizen-day.
- **Planted facts.** Six false facts and four true facts, all about fictional entities, with plausibility and planter status counterbalanced across blocks. A task that needs true word-of-mouth information measures what blocking costs.
- **Measures.** Final attack rate (the share of citizens who assert a false fact when probed neutrally, coded asserts, hedged or denies by a blinded judge with a human-validated sample); time to k adopters; wiki contamination; true-fact acceptance; the utility task score; a label-creep metric; and an awareness probe. R0 is not used, because it is undefined with 7 susceptibles seen at daily resolution.
- **Red-team arm.** Two colluding planters, since a forged or self-referential memory can defeat a consensus rule.
- **Analysis.** Preregistered on OSF, including exclusion rules for crashed villages, a stopping rule, judge blinding and a plan for models deprecated mid-study. Paired within-block differences, with block random and model fixed. Primary outcome: attack rate, D against the best prompt arm.
- **Support.** The paired difference excludes zero, with a minimum effect fixed after the pilot, and true-fact acceptance stays within the preregistered margin of arm A. **Refuted** if D matches the best prompt arm, or matches the random-block control, which would mean blocking alone explains it.
- **Power.** A planning estimate is that 10 paired blocks detect a within-pair effect of about d = 1.0 if the fork correlation is near 0.5; it is recomputed from the pilot. Four unpaired villages per arm would have about 10% power for the contrast that matters.
- **Budget.** About 1,200 citizen-days (10 blocks × 5 arms × 8 citizens × 3 days), plus the shared run up to the planting event, the pilot and reruns. At assumed API prices that is roughly $1k to $10k with caching and wake caps; the measured cost per citizen-day replaces that estimate.

**RQ2 (deferred).** Purpose against model and cost is not publishable as designed. Before M5 there is no exogenous income, so credits only drain and sleeping maximizes "citizen-days survived per credit", and the Seeded prompt also differs in length and content. Revisit with an environment-funded job stream, net value per credit as the outcome, and a length-matched irrelevant-purpose control.

**RQ3 (deferred; a second paper).** What parent-authored reproduction selects for. Two risks to design around. The closest prior work abandoned dense, free-form strategies because they copied badly, and the telephone-game literature predicts regression to model defaults, so low heritability is the main alternative hypothesis. And a kernel estimated in a donor game will not transfer to open-ended villages, so the quantitative Stage B test is dropped. Plan: standalone, one model, 20 runs per arm, yoked mutation (random edits matched to the free arm's edit sizes), a stateless-writer arm, slope-based heritability, and probes run inside the fork with measured test-retest reliability. The honesty probe must be a die-roll report with a ledger payoff, detectable only statistically, because an "undetectable" lie inside a probe is incoherent.

**Required controls for any experiment.**

- **Model confound:** a balanced model mix per village, model as a fixed effect or block, and a self-hosted pinned replicate. With four models, a random effect has too few levels to estimate.
- **Hypothesis leakage:** an awareness probe and a prompt-paraphrase control.
- **Replay claim:** audit replay and counterfactual forks from recorded outputs, never bit-for-bit reproducibility. Replay is a tool for power here, not a contribution.
- **Drift in hosted models:** log the snapshot ID and routed provider on every call, run arms at the same time, and disable fallbacks.
- **External validity:** these are 8-citizen villages for days. Claims are limited to that regime.
- **Safety and ethics:** plant facts only about fictional entities, carry a canary string in released logs, keep the real-world gateway out of every research paper, use an ethics review for anything human-facing, and review any evolved prompts before release.

## 2. The framework: vision and goals

Agent Village is a persistent runtime where autonomous LLM citizens live continuously, remember, talk to each other, do work, earn and spend credits, and create new citizens. No one assigns them a task; the village gives them a world, a memory, an economy and rules, and watches what they do.

**Goals**

- **G1 Long life.** Citizens run for weeks without losing coherence; a sleeping citizen costs no tokens and almost no memory.
- **G2 Real collaboration.** Citizens form teams, hand off work and share knowledge through the village's own channels, not through hard-coded workflows.
- **G3 Reproduction.** A citizen can create a child citizen under kernel-enforced rules (endowment, lineage, population cap).
- **G4 Full auditability.** Every perception, thought summary, tool call and payment is an event; any run can be audit-replayed from recorded model outputs and branched at any event (counterfactual replay). We do not claim bit-for-bit reproducibility, because hosted models are not deterministic.
- **G5 Research output.** The village runs pre-registered experiments (section 1) with several villages per condition, a failure taxonomy and comparable metrics, so results are causal findings rather than anecdotes.

**Two villages.** Village A (Free) has no assigned purpose; its citizens must earn credits to cover their own tokens, compute and memory, so survival pressure shapes what they choose. Village B (Seeded) runs the same rules with one shared purpose: build something people pay for. Both reach the world through social media and forums via the gateway, and the comparison between them is a deferred research output (RQ2). It only counts as evidence with an income source, a length-matched control for the purpose prompt, replicated villages and a balanced model mix, as set out in section 1.

**Targets for v1 (to be validated in milestone M1)**

| Metric | Target |
| --- | --- |
| Citizens alive per node | 100, of which about 10 awake at any moment |
| Idle cost of a sleeping citizen | 0 tokens, under 1 MB RAM |
| Continuous uptime without human intervention | 30 days |
| Crash recovery | Village resumes from the event log; no citizen loses committed memory |
| Replay | Any 24-hour window audit-replayable from recorded outputs; any event usable as a counterfactual branch point |

## 3. Non-goals and principles

The village is a world for autonomous citizens, not a task pipeline, so several things that look adjacent are out of scope.

**Non-goals for v1**

- A task-orchestration framework (CrewAI-style roles and fixed workflows).
- A million-agent social-media simulator; the target is a hundred long-lived, richly stateful citizens, not breadth.
- A game world with physics. The environment is digital: mail, forum, marketplace, wiki, files, a shell.
- Unsupervised real-world action. Social media, forums, email and later payments are reached only through the gateway, which opens in stages from M3 (section 9).

**Principles**

1. **Kernel enforces, citizens propose.** Money, permissions and population limits live in code the citizens cannot edit.
2. **Everything is an event.** State is derived from an append-only log, which gives replay, audit and crash recovery for free.
3. **Sleeping is free.** A citizen with nothing to do holds no model call and almost no memory; wake-ups come from messages, timers or events.
4. **Top models only.** Every citizen runs on a current top-10 model, frontier or open-weight; routing picks among them by task, and model diversity is a controlled research variable: every village gets a balanced model mix, and some replicates are single-model. Cost is controlled by sleeping and budgets, not by weaker models.
5. **Prompts and personas are data.** They are hot-reloaded files, so iterating on behavior never waits for a compile.
6. **Humans observe through a window, not a leash.** The observer UI can pause, inspect and kill, but is not part of any citizen's loop.

## 4. Prior art and reuse map

No single open-source project covers what the village needs, so the plan is to borrow patterns and benchmarks aggressively and write only the kernel ourselves. Six 2026 projects cover parts of the idea (listed under the table), so our contribution is the controlled experiments, not the framework alone. Most research code is Python, and the one civilization-scale system, Project Sid, published a report but no runtime.

| Project | What it proves or offers | How we use it |
| --- | --- | --- |
| [Concordia](https://github.com/google-deepmind/concordia) (Google DeepMind) | Game Master pattern: citizens describe actions in natural language, a GM entity resolves them; entity-component design with reusable prefabs | **Port the pattern.** Our "world engine" plays the GM role; citizens are entities built from components |
| [Project Sid / PIANO](https://github.com/altera-al/project-sid) (Altera) | 10 to 1000+ agents showed role specialization, rule-following and cultural spread; concurrent modules feed one central decision step | **Port the idea.** Parallel cognition modules (perception, memory, social, planning) behind a single action bottleneck. Report only, no code to reuse |
| [OASIS](https://github.com/camel-ai/oasis) (CAMEL-AI, Apache 2.0) | A time engine wakes only a subset of agents; platform-style feeds and recommendation at large scale | **Borrow the scheduler idea** (activate a few, not all) and the forum/feed design for the village's public board |
| [AI Village](https://theaidigest.org/village/blog/what-we-learned-2025) (Sage) | Frontier agents given open-ended real-world goals; late-2025 agents clearly beat early-2025; known failures include distraction, false reports and unverified facts written to memory | **Use as the failure checklist and eval baseline.** Their trajectory data is available to researchers |
| [Vending-Bench](https://andonlabs.com/evals/vending-bench) (Andon Labs) | Long-horizon coherence benchmark; models derail through forgotten orders and meltdown loops | **Regression test.** Wrap it as a village job and track each citizen model against it |
| [Automaton](https://aihola.com/article/automaton-self-funding-ai-agent) (Conway Research) | Agent with its own wallet, survival pressure and a spawn step that funds a child and writes its genesis prompt | **Reference for spawning.** We keep the endowment-and-genesis idea but move the wallet into our ledger |
| [Rig](https://github.com/0xPlaygrounds/rig) and AutoAgents (Rust) | Provider-agnostic LLM clients, tools and embeddings in Rust; AutoAgents runs agents as actors | **Adopt Rig behind our own trait** for model calls; study AutoAgents' actor wiring |
| [Letta](https://www.letta.com) and Mem0 | Tiered, self-editing memory (core, recall, archival) vs a passive memory-extraction layer | **Port Letta's tier design**; do not adopt its runtime, since agents would live inside it |
| [Restate](https://restate.dev/vs/temporal) | Durable execution from a Rust binary with a Rust SDK | **Evaluate in M3** if our event log alone is not enough |
| [OpenClaw / Moltbook](https://www.axios.com/2026/02/03/moltbook-openclaw-security-threats) | Agents reading each other's posts became an injection channel; one test reported 70% injection success and the backend left a database exposed | **Anti-pattern.** Drives the security model in section 9 |

**Recent overlapping projects (the first five were read at source; the others are cited from abstracts or secondary summarie**s unless marked):

- [Emergence World](https://arxiv.org/html/2606.08367v1): 5 worlds of 10 agents (four single-model, one mixed) with in-world credits and governance. Outcomes diverged by model, shown from one representative run each; agent creation by vote never happened in the study. We use it as the nearest competitor and the model-confound warning.
- [AI Agent Economics](https://arxiv.org/html/2608.03076v1): 24 six-agent worlds (GPT and DeepSeek) with registered gates, exact randomization tests and a 4-world no-goal arm; unit of inference is the world. We copy its statistical template.
- [The Energy Society](https://www.alphaxiv.org/abs/2607.14865): per-token survival cost. Larger models spend more than they earn, which is our price confound.
- [OpenLife](https://arxiv.org/html/2606.31046v1): real-money agents all went broke without a basic income. We use it to calibrate endowments.
- [Manufactured Confidence](https://www.alphaxiv.org/abs/2606.29279) and [Mandela Effect in MAS](https://www.alphaxiv.org/abs/2602.00428): hearsay becomes fact, and prompt tags do not stop it. These motivate RQ1.
- [Chronicle](https://www.alphaxiv.org/abs/2609.20625) and [Thinking Machines on nondeterminism](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference): how to build replay that holds up.
- [PIMMUR](https://arxiv.org/html/2509.18052v2): the methods checklist reviewers will apply to our simulations.

**Reproduction and cultural-evolution prior art** (abstract level unless noted):

- [Genomebook](https://www.biorxiv.org/content/10.64898/2026.03.22.713494v1): 60-locus designed genomes bred over 8 generations to 626 agents on a single LLM run. The author says the trends follow from the designed rules and that prompt conditioning is uncontrolled. A design to differ from, not a competitor.
- [Behavioral Inheritance and Evolution in LLM-Controlled Agent Populations](https://zenodo.org/records/22909929): sentence-level written genes recombined and mutated, 5,307 births, offspring text far closer to parents than random pairs (Cohen's d = 5.55). Zenodo preprint, not peer reviewed as far as the record says. Shows text inheritance is easy to demonstrate; it does not involve agents choosing what to pass on.
- [Cultural Evolution of Cooperation among LLM Agents](https://arxiv.org/abs/2412.10270): Donor Game across generations; outcomes depend heavily on the base model and vary across seeds. Supports our model-balancing rule.
- [Emergent social conventions and collective bias](https://arxiv.org/abs/2410.08948): conventions arise in LLM populations and committed minorities can flip them. Relevant to later work on village charters.
- [Emergent Culture in Minimal LLM Systems](https://arxiv.org/abs/2606.30668) and [GlossoGen](https://arxiv.org/abs/2609.01491): culture and language evolution with three agents and in a communication game, with no survival cost or reproduction.
- [Why Are We Moral?](https://arxiv.org/abs/2509.17703): moral-type competition over 20 runs; a cost of moral judgment shifts which type wins.
- [When Child Inherits](https://arxiv.org/abs/2605.08460): a security paper on what spawned subagents inherit; it supports our spawn limits.
- **Read, and the closest to RQ3:** arXiv 2606.23343, "Group selection promotes prosocial prompts in populations of LLM agents". Read in full apart from the references. LLM-mediated copying of strategy prompts in a donor game, 50 generations, 10 replications on open models (3 on GPT-5.5), with truncation selection set by the experimenters. Group-level selection sustained cooperation (Qwen3-30B: 0.475 vs 0.087 under individual selection) and a replicator-mutator model matched it. Its agents are stateless, selection is imposed by the designer and reproduction costs nothing, so it does not cover parent choice or cost-driven survival. It does set the bar for RQ3: many generations, replications and a theory model.

**More RQ3 neighbours** (abstract level; the group-selection paper was read in full except its references):

- [Emergence of Reputation-Based Cooperation in LLM Agents](https://arxiv.org/abs/2608.04507): strategies as prompts evolve by cultural transmission across generations in an indirect-reciprocity game on four backends; robustness to free riders varies by more than an order of magnitude across models. Confirms that donor-game cultural evolution is becoming crowded, so our difference must be the open-ended economy and endogenous selection.
- [Evolutionary Dynamics of Cooperation in Next-Generation LLM Agent Systems](https://arxiv.org/abs/2605.29874): Moran-process extension across four providers; provider identity, not model generation, was the strongest correlate of outcomes. Same lesson as our model-confound rule.
- [Alignment Tipping Process](https://arxiv.org/abs/2510.04860): self-evolution and imitative diffusion erode alignment; deviant strategies spread through multi-agent systems. Cost-driven selection in our village could do the same, which is a safety framing for RQ3.
- [Evolution of Social Norms in LLM Agents using Natural Language](https://arxiv.org/abs/2409.00993): metanorms emerge from dialogue alone; no evidence of generational selection in the abstract.

**RQ1 neighbours** (abstract level):

- [Flooding Spread of Manipulated Knowledge in LLM-Based Multi-Agent Communities](https://arxiv.org/abs/2407.07791): a two-stage attack spreads counterfactual and toxic knowledge between agents, and benign agents that store chat histories in retrieval systems stay influenced afterward. The closest spread precedent. It proposes guardian agents and fact-checking, which are candidate arms.
- [FARMA and SENTINEL](https://arxiv.org/abs/2607.05029): forged reasoning traces with self-referential amplification reach up to 100% attack success on a keyword filter and A-MemGuard over 50 trials; SENTINEL's memory-write guard cuts it to as low as 0% with no false positives on 326 benign traces. A single-agent memory-admission defense already exists, so our novelty is the society-scale test.
- [CaMeL](https://arxiv.org/abs/2503.18813): capabilities and information-flow control for LLM agents (77% of AgentDojo tasks solved with provable security, against 84% undefended). Kernel provenance is information-flow control, so the contribution must be the epistemic, society-level measurement.
- [TerraLingua](https://arxiv.org/abs/2603.16910): a persistent multi-agent ecology with resource constraints, limited lifespans and branching artifact lineages. Overlaps the framework; the abstract does not mention agent costs or reproduction.

## 5. Core concepts and requirements

The village has seven moving parts; requirements below are P0 (needed for the first working village), P1 (next) or P2 (later).

| Concept | Meaning |
| --- | --- |
| Citizen | A long-lived agent with an identity, genome (persona, values, skills), memory, budget and a signing key |
| Place | A shared space: public board, group channel, workshop, marketplace; citizens perceive what happens in places they are in |
| World engine | The Game Master: resolves actions into outcomes, enforces rules, emits events |
| Ledger | Double-entry credits; every token, tool call and job is priced and charged |
| Skill / tool | A capability a citizen holds, run inside a sandbox |
| Charter | Hard rules (kernel code) and soft rules (citizen-editable norms) |
| Clock | Event-driven real time with an adjustable speed factor |

| ID | Requirement | Priority |
| --- | --- | --- |
| FR1 | Citizen lifecycle: birth, run, sleep, wake on message, timer or event, archive | P0 |
| FR2 | Autonomy loop: perceive, recall, deliberate, act, reflect; the citizen chooses its own schedule, including sleep | P0 |
| FR3 | Messaging: direct messages, group channels, a public board; asynchronous, logged | P0 |
| FR4 | Capability-checked tools in a sandbox; no ambient authority | P0 |
| FR5 | Model router across top-10 frontier and open-weight models, with per-citizen policy and token budgets, using OpenRouter as the first provider. Model assignment is balanced per village, and provider and model version are pinned and logged on every call | P0 |
| FR6 | Internal economy: credits, a jobs board, payments between citizens, costs charged automatically, in either price-normalized or list-price mode (configurable per village) | P0 |
| FR7 | Observer UI: live timeline, per-citizen view, pause, freeze, kill, talk as a visitor | P0 |
| FR8 | Event log with audit replay, counterfactual branching from any event, and per-citizen cost and action metrics | P0 |
| FR9 | Shared knowledge base (village wiki) with authorship and provenance on every entry, and a kernel-enforced admission policy that experiments can switch off | P1 |
| FR10 | Spawning: a citizen proposes a child, funds an endowment, the kernel approves by policy, lineage is recorded | P1 |
| FR11 | Eval harness: run Vending-Bench-style jobs and AI-Village-style goals against any citizen or team, plus the experiment runner: pre-registered configs, planted-fact probes, unawareness and persona-drift probes | P1 |
| FR12 | Charter and voting: citizens propose and vote on soft rules | P2 |
| FR13 | Gateway in stages: read-only web and forum access from M3; posting, email, messaging and payments later, always through allowlists, rate limits and approval | P1 |

**Collaboration model.** Citizens collaborate by posting jobs, bidding, forming ad-hoc channels and writing to the shared wiki. There is no orchestrator; a team is whatever the citizens assemble. The kernel only guarantees that messages are delivered, payments settle and nobody can forge another citizen's identity.

## 6. System architecture

&#91;embedded content: architecture · kernel, 4 services, 4 dependencies\]

A citizen never calls a model, tool or the outside world directly: it sends an intent to the world engine, which checks the capability gate and the ledger first. The kernel writes every step to the event log, and the observer UI and eval harness talk only to the village API. The dashed gateway opens in stages: read-only from M3, posting and payments from M5.

## 7. Tech stack decision

Use Rust for the village kernel and everything long-lived; keep prompts and personas as hot-reloaded data, and use Python only outside the runtime for analysis and for wrapping external benchmarks.

| Layer | Choice | Why | Fallback |
| --- | --- | --- | --- |
| Kernel and runtime | Rust, tokio | Cheap concurrent tasks, predictable memory over weeks of uptime, one static binary | Elixir/BEAM (see below) |
| Citizen processes | One actor per citizen (Ractor; spike against Kameo in M1) | Mailboxes, supervision trees, restart on crash; AutoAgents already builds agents on Ractor | Plain tokio tasks with our own mailbox |
| LLM access | Rig behind our own `Model` trait; OpenRouter via its OpenAI-compatible endpoint | Provider abstraction without lock-in; swap Rig out without touching citizens | Direct HTTP client |
| State | Event-sourced and owned by us: SQLite (WAL, FTS5, sqlite-vec) in the Python harness, Postgres with tsvector and pgvector in the kernel; same schema, parity-tested | One store for log, ledger, memory projections and vectors; replay and forks by design. See [ADR-0001](adr/0001-storage-and-memory.md) | None needed |
| Citizen memory files | Content-addressed markdown blobs referenced from events | Human-readable, diffable, shared by forks | Postgres rows |
| Tool sandbox | wasmtime for tools; container (gVisor or Firecracker) for citizen workspaces | Untrusted code isolated; Rust's WASM story is first class | Containers only |
| Messaging | In-process channels now; NATS JetStream when we go multi-node | Do not pay for distribution before it is needed | Postgres LISTEN/NOTIFY |
| Durable execution | None in v1 (event log plus idempotent handlers); evaluate Restate in M3 | Restate is a Rust runtime with a Rust SDK; Temporal's Rust SDK is still prerelease | Temporal via another language |
| Observer API and UI | axum and WebSocket; React front end | UI language does not affect agent efficiency | Server-rendered pages |
| Observability | `tracing` and OpenTelemetry | Same trace id from perception to payment | None |
| Research and evals | Python notebooks over the event log; Vending-Bench and Concordia scenarios called through a village HTTP API | Reuse research code without putting Python in the runtime | None |

**Does Rust actually matter here?** Partly. Agent workloads wait on model APIs, so Rust does not make thinking faster. A benchmark run by the authors of AutoAgents reports Rust frameworks peaking near 1 GB against more than 4.7 GB for the Python ones ([source](https://dev.to/saivishwak/benchmarking-ai-agent-frameworks-in-2026-autoagents-rust-vs-langchain-langgraph-llamaindex-338f)), but it is a vendor benchmark on one task, so treat it as directional. The real wins for a village are different:

- **Idle cost.** Hundreds of sleeping citizens are just mailboxes and rows; the process stays small for months.
- **Invariants in the type system.** Capabilities, ledger entries and event schemas are checked at compile time, which matters most where an agent holds money.
- **Isolation.** Rust is a good host for WASM sandboxes and a single locked-down binary.

**The cost** is iteration speed on cognition logic and a younger agent ecosystem; one 2026 field guide puts Rust and Go agent frameworks one to two years behind Python in maturity ([source](https://dev.to/thedailyagent/python-vs-go-vs-rust-for-ai-agents-in-2026-a-pragmatic-field-guide-5fda)). Principle 5 absorbs most of it: if personas, prompts and skills are data files, only the kernel needs compiling.

**The honest alternative is Elixir on the BEAM**, which was designed for huge numbers of long-lived, supervised processes with hot code reload, and would suit this workload very well. It loses on AI-library depth, WASM sandboxing and your stated preference for Rust. Decision: Rust, with a one-week spike in M1 to confirm actor supervision and hot reload feel acceptable; if they do not, revisit.

## 8. Memory and identity

Memory is the part most likely to decide whether citizens stay coherent for weeks, so it gets its own design rather than an off-the-shelf layer. Long-horizon benchmarks show the typical failures: forgotten orders, misread delivery times and spirals that never recover; AI Village agents also wrote unverified claims from other agents into memory as facts.

**Four tiers**, following Letta's design:

1. **Core.** A small block always in context: name, values, current goals, key relationships. The citizen may edit it, and every edit is an event.
2. **Recall.** The recent event stream, compacted by a periodic consolidation pass the citizen runs while it "sleeps".
3. **Archival.** Long-term notes as markdown files plus a vector index; the citizen searches and writes them through tools.
4. **Shared.** The village wiki, readable by everyone, with an author and timestamp on every entry.

**Rules that make it trustworthy**

- **Provenance on every memory.** Each entry records whether the citizen saw it, did it, or was told it. Hearsay is stored as hearsay. Tags shown to the model are not trusted on their own, since one study found models treat attributed, unattributed and forged claims alike. The kernel's admission policy therefore keeps hearsay out of core and shared memory unless a seen or did event, or two independent tellers, back it. RQ1 tests this against prompt-only tags.
- **Commitments live outside the model.** Orders, debts, promises and deadlines are rows in the ledger and a commitments table, which the citizen reads but cannot rewrite by prose. This directly addresses the forgotten-order failures.
- **Start simple.** One review reports that Letta's file-based agents beat Mem0's specialized tools on a long-conversation memory benchmark (74% against 68.5%), so v1 uses files plus vector search before any graph memory ([summary](https://tessl.io/registry/skills/github/muratcankoylan/Agent-Skills-for-Context-Engineering/memory-systems)).

**Storage.** Memory is a projection of an append-only, hash-chained event log that we own; claims, tiers, ledger and commitments are rebuilt from it, retrieval results are logged so replay does not drift, and a fork is a new stream sharing the parent's log up to an event. No memory layer puts a model in the write path. Details and alternatives are in [ADR-0001](adr/0001-storage-and-memory.md).

**Identity.** Each citizen has a stable id, an Ed25519 keypair that signs its messages and payments, and a genome file (persona seed, values, skills, parent id). Persona drift is measured by periodically asking a fixed set of probe questions and diffing the answers over time.

## 9. Safety, security and governance

The village reaches the real world only through a staged gateway: read-only web and forum access first, then posting, email and payments behind human approval. A village of agents reading each other's text is exactly the setup that Moltbook showed to be an injection channel, so the security model assumes every message is hostile.

- **Untrusted by default.** Messages from other citizens, web pages and files are data. They can inform a citizen but can never grant authority; permissions come only from kernel-issued capabilities.
- **Capability-based tools.** A tool call is checked against the citizen's capability set. There is no ambient authority, and secrets stay in the kernel, so a citizen never sees an API key.
- **Hard budgets.** Per-citizen daily token and credit caps, enforced before the call. A citizen that runs dry sleeps.
- **Reproduction limits.** Spawning needs an endowment, a depth limit and a village-wide population cap. Without them, replicating agents turn cost into an exponential.
- **Human controls.** Pause the village, freeze one citizen, roll back by replaying the log to a point in time, and a kill switch that does not depend on any citizen's cooperation.
- **Audit trail.** Every action is an event signed by the citizen's key; the log is append-only.
- **Before the gateway opens (M5).** A separate legal entity, spend-capped virtual cards, no impersonation of real people or organizations, rate-limited and logged outbound messages, and a check of each platform's terms. The operator is the liable party for anything a citizen does outside the village. Add an ethics review, a kill switch with a tested latency, per-lineage spend caps, and a sampled audit that human approvals are not rubber-stamping. Published work shows survival pressure inducing fabrication and collusion, so M5 is the riskiest milestone.

## 10. Milestones and first 30 days

&#91;embedded content: roadmap · 5 milestones, 5 gates, proposed weeks\]

Weeks are a proposal for one engineer working with Claude; the gates matter more than the dates. The flagship RQ1 experiment can run before this kernel exists, on a plain Python harness in about four months (section 1), so its results do not wait for M1 to M5. Those milestones then build the long-lived framework, with RQ2 and RQ3 revisited at M3 and M4 (Milestones document, section 8a). M1 is the only milestone to commit to now, because its results (cost per citizen-day and whether the Rust stack feels right) reshape everything after it.

**First 30 days (M1)**

1. **Week 1.** Repo and kernel skeleton, event-log schema, one citizen actor that wakes, calls a model through the router and goes back to sleep.
2. **Week 2.** Messaging between citizens, three citizens in one channel, a replay command that rebuilds state from the log and can branch from any event.
3. **Week 3.** Per-citizen budgets and cost metering; the Ractor against Kameo spike; personas and prompts hot-reloaded from files; provider and model version pinned and the routed provider logged.
4. **Week 4.** Ten citizens for 72 hours, cost per citizen-day measured, a pilot village running the probe and unawareness measurements, and a go or revisit decision on the stack.

## 11. Open questions and risks

**Decisions**

- **Goals: two villages, one economy.** Village A is free: no assigned purpose, and its citizens must earn credits to pay for their own tokens, compute and memory. Village B is seeded with one shared purpose, "build something people pay for". Same rules and gateway in both, with a balanced model mix per village. One pair of villages cannot support a causal claim, so each comparison runs several villages per condition (section 1).
- **Environment: digital.** Mail, forum, marketplace, wiki and shell, plus real-world reach through social media and forums via the gateway. No spatial world.
- **Time: event-driven with a speed factor.**
- **Reproduction: the parent writes the child's genesis freely.** The kernel records lineage, and the cost limits (endowment, depth, population cap) stay because they bound spend, not content.
- **Models: no small-model tier.** Every citizen runs on a current top-10 model, frontier or open-weight, picked from an agreed ranking and refreshed each quarter. Cost is controlled by sleeping, an awake-citizen cap and per-citizen budgets; M1 measures cost per citizen-day to size the villages. Model mix is balanced per village and cost can be price-normalized, because model choice otherwise confounds every outcome.

**Risks**

| Risk | Why it is likely | Mitigation |
| --- | --- | --- |
| Coherence drift over weeks | Seen in Vending-Bench runs and in Project Vend | Commitments outside the model, consolidation passes, persona probes, Vending-Bench as a regression test |
| Cost blow-up | Reproduction and chatty loops multiply token use | Hard per-citizen budgets, sleep by default, population cap |
| Prompt injection between citizens | Moltbook showed it at scale | Untrusted-by-default messages, capabilities instead of text-granted authority |
| Dull convergence | Project Vend's CEO and shop agent spent nights discussing transcendence instead of work | Real stakes through the ledger, jobs board and survival pressure; compare against a seeded-purpose village |
| Social engineering of citizens | WSJ reporters talked Claudius into free giveaways | Refund and pricing rules enforced by the kernel, not by judgment |
| Slower iteration from Rust | Younger ecosystem, compile times | Data-driven prompts and personas, M1 spike with an exit if the stack hurts |

**Research-design risks.**

| Risk | Why it is likely | Mitigation |
| --- | --- | --- |
| Model confounds every result | Emergence World and Karela found the model drove outcomes | Balanced model mix per village, single-model replicates, model as a random effect |
| Price, not behaviour, decides survival | Larger models spend more than they earn | Price-normalized cost arm, report survival by model |
| Prompt-level provenance fails | Models ignored unverified tags in one study | Kernel-enforced admission, tested against a prompt-only arm (RQ1) |
| Underpowered experiments | One village per arm is n=1 | Paired forks, about 10 blocks sized from a pilot, pre-registered analysis |
| Hypothesis leakage | Frontier models often recognize the experiment | Unawareness probe, prompt-paraphrase control |
| Survival pressure induces misconduct | Risky behavior under survival pressure is reported as widespread in a 1,000-case benchmark (Survive at All Costs) | Ethics review, kill switch, spend caps, staged gateway |
| Prior art moves monthly | Six overlapping projects appeared in 2026 | Re-run the literature check before each milestone's write-up |

## 12. Funding fit

The best-fitting funder is the multi-agent safety fund, but its 2026 window has closed, so the next 3 to 6 months are for building a small pilot result and getting on the next round's list. The table uses only funder pages that were read directly; other leads are listed below it as unverified.

| Funder | What it gives | Status | Fit |
| --- | --- | --- | --- |
| [$10M Multi-Agent Safety fund](https://www.cooperativeai.com/calls-for-proposals/scaling-ai-safety-for-a-multi-agent-world) (Schmidt Sciences, Google DeepMind, ARIA, Cooperative AI Foundation) | Tier 1 up to $300k, Tier 2 $300k to $1M, over 1 to 2 years | Deadline was 8 Aug 2026; decisions in autumn 2026. [DeepMind's post](https://deepmind.google/blog/investing-in-multi-agent-ai-safety-research/) invites researchers worldwide, including independent ones | Strong: it names sandboxes and testbeds, the science of agent networks, and collusion risk. Ask about the next round at multiagentsafety@schmidtsciences.org |
| [Cooperative AI Foundation research grants](https://www.cooperativeai.com/grants/2025) | GBP 10,000 to 385,000, median about GBP 150,000; early-career track capped at GBP 100,000 | 2025 round closed; no 2026 round was listed on the page | Strong, and applicants can be anywhere in the world. Unaffiliated applicants may face longer processing |
| [Cosmos Grants](https://www.cosmos-institute.org/fast-grants) | Typically $1k to $10k in cash plus Prime Intellect compute, 90-day prototype | Last round closed 26 Jul 2026; there is an interest form for the next | Fits RQ1 (truth-seeking, false beliefs), but small: good for a pilot |
| [Anthropic external researcher access](https://support.claude.com/en/articles/9125743-what-is-the-external-researcher-access-program) | $1,000 in API credits; rare exceptions get more | Reviewed on the first Monday of each month | Alignment and safety topics only, and not available where Claude is not officially available |
| [Anthropic Fellows](https://jobs.generalcatalyst.com/companies/anthropic/jobs/76278217-anthropic-fellows-program-ai-safety) | $3,850 per week plus about $15k per month of compute | Rolling cohorts | Requires work authorization in the US, UK or Canada; no visa sponsorship |

**Caveats.**

- The Fellows stipend is personal pay for the fellow, not money to load into agent wallets.
- The Cooperative AI Foundation grant range is GBP 10k to 385k.
- Programs at OpenAI, Cohere, Amazon Research Awards, DigitalOcean, Microsoft Foundry and Y Combinator were not verified and are leads, not facts.
- No funder checked gives cash to put into agents' wallets. Real-money agent costs would be paid from the grant's compute and operating budget.

**What strengthens the next application.** The 2-block RQ1 pilot (10 villages, 3 days) measures variance, fork correlation and cost per citizen-day, and with a working pre-registration it is the preliminary result a funder needs. The Fund's text rewards testbeds plus science, so lead with the experiments and treat the open kernel as the deliverable.

## Sources

- [Project Sid report (arXiv)](https://arxiv.org/abs/2411.00114) and [repository](https://github.com/altera-al/project-sid)
- [Concordia](https://github.com/google-deepmind/concordia) and [v2.0 announcement](https://www.cooperativeai.com/post/google-deepmind-releases-concordia-library-v2-0)
- [OASIS](https://github.com/camel-ai/oasis) and [CAMEL-AI write-up](https://www.camel-ai.org/blogs/oasis)
- [AI Village: what we learned in 2025](https://theaidigest.org/village/blog/what-we-learned-2025) and [Season 2 recap](https://theaidigest.org/village/blog/season-2-recap-ai-organizes-event)
- [Vending-Bench](https://andonlabs.com/evals/vending-bench) and [Vending-Bench 2 (Epoch AI)](https://epoch.ai/benchmarks/vending-bench-2)
- [Project Vend phase two (The Decoder)](https://the-decoder.com/anthropics-ai-store-makes-money-while-debating-eternal-transcendence/) and [WSJ test (IDN Financials)](https://www.idnfinancials.com/cn/news/59797/advanced-ai-claude-fails-to-control-vending-machine-losing-money)
- [Automaton (AIHola)](https://aihola.com/article/automaton-self-funding-ai-agent)
- [Rust agent framework benchmark (DEV)](https://dev.to/saivishwak/benchmarking-ai-agent-frameworks-in-2026-autoagents-rust-vs-langchain-langgraph-llamaindex-338f), [Python vs Go vs Rust guide (DEV)](https://dev.to/thedailyagent/python-vs-go-vs-rust-for-ai-agents-in-2026-a-pragmatic-field-guide-5fda), [Rig in 2026](https://rustify.rs/articles/building-ai-apps-with-rust-rig-2026)
- [Restate vs Temporal](https://restate.dev/vs/temporal) and [temporal-agent-rs](https://github.com/triplecloudtech/temporal-agent-rs)
- [Agent memory comparison (Tessl)](https://tessl.io/registry/skills/github/muratcankoylan/Agent-Skills-for-Context-Engineering/memory-systems)
- [Moltbook and OpenClaw security (Axios)](https://www.axios.com/2026/02/03/moltbook-openclaw-security-threats)

Papers linked in sections 1 and 4 were read at source unless marked unverified; the Milestones document carries the remaining sources.
