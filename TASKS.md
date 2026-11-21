# CloudCost Watch Task Board

The single place to track progress. Tick a box only when its **Done when** check has really been verified, and add the date. Decisions `D-xxx` are in `DECISIONS.md`.

Legend: `[ ]` todo · `[~]` in progress · `[x]` done · `[-]` dropped (say why) · 💰 creates billable AWS resources (ask first) · 🧹 includes teardown

## Progress overview

| Phase | Goal | Status |
|---|---|---|
| (pre) | EKS platform skeleton (lab): Terraform, K8s, CI, verified locally | ✅ Done (2026-11-20) |
| 0 | Rebrand to CloudCost Watch, account checks, tag activation | In progress (P0-01 done) |
| 1 | Cost ingestion + cost API, locally | Not started |
| 2 | Waste scanner | Not started |
| 3 | Dashboard frontend | Not started |
| 4 | Production platform: staging/prod, HTTPS, Cognito, Pod Identity, ESO, CronJobs, Argo CD (first AWS deploy) | Not started |
| 5 | Alerts and observability, SLOs, runbooks | Not started |
| 6 | Hardening, CUR 2.0, portfolio polish | Not started |

Phases 1–3 are built and tested **locally at USD 0** (Docker Compose / minikube, fakes for AWS), except a few real read-only Cost Explorer calls in P1-07.

---

## Phase 0: Rebrand and account checks

- [x] **P0-01** (2026-11-21: repo renamed, remote updated, Terraform `project` default, ECR repo name, tags and labels now `cloudcost-watch`) Rename the GitHub repo to `cloudcost-watch` (`gh repo rename cloudcost-watch`), update the local remote, change Terraform `project` default, ECR repo name, tags and README links (D-015).
  - Done when: `git remote -v` shows the new URL and CI is green.
- [ ] **P0-02** Sign in to AWS on the dev machine (`aws login` or `aws sso login --profile <profile>`); record the profile name in `CURRENT_STATE.md`.
  - Done when: `aws sts get-caller-identity` returns the admin identity.
- [ ] **P0-03** Rewrite `README.md` for CloudCost Watch: problem, users, screenshots placeholder, architecture diagram from `ARCHITECTURE.md`, how to run locally, cost section, roadmap.
  - Done when: README no longer describes a lab; links work.
- [ ] **P0-04** Check account facts: EKS versions in standard support (`aws eks describe-cluster-versions`), Route 53 hosted zone for `vuongdomain.click`, existing GitHub OIDC provider, whether IAM roles need a permissions boundary, SES sandbox status.
  - Done when: findings written into `CURRENT_STATE.md` §5 and `kubernetes_version` set accordingly.
- [ ] **P0-05** Activate cost allocation tags `Project` and `Environment` in Billing → Cost allocation tags. (Not retroactive; up to 24 h.)
  - Done when: both tags show `Active`.
- [ ] **P0-06** Account budget: USD 30/month (actual 50/80/100%, forecast 100%) plus a USD 10 "left running" budget filtered by tag `Project=cloudcost-watch`.
  - Done when: both budgets exist and the email recipient is confirmed.

## Phase 1: Cost ingestion and cost API (local)

- [ ] **P1-01** Create `services/cloudcost` package skeleton (`pyproject.toml`, `config.py` with pydantic-settings, `cli.py` subcommands, ruff, pytest), Dockerfile (non-root), CI job.
  - Done when: `cloudcost --help` lists subcommands; CI green.
- [ ] **P1-02** SQLAlchemy models + first Alembic migration for `cost_daily_service`, `cost_daily_tag`, `cost_forecast`, `job_run` (see `DATABASE_DESIGN.md`); `cloudcost migrate`.
  - Done when: migration runs against Compose Postgres, `alembic downgrade base` and `upgrade head` both work.
- [ ] **P1-03** Cost Explorer client interface + boto3 implementation (pagination with `NextPageToken`, us-east-1 endpoint) + fake implementation for tests.
  - Done when: unit tests cover pagination and the `Estimated` flag using the fake.
- [ ] **P1-04** `cloudcost ingest`: last 35 days by service and by tags `Project`, `Environment`; forecast for the current month; idempotent upserts; `job_run` row.
  - Done when: running ingest twice with the fake gives identical tables (test).
- [ ] **P1-05** API: `/api/healthz`, `/api/readyz`, `/api/costs/summary`, `/api/costs/daily`, `/api/costs/top-services` per `API_SPECIFICATION.md`, with tests on a seeded DB.
  - Done when: tests pass; OpenAPI at `/api/docs` matches the spec.
- [ ] **P1-06** Docker Compose: postgres + `migrate` + `api` + one-shot `ingest` using the fake (`CLOUDCOST_AWS_MODE=fake`) with realistic sample data.
  - Done when: `docker compose up` then `curl /api/costs/summary` returns sample numbers.
- [ ] **P1-07** 💰 (≈ USD 0.05) Run `ingest` locally against the real account with your read-only CLI credentials (`CLOUDCOST_AWS_MODE=real`).
  - Done when: summary matches the Cost Explorer console for month-to-date within a few cents.
- [ ] **P1-08** Kustomize: `deploy/k8s/base` with `api` Deployment, `ingest` CronJob, `migrate` Job; `local` overlay; run on minikube with the fake.
  - Done when: on minikube, a manual Job from the CronJob succeeds and the API serves the data.
