# Decisions

Each decision has an ID. To change one, add a new entry that says which one it supersedes.

| ID | Decision | Why | Status |
|---|---|---|---|
| D-001 | Run on **Amazon EKS** (not ECS/Fargate) | Kubernetes is the learning and CV goal; ECS would be cheaper and simpler | Accepted |
| D-002 | MVP cost source is the **Cost Explorer API** (`GetCostAndUsage`, `GetCostForecast`); **CUR 2.0 Data Exports** (Parquet in S3) is a later upgrade | CE API needs no S3/Athena setup and data is already aggregated; CUR gives line items and resource IDs later | Accepted |
| D-003 | Store aggregates and findings in **RDS PostgreSQL** (already in Terraform) | Relational queries, upserts, JSONB for rule details; reuse existing infra | Accepted |
| D-004 | App pods get AWS access via **EKS Pod Identity**; the LB controller stays on **IRSA** | Pod Identity is the newer, simpler option (agent add-on already installed); IRSA already works for the controller | Accepted |
| D-005 | Secrets via **AWS Secrets Manager + External Secrets Operator**, replacing `scripts/create-db-secret.sh` | No manual step, rotation-friendly, nothing secret in git | Accepted |
| D-006 | Delivery: GitHub Actions builds and pushes images; **Argo CD** deploys from git (GitOps). `deploy.yml` is kept only until Argo CD works | Git is the record of what runs; easy rollback; common in industry | Accepted |
| D-007 | **staging** and **prod** as separate Terraform root folders (`envs/`) using shared modules, separate state keys, in **one AWS account** | Clear separation with low cost; README states that real prod would use separate accounts | Accepted |
| D-008 | Frontend: **React + TypeScript + Vite**, served by nginx in its own Deployment behind the same ALB (`/` frontend, `/api` api) | Same stack as CloudDocs-AI; one domain, no CORS | Accepted |
| D-009 | Sign-in: **Cognito user pool with ALB authentication** (`alb.ingress.kubernetes.io/auth-type: cognito`); API verifies the ALB-signed JWT | No auth code in the frontend; admin-created users only | Accepted |
| D-010 | Region `ap-southeast-1` for everything; Cost Explorer is called at its `us-east-1` endpoint | CE is a global service served from us-east-1 | Accepted |
| D-011 | Alerts by **Amazon SES** email (+ optional Slack webhook in Secrets Manager); dedupe by fingerprint | SES is cheap and native; SES sandbox is fine for verified recipients | Accepted |
| D-012 | Environments run **on demand**, not 24/7; costs documented per hour | Always-on prod ≈ USD 275/month is too much for a portfolio | Accepted |
| D-013 | **One Python package and one image** (`services/cloudcost`) with subcommands `api`, `ingest`, `scan`, `notify`, `migrate` | Shared models/config, one build, one scan; separate Deployments/CronJobs still scale and fail independently | Accepted |
| D-014 | Waste prices from a **static price table** per region in config for MVP; AWS Pricing API later | Predictable, testable; Pricing API adds complexity | Accepted |
| D-015 | Repository renamed to **`cloudcost-watch`**; Terraform `project` default becomes `cloudcost-watch` | The project is no longer a lab | Accepted (done 2026-11-21) |
| D-016 | Kubernetes packaging stays **Kustomize** (no Helm chart for our own app) | Already in place and simple; Helm used only for third-party add-ons | Accepted |
