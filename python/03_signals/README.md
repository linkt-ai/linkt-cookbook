# Signal Examples

This directory contains examples for setting up signal monitoring from different sources and querying the results.

## Prerequisites

- LINKT_API_KEY in `.env` file at repository root
- Python 3.9+
- `pip install -r requirements.txt` from parent directory

## Signal Source Types

Linkt supports three signal source types, each suited for different workflows:

| Source Type | Script | When to Use |
|-------------|--------|-------------|
| **Sheet** | `signals_from_sheet.py` | Monitor companies already discovered in an ICP |
| **CSV** | `signals_from_csv.py` | Monitor companies from an uploaded CSV file |
| **Topic** | `signals_from_topic.py` | Monitor by topic criteria (no pre-existing entities needed) |

All three scripts:
- Create a signal task with the appropriate source type
- Execute the first monitoring run
- Set up a recurring schedule automatically
- Support optional `--webhook` for notifications

## Examples

### signals_from_sheet.py

Monitor signals on entities already discovered in a sheet (ICP).

**Usage:**
```bash
python signals_from_sheet.py <source_icp_id> [--webhook URL] [--frequency weekly]

# Examples
python signals_from_sheet.py abc123
python signals_from_sheet.py abc123 --frequency daily
python signals_from_sheet.py abc123 --webhook https://example.com/hook
```

**Expected Output:**
```
[1/4] Verifying source ICP...
   Found ICP: abc123
   Companies to monitor: 50

[2/4] Creating signal-sheet task...
   Task ID: task_abc123

[3/4] Starting first monitoring run...
   Run ID: run_xyz789

[4/4] Creating recurring schedule...
   Schedule ID: sched_def456
   Next run: 2026-02-10T09:00:00Z
```

### signals_from_csv.py

Monitor signals on companies from an uploaded CSV file.

**Usage:**
```bash
python signals_from_csv.py <csv_path_or_file_id> [--webhook URL] [--frequency daily]

# Upload and monitor a CSV file
python signals_from_csv.py ../02_ingest/sample_data/companies.csv

# Use an existing file_id
python signals_from_csv.py file_abc123 --frequency weekly
```

### signals_from_topic.py

Monitor signals by topic criteria (no pre-existing entities needed).

**Usage:**
```bash
python signals_from_topic.py "<topic_criteria>" [--webhook URL] [--frequency weekly]

# Examples
python signals_from_topic.py "AI startups in healthcare"
python signals_from_topic.py "Series B SaaS companies adopting AI" --frequency daily
```

### query_signals.py

Query and display signals produced by any signal task.

**Usage:**
```bash
python query_signals.py <task_id>                    # All signals for a task
python query_signals.py --icp <icp_id>               # All signals for an ICP
python query_signals.py --days 7                      # Recent signals
python query_signals.py <task_id> --type funding      # Filter by type
python query_signals.py <task_id> --strength strong   # Filter by strength
```

**Expected Output:**
```
[1/3] Building query...
   Task: task_abc123
   Days: 30

[2/3] Fetching signals...
   Found 25 signals

[3/3] Signals:
1. [HIGH] AI Initiatives
   Score: 0.92 | Strength: strong | Detected: Feb 01, 2026
   Summary: Company announced major AI initiative...
   Entity: ent_abc123

Summary Statistics
   By Type:
     AI Initiatives: 10
     Funding Rounds: 8
     Leadership Changes: 7

   Score Distribution:
     HIGH (0.8+):    5
     MEDIUM (0.5+):  15
     LOW (<0.5):     5
     Average score:  0.67
```

## Schedule Auto-Creation

All signal source scripts automatically create a recurring schedule. Default frequencies:

| Frequency | Cron Expression | Description |
|-----------|-----------------|-------------|
| `daily` | `0 9 * * *` | Daily at 9 AM |
| `weekly` | `0 9 * * 1` | Monday at 9 AM |
| `monthly` | `0 9 1 * *` | 1st of month at 9 AM |

Manage schedules with:
```bash
python ../04_advanced/schedule_management.py list
```

## Webhook Support

All signal source scripts support `--webhook URL` to receive notifications when monitoring runs complete:

```bash
python signals_from_sheet.py abc123 --webhook https://example.com/hook
```

## Signal Types

Linkt supports 17 signal types:

| Type | Description |
|------|-------------|
| `funding` | Funding rounds, investments |
| `leadership_change` | New executives, leadership changes |
| `layoff` | Workforce reductions |
| `product_launch` | New product announcements |
| `partnership` | Strategic partnerships |
| `acquisition` | M&A activity |
| `expansion` | Geographic or market expansion |
| `award` | Industry recognition |
| `pivot` | Strategic direction changes |
| `regulatory` | Compliance, regulatory news |
| `rfp` | Request for proposals |
| `contract_renewal` | Contract renewals |
| `hiring_surge` | Rapid hiring activity |
| `infrastructure` | Technology investments |
| `compliance` | Compliance updates |
| `job_posting` | Specific job postings |
| `other` | Custom signals (AI Initiatives, etc.) |

## Signal Score Field

Each signal has a `score` field (0.0-1.0) for prioritization:

| Score Range | Tier | Action |
|-------------|------|--------|
| 0.8-1.0 | HIGH | Prioritize for immediate outreach |
| 0.5-0.79 | MEDIUM | Monitor and follow up soon |
| 0.0-0.49 | LOW | Informational, lower priority |

## Next Steps

1. **Use Claude Code skills**:
   - `/linkt-signals` - Interactive signal viewing and outreach
   - `/linkt-status` - Update entity status based on signals

2. **Manage schedules**:
   ```bash
   python ../04_advanced/schedule_management.py list
   ```
