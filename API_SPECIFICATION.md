# API Specification

Base path `/api`. JSON. Behind the ALB, every request (except health) arrives already signed in through Cognito; the ALB adds `x-amzn-oidc-identity` and `x-amzn-oidc-data` headers. The API **must verify** the `x-amzn-oidc-data` JWT signature (ALB public key for the region) and never trust the headers blindly.

Errors use one shape: `{"error": {"code": "string", "message": "string"}}`.

## Health (no auth)

| Method | Path | Response |
|---|---|---|
| GET | `/api/healthz` | `{"status":"ok"}`: process alive, no DB call |
| GET | `/api/readyz` | `{"status":"ready"}` or 503: DB reachable and migrations at head |

## Costs

### `GET /api/costs/summary?month=YYYY-MM`
Default month: current (UTC).
```json
{
  "month": "2026-11",
  "month_to_date_usd": "42.1830",
  "forecast_usd": "61.0200",
  "last_month_usd": "55.4000",
  "change_vs_last_month_pct": 10.1,
  "budget_usd": "60.00",
  "budget_status": "forecast_over",
  "data_as_of": "2026-11-20",
  "estimated": true
}
```
`budget_status`: `ok` | `forecast_over_80` | `forecast_over` | `actual_over`.

### `GET /api/costs/daily?from=YYYY-MM-DD&to=YYYY-MM-DD&group_by=service|tag:<Key>`
Max range 93 days. Response:
```json
{
  "group_by": "service",
  "days": ["2026-11-01", "2026-11-02"],
  "series": [
    {"key": "Amazon Elastic Kubernetes Service", "amounts_usd": ["2.4000", "2.4000"]},
    {"key": "Other", "amounts_usd": ["0.3100", "0.2900"]}
  ],
  "total_usd": ["2.7100", "2.6900"]
}
```
Top 8 keys by total; the rest are summed into `Other`.

### `GET /api/costs/top-services?month=YYYY-MM&limit=10`
`[{"service": "...", "amount_usd": "...", "share_pct": 31.2}]`

## Findings

| Method | Path | Notes |
|---|---|---|
| GET | `/api/findings?status=open&rule_id=&limit=50&cursor=` | Paginated list, newest `last_seen` first |
| GET | `/api/findings/summary` | `{"open": 7, "est_monthly_saving_usd": "24.9000", "by_rule": [{"rule_id": "...", "count": 3, "saving_usd": "..."}]}` |
| PATCH | `/api/findings/{id}` | Body `{"status": "ignored", "reason": "kept for DR test"}` or `{"status": "open"}`. 422 on other transitions |

Finding object:
```json
{
  "id": "uuid",
  "rule_id": "ebs-unattached",
  "resource_id": "vol-0abc",
  "region": "ap-southeast-1",
  "details": {"size_gb": 100, "volume_type": "gp3", "age_days": 41},
  "est_monthly_saving_usd": "9.6000",
  "status": "open",
  "first_seen": "2026-11-10T02:30:11Z",
  "last_seen": "2026-11-20T02:30:09Z"
}
```

## Jobs

| Method | Path | Notes |
|---|---|---|
| GET | `/api/jobs/runs?job=ingest&limit=20` | Latest runs with status and errors |

Triggering jobs from the UI is out of scope for MVP. Run manually with `kubectl -n <ns> create job --from=cronjob/ingest ingest-manual-$(date +%s)`.
