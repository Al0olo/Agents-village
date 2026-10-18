---
paths:
  - "infra/**"
  - ".github/workflows/**"
  - "**/Dockerfile"
---

# Infrastructure rules

- Terraform (pinned version), remote state with locking, one module per concern, one env per purpose. No hand-built resources.
- `terraform fmt -check`, `terraform validate` and a `plan` reviewed in the PR before any `apply`. Apply only from CI or by the owner.
- No static cloud credentials: GitHub OIDC roles with least privilege. No secrets in code, variables files or state outputs.
- Research runners: egress allow-listed to the model gateway only; versioned storage; budget alarm plus a tested kill switch before any live run.
- Tag every resource with project, sprint and owner so cost can be attributed.
- Containers first: nothing may depend on a cloud-only service without a plain equivalent (see ADR-0002).
