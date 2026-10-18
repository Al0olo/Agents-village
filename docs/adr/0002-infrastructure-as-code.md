# ADR-0002 — Infrastructure as code: Terraform on AWS, kept minimal

- **Status:** Proposed (owner to confirm cloud and tool)
- **Date:** 2026-10-18
- **Authors:** Abdullah Farag, Claude
- **Context links:** [PRD section 7](../prd.md), [S2](../sprints/S2-rq1-pilot.md), [S3](../sprints/S3-rq1-main.md), [S4](../sprints/S4-rust-kernel.md), [ADR-0001](0001-storage-and-memory.md)

## Context

The RQ1 pilot and main run need repeatable infrastructure: somewhere to run many villages in parallel, durable storage for logs and blobs, secrets for model keys, and a hard spend cap with a kill switch. The kernel (S4) later needs Postgres and a service deployment. Click-built infrastructure would make results hard to reproduce and the cost cap hard to trust.

The owner already runs AWS and Terraform for another product, so the tooling and habits exist. Nothing here needs always-on capacity until S4.

## Decision

1. **IaC is a first-class deliverable, in `infra/`**, reviewed through pull requests like code. Nothing is created by hand except the state backend bootstrap.
2. **Tool:** Terraform (pinned, with OpenTofu as a drop-in) and remote state in S3 with locking. Proposed, pending the owner's confirmation.
3. **Cloud:** AWS, one region, chosen for the owner's existing expertise and billing setup. Every service used must have a plain equivalent (Postgres, S3-protocol storage, containers) so the project is not locked in.
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
- Owner to confirm cloud and tool, then set this ADR to Accepted.
- A rule for agents working in `infra/` is in `.claude/rules/infra.md`.

## Alternatives considered

1. **Pulumi or CDK.** Fine tools, but the owner's existing Terraform practice wins on speed.
2. **A single VM with Docker Compose.** Cheapest for the pilot, but weak for parallel arms, secrets, state and a trustworthy kill switch; may be used locally.
3. **Serverless batch (AWS Batch, Modal, Lambda).** Possible later; adds a second execution model before one is proven.
4. **No IaC until S4.** The pilot and main run would run on hand-built infrastructure, and the cost cap would be a promise.

## References

- [PRD section 7, tech stack](../prd.md)
- Sprint tickets listed above
