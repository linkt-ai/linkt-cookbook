---
name: linkt-signals
description: Legacy V1 only. Pull recent signals from Linkt and display contacts for outreach. Use when user wants to see business signals, find leads to contact, or prepare for LinkedIn outreach.
user-invocable: true
allowed-tools: mcp__linkt__list_signals_v1_signal_get, mcp__linkt__get_signal_v1_signal, mcp__linkt__list_entities_v1_entity_get, mcp__linkt__get_entity_v1_entity, mcp__linkt__list_icps_v1_icp_get
---

**Legacy V1.** This skill uses deprecated V1 tools. Use it only for an existing V1 workflow. New integrations use the V2 HTTP/MCP guidance in `v2/README.md`.


# Linkt Signals Skill

Display recent business signals with associated company and contact information for sales outreach.

## Workflow

### Step 1: Fetch Recent Signals

Use `mcp__linkt__list_signals_v1_signal_get` to fetch signals:
- Default: last 30 days
- Page size: 10-20 signals
- Sort by: `detected_at` descending (most recent first)

If no signals found, inform the user they may need to:
1. Set up signal monitoring first (see `python/03_signals/signals_from_sheet.py`)
2. Wait for the monitoring run to complete
3. Check if the ICP has companies to monitor

### Step 2: Enrich with Entity Data

For each signal, get the associated entity (company) using `mcp__linkt__get_entity_v1_entity` with the signal's `entity_id`.

Key fields to extract from company entity:
- `data.name` - Company name
- `data.website` - Company website
- `data.industry` - Industry
- `data.employee_count` - Company size
- `data.description` - Company description

### Step 3: Get Contacts for Each Company

For companies with interesting signals, fetch associated contacts using `mcp__linkt__list_entities_v1_entity_get`:
- Filter by `entity_type: "person"`
- Filter by `icp_id` from the company's ICP

Key contact fields:
- `data.name` or `data.full_name` - Contact name
- `data.title` or `data.job_title` - Job title
- `data.linkedin_url` or `data.linkedin` - LinkedIn profile URL
- `data.email` - Email address (if available)

### Step 4: Present Results

Format output as follows:

```markdown
## Recent Signals (Last 30 Days)

### 1. [Company Name] - [Signal Type Display Name]
**Signal:** [Summary from signal]
**Strength:** [Strong/Moderate/Weak] | **Score:** [0.85] | **Detected:** [Date]
**Source:** [source_url if available]

**Company:** [Industry] | [Employee Count] employees
[Company description snippet]

**Contacts:**
- [Name] ([Title]) - [LinkedIn](url)
- [Name] ([Title]) - [LinkedIn](url)

---

### 2. [Next Company]...
```

### Step 5: Offer Outreach

After displaying signals, ask the user:

> Would you like to reach out to any of these contacts? Enter a number to select a contact, or type 'skip' to exit.

If user selects a contact, provide context for the `/linkt-outreach` skill:
- Signal summary and type
- Company name and context
- Contact name, title, and LinkedIn URL

## Signal Types

Common signal types to highlight:
- `AI Initiatives` - AI projects, ML implementations
- `AI Thought Leadership` - LinkedIn posts about AI
- `AI Job Postings` - Hiring for AI roles
- `funding` - Funding rounds
- `leadership_change` - New executives
- `hiring_surge` - Rapid hiring
- `product_launch` - New products
- `partnership` - Strategic partnerships
- `expansion` - Geographic or market expansion
- `acquisition` - M&A activity
- `layoff` - Workforce reductions
- `award` - Industry recognition
- `pivot` - Strategic direction change
- `regulatory` - Compliance/regulatory news
- `rfp` - Request for proposals
- `contract_renewal` - Contract renewals
- `infrastructure` - Technology investments
- `compliance` - Compliance updates

## Signal Score

Each signal has a `score` field (0.0-1.0) indicating relevance/priority:
- **0.8-1.0**: High priority signals - strong buying signals
- **0.5-0.79**: Medium priority - worth monitoring
- **0.0-0.49**: Lower priority - informational

Display the score alongside strength for prioritization.

## Error Handling

- If API returns no signals: Suggest setting up monitoring
- If entity fetch fails: Skip that signal, continue with others
- If no contacts found: Note "No contacts enriched yet" for that company

## Example Output

```markdown
## Recent AI Signals (Last 30 Days)

Found 3 signals across 2 companies.

---

### 1. TechCorp Inc - AI Thought Leadership
**Signal:** CEO published LinkedIn article on "How AI is Transforming Enterprise Sales"
**Strength:** Strong | **Score:** 0.92 | **Detected:** Jan 28, 2026
**Source:** [LinkedIn Post](https://linkedin.com/posts/...)

**Company:** Enterprise Software | 500-1000 employees
Leading provider of sales automation tools for mid-market companies.

**Contacts:**
1. Sarah Chen (VP of Sales) - [LinkedIn](https://linkedin.com/in/sarahchen)
2. Mike Johnson (Head of Partnerships) - [LinkedIn](https://linkedin.com/in/mikej)

---

### 2. DataFlow Systems - AI Job Postings
**Signal:** Posted 5 AI/ML engineering roles in the past week
**Strength:** Strong | **Score:** 0.88 | **Detected:** Jan 27, 2026

**Company:** Data Infrastructure | 200-500 employees
Cloud-native data platform for real-time analytics.

**Contacts:**
3. Alex Rivera (CTO) - [LinkedIn](https://linkedin.com/in/alexrivera)
4. Jordan Lee (VP Engineering) - [LinkedIn](https://linkedin.com/in/jordanlee)

---

**Select a contact for outreach (1-4) or 'skip':**
```
