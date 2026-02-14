# DB Check Logs and Telemetry

This directory stores structured logs and telemetry for the DB check infrastructure.

## Files

| File | Format | Description |
|------|--------|-------------|
| `db_check.log` | NDJSON | Structured log entries (component, action, status, duration, data) |
| `telemetry.ndjson` | NDJSON | Telemetry events (passed/failed/skipped counts per run) |
| `telemetry_summary.json` | JSON | Latest telemetry per component:action |

## Log Format (NDJSON)

Each line is a JSON object:

```json
{"ts": 1739481234.5, "component": "db_check", "action": "validate", "status": "ok", "message": "", "data": {"passed": 1, "failed": 0}, "duration_ms": 1234.56}
```

## Components

- `db_check` - validate, format, qa, integrity, compliance, qa-suite, full
- `integrity` - run
- `pre_commit` - run
- `gdpval` - run
- `mvc_backend_test` - run

## Rotation

To trim logs and prevent unbounded growth:

```bash
python3 scripts/rotate_logs.py --max-lines 10000 --max-telemetry 1000
```

## .gitignore

Add `logs/*.log` and `logs/*.ndjson` to .gitignore if you don't want to commit logs. `telemetry_summary.json` can be committed for CI visibility.
