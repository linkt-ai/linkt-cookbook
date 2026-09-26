# Legacy V1

These examples target the deprecated V1 SDK. Existing versions remain available.
New integrations use the [V2 HTTP examples](../../v2/README.md).

# Advanced Examples

This directory contains advanced patterns for schedule management, bulk operations, and data export.

## Prerequisites

- LINKT_API_KEY in `.env` file at repository root
- Python 3.9+
- `pip install -r requirements.txt` from parent directory
- Completed basic examples in `01_search/`

## Examples

### schedule_management.py

Manage recurring schedules for automated task execution.

**Features:**
- Create schedules with cron expressions
- List and view schedules
- Update schedule frequency
- Delete schedules

**Usage:**
```bash
# List all schedules
python schedule_management.py list

# Create a daily schedule for a task
python schedule_management.py create <task_id> --frequency daily

# Create with custom cron (weekly on Tuesday at 10am)
python schedule_management.py create <task_id> --cron "0 10 * * 2"

# Update schedule frequency
python schedule_management.py update <schedule_id> --frequency weekly

# Disable a schedule
python schedule_management.py update <schedule_id> --disable

# Delete a schedule
python schedule_management.py delete <schedule_id>
```

**Frequency Options:**
| Frequency | Cron Expression | Description |
|-----------|-----------------|-------------|
| `daily` | `0 9 * * *` | Daily at 9 AM |
| `weekly` | `0 9 * * 1` | Monday at 9 AM |
| `monthly` | `0 9 1 * *` | 1st of month at 9 AM |

### entity_status_workflow.py

Manage entity status for sales workflow tracking.

**Features:**
- View status breakdown by entity type
- Update individual entity status
- Filter entities by status
- Track workflow progression

**Usage:**
```bash
# View status summary
python entity_status_workflow.py <icp_id>

# Filter by status
python entity_status_workflow.py <icp_id> --status new

# Update single entity status
python entity_status_workflow.py <icp_id> \
  --update <entity_id> \
  --set-status reviewed
```

**Status Values:**
| Status | Description |
|--------|-------------|
| `new` | Newly discovered, not reviewed |
| `reviewed` | Reviewed and qualified |
| `passed` | Not a fit, disqualified |
| `contacted` | Outreach initiated |

### bulk_operations.py

Bulk update operations for managing large numbers of entities.

**Features:**
- Count entities by status
- Bulk status updates
- Batch processing with progress tracking
- Error handling for large operations

**Usage:**
```bash
# Count entities by status
python bulk_operations.py <icp_id> --action count

# Bulk update: all "new" to "reviewed"
python bulk_operations.py <icp_id> \
  --action status \
  --from new \
  --to reviewed

# Update specific entities
python bulk_operations.py <icp_id> \
  --action status \
  --entity-ids id1 id2 id3 \
  --to contacted

# Limit number of entities to update
python bulk_operations.py <icp_id> \
  --action status \
  --from new \
  --to reviewed \
  --limit 100
```

### export_entities.py

Export entities to CSV format.

**Features:**
- Export companies or contacts to CSV
- Filter by status
- Multi-ICP export (combined or separate files)
- Configurable output path

**Usage:**
```bash
# Export companies from single ICP
python export_entities.py <icp_id>

# Export contacts with custom output file
python export_entities.py <icp_id> \
  --entity-type person \
  --output contacts.csv

# Export only "reviewed" entities
python export_entities.py <icp_id> --status reviewed

# Multi-ICP export (separate files)
python export_entities.py \
  --icp-ids abc123 def456 \
  --format separate
```

**Exported Fields:**

Companies:
- entity_id, status, name, website, industry
- employees, revenue, headquarters, description, linkedin_url

Contacts:
- entity_id, status, name, title, company
- email, mobile_phone, location, linkedin_url

## Schedule Cron Reference

Cron expressions use 5 fields: `minute hour day month weekday`

| Expression | Description |
|------------|-------------|
| `0 9 * * *` | Daily at 9:00 AM |
| `0 9 * * 1` | Weekly on Monday at 9 AM |
| `0 9 1 * *` | Monthly on the 1st at 9 AM |
| `0 9 * * 1-5` | Weekdays at 9 AM |
| `0 9,14 * * *` | Daily at 9 AM and 2 PM |
| `*/15 * * * *` | Every 15 minutes |

## Workflow Integration

These advanced examples support complete GTM workflows:

1. **Search** (01_search)
2. **Import** (02_ingest)
3. **Monitor** (03_signals)
5. **Schedule** - Automate recurring tasks
6. **Process** - Update status as leads progress
7. **Export** - Extract data for external tools

## Next Steps

- Use `/linkt-schedule` skill for interactive schedule management
- Use `/linkt-status` skill for interactive status updates
- Set up webhooks for real-time notifications
