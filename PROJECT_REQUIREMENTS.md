# CloudCost Watch: Project Requirements

## 1. Purpose

Teams that run on AWS often overspend and cannot see **who** or **what** is driving the bill. CloudCost Watch is a self-hosted FinOps platform that:

1. imports AWS cost data every day,
2. shows spend by service, by team/project tag and over time, with a month-end forecast,
3. finds resources that cost money but do nothing (waste) and estimates the monthly saving,
4. alerts when spend spikes or a budget is about to be exceeded.

It runs on Amazon EKS and is built to production standards (HTTPS, sign-in, separate staging/prod, GitOps, monitoring, backups, runbooks).

**Real use case from day one:** it analyses the developer's own AWS account, including the cost of the platform it runs on.

### Why this project (portfolio context)

Built for an AWS internship application at SoftwareOne, whose cloud business includes FinOps / cost optimization, migration and managed services. It complements the other two CV projects:

| Project | Shows |
|---|---|
| Say Coffee | Serverless web (S3, CloudFront, Lambda, API Gateway, DynamoDB), SAM + Terraform, GitHub OIDC CI/CD |
| CloudDocs-AI | AI on AWS: Bedrock Knowledge Bases (RAG), Cognito, CDK |
| **CloudCost Watch** | Containers and Kubernetes (EKS), networking, data jobs, observability, FinOps |

## 2. Users

| Persona | Needs |
|---|---|
| **Cloud owner / FinOps lead** | Monthly spend, forecast, which services and teams cost the most, savings list |
| **Engineer on a team** | Their team's spend (by `Project`/`Team` tag), waste in their resources |
| **Platform admin** | Health of the jobs, alert channels, users |

MVP has a single account and a small set of admin-created users (Cognito).

## 3. Functional requirements

### FR-1 Cost ingestion
- FR-1.1 A scheduled job imports **daily unblended cost** for the last N days (default 35) from the Cost Explorer API, grouped by `SERVICE`, and separately by the cost allocation tags `Project` and `Environment`.
- FR-1.2 The job is idempotent (upsert) and re-imports recent days, because AWS revises costs for up to ~3 days.
- FR-1.3 The job stores the month-end forecast (`GetCostForecast`).
- FR-1.4 Every run is recorded (start, end, status, rows, error) and visible in the UI.
- FR-1.5 (Later) Switch or add line-item detail from **CUR 2.0 Data Exports** (Parquet in S3).

### FR-2 Cost views
- FR-2.1 Overview: month-to-date, forecast, last month, % change, budget status.
- FR-2.2 Daily cost chart for a date range, grouped by service or by a tag.
- FR-2.3 Top 10 services for a month.

### FR-3 Waste finder (scanner job)
Rules for MVP, each producing a **finding** with resource ID, region, details and estimated monthly saving:

| Rule ID | Detects | Saving estimate |
|---|---|---|
| `ebs-unattached` | EBS volumes in `available` state | size GB × price per GB-month for its type |
| `eip-unassociated` | Elastic IPs not attached | public IPv4 hourly price × 730 |
| `snapshot-old` | Own EBS snapshots older than 90 days | size GB × snapshot price per GB-month |
| `alb-idle` | Load balancers with 0 requests in 7 days | ALB hourly price × 730 |
| `ec2-low-cpu` | Running EC2 with max CPU < 10% for 14 days | "consider a smaller size" (no fixed number in MVP) |
| `ec2-stopped-with-ebs` | Instances stopped > 14 days that still have EBS volumes | attached volume cost |

- FR-3.1 Findings keep `first_seen`/`last_seen`; a finding not seen in the latest scan becomes `resolved`.
- FR-3.2 A user can mark a finding `ignored` with a reason.
- FR-3.3 Prices come from a static table per region in config (MVP); AWS Pricing API later.

### FR-4 Alerts
- FR-4.1 **Spike:** yesterday's cost > mean + 3σ of the previous 14 days **and** more than USD 1 above the mean.
- FR-4.2 **Budget:** forecast passes 80% / 100% of the monthly budget set in config.
- FR-4.3 **New waste:** new findings with total saving > USD 5.
- FR-4.4 Channels: email (Amazon SES) and optional Slack webhook. One alert per event (deduplicated by fingerprint).

### FR-5 Access
- FR-5.1 Dashboard and API only reachable over HTTPS, after Cognito sign-in (ALB authentication).
- FR-5.2 Health endpoints are open for the load balancer only.

## 4. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-1 | Availability target (SLO) for the API in prod: 99.5% of requests succeed over 30 days |
| NFR-2 | Overview page loads in < 1 s p95 (data is pre-aggregated in Postgres) |
| NFR-3 | All infrastructure in Terraform; all app deploys through Git (Argo CD) |
| NFR-4 | No long-lived AWS keys anywhere; least-privilege IAM per workload |
| NFR-5 | Data encrypted at rest (RDS, S3) and in transit (TLS) |
| NFR-6 | Staging and prod are separate (state, namespaces, database, domain) |
| NFR-7 | Platform cost is documented per hour and per month; budget alerts on the account |
| NFR-8 | Every incident type has a runbook in `docs/runbooks/` |

## 5. Out of scope (for now)

- Multiple AWS accounts / AWS Organizations (design for it, build for one account)
- Billing for customers, multi-tenant SaaS
- Automatically deleting wasted resources (we only report)
- Reserved Instance / Savings Plan purchase advice
- Mobile app
