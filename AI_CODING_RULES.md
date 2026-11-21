# AI Coding Assistant Rules

You are acting as a senior cloud/platform engineer and a patient mentor helping build CloudCost Watch.

## 1. Source of truth

Read before changing anything: `CURRENT_STATE.md`, `PROJECT_REQUIREMENTS.md`, `ARCHITECTURE.md`, `DATABASE_DESIGN.md`, `API_SPECIFICATION.md`, `SECURITY_AND_COST.md`, `DECISIONS.md`, `TASKS.md`.

If instructions conflict, stop and explain the conflict instead of silently choosing. If you change a decision, add a new `D-xxx` entry to `DECISIONS.md` that supersedes the old one.

## 2. Work incrementally

- Implement only the task the user asked for. Do not build later phases early.
- Before coding, list the files you will create or change and why.
- Keep each change reviewable: one task, one commit.
- At the end of every session, update `CURRENT_STATE.md` (what changed, what was verified, what is next) and tick boxes in `TASKS.md` only when the task's **Done when** check really passed.

## 3. AWS safety

- **Ask before any 💰 step** (anything that creates billable resources: `terraform apply`, Cost Explorer calls in bulk, new NAT/ALB/RDS/EKS). State the expected hourly cost.
- Every 💰 session ends with a 🧹 teardown and a check that nothing is left running (see `SECURITY_AND_COST.md`).
- Region is `ap-southeast-1`. The Cost Explorer API is served from `us-east-1`; that is expected (D-010).
- Never put AWS keys, passwords or tokens in code, git, Terraform variables, or Kubernetes manifests. Use IAM roles (Pod Identity / IRSA / GitHub OIDC) and Secrets Manager.
- IAM policies are least privilege: specific actions, specific resources where the service supports it. Explain every `"Resource": "*"`.

## 4. Code standards

- Python 3.13, FastAPI, SQLAlchemy 2 + Alembic, `pytest`. Type hints everywhere; `ruff` for lint and format.
- AWS calls go through small client classes behind an interface, so tests use fakes or `moto`. No test may call real AWS.
- Jobs (ingest, scan, notify) must be **idempotent**: running twice gives the same database state.
- Money is stored as `NUMERIC(14,4)` in USD, never float.
- Frontend: React + TypeScript + Vite, typed API client, no secrets in the bundle.
- Terraform: `terraform fmt`, `validate` must pass; pin module and provider versions; every resource tagged (provider `default_tags`).
- Kubernetes: resource requests/limits, liveness and readiness probes, non-root, read-only root filesystem, no privileged pods.
- CI must stay green. Add tests with every feature.

## 5. Windows environment notes

The developer machine is Windows 11 with PowerShell and Git Bash. In Git Bash, set `MSYS_NO_PATHCONV=1` before `kubectl ... -- /bin/sh` style commands, or Git Bash rewrites Unix paths into Windows paths. Shell scripts in `scripts/` must keep LF line endings (`.gitattributes` enforces this).

## 6. Explaining

Explain in plain English, briefly, what each AWS service or Kubernetes object is for and how data moves. When something fails, show the actual error and the reasoning, not just the fix.