- [ ] **P1-09** Remove the placeholder `app/` and `k8s/` folders; update CI and docs.
  - Done when: no references to the notes app remain; CI green.

## Phase 2: Waste scanner

- [ ] **P2-01** `finding` table migration; static price table for ap-southeast-1 (`pricing.py`, D-014) with a test that every rule has a price.
- [ ] **P2-02** Rule framework: each rule returns findings; scanner upserts, resolves missing, keeps `ignored`. Tests for the state changes.
- [ ] **P2-03** Rules `ebs-unattached`, `eip-unassociated`, `snapshot-old` with **moto** tests.
- [ ] **P2-04** Rules `alb-idle`, `ec2-low-cpu`, `ec2-stopped-with-ebs` (CloudWatch `GetMetricData`; fake for metrics).
- [ ] **P2-05** API `/api/findings`, `/api/findings/summary`, `PATCH /api/findings/{id}`; `/api/jobs/runs`.
- [ ] **P2-06** `scan` CronJob in Kustomize; local run with moto server or fake.
  - Done when (phase): on minikube, a scan creates findings from fake data, a second scan with one resource removed marks it `resolved`.

## Phase 3: Dashboard frontend

- [ ] **P3-01** `frontend/` React + TS + Vite skeleton, typed API client, TanStack Query, lint/test in CI.
- [ ] **P3-02** Overview page: MTD, forecast, last month, budget status, daily chart.
- [ ] **P3-03** Costs page: date range, group by service / tag, top services table.
- [ ] **P3-04** Findings page: filter by rule/status, total saving, ignore with reason.
- [ ] **P3-05** Jobs page: last runs and errors.
- [ ] **P3-06** nginx image (non-root), `frontend` Deployment + Service, path routing `/` vs `/api` in the Ingress; works on minikube.
  - Done when (phase): full app usable on minikube with fake data; screenshots saved in `docs/images/`.

## Phase 4: Production platform on AWS (first real deploy) 💰 🧹

- [ ] **P4-01** Split Terraform: move current code into `modules/platform`; create `envs/staging` and `envs/prod`; S3 remote state with lockfile (one key per env). `plan` shows no surprises.
- [ ] **P4-02** `modules/edge`: Route 53 records, ACM certificates (DNS validation), Cognito user pool + app client + hosted UI domain.
- [ ] **P4-03** `modules/app-iam`: Pod Identity roles + associations for `ingest`, `scan`, `notify`, ESO (policies in `SECURITY_AND_COST.md`).
- [ ] **P4-04** Helm add-ons pinned to versions: LB controller, metrics-server, External Secrets Operator, Argo CD. RDS app users + secrets in Secrets Manager; `ExternalSecret` objects.
- [ ] **P4-05** Ingress: HTTPS (ACM), HTTP→HTTPS redirect, Cognito auth on `/` and `/api/*` except health; API verifies ALB JWT.
- [ ] **P4-06** CI: `build-image.yml` pushes `services/cloudcost` and `frontend` images (tag = git SHA) via OIDC; Trivy gate; updates image tags in `deploy/k8s/overlays/<env>` by commit (or Argo CD Image Updater).
- [ ] **P4-07** Argo CD `Application` per env; `migrate` as PreSync hook; retire `deploy.yml`.
- [ ] **P4-08** 💰 Apply **staging**, deploy via Argo CD, run ingest + scan for real, sign in through Cognito. 🧹 Destroy, run teardown checklist.
  - Done when: `https://cost-staging.vuongdomain.click` shows real costs after Cognito sign-in; teardown verified next day in Cost Explorer.
- [ ] **P4-09** `terraform-plan.yml`: plan on PRs for both envs (read-only OIDC role), like Say Coffee.

## Phase 5: Alerts and observability

- [ ] **P5-01** `alert` table; `notify` job: cost spike, budget 80/100%, new waste; fingerprint dedupe; SES email (verified identity); optional Slack.
- [ ] **P5-02** App metrics (`prometheus-fastapi-instrumentator`, job last-success gauge); kube-prometheus-stack (pinned); ServiceMonitors.
- [ ] **P5-03** Grafana dashboards as code: API latency/errors, job freshness, pod resources, platform cost (from our own DB).
- [ ] **P5-04** Alert rules: API 5xx rate, SLO burn rate (99.5%), ingest not succeeded in 26 h, pods crash-looping, RDS CPU/storage (CloudWatch alarms).
- [ ] **P5-05** Runbooks in `docs/runbooks/`: ingest-failed, db-restore, rollback (Argo CD), rotate-secrets, teardown, node-spot-interruption.

## Phase 6: Hardening and portfolio polish

- [ ] **P6-01** NetworkPolicies (default deny) and Pod Security Admission `restricted` on app namespaces.
- [ ] **P6-02** AWS WAF on the ALB: managed rule groups + rate limit.
- [ ] **P6-03** Prod RDS Multi-AZ, 7-day backups, deletion protection; **tested** point-in-time restore written up in the db-restore runbook.
- [ ] **P6-04** CUR 2.0 Data Export to S3 (Parquet) and an ingest path that reads it (resource-level cost) (D-002 upgrade).
- [ ] **P6-05** Optional: Karpenter for right-sized Spot nodes; compare cost with managed node group.
- [ ] **P6-06** 💰 🧹 Prod demo session: apply prod, record a 3–5 minute walkthrough video, screenshots, then destroy.
- [ ] **P6-07** Final README: architecture, decisions, real cost of the demo sessions from Cost Explorer, "what I learned", CV bullets.
