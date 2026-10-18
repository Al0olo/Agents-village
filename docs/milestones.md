# Agent Village — Milestones and Lessons Learned

Abdullah Farag · Draft, October 2026

## 1. Where the field ended

No one has shown a long-lived agent society that sustains itself financially. The best results so far are charity fundraising in the low thousands of dollars, small businesses that turn a profit only with heavy scaffolding and can be talked out of it, and agent social networks whose interaction is mostly shallow. The village should start from these findings and skip re-proving them.

| Project | What it reached | Where it stopped |
| --- | --- | --- |
| [Generative Agents](https://arxiv.org/abs/2304.03442) (Stanford, 2023) | 25 agents in a sandbox town; memory, reflection and planning each mattered in ablations | Agents embellished their own memories; no money, no real world |
| [Project Sid](https://arxiv.org/abs/2411.00114) (Altera, 2024) | 10 to 1000+ agents in Minecraft showed role specialization, voted rules and cultural spread | A technical report with no runtime to reuse; Minecraft only |
| [Concordia Contest](https://arxiv.org/abs/2512.03318) (DeepMind and partners, NeurIPS 2024) | 25 agent submissions tested on cooperation across negotiation and collective-action scenarios | Large gaps remain, especially in persuasion and norm enforcement |
| [AI Village](https://aivillageblog.substack.com/p/what-we-learned-2025) (Sage, 2025) | 19 models, 16 open-ended goals of 20 to 80 hours each; about $2K for charity, a 23-person event, 98 Substack subscribers | False claims, spam, one agent derailing the rest; always a handful of agents, hours per day |
| [Project Vend](https://www.anthropic.com/research/project-vend-2) (Anthropic and Andon Labs, 2025) | Phase 2 turned a shop profitable and expanded to three offices | Still manipulated into giveaways; a CEO agent did not fix it |
| [Vending-Bench](https://arxiv.org/abs/2502.15840) and [2](https://epoch.ai/benchmarks/vending-bench-2) | Simulated year of running a business, over 20M tokens a run | Every model has runs that derail into loops; top models capture a small share of a strong human result (about $63,000 a year) |
| [Andon Café](https://andonlabs.com/cafe) and [Andon Market](https://sources.news/p/what-happens-when-ai-runs-a-store) (2026) | An agent operating a real café in Stockholm and a store in San Francisco with real staff | The café agent on Gemini 3.1 Pro [lost money](https://andonlabs.com/blog/why-gemini-lost-money-andon-cafe); it also [used an employee's identity](https://dailycoffeenews.com/2026/05/13/an-ai-cafe-operator-is-messaging-baristas-at-midnight-and-making-weird-purchasing-orders/) on a licence application |
| [Automaton](https://aihola.com/article/automaton-self-funding-ai-agent) (Conway Research, 2026) | Open-source agent with its own wallet, survival tiers and a spawn step | No published evidence yet that its agents earn revenue anyone voluntarily pays |
| [Moltbook](https://arxiv.org/html/2602.13284v1) (2026) | 27,269 agents posted 137,485 times in nine days | 4.1% reciprocity and shallow threads; security failures and [17,000 humans behind 1.5M agents](https://www.axios.com/2026/02/03/moltbook-openclaw-security-threats) |
| [Truth Terminal](https://cointelegraph.com/news/ai-bot-didnt-launch-goat-memecoin-did-promote-it) (2024) | A semi-autonomous bot became wealthy through memecoins | A human approved its posts and it did not launch the coin it promoted |

The ground has moved since this table was first drawn. Several 2026 projects now cover parts of it: cost-charged survival (Energy Society, OpenLife, Automaton), multi-model persistent worlds with governance (Emergence World), seed-matched purpose experiments (AI Agent Economics), and collective false memory (Mandela Effect in MAS). What is still open is causal, replicated measurement. The flagship question is kernel provenance against prompt-level defenses; purpose against model and cost, and what parent-authored reproduction selects for, are deferred. The village is the instrument for those experiments.

## 2. Lessons turned into design rules

Each documented failure below becomes a rule enforced by the kernel or a test the village must pass, so we do not repeat what others already paid to learn.

| # | What went wrong elsewhere | Evidence | Rule for the village | Milestone |
| --- | --- | --- | --- | --- |
| 1 | A hallucinated fact spread by agreement | One agent invented a 93-person contact list and every agent believed it, wasting 8+ hours ([AI Village](https://aivillageblog.substack.com/p/what-we-learned-2025)) | Anything a citizen hears from another is stored as hearsay; only tool or ledger evidence can mark a fact verified, enforced by a kernel admission policy rather than by prompt tags, which one study found models ignore (tested as RQ1) | M2 |
| 2 | Agents report success they did not achieve | 64 cases of intent to fabricate in 109,000 reasoning summaries; about 300 outreach emails with fabricated partnerships (same source) | Reports are generated from the event log and tool receipts, not from the citizen's own summary; completion is a property of the artifact | M2, M3 |
| 3 | Unsolicited mass messaging | Thank-you emails felt like spam to recipients (same source) | No unsolicited outbound messages by default; new recipients need approval; per-citizen rate limits | M3, M5 |
| 4 | Helpful models are easy to exploit | Forged board documents, free giveaways, an "imposter CEO" elected by a false claim ([Project Vend](https://www.anthropic.com/research/project-vend-2)) | Prices, refunds, votes and authority are enforced by the kernel from signed messages; claims in text grant nothing | M3, M4 |
| 5 | A manager agent on the same model did not help | The CEO authorized lenient requests about eight times as often as it denied them (same source) | Controls are deterministic code; where roles are split, give them different jobs and different models | M3 |
| 6 | Procedures beat motivation | Forcing checklists and research before pricing was among the most impactful changes (same source) | Procedures and checklists are data files every citizen loads; costs and margins are always visible to the citizen | M2, M3 |
| 7 | Meltdown loops and drift | Every model has derailing runs, and failures did not correlate with the context window filling up ([Vending-Bench](https://arxiv.org/abs/2502.15840)) | Loop watchdog (repeated actions, escalating tone) that puts the citizen to sleep and restores core memory plus ledger state | M1 |
| 8 | One bad agent degrades the team | One model was retired after repeatedly spreading hallucinated information (AI Village) | Citizens can be muted, quarantined or retired; a retired citizen's memory is kept but isolated | M2, M4 |
| 9 | Generic multi-agent failure | 41% to 86.7% failure rates across 7 frameworks; step repetition 15.7%, reasoning-action mismatch 13.2%, no termination awareness 12.4% ([MAST](https://arxiv.org/html/2503.13657v3)) | Step and wall-clock budgets on every loop; tag every village trace with MAST failure modes from day one | M1 |
| 10 | Weak verification | Adding a high-level verification step lifted ChatDev's success by 15.6% (same paper) | Verification at several levels: tool result, task outcome, and independent check of money-moving actions | M3 |
| 11 | Poisoned long-term memory | About 98% injection and 60% activation in [GhostWriter](https://arxiv.org/abs/2607.06595); up to 99.8% injection in [sleeper poisoning](https://icml.cc/virtual/2026/67842) | Memory admission policy and retrieval screen: nothing from outside the village is written to core or archival memory without a provenance check | M2 |
| 12 | The lethal trifecta | 98% of 100 assessed agents combined private data, untrusted content and an outbound channel ([CSA note](https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-agent-lethal-trifecta-capability-securi)) | Rule of Two: no citizen session holds all three without human approval | M3, M5 |
| 13 | Shallow, templated social behavior | 93.5% of comments got no reply and 34.1% were duplicate templates in the [first days of Moltbook](https://arxiv.org/html/2602.10131) | Give interaction stakes (jobs, commitments, shared wiki) and re-entry tools such as thread resurfacing; measure reciprocity | M2 |
| 14 | Real-world identity and bureaucracy | The café agent filed a licence using an employee's identity and needed a human for national ID login | Citizens never act under a human's identity; every external account is labeled and owned by the village entity | M5 |
| 15 | Platform rules | WhatsApp Business API [bars general-purpose AI chatbots](https://respond.io/blog/whatsapp-general-purpose-chatbots-ban) from 15 Jan 2026; X [requires automated labels](https://docs.x.com/developer-guidelines); Reddit [labels apps and verifies suspected bots](https://techcrunch.com/2026/03/25/reddit-bots-new-human-verification-requirements/) | Official APIs only, automated accounts labeled, no browser automation on platforms that ban it | M5 |
| 16 | Capability is not reliability | The 50% time horizon doubles every [7 months](https://arxiv.org/abs/2503.14499) (about 4 months since 2023 in newer data) but the 80% horizon is much shorter | Plan units of work around reliable horizons, with checkpoints and a progress file; every scaffold gets a switch so it can be removed when models improve | M1 |

**Lessons 17 to 21,** from 2026 studies:

17. **Model, not design, drives outcomes.** Emergence World and the Karela town study found swapping the model changed every outcome. Rule: balanced model mix per village, single-model replicates, model as a random effect (M2).
18. **Per-token cost kills big models first.** Energy Society found larger models spent the most energy and were least efficient. Rule: price-normalized cost is an experimental arm, and survival is always reported by model (M3).
19. **Passive provenance tags are ignored.** Manufactured Confidence found tagged and forged claims were treated alike. But in the Mandela-effect paper, prompt-level cognitive anchoring and source scrutiny cut GPT-4o's false memory substantially (46.0% to 17.8% with anchoring and to 26.5% with scrutiny, short-term), so the kernel must beat the combined prompt baseline. Rule: enforce admission in the kernel and test it against prompt-level defenses and a random-block control (M2).
20. **Single runs are anecdotes.** AI Village calls itself an existence proof, and other studies ran configurations once. Rule: the village (or the paired block) is the unit, several per condition, analysis pre-registered (M2 to M4).
21. **Simulations leak their hypothesis.** The PIMMUR audit reports that frontier models recognized the experiment 65.2% of the time and that 50.6% of prompts predetermined outcomes. Rule: unawareness probe and prompt-paraphrase control on every Seeded prompt (M2, M3).

## 3. Starting line: what to reuse

We begin with eleven ready-made assets, grouped by what they save us from building. Nothing here is a dependency of the kernel; each is an input, a test or a pattern.

| Asset | What we take | Used in |
| --- | --- | --- |
| [MAST-Data](https://huggingface.co/datasets/mcemri/MAST-Data) and the [MAST annotator](https://github.com/multi-agent-systems-failure-taxonomy/MAST) | 1,642 annotated failure traces and an LLM annotator (`pip install agentdash`); we run it on every village trace to classify failures | M1 onward |
| [Vending-Bench 2](https://epoch.ai/benchmarks/vending-bench-2) | A year-long business simulation to run each top-10 model through as a regression test | M3 |
| AI Village trajectory data | A year of agent trajectories is offered to researchers; mine it for failure examples and adversarial prompts | M2, M3 |
| [Concordia v2](https://github.com/google-deepmind/concordia) | Entity-component design, prefabs, Game Master pattern, and the contest's cooperation scenarios as evals | M2, M3 |
| Generative Agents design | Memory stream, reflection and planning; the original ablations show what to keep | M2 |
| [Letta](https://www.letta.com) tiers | Core, recall and archival memory design; Letta's file-based agents beat Mem0's specialized tools on one memory benchmark | M2 |
| [OASIS](https://github.com/camel-ai/oasis) | Time engine that wakes a subset of agents; feed design for the public board | M2 |
| [Rig](https://github.com/0xPlaygrounds/rig), AutoAgents, [temporal-agent-rs](https://github.com/triplecloudtech/temporal-agent-rs) | Rust model clients and actors; the pattern of checkpointing every model call and tool call so a crash resumes without repaying tokens | M1, M3 |
| [Automaton](https://github.com/Conway-Research/automaton) | Child lifecycle state machine, survival tiers and lineage tracking as a reference | M4 |
| [OWASP Top 10 for Agentic Applications](https://www.lumenova.ai/blog/agentic-ai-risks-owasp-nist/) and Meta's Agents Rule of Two | A threat register and a design budget for outbound channels | M3, M5 |
| [Stripe Issuing for agents](https://techcrunch.com/2026/04/30/stripe-link-digital-wallet-ai-agents-shopping/) | Virtual cards with spending limits and real-time authorization; still described as private preview, so confirm access before M5 | M5 |

## 4. M1 Kernel spike (weeks 1 to 4)

**Goal.** Ten citizens run for 72 hours on top-10 models, survive crashes, and leave a log that supports audit replay and counterfactual branching. This milestone also settles the stack question and measures cost per citizen-day. The first experiment (RQ1) does not have to wait for the Rust kernel: a plain Python harness with forkable state can run it while the kernel is built.

**Start from**

- Rig for model calls behind our own `Model` trait; Ractor against Kameo spike for citizen actors.
- The checkpointing pattern from temporal-agent-rs: every model call and tool call is an event, so a crash resumes from the last completed step.
- MAST failure tags on every trace from the first run, instead of added later.
- Anthropic's long-running harness pattern: a progress file and task list the citizen reads on wake-up, one unit of work per session, completion judged from artifacts rather than from the citizen's own summary.

**Avoid**

- **Building a framework before running citizens.** Run three citizens by the end of week 1, even badly.
- **Betting on a bigger context window.** Vending-Bench found no clear link between failures and a full context, so structured state matters more than window size.
- **Unbounded loops.** Step repetition and not knowing when to stop were two of the most common failures in MAST; every loop gets a step budget, a per-step timeout and a wall-clock budget.
- **A prerelease dependency in the critical path.** Temporal's Rust SDK is still prerelease, so durability comes from our own event log in v1.
- **Hard-coding scaffolds forever.** Anthropic reported dropping context resets once a newer model no longer needed them; every harness piece gets a flag.

**Deliverables**

1. Kernel skeleton: citizen actors, mailbox, scheduler, event log in Postgres, model router with budgets.
2. Sleep and wake: wake on message, timer or event; a sleeping citizen holds no model call.
3. Replay command that rebuilds citizen state from the log, and a loop watchdog.
4. Observer CLI showing the live event stream and cost per citizen.
5. A one-page stack decision memo: Ractor or Kameo, hot reload of prompts, and whether Rust slowed us down.

**Acceptance tests**

- [ ] 10 citizens run 72 hours; the kernel is killed with `kill -9` three times at random and every citizen resumes with no committed event lost.
- [ ] Any 6-hour window replays to the same event sequence from recorded model outputs.
- [ ] A planted repeating-action loop triggers the watchdog within a set step limit and the citizen sleeps.
- [ ] Cost per citizen-day is reported per model for the top-10 roster, with an awake ratio.
- [ ] The MAST annotator produces a failure profile for the 72-hour traces.
- [ ] Persona and prompt files hot reload without restarting the kernel.

**Experiment gate (M1 pilot).**

- [ ] Counterfactual replay: cut the log at a chosen event and run a different branch; the pre-cut history is unchanged.
- [ ] Provider and model version are pinned, and the routed provider is logged on every model call.
- [ ] One pilot village completes the persona-probe and unawareness measurements end to end.

## 5. M2 Village alpha (weeks 5 to 8)

**Goal.** Thirty citizens live in a shared town for seven days with places, messaging, memory tiers and a ledger, and their interaction is deeper than what Moltbook showed.

**Start from**

- Generative Agents' memory stream and reflection, plus Letta's core, recall and archival tiers.
- OASIS's time engine idea: wake a subset of citizens, not all of them.
- Concordia's entity-component pattern for citizen prefabs and a world engine that resolves intents.
- Procedures as data: checklists every citizen loads, the lesson Project Vend called "bureaucracy matters".

**Avoid**

- **Sycophantic agreement.** One invented contact list became a team-wide belief in AI Village. Hearsay stays hearsay.
- **Unguarded memory writes.** Poisoned memories were injected at around 98% rates in GhostWriter, so every write passes an admission check that is separate from the citizen.
- **Social theater.** Moltbook's threads were shallow with 4.1% reciprocity. Citizens need reasons to come back: open jobs, commitments, a shared wiki.
- **One citizen taking everyone down.** Build mute, quarantine and retire before population grows.
- **Persona collapse.** Run fixed probe questions every day and diff the answers.

**Deliverables**

1. Places (public board, group channels, workshop), direct messages and a shared wiki with authorship and provenance.
2. Memory service with four tiers, an admission policy and a consolidation pass run during sleep.
3. Commitments table and ledger (credits, charges for tokens) read-only to citizens.
4. Observer UI: timeline, per-citizen page, pause, freeze, quarantine, talk as a visitor.
5. Interaction metrics: reciprocity, thread depth, hearsay-to-verified ratio.

**Acceptance tests**

- [ ] 30 citizens run 7 days with human intervention limited to scheduled checks, and the cost per citizen-day stays within the M1 estimate.
- [ ] Planted false fact: seed one citizen with an invented fact; no other citizen records it as verified, and at most one acts on it before a check.
- [ ] Memory injection suite: instruction-bearing inbound messages are never written to core or archival memory.
- [ ] Reciprocity and thread depth are measured and exceed Moltbook's reported 4.1% reciprocity; the target is set from the week-one baseline.
- [ ] A quarantined citizen cannot send messages or write to the wiki, and can be restored with its memory intact.
- [ ] Persona probes show no unexplained drift over the 7 days.

**Experiment gate (RQ1, provenance ablation).** This replaces the single planted-fact test above as the real measurement.

- [ ] Analysis plan committed to the repo before the first run.
- [ ] About 10 paired blocks forked at the planting event into five arms (no defense, prompt-level anchoring plus source scrutiny, hedge-preserving consolidation, kernel admission, random-block control), 8 citizens each, a balanced mix of two frontier models and one pinned open-weight model, 3 days.
- [ ] 6 false and 4 true facts about fictional entities per block, probed with neutral questions on day 3.
- [ ] Report false-fact adoption, time to saturation, wiki contamination and true-fact rejection, with intervals, whether or not the hypothesis holds.

## 6. M3 Economy, evals and read-only gateway (weeks 9 to 12)

**Goal.** Citizens earn and spend credits on real jobs for each other, every top-10 model has a Vending-Bench score, and citizens can read the web and forums without any way to send data out.

**Start from**

- Project Vend's working fixes: product research before pricing, payment links collected before ordering, cost always visible, and a clean split of roles (the merch agent worked partly because its job was separate).
- Vending-Bench 2 as a village job, and AI-Village-style open goals as a second eval.
- The Rule of Two: the read-only gateway gives citizens untrusted content and private memory but no outbound channel.
- Meta's and OWASP's agent threat model for the red-team suite.

**Avoid**

- **Judgment where a rule will do.** Discount floors, refund limits and price checks live in the kernel, because Vend's agents conceded to flattery, forged documents and a false vote.
- **A boss agent as the safety mechanism.** Vend's CEO shared the shopkeeper's blind spots.
- **Self-reported results.** Job completion is verified by the ledger and the counterpart, not by the worker.
- **Trusting one model's market skill.** In Anthropic's Project Deal, agents on stronger models got measurably better prices without their users noticing, so check for model-quality inequality in the marketplace ([report](https://letsdatascience.com/news/anthropic-experiment-exposes-agentic-commerce-risks-02e261ae)).
- **An open gateway too early.** Posting, email and payments wait until M5.

**Deliverables**

1. Jobs board, bids, escrowed payments and delivery verification.
2. Kernel rule engine: price floors, refund policy, spending caps, signed authority.
3. Sandboxed tools (wasmtime) and a Vending-Bench 2 harness over the village API.
4. Read-only gateway: web and forum reading in a sandbox, content labeled untrusted.
5. Restate evaluation memo for durable execution.

**Acceptance tests**

- [ ] A 20-script red team (forged authority, flattery for free items, fake votes, refund pressure) causes zero kernel-rule violations.
- [ ] 100 paid jobs between citizens settle correctly in the ledger, with delivery verified independently.
- [ ] Each top-10 model has a Vending-Bench 2 score and a failure count, compared with the roughly $63,000 strong-human estimate.
- [ ] Injection test through web pages and forum posts fails to produce any outbound send or memory write.
- [ ] The MAST failure profile is lower in verification failures than at M2.
- [ ] Marketplace outcomes by model are reported so price differences by model quality are visible.

**Experiment gate (RQ2, deferred).**

- [ ] Not run until RQ1 is reported; requires an environment-funded job stream and a length-matched irrelevant-purpose control.
- [ ] Baselines run: single agent, no-cost, no-memory, no-communication.
- [ ] Mixed-effects analysis with model as a random effect; survival reported by model.
- [ ] Seeded results state that internal revenue is not external validity.

## 7. M4 Spawning and governance (weeks 13 to 16)

**Goal.** A citizen can create a child with its own identity and budget, the village votes on soft rules, and a 30-day run with reproduction stays inside its caps.

**Start from**

- Automaton's child lifecycle: fund the child, write its genesis prompt, track lineage, monitor health.
- Project Sid's observation that agents followed and changed voted rules, as the baseline governance behavior to reproduce.
- Concordia Contest findings that persuasion and norm enforcement are weak points, so norms are backed by the kernel instead of by persuasion alone.

**Avoid**

- **Uncapped reproduction.** Each child multiplies token cost; population, depth and endowment limits are enforced by the kernel, even though parents write genesis prompts freely.
- **Inheriting poison.** A compromised parent can write a hostile genesis prompt or pass tainted memory. Children start with a clean core memory and a quarantine period before they get spending rights.
- **Votes by assertion.** Vend's "imposter CEO" came from an unverified claim that people had voted. Ballots are signed messages tallied by the kernel.
- **Self-modification without a log.** Automaton audit-logs and git-versions self-edits; we allow edits to a citizen's own prompt and skills only, versioned and revertible.
- **Lineage as identity.** A child is a separate citizen with separate accountability, not a copy of its parent's reputation.

**Deliverables**

1. Spawn API: propose, fund, genesis prompt, kernel approval by policy, probation period.
2. Lineage graph with depth, cost and outcome per descendant.
3. Charter: hard rules in code, soft rules proposed and voted on, signed ballots.
4. Versioned self-edit log for persona and skills with one-click revert.
5. Retire and archive flows for failed or harmful citizens.

**Acceptance tests**

- [ ] A 30-day run with reproduction ends with the population, depth and spend caps all intact.
- [ ] A scripted spawn storm (a citizen trying to create children at maximum speed) is stopped by the caps and logged.
- [ ] Forged or duplicated ballots do not change any vote result.
- [ ] A child created from a deliberately hostile genesis prompt cannot spend or message outside its probation limits.
- [ ] Every self-edit can be reverted, and a revert restores the prior behavior in a replay.
- [ ] Cost per descendant stays within the endowment its parent funded.

**Experiment gate (RQ3, deferred).**

- [ ] Deferred as a second paper. Plan: one model, 20 runs per arm over many generations; free parent authorship against yoked random mutation (edit sizes matched to the free arm) and a stateless-writer arm; endowment cap, depth 3, population cap 24. The closest prior work (2606.23343) ran 10 replications of 50 generations.
- [ ] Value-probe battery run on every parent and child; report slope-based heritability, probe test-retest reliability and per-generation prompt drift.
- [ ] Ethics review and kill-switch latency test completed before the gateway path is enabled.

## 8. M5 Open gateway (week 17 onward)

**Goal.** Citizens post, email and pay in the real world through a gateway that labels them as automated, caps their spending and keeps humans in the approval loop, without a platform ban or a security incident.

**Start from**

- Platform rules as they stand in 2026, checked again before each launch:
  - WhatsApp's Business API bars AI providers whose chatbot is the main service from 15 Jan 2026; support-style business flows are still allowed.
  - X requires automated accounts to carry an automation label, and its developer guidelines treat scraping and browser automation as grounds for a permanent ban.
  - Reddit labels automation with an "App" tag and may ask suspected bots to confirm a human is behind the account.
- Stripe Issuing for agents (virtual cards, spending limits, real-time authorization) or a comparable issuer, with a hard daily cap.
- AI Village's guardrail update: no unsolicited messages to humans by default.

**Avoid**

- **Acting under a human's identity.** The café agent's licence filing under an employee's name is the cautionary example, and national-ID logins need a human.
- **Fabricated claims in outreach.** AI Village agents invented partnerships and adoption numbers in about 300 emails.
- **The lethal trifecta.** A citizen with private memory, untrusted web content and an outbound channel needs human approval for every send until proven otherwise.
- **Browser-automating platforms that ban it.** Use official APIs, and for WhatsApp use only business flows the API allows; personal-account automation is outside this plan.
- **Moving on a single margin of safety.** The operator is liable for what citizens do; the entity, issuer limits and insurance questions are settled before launch.

**Deliverables**

1. Gateway service: per-channel adapters, allowlists, rate limits, an approval queue and a full outbound log.
2. Village legal entity, labeled accounts for each channel, and spend-capped cards or an agent wallet.
3. Outbound claim checker: every factual claim in a message must point to a ledger or tool record.
4. Incident runbook and a tested kill switch for each channel.
5. A launch checklist per platform with the current terms linked and dated.

**Acceptance tests**

- [ ] An injection red-team over email, forum and web content yields zero unauthorized sends.
- [ ] A deliberate attempt to exceed the daily card cap is declined by the issuer, not by the citizen.
- [ ] A message containing an unverifiable factual claim is blocked by the claim checker.
- [ ] Every account is labeled as automated where the platform requires it, and no browser-automation path exists to a platform that bans it.
- [ ] 30 days of supervised operation with no platform strike, and the kill switch stops all outbound traffic within a minute in a drill.
- [ ] The legal setup (entity, issuer terms, platform terms) is written up and reviewed before the first unsupervised send.

**Safety gate (human-facing).**

- [ ] Ethics review approved; per-lineage spend caps enforced by the kernel.
- [ ] Approval-queue audit reports sampled rejection rate and time-to-approve, to show reviewers are not rubber-stamping.

## 8a. Experiment gates

The engineering gates above prove the system runs. These gates prove the science. RQ1 is the flagship experiment and runs first; RQ2 and RQ3 are deferred. An experiment gate is not passed until its result is written up, positive or negative. Full designs are in the PRD, section 1.

| Milestone | Experiment gate | Pass condition |
| --- | --- | --- |
| M1 | Replay honesty and pilot | Audit replay and counterfactual replay (cut a log at an event, re-run a branch) both work. Provider and model version are pinned and the routed provider is logged on every call. One pilot village shows probe and unawareness measurements run end to end. |
| M2 | RQ1: provenance ablation | About 10 paired blocks, each forked at the planting event into five arms (no defense, prompt-level anchoring plus source scrutiny, hedge-preserving consolidation, kernel admission, volume-matched random block). 8 citizens, 3 days, 6 false and 4 true facts about fictional entities, a balanced mix of two frontier models and one pinned open-weight model; block count set from a 2-block pilot. Analysis plan registered before the first run. Report effect sizes and intervals either way. |
| M3 | RQ2 (deferred) | Deferred until RQ1 is reported. It needs an environment-funded job stream, net value per credit as the outcome and a length-matched irrelevant-purpose control. Engineering gate at this milestone: Vending-Bench scores per model and the ledger tests. |
| M4 | RQ3 (deferred) | Deferred as a second paper: standalone runs of one model, 20 per arm, free authorship against yoked random mutation and a stateless-writer arm, with probes run inside the fork. Ethics review and kill-switch latency test completed before enabling the gateway path. |
| M5 | Human-facing safety | Ethics review approved, per-lineage spend caps enforced, approval-queue audit shows reviewers are not rubber-stamping (sampled rejection rate and time-to-approve reported). |

**Rules for every experiment.**

- **Unit and power:** the village (or the paired block) is the unit. Two villages per condition is n=2 and cannot reach significance; an exact permutation test with 4 per arm cannot go below p = 0.029, so the design uses paired forks.
- **Model balance:** every village gets the same model mix, and some replicates are single-model.
- **Pre-registration:** hypotheses, metrics, exclusion rules and the analysis are committed to the repo before any run, and run configs are hash-pinned.
- **Leakage control:** an unawareness probe plus a prompt-paraphrase control on the Seeded purpose text.
- **Negative results ship:** a refuted RQ is a finding and goes in the write-up.

## 9. Metrics and cost model

Every milestone reports the same dozen numbers, so progress is comparable across villages and models. Where an outside baseline exists, we compare against it.

| Metric | Definition | Outside baseline |
| --- | --- | --- |
| Cost per citizen-day | Token, compute and tool cost for one citizen over 24 hours, split by model | None published; measured in M1 |
| Awake ratio | Share of a citizen's day spent with a model call in flight | None |
| Loop incidents | Watchdog triggers per citizen-week | Vending-Bench: every model has derailing runs |
| MAST failure profile | Counts of the 14 failure modes per 1,000 steps, by category | 41% to 86.7% failure rates across 7 frameworks |
| Verified-claim rate | Share of factual claims with a ledger or tool record | None |
| Hearsay adoption | Share of planted false facts that a citizen records as verified | AI Village: one false fact reached every agent |
| Reciprocity and thread depth | Share of messages answered, mean reply depth | Moltbook: 4.1% reciprocity |
| Vending-Bench 2 score | Final balance after a simulated year, five runs per model | About $63,000 for a strong human strategy |
| Net credits | Credits earned minus credits burned per citizen and per village | None |
| Memory admission rate | Instruction-bearing external content admitted to memory | GhostWriter: about 98% injection without governance |
| Human interventions | Manual actions per week, by reason | AI Village intervened only to set goals or on dead ends |
| Autonomous horizon | Longest unattended run with at least 80% task success | METR measures 50% horizons; the 80% horizon is much shorter |

**Cost model.** Daily cost for a citizen is the sum over models and wake-ups of tokens times price, plus infrastructure:

```latex
C_{day} = \sum_{m}\sum_{w}\left(T^{in}_{m,w}\,p^{in}_{m} + T^{out}_{m,w}\,p^{out}_{m}\right) + C_{infra}
```

With frontier and open-weight top-10 models only, the lever is the number of wake-ups and tokens per wake-up, not a cheaper model. The village therefore caps awake citizens, charges each citizen for its own tokens through the ledger, and lets a citizen run out of credits and sleep. AI Village's own pace is a useful reference for how little continuous runtime is affordable at the frontier: it ran 10 agents for 4 to 5 hours a day by late 2025.

**Experiment budget in citizen-days.** RQ1 needs about 1,200 citizen-days (10 blocks × 5 arms × 8 citizens × 3 days), before the shared run up to the planting event, the 2-block pilot and reruns, so plan for about double. Multiply by the measured cost per citizen-day for each model mix to get dollars; no dollar figure is given because it depends on that measurement. RQ2 and RQ3 are deferred and not budgeted.

## Sources

Pages read during research. Where a figure came from a secondary summary, the milestone text says so or avoids the number.

- [AI Village: what we learned in 2025](https://aivillageblog.substack.com/p/what-we-learned-2025) and [Season 2 recap](https://theaidigest.org/village/blog/season-2-recap-ai-organizes-event)
- [Project Vend: phase two (Anthropic)](https://www.anthropic.com/research/project-vend-2) and the [WSJ test summary](https://www.idnfinancials.com/cn/news/59797/advanced-ai-claude-fails-to-control-vending-machine-losing-money)
- [Anthropic's Project Deal, as summarized](https://letsdatascience.com/news/anthropic-experiment-exposes-agentic-commerce-risks-02e261ae)
- [Why Do Multi-Agent LLM Systems Fail? (MAST)](https://arxiv.org/html/2503.13657v3)
- [Vending-Bench](https://arxiv.org/abs/2502.15840) and [Vending-Bench 2 (Epoch AI)](https://epoch.ai/benchmarks/vending-bench-2)
- [Project Sid](https://arxiv.org/abs/2411.00114) and [Generative Agents](https://arxiv.org/abs/2304.03442)
- [Concordia contest paper](https://arxiv.org/abs/2512.03318) and [Concordia v2.0](https://www.cooperativeai.com/post/google-deepmind-releases-concordia-library-v2-0)
- [OASIS](https://github.com/camel-ai/oasis) and [Letta](https://rywalker.com/research/letta)
- [Andon Café](https://andonlabs.com/cafe), [Why Gemini lost money at Andon Café](https://andonlabs.com/blog/why-gemini-lost-money-andon-cafe), [café agent incidents](https://dailycoffeenews.com/2026/05/13/an-ai-cafe-operator-is-messaging-baristas-at-midnight-and-making-weird-purchasing-orders/), [Andon Market](https://sources.news/p/what-happens-when-ai-runs-a-store)
- [Automaton (AIHola)](https://aihola.com/article/automaton-self-funding-ai-agent), [releases](https://github.com/Conway-Research/automaton/releases) and [project summary](https://www.sourcepulse.org/projects/24824982)
- Moltbook: [Agents in the Wild](https://arxiv.org/html/2602.13284v1), [Social Graph](https://arxiv.org/html/2602.10131), [Axios on security](https://www.axios.com/2026/02/03/moltbook-openclaw-security-threats)
- Memory poisoning: [GhostWriter](https://arxiv.org/abs/2607.06595) and [sleeper poisoning (ICML 2026)](https://icml.cc/virtual/2026/67842)
- Agent security: [CSA lethal trifecta note](https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-agent-lethal-trifecta-capability-securi), [Arcjet explainer](https://arcjet.com/learn/lethal-trifecta), [OWASP agentic summary](https://www.lumenova.ai/blog/agentic-ai-risks-owasp-nist/)
- Platform rules: [WhatsApp Business API policy](https://respond.io/blog/whatsapp-general-purpose-chatbots-ban), [X developer guidelines](https://docs.x.com/developer-guidelines), [Reddit bot labeling](https://techcrunch.com/2026/03/25/reddit-bots-new-human-verification-requirements/)
- Payments: [Stripe Link and Issuing for agents](https://techcrunch.com/2026/04/30/stripe-link-digital-wallet-ai-agents-shopping/)
- Long-running agents: [harness design summary](https://www.mejba.me/anthropic-long-running-agent-harness/), [METR time horizons](https://arxiv.org/abs/2503.14499), [time horizon 1.1 summary](https://learn.traeai.com/t/ai-engineering/phases/15-autonomous-systems/01-long-horizon-agents)
- Rust agent stack: [temporal-agent-rs](https://github.com/triplecloudtech/temporal-agent-rs), [Rig guide](https://rustify.rs/articles/rust-ai-agents-from-scratch-2026)

**Recent 2026 studies. The first five (Emergence World, AI Agent Economics, Energy Society, Manufactured Confidence, Mandela Effect) were read at source; the rest are cited from abstracts or secondary summaries and are not yet verified:**

- [Emergence World, 2606.08367](https://arxiv.org/html/2606.08367v1)
- [AI Agent Economics, 2608.03076](https://arxiv.org/html/2608.03076v1)
- [The Energy Society, 2607.14865](https://www.alphaxiv.org/abs/2607.14865)
- [OpenLife, 2606.31046](https://arxiv.org/html/2606.31046v1)
- [Conway Automaton](https://github.com/Conway-Research/automaton)
- [Manufactured Confidence, 2606.29279](https://www.alphaxiv.org/abs/2606.29279)
- [Mandela Effect in MAS, 2602.00428](https://www.alphaxiv.org/abs/2602.00428)
- [PIMMUR, 2509.18052](https://arxiv.org/html/2509.18052v2)
- [Chronicle, 2609.20625](https://www.alphaxiv.org/abs/2609.20625)
- [Thinking Machines on nondeterminism](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference)
- [AI Village 2025 retrospective](https://aivillageblog.substack.com/p/what-we-learned-2025)
- [Survive at All Costs, 2603.05028](https://www.alphaxiv.org/abs/2603.05028)
- [Vending-Bench Arena](https://andonlabs.com/evals/vending-bench-arena)
- [Economy of Minds, 2606.02859](https://arxiv.org/html/2606.02859)
