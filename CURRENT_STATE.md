# Current State (handoff)

_Last updated: 2026-11-21. Update this file at the end of every work session._

## 1. Summary

The repository contains a **working EKS platform skeleton** (Terraform + Kubernetes + CI/CD) running a placeholder **notes API**. It was built as `eks-platform-lab` and is now being turned into **CloudCost Watch** (see `PROJECT_REQUIREMENTS.md`). The infrastructure is reused; the notes app will be replaced in Phase 1.

- GitHub: https://github.com/vuongnguyen-se/cloudcost-watch (public, renamed from `eks-platform-lab` on 2026-11-21; old URL redirects, branch `main`)
- Local path: `C:\Users\Vuong\Downloads\eks-platform-lab`
- Commits so far: `c908cbf` (platform skeleton), `dcbcb6b` (Actions bumped to Node 24 versions), `f4355ee` (handoff docs), then the rename commit
- **Nothing has ever been deployed to AWS.** No AWS resources exist for this project.

## 2. What exists

| Path | What it is | Status |
|---|---|---|
| `app/` | FastAPI "notes" API (placeholder). Postgres via `DATABASE_URL`, in-memory otherwise. `/healthz`, `/readyz`, `/`, `/notes`, `/burn` (CPU load for HPA demos). 5 pytest tests. Non-root Dockerfile. | ✅ works; **to be replaced** by `services/cloudcost` |
| `docker-compose.yml` | App + Postgres 17 locally | ✅ verified |
| `infra/terraform/` | One root module: VPC (2 AZ, public/private/database subnets, 1 NAT), EKS (module v20, managed Spot node group AL2023, access entries), AWS Load Balancer Controller (Helm, IRSA), metrics-server (Helm), ECR (immutable, scan on push, keep 10), RDS PostgreSQL 17 (`db.t4g.micro`, password managed in Secrets Manager), GitHub OIDC deploy role, AWS Budgets | ✅ `fmt`/`validate` pass; **never applied** |
| `k8s/base` | Namespace `notes`, Deployment (probes, non-root, read-only FS, topology spread), Service, HPA (CPU 60%, 2–6), PDB | ✅ verified on minikube |
| `k8s/overlays/aws` | + ALB Ingress (internet-facing, target-type ip, HTTP only) | renders; not deployed |
| `k8s/overlays/local` | HPA min 1 for minikube/kind | ✅ verified |
| `scripts/create-db-secret.sh` | Reads RDS secret → creates K8s Secret `notes-db` | untested (needs AWS); **to be replaced** by External Secrets (D-005) |
| `scripts/load-test.sh` | busybox load generator for HPA demo | ✅ verified (Git Bash path bug fixed) |
| `.github/workflows/ci.yml` | pytest + docker build, terraform fmt/init/validate, kustomize render | ✅ green on GitHub |
| `.github/workflows/deploy.yml` | Manual: OIDC → build/push ECR → `kubectl apply -k` | **never run** (no cluster) |
| `README.md` | Written for the lab; **must be rewritten** for CloudCost Watch (task P0-03) | outdated |

### Pinned versions
Terraform ≥ 1.6 (local 1.17.1) · AWS provider `>= 5.95, < 6.0` · Helm provider `~> 2.17` · `terraform-aws-modules/vpc ~> 5.21` · `eks ~> 20.37` · `iam ~> 5.55` · Kubernetes `1.35` (**unverified**: check standard support with `aws eks describe-cluster-versions`) · Helm charts **unpinned** (pin in Phase 4) · Python 3.13 · Actions: checkout v7, setup-python v7, setup-terraform v4, configure-aws-credentials v6, amazon-ecr-login v2.

## 3. Verified on 2026-11-19 / 2026-11-20

- `pytest`: 5 passed.
- `terraform fmt -check`, `init -backend=false`, `validate`: pass (locally and in CI).
- Docker Compose: API stored a note in Postgres; still there after restarting the API.
- minikube (`-p eks-lab`, docker driver, metrics-server addon): 2 pods Ready with all security settings; under load the HPA scaled **1 → 6 pods** (CPU 756% of target).
- GitHub CI: all 3 jobs green, no deprecation warnings.

## 4. Developer machine notes (Windows 11)

- Shells: PowerShell 5.1 and Git Bash. In Git Bash use `MSYS_NO_PATHCONV=1` for commands that pass Unix paths into containers.
- **Terraform** installed with winget: `C:\Users\Vuong\AppData\Local\Microsoft\WinGet\Packages\Hashicorp.Terraform_Microsoft.Winget.Source_8wekyb3d8bbwe\terraform.exe`. Open a new terminal for `terraform` to be on PATH.
- **Docker Desktop** is installed per-user (`%LOCALAPPDATA%\Programs\DockerDesktop`); start it before building.
- **minikube** profile `eks-lab` exists (stopped) with the notes app deployed. `minikube start -p eks-lab` resumes it; `minikube delete -p eks-lab` removes it.
- kubectl 1.36, AWS CLI 2.35, gh CLI (signed in as `vuongnguyen-se`), Python 3.13. Helm CLI not installed (Terraform installs charts).
- **AWS CLI is not signed in** on this machine. Sign in with `aws login`, or with the IAM Identity Center profile used for CloudDocs-AI (`aws sso login --profile clouddocs-dev`) if it is the same account.

## 5. AWS account facts (same account as the other projects)

- Region `ap-southeast-1`.
- A **GitHub OIDC provider already exists** (created for Say Coffee) → keep `create_github_oidc_provider = false`.
- The Say Coffee project attaches a permissions boundary to Lambda roles (`SayCafeLambdaBoundary`). Check whether account guardrails require boundaries on new IAM roles before Phase 4.
- Domain `vuongdomain.click` is used by Say Coffee. Check in Route 53 that a hosted zone exists before planning `cost.vuongdomain.click` (Phase 4).
- Cost allocation tags `Project` and `Environment` must be **activated** in Billing before tag grouping returns data (task P0-05). Activation is not retroactive and takes up to 24 h.

## 6. Known issues / caveats

1. Teardown order: `kubectl delete -k k8s/overlays/aws` **before** `terraform destroy`, or the controller-made ALB blocks VPC deletion.
2. The ALB Ingress is HTTP only; HTTPS + Cognito come in Phase 4.
3. `deploy.yml` must not use a GitHub `environment:` unless the IAM trust policy is changed (the OIDC `sub` claim would change).
4. Single NAT gateway and single-AZ RDS: fine for staging, not for prod (Phase 4/6).
5. The Terraform layout is a single root module; Phase 4 splits it into `modules/` + `envs/staging|prod`.

## 7. Next step

Continue **Phase 0** in `TASKS.md` from P0-02 (AWS sign-in checks, tag activation), then **Phase 1** (cost ingestion, built and tested locally first).
