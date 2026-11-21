# Database Design (PostgreSQL 17)

Managed with **Alembic** migrations (`services/cloudcost/src/cloudcost/db/alembic/`). Money is `NUMERIC(14,4)` in USD. Timestamps are `TIMESTAMPTZ` in UTC. Dates of usage are `DATE` (UTC, as Cost Explorer reports them).

## Tables

### `cost_daily_service`
Daily cost per AWS service. Source: `GetCostAndUsage`, granularity `DAILY`, metric `UnblendedCost`, group by `DIMENSION SERVICE`.

| Column | Type | Notes |
|---|---|---|
| `usage_date` | DATE | PK part |
| `account_id` | VARCHAR(12) | PK part (one account in MVP, ready for more) |
| `service` | TEXT | PK part, e.g. `Amazon Elastic Compute Cloud - Compute` |
| `amount_usd` | NUMERIC(14,4) | |
| `estimated` | BOOLEAN | Cost Explorer's `Estimated` flag (recent days change) |
| `updated_at` | TIMESTAMPTZ | last upsert |

PK `(usage_date, account_id, service)`. Index `(usage_date)`.

### `cost_daily_tag`
Daily cost per value of one cost allocation tag. Same source, group by `TAG <key>`.

| Column | Type | Notes |
|---|---|---|
| `usage_date` | DATE | PK part |
| `account_id` | VARCHAR(12) | PK part |
| `tag_key` | TEXT | PK part, e.g. `Project` |
| `tag_value` | TEXT | PK part; empty string = untagged |
| `amount_usd` | NUMERIC(14,4) | |
| `estimated` | BOOLEAN | |
| `updated_at` | TIMESTAMPTZ | |

### `cost_forecast`
| Column | Type | Notes |
|---|---|---|
| `month` | DATE | PK part; first day of month |
| `account_id` | VARCHAR(12) | PK part |
| `amount_usd` | NUMERIC(14,4) | forecast of the whole month |
| `lower_usd`, `upper_usd` | NUMERIC(14,4) | prediction interval |
| `generated_at` | TIMESTAMPTZ | |

### `finding`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `rule_id` | TEXT | e.g. `ebs-unattached` |
| `resource_id` | TEXT | e.g. `vol-0abc...` |
| `resource_arn` | TEXT | nullable |
| `region` | TEXT | |
| `details` | JSONB | rule-specific (size, type, age, metrics) |
| `est_monthly_saving_usd` | NUMERIC(14,4) | nullable (e.g. `ec2-low-cpu`) |
| `status` | TEXT | `open` / `resolved` / `ignored` |
| `ignored_reason` | TEXT | nullable |
| `first_seen`, `last_seen` | TIMESTAMPTZ | |
| `resolved_at` | TIMESTAMPTZ | nullable |

Unique `(rule_id, resource_id)`. Index `(status)`. A scan upserts every finding it sees (updates `last_seen`); open findings not seen by a successful scan become `resolved`. `ignored` stays ignored.

### `alert`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `kind` | TEXT | `cost-spike` / `budget` / `new-waste` |
| `fingerprint` | TEXT | unique; e.g. `cost-spike:2026-11-20`, `budget:2026-11:80` |
| `payload` | JSONB | what was sent |
| `channels` | TEXT[] | `email`, `slack` |
| `sent_at` | TIMESTAMPTZ | |

The unique `fingerprint` is what stops duplicate alerts.

### `job_run`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `job` | TEXT | `ingest` / `scan` / `notify` |
| `started_at`, `finished_at` | TIMESTAMPTZ | |
| `status` | TEXT | `running` / `succeeded` / `failed` |
| `rows_written` | INTEGER | |
| `error` | TEXT | nullable, truncated |

Jobs also expose metrics (`cloudcost_job_last_success_timestamp`) for Prometheus alerts.

## Database users

- `cloudcost_migrator`: owns the schema; used only by the `migrate` Job.
- `cloudcost_app`: `SELECT/INSERT/UPDATE` on the tables; used by api and jobs.
- The RDS master user is only for creating these two (documented in a runbook).
