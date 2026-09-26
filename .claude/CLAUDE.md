# Legacy V1

These instructions support existing V1 workflows. New integrations use `v2/README.md` and `v2/mcp.json`.
The root `.mcp.json` connects the legacy tools used here. Do not apply these tool names to V2.

# Linkt Cookbook

This repository contains practical examples and Claude Code skills for building AI-powered GTM (Go-To-Market) workflows with the Linkt platform.

## Purpose

The cookbook demonstrates how to:
- Discover and monitor companies matching your Ideal Customer Profile (ICP)
- Track business signals (AI initiatives, leadership changes, funding, etc.)
- Enrich contacts with LinkedIn profiles for personalized outreach
- Automate LinkedIn connection requests based on signal context

## Available Skills

| Skill | Description |
|-------|-------------|
| `/linkt-init` | Set up your profile for personalized outreach |
| `/linkt-signals` | Pull recent signals and display contacts for outreach |
| `/linkt-outreach` | Draft LinkedIn message and post to Slack for manual sending |
| `/linkt-schedule` | Manage recurring signal monitoring schedules |
| `/linkt-status` | Bulk update entity status for workflow management |

## Linkt MCP Tools

This project uses the Linkt MCP Server. Key tools available:

### Signals
- `mcp__linkt__list_signals_v1_signal_get` - List recent signals (filter by days, type, strength)
- `mcp__linkt__get_signal_v1_signal` - Get signal details by ID

### Entities (Companies & Contacts)
- `mcp__linkt__list_entities_v1_entity_get` - List entities with filtering
- `mcp__linkt__get_entity_v1_entity` - Get entity details by ID
- `mcp__linkt__search_entities_v1_entity_search_get` - Search entities by text

### ICPs & Sheets
- `mcp__linkt__list_icps_v1_icp_get` - List ICPs (discovery or monitoring)
- `mcp__linkt__list_sheets_v1_sheet_get` - List sheets by ICP or entity type

### Schedules
- `mcp__linkt__create_schedule_v1_schedule_post` - Create recurring schedule
- `mcp__linkt__list_schedules_v1_schedule_get` - List schedules
- `mcp__linkt__get_schedule_v1_schedule` - Get schedule details
- `mcp__linkt__update_schedule_v1_schedule` - Update schedule
- `mcp__linkt__delete_schedule_v1_schedule` - Delete schedule

## Common Commands

```bash
# Run Python examples
cd python
source .venv/bin/activate
python 01_search/first_search.py

# Check API connectivity
python 01_search/first_search.py

# Set up signal monitoring
python 03_signals/signals_from_sheet.py <icp_id>
```

## Environment Variables

Required in `.env` file at repository root:
```
LINKT_API_KEY=sk-...
```

Optional:
```
LINKT_API_ENVIRONMENT=staging  # Use staging API (default: production)
```

For Slack integration (required for `/linkt-outreach`):
```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_TEAM_ID=T01234567
```

See `docs/slack-setup.md` for detailed Slack app setup instructions.

## User Context

The `/linkt-init` skill creates a user context file at `.claude/user-context.json` that stores:

- **Company info:** name, domain, description, industry
- **User info:** name, role
- **Outreach settings:** use case, target audience, value proposition, talking points

This context is used by `/linkt-outreach` to draft more personalized LinkedIn connection messages. Run `/linkt-init` before your first outreach to set up your profile.

**File location:** `.claude/user-context.json` (gitignored - contains personal info)

## Conventions

- All Python examples load `.env` from repository root
- Entity types: `company`, `person`, `job_board`, `school_district`, `product`
- Signal strengths: `strong`, `moderate`, `weak`
- Signal `score` field: 0.0-1.0 numeric score for prioritization
- Status values: `new`, `reviewed`, `passed`, `contacted`
- Use `icp_ids` parameter (list) for multi-ICP filtering on signals and entities
- Schedule frequencies: `daily`, `weekly`, `monthly`
