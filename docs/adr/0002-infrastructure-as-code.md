# ADR-0002 — Infrastructure as code: OpenTofu on AWS, kept minimal

- **Status:** Accepted (2026-10-18; owner delegated the choice and asked for the best option)
- **Date:** 2026-10-18
- **Authors:** Abdullah Farag, Claude
- **Context links:** [PRD section 7](../prd.md), [S2](../sprints/S2-rq1-pilot.md), [S3](../sprints/S3-rq1-main.md), [S4](../sprints/S4-rust-kernel.md), [ADR-0001](0001-storage-and-memory.md)

## Context

The RQ1 pilot and main run need repeatable infrastructure: somewhere to run many villages in parallel, durable storage for logs and blobs, secrets for model keys, and a hard spend cap with a kill switch. The kernel (S4) later needs Postgres and a service deployment. Click-built infrastructure would make results hard to reproduce and the cost cap hard to trust.

The owner already runs AWS and Terraform for another product, so the tooling and habits exist. The workload is light on compute: villages mostly wait on model APIs. Nothing here needs always-on capacity until S4.

## Decision

1. **IaC is a first-class deliverable, in `infra/`**, reviewed through pull requests like code. Nothing is created by hand except the state backend bootstrap.
2. **Tool:** OpenTofu (pinned minor version), with remote state in S3 using locking and OpenTofu's client-side state encryption (AWS KMS key). Reasons: the project is open source and OpenTofu is MPL-2.0 under Linux Foundation stewardship, so contributors and forks can use it freely; it is a drop-in for Terraform configurations and providers (its site cites 3,900+ providers and 23,600+ modules), so the owner's Terraform knowledge transfers; and native state encryption matters because state can hold secrets. Terraform itself is under the BUSL licence, which is why it is not the default here. Terraform stays a fallback because the configurations are compatible.
3. **Cloud:** AWS, one region, chosen for the owner's existing expertise and billing setup. Every service used must have a plain equivalent (Postgres, S3-protocol storage, containers) so the project is not locked in.
   **Compute:** ECS Fargate on-demand for experiment runners (no Spot: an interrupted village invalidates a block). Fargate removes host management and is enough for API-bound workloads; EC2 is reconsidered only if cost per citizen-day shows it matters.
4. **Phased scope:**
   - S2 and S3: object storage (versioned) for logs and blobs, secrets for model keys, budget alarms and a spend kill switch, a container image and a batch runner (ECS Fargate or EC2 spot) that launches arms together, CI deploys through GitHub OIDC with no static keys.
   - S4: RDS Postgres 16, the kernel service, observability.
   - S8: gateway infrastructure, only after the ethics review.
5. **Cost safety is infrastructure, not policy:** a budget alarm, an API-key spend limit at the router, and a kill switch that stops all runners.
6. **Research runs never get outbound access beyond the model gateway.** Network egress is allow-listed in the runner's security group.

## Consequences

### Positive

- Runs are reproducible and the environment is reviewable; the spend cap is enforced.
- Reuses the owner's existing knowledge, so the first runs are not delayed by tooling.

### Negative / trade-offs

- Setup time lands in S2, before the pilot.
- AWS is a commitment of convenience, not necessity; the container-first design keeps exit cheap.

### Follow-ups

- Tickets: S2-T13 to T17, S3-T13, S4-T19 to T21.
- The OpenTofu and Fargate choices rest on the vendor pages read for this ADR (OpenTofu's site and repository); a cost comparison of Fargate and EC2 waits for the measured cost per citizen-day.
- A rule for agents working in `infra/` is in `.claude/rules/infra.md`.

## Alternatives considered

1. **Terraform (BUSL).** Same configurations and skills, but a source-available licence is a poor default for an open-source research repo, and it lacks OpenTofu's native state encryption.
2. **Pulumi or CDK.** Fine tools, but the owner's existing Terraform-style practice wins on speed.
3. **A single VM with Docker Compose.** Cheapest for the pilot, but weak for parallel arms, secrets, state and a trustworthy kill switch; may be used locally.
4. **Serverless batch (AWS Batch, Modal, Lambda).** Possible later; adds a second execution model before one is proven.
5. **No IaC until S4.** The pilot and main run would run on hand-built infrastructure, and the cost cap would be a promise.

## References

- [OpenTofu](https://opentofu.org/) and its [repository](https://github.com/opentofu/opentofu) (MPL-2.0)
- [PRD section 7, tech stack](../prd.md)
- Sprint tickets listed above
