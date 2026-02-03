# Monitor Leads

Set up automated signal monitoring for companies discovered through search workflows.

## Examples

| File | Description | Duration |
|------|-------------|----------|
| `setup_signal_monitoring.py` | Configure weekly news & social monitoring | Instant |

## Prerequisites

- Completed setup from `python/README.md`
- Valid API key with staging or production access
- **ICP ID from a completed discovery** (run `01_getting_started/first_discovery.py` first)

## Core Concepts

### Signal Monitoring

Signal monitoring tracks business events for entities in your ICP. Instead of discovering new companies, it watches companies you've already found for relevant activity.

### Signal Types

Configurable event categories to monitor:
- **funding**: Investment rounds, venture capital, acquisitions
- **leadership_change**: Executive appointments, C-suite changes, departures
- **hiring_surge**: Rapid headcount growth, recruiting initiatives
- **product_launch**: New product or feature announcements
- **partnership**: Strategic partnerships, integrations
- **expansion**: New markets, office openings
- **layoff**: Workforce reductions
- **acquisition**: M&A activity
- **job_posting**: Open positions (by department/role)
- **other**: Custom signal criteria

### Signal-Sheet Task

The `signal-sheet` task type monitors entities from an existing ICP's sheet:
- Links to companies discovered in a previous search workflow
- No CSV upload required - uses existing entity data
- Can filter to specific companies using `entity_filters`

### Monitoring Frequency

How often the system checks for new signals:
- `daily`: Check every day
- `weekly`: Check every week (default)
- `monthly`: Check every month

## Workflow

1. **Run discovery first**: Complete `01_getting_started/first_discovery.py` and note the ICP_ID
2. **Wait for completion**: Use `monitor_discovery.py` to wait for search to finish
3. **Set up monitoring**: Run `setup_signal_monitoring.py` with the ICP_ID
4. **Review signals**: (Coming soon) View detected signals in the dashboard

## What's Next?

After setting up signal monitoring:
- View detected signals in the dashboard: `https://app.linkt.ai/icp/{icp_id}`
- Explore `02_search/` for advanced discovery options
- Try `03_ingest/` to monitor your own company lists
