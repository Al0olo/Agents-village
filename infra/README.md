# infra

Infrastructure as code for Agent Village. OpenTofu on AWS. Planned, not built yet: see [ADR-0002](../docs/adr/0002-infrastructure-as-code.md) and tickets S2-T13 to T17, S3-T13 and S4-T19 to T21.

Planned layout: `tofu/modules/` (storage, secrets, budget, runner, database) and `tofu/envs/` (pilot, main, kernel).
