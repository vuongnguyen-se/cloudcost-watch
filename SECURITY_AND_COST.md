# Security and Cost

## 1. Security controls

| Area | Control |
|---|---|
| Identity for people | IAM Identity Center user with MFA; root has MFA and no keys |
| Identity for CI | GitHub OIDC role, trusted only for `repo:<owner>/<repo>:ref:refs/heads/main`; can push to one ECR repo and describe one cluster |
| Identity for pods | **EKS Pod Identity**, one IAM role per workload (ingest, scan, notify, ESO). Read-only for ingest/scan. LB controller keeps IRSA |
| Cluster access | EKS access entries. Admin = the Terraform caller. CI role = edit in its namespace only. Argo CD runs in-cluster |
| Kubernetes API | Public endpoint restricted to the developer IP (`cluster_endpoint_public_access_cidrs`) |
| Network | Nodes in private subnets; RDS in isolated database subnets, port 5432 only from node SG; Kubernetes NetworkPolicies: default deny, allow ALB→frontend/api, api/jobs→RDS, jobs→AWS APIs |
| Edge | HTTPS only (ACM), HTTP→HTTPS redirect, Cognito sign-in on the ALB, AWS WAF managed rule groups (Common, KnownBadInputs, IP reputation) + rate limit |
| Secrets | Secrets Manager → External Secrets Operator → K8s Secrets. Nothing secret in git, Terraform vars or images |
| Data | RDS encrypted (KMS), TLS to RDS (`sslmode=require`), backups; S3 (CUR, later) encrypted, Block Public Access |
| Pods | non-root, read-only root FS, drop all capabilities, seccomp RuntimeDefault, no service account token unless needed, Pod Security Admission `restricted` on app namespaces |
| Supply chain | ECR scan on push; CI fails on HIGH/CRITICAL (Trivy); immutable tags = git SHA; pinned module/provider/chart versions; Dependabot |
| Audit | CloudTrail (account default), EKS control plane audit logs to CloudWatch (prod, 7-day retention) |

### IAM policies for the jobs (sketch)

```json
{"Sid": "IngestCosts", "Effect": "Allow",
 "Action": ["ce:GetCostAndUsage", "ce:GetCostForecast"], "Resource": "*"}
```
Cost Explorer does not support resource-level permissions, so `*` is required here (documented exception).

```json
{"Sid": "ScanReadOnly", "Effect": "Allow",
 "Action": ["ec2:DescribeVolumes", "ec2:DescribeSnapshots", "ec2:DescribeAddresses", "ec2:DescribeInstances",
            "elasticloadbalancing:DescribeLoadBalancers", "elasticloadbalancing:DescribeTargetGroups",
            "elasticloadbalancing:DescribeTargetHealth", "cloudwatch:GetMetricData"],
 "Resource": "*"}
```
Describe calls do not support resource-level permissions either.

## 2. Cost

Approximate, ap-southeast-1, on-demand. Always check the AWS Pricing Calculator before applying.

| Item | staging ≈ USD/h | prod ≈ USD/h |
|---|---|---|
| EKS control plane (standard support) | 0.10 | 0.10 |
| Nodes | 0.03 (2 × Spot t3.medium) | 0.08 (1 on-demand + 1–2 Spot) |
| NAT gateway | 0.06 | 0.06 |
| ALB | 0.03 | 0.03 |
| RDS PostgreSQL | 0.03 (t4g.micro single-AZ) | 0.06 (t4g.micro Multi-AZ) |
| Public IPv4 | 0.015 | 0.015 |
| WAF (web ACL + rules, monthly prorated) | ~0.01 | ~0.01 |
| Route 53 zone, Secrets Manager, ECR, SES, CloudWatch logs | ~0.01 | ~0.02 |
| **Total** | **≈ 0.29/h** | **≈ 0.38/h** |

Cost Explorer API: USD 0.01 per request. Ingest uses ~4 requests/day (service, 2 tags, forecast) ≈ USD 1.20/month.

**Always-on would cost ≈ USD 210 (staging) + 275 (prod) per month.** So (D-012):
- Build and test everything locally first (Docker Compose, minikube) at USD 0.
- Bring staging up only for a working session; tear it down after.
- Bring prod up for demos, screenshots and the final recorded walkthrough; tear down after.
- Keep the account budget alert (e.g. USD 30/month) and a separate alert at USD 10 for "something was left running".

## 3. Teardown checklist 🧹

1. `kubectl delete` the app Ingress (or let Argo CD prune it) and wait until the ALB is gone in the EC2 console.
2. `terraform destroy` in `envs/<env>`.
3. Check: EKS clusters, EC2 instances, NAT gateways, Elastic IPs, load balancers, RDS instances and snapshots, EBS volumes: none left for the project (filter by tag `Project`).
4. Next day: Cost Explorer, filter `Project`, confirm spend stopped.

The CloudCost Watch scanner itself should be able to flag anything left behind. Good demo material.
