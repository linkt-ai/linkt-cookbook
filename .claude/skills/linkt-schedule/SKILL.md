---
name: linkt-schedule
description: Manage recurring signal monitoring schedules. Use when user wants to set up automated signal monitoring, create schedules, or manage existing schedules.
user-invocable: true
allowed-tools: mcp__linkt__list_schedules_v1_schedule_get, mcp__linkt__create_schedule_v1_schedule_post, mcp__linkt__get_schedule_v1_schedule, mcp__linkt__update_schedule_v1_schedule, mcp__linkt__delete_schedule_v1_schedule, mcp__linkt__list_icps_v1_icp_get, mcp__linkt__list_tasks_v1_task_get, AskUserQuestion
---

# Linkt Schedule Skill

Manage recurring schedules for signal monitoring tasks.

## Workflow

### Step 1: List Existing Schedules

Use `mcp__linkt__list_schedules_v1_schedule_get` to fetch all schedules.

Display schedules in a table format:
```markdown
## Your Schedules

| # | Name | Task | Frequency | Next Run | Status |
|---|------|------|-----------|----------|--------|
| 1 | Daily AI Signals | Signal Monitor: 50 companies | daily | Feb 6, 2026 09:00 | active |
| 2 | Weekly Updates | Signal Monitor: 100 companies | weekly | Feb 10, 2026 09:00 | paused |

**Actions:** [Create New] [Update] [Delete]
```

If no schedules exist:
```markdown
## Your Schedules

No schedules found. Would you like to create one?

To set up recurring signal monitoring:
1. First, ensure you have a signal monitoring task (see `/linkt-signals` or run `python 03_signals/signals_from_sheet.py`)
2. Then create a schedule to run it automatically
```

### Step 2: Handle User Action

Ask the user what they want to do:

```markdown
What would you like to do?
1. Create a new schedule
2. Update an existing schedule
3. Delete a schedule
4. View schedule details
```

### Step 3a: Create New Schedule

If creating a new schedule:

1. **List available tasks** using `mcp__linkt__list_tasks_v1_task_get` with `flow_name: "signal"`
2. **Ask user to select a task** to schedule
3. **Ask for frequency**: daily, weekly, or monthly
4. **Ask for preferred time** (optional, defaults to 09:00 UTC)
5. **Create the schedule** using `mcp__linkt__create_schedule_v1_schedule_post`

Schedule creation parameters:
- `task_id`: The task to run on schedule
- `frequency`: "daily", "weekly", or "monthly"
- `cron_expression`: Optional cron expression for custom schedules
- `enabled`: true (default)

Example cron expressions:
- Daily at 9am: `0 9 * * *`
- Weekly on Monday at 9am: `0 9 * * 1`
- Monthly on the 1st at 9am: `0 9 1 * *`

### Step 3b: Update Schedule

If updating an existing schedule:

1. **Ask which schedule** to update (by number)
2. **Ask what to change**: frequency, time, or status (enable/disable)
3. **Execute the update** using `mcp__linkt__update_schedule_v1_schedule`

### Step 3c: Delete Schedule

If deleting a schedule:

1. **Ask which schedule** to delete (by number)
2. **Confirm deletion** - this cannot be undone
3. **Execute deletion** using `mcp__linkt__delete_schedule_v1_schedule`

### Step 4: Confirm Result

After any action, display confirmation:

```markdown
## Schedule Created

**Name:** Daily AI Signal Monitor
**Task:** Signal Monitor: 50 companies
**Frequency:** Daily at 9:00 AM UTC
**Next run:** Feb 6, 2026 09:00 UTC
**Status:** Active

The task will run automatically on schedule. View results with `/linkt-signals`.
```

## Schedule Frequencies

| Frequency | Description | Default Time |
|-----------|-------------|--------------|
| `daily` | Runs every day | 09:00 UTC |
| `weekly` | Runs every Monday | 09:00 UTC |
| `monthly` | Runs on the 1st of each month | 09:00 UTC |

Custom schedules can be set using cron expressions.

## Error Handling

- If no tasks available: Direct user to create a signal monitoring task first
- If schedule creation fails: Show error message and suggest checking task configuration
- If update fails: Show error and current schedule state

## Example Output

```markdown
## Your Schedules

| # | Name | Task | Frequency | Next Run | Status |
|---|------|------|-----------|----------|--------|
| 1 | Daily AI Signals | Signal Monitor: 50 companies | daily | Feb 6, 2026 09:00 | active |

---

What would you like to do?

1. **Create new schedule** - Set up automated monitoring for a task
2. **Update schedule #1** - Change frequency, time, or status
3. **Delete schedule #1** - Remove this schedule
4. **View details #1** - See full schedule configuration
```

## Do NOT

- Create schedules for tasks that don't exist
- Delete schedules without user confirmation
- Change schedule frequency without asking
- Assume which task the user wants to schedule
