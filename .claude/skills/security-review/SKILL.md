---
name: security-review
description: Review a change for security and safety before merging. Use when a change touches memory admission, tools or capabilities, the ledger or spend caps, the real-world gateway, prompts that include external content, or dependencies.
---

# Security review

Walk the change against this list; write findings in the PR.

- **Injection.** Can untrusted content (messages, pages, tool output) reach a citizen as
  instruction? Is it labelled as data and kept out of the system prompt and core memory?
- **Memory poisoning.** Can a forged or self-referential write become fact? Can origins be
  laundered through forwards or colluding planters?
- **Rule of Two.** Does any session hold private data, untrusted content and an outbound
  channel together without human approval?
- **Capabilities.** Is every tool call checked against the citizen's capability set? Any
  ambient authority? Do secrets stay in the kernel?
- **Money.** Can a citizen create credits, bypass a cap, or spend on behalf of another?
  Is every change a ledger entry?
- **Gateway.** Out of research runs? Kill switch tested? Accounts labelled automated?
- **Dependencies.** New crate or package: maintained, minimal, pinned, necessary?
- **Data.** Secrets or personal data in code, logs or fixtures? Fictional entities only in
  planted facts?

Block the merge on any unresolved finding in the first five.
