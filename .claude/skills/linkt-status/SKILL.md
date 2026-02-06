---
name: linkt-status
description: Bulk update entity status for workflow management. Use when user wants to mark leads as reviewed, passed, or contacted, or manage their sales pipeline status.
user-invocable: true
allowed-tools: mcp__linkt__list_entities_v1_entity_get, mcp__linkt__get_entity_v1_entity, mcp__linkt__update_entity_v1_entity, mcp__linkt__bulk_update_status_v1_entity_status_bulk_patch, mcp__linkt__list_icps_v1_icp_get, AskUserQuestion
---

# Linkt Status Skill

Bulk update entity status for sales workflow management.

## Status Values

| Status | Description | Typical Use |
|--------|-------------|-------------|
| `new` | Newly discovered entity | Default for new leads |
| `reviewed` | Entity has been reviewed | After initial qualification |
| `passed` | Not a fit, passing on this lead | Disqualified leads |
| `contacted` | Outreach initiated | After sending message |

## Workflow

### Step 1: Select ICP

Use `mcp__linkt__list_icps_v1_icp_get` to list available ICPs.

Ask user which ICP to manage:
```markdown
## Select an ICP

| # | Name | Companies | Contacts |
|---|------|-----------|----------|
| 1 | AI-First Companies | 150 | 450 |
| 2 | Series B Startups | 75 | 200 |

Which ICP would you like to manage? (Enter number)
```

### Step 2: Filter by Current Status

Ask user which entities to view:
```markdown
## Filter Entities

Which entities would you like to see?
1. All entities
2. New (not yet reviewed)
3. Reviewed
4. Passed
5. Contacted
```

### Step 3: List Entities

Use `mcp__linkt__list_entities_v1_entity_get` with filters:
- `icp_id`: Selected ICP
- `entity_type`: "company" or "person"
- `status`: Filter if selected (new, reviewed, passed, contacted)

Display in table format:
```markdown
## Companies - New (25 total)

| # | Company | Industry | Employees | Status |
|---|---------|----------|-----------|--------|
| 1 | TechCorp Inc | Software | 500 | new |
| 2 | DataFlow Systems | Data | 200 | new |
| 3 | AI Solutions | AI/ML | 150 | new |
| 4 | CloudFirst | Cloud | 300 | new |
| 5 | Innovate Labs | R&D | 100 | new |

Showing 5 of 25. [Next Page] [Select All]
```

### Step 4: Select Entities

Ask user to select entities for status update:
```markdown
Select entities to update:
- Enter numbers separated by commas (e.g., 1, 3, 5)
- Enter a range (e.g., 1-5)
- Enter "all" to select all on this page
- Enter "all-pages" to select all matching the filter
```

### Step 5: Choose New Status

Ask user for the new status:
```markdown
## Update Status

Selected: 3 companies (TechCorp Inc, DataFlow Systems, AI Solutions)

What status should these entities have?
1. **reviewed** - Mark as reviewed/qualified
2. **passed** - Mark as not a fit
3. **contacted** - Mark as outreach sent
4. **new** - Reset to new
```

### Step 6: Execute Update

For single entity updates, use `mcp__linkt__update_entity_v1_entity`.

For multiple entities, use `mcp__linkt__bulk_update_status_v1_entity_status_bulk_patch`:
- `entity_ids`: List of entity IDs to update
- `status`: New status value

### Step 7: Confirm Result

Display confirmation:
```markdown
## Status Updated

Successfully updated 3 companies to "reviewed":
- TechCorp Inc
- DataFlow Systems
- AI Solutions

**Summary:**
- New: 22 remaining
- Reviewed: 3 (just updated)
- Passed: 0
- Contacted: 0
```

## Bulk Operations

For large updates, the skill supports:
- Updating all entities matching a filter
- Updating across entity types (companies + contacts)
- Resetting status back to "new"

Example bulk update:
```markdown
## Bulk Update

You're about to update **all 150 companies** in "AI-First Companies" to "reviewed".

This will:
- Update 150 company records
- This action can be reversed by setting status back to "new"

Proceed? (yes/no)
```

## Error Handling

- If no entities found: Suggest checking ICP or running discovery
- If update fails: Show which entities failed and why
- If partial failure: Show success count and list failures

## Example Flow

```markdown
You: /linkt-status

Claude: ## Select an ICP

| # | Name | Companies | Contacts |
|---|------|-----------|----------|
| 1 | AI-First Companies | 150 | 450 |

Which ICP would you like to manage?

You: 1

Claude: ## Filter Entities

Which entities would you like to see?
1. All entities
2. New (not yet reviewed)
3. Reviewed
...

You: 2

Claude: ## Companies - New (25 total)

| # | Company | Industry | Status |
|---|---------|----------|--------|
| 1 | TechCorp Inc | Software | new |
| 2 | DataFlow Systems | Data | new |
...

Select entities to update (e.g., 1,2,3 or 1-5 or all):

You: 1-3

Claude: Selected: TechCorp Inc, DataFlow Systems, AI Solutions

What status should these entities have?
1. reviewed
2. passed
3. contacted

You: 1

Claude: ## Status Updated

Successfully updated 3 companies to "reviewed".
```

## Do NOT

- Update status without user confirmation
- Assume which status the user wants
- Update entities outside the selected ICP
- Make destructive changes without warning (bulk updates > 50 entities)
