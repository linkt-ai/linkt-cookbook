# Legacy V1

These instructions support existing V1 workflows. New integrations use `v2/README.md` and `v2/mcp.json`.
The root `.mcp.json` connects the legacy tools used here. Do not apply these tool names to V2.

# Claude Code Skills Overview

This cookbook includes Claude Code skills that demonstrate AI-powered GTM workflows using the Linkt platform.

## Available Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Linkt Init | `/linkt-init` | Set up your profile for personalized outreach |
| Linkt Signals | `/linkt-signals` | Pull recent business signals and display contacts for outreach |
| Linkt Outreach | `/linkt-outreach` | Draft and send LinkedIn connection requests based on signal context |
| Linkt Schedule | `/linkt-schedule` | Manage recurring signal monitoring schedules |
| Linkt Status | `/linkt-status` | Bulk update entity status for workflow management |

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/linkt-ai/linkt-cookbook.git
cd linkt-cookbook
```

### 2. Configure Environment

Create a `.env` file in the repository root:

```bash
LINKT_API_KEY=sk-your-api-key-here
```

Get your API key from [app.linkt.ai/settings/api-keys](https://app.linkt.ai/settings/api-keys).

### 3. Open in Claude Code

```bash
claude
```

Claude Code will automatically detect the `.claude/` directory and load the skills.

### 4. Use the Skills

Type `/linkt-signals` to pull recent signals and find contacts for outreach.

## Skill Details

### `/linkt-signals`

**Purpose:** Display recent business signals (AI initiatives, hiring, funding, etc.) with associated company and contact information.

**What it does:**
1. Fetches signals from the last 30 days via Linkt MCP
2. Enriches each signal with company details
3. Finds contacts associated with each company
4. Presents a formatted summary with LinkedIn URLs
5. Offers to help with outreach to selected contacts

**Example output:**
```
## Recent AI Signals (Last 30 Days)

### 1. TechCorp Inc - AI Thought Leadership
**Signal:** CEO published article on AI transformation
**Strength:** Strong | **Score:** 0.92 | **Detected:** Jan 28, 2026

**Contacts:**
1. Sarah Chen (VP Sales) - [LinkedIn](url)
2. Mike Johnson (Partnerships) - [LinkedIn](url)

Select a contact for outreach (1-2) or 'skip':
```

**Signal Score:**
Each signal includes a score field (0.0-1.0) for prioritization:
- **0.8-1.0**: High priority - strong buying signals
- **0.5-0.79**: Medium priority - worth monitoring
- **0.0-0.49**: Lower priority - informational

**Prerequisites:**
- Linkt API key configured
- Signal monitoring set up (see `python/03_signals/signals_from_sheet.py`)

### `/linkt-outreach`

**Purpose:** Draft and send personalized LinkedIn connection requests based on signal context.

**What it does:**
1. Takes signal context and contact information
2. Drafts a personalized connection message (max 300 chars)
3. Presents the draft for user approval
4. Uses Browser-use MCP to navigate and send (or provides manual instructions)

**Example flow:**
```
## LinkedIn Connection Request

**To:** Sarah Chen (VP Sales) at TechCorp Inc
**Profile:** https://linkedin.com/in/sarahchen

**Draft Message:**
---
Hi Sarah,

Your article on AI in enterprise sales resonated - we're
seeing similar patterns. Would love to connect and exchange
insights on where AI is heading in GTM.
---

Type 'send' to proceed, 'edit' to modify, or 'cancel':
```

**Prerequisites:**
- Linkt API key configured
- Browser-use MCP configured (optional, for automation)

### `/linkt-schedule`

**Purpose:** Manage recurring schedules for automated signal monitoring.

**What it does:**
1. Lists existing schedules with status
2. Creates new schedules (daily, weekly, monthly)
3. Updates schedule frequency or status
4. Deletes schedules

**Example output:**
```
## Your Schedules

| # | Name | Task | Frequency | Next Run | Status |
|---|------|------|-----------|----------|--------|
| 1 | Daily AI Signals | Signal Monitor: 50 companies | daily | Feb 6, 2026 09:00 | active |

What would you like to do?
1. Create new schedule
2. Update schedule #1
3. Delete schedule #1
```

### `/linkt-status`

**Purpose:** Bulk update entity status for sales workflow management.

**What it does:**
1. Lists entities filtered by status
2. Allows selection of multiple entities
3. Updates status (new/reviewed/passed/contacted)
4. Shows status summary

**Example output:**
```
## Companies - New (25 total)

| # | Company | Industry | Status |
|---|---------|----------|--------|
| 1 | TechCorp Inc | Software | new |
| 2 | DataFlow Systems | Data | new |

Select entities to update (1,2,3 or 1-5 or all):
```

## Demo Walkthrough

This walkthrough demonstrates the complete signal-to-outreach flow:

### Step 1: Pull Signals

```
You: /linkt-signals
```

Claude displays recent signals with companies and contacts.

### Step 2: Select a Contact

```
You: 1
```

Select a contact by number to initiate outreach.

### Step 3: Review Message

Claude drafts a personalized connection request based on the signal context.

### Step 4: Approve and Send

```
You: send
```

If Browser-use MCP is configured, Claude navigates to LinkedIn and sends the request. Otherwise, provides copy-paste instructions.

## Customization

### Filtering Signals

Modify the skill to filter by specific signal types:
- Edit `.claude/skills/linkt-signals/SKILL.md`
- Add filters in the API call instructions (e.g., `signal_type: "AI Thought Leadership"`)

### Message Templates

Customize outreach message style:
- Edit `.claude/skills/linkt-outreach/SKILL.md`
- Modify the "Message Template Structure" section
- Add your company's value proposition

### Adding New Signal Types

The Linkt platform supports 17 signal types:
- `funding` - Funding rounds
- `leadership_change` - Executive changes
- `layoff` - Workforce reductions
- `product_launch` - New products
- `partnership` - Strategic partnerships
- `acquisition` - M&A activity
- `expansion` - Geographic/market expansion
- `award` - Industry recognition
- `pivot` - Strategic direction changes
- `regulatory` - Compliance/regulatory news
- `rfp` - Request for proposals
- `contract_renewal` - Contract renewals
- `hiring_surge` - Rapid hiring
- `infrastructure` - Technology investments
- `compliance` - Compliance updates
- `job_posting` - Specific job postings
- `other` - Custom signals (AI Initiatives, etc.)

To monitor specific types, update your signal monitoring task configuration.

## Troubleshooting

### No signals found

1. Verify your API key is correct
2. Check if signal monitoring is set up:
   ```bash
   cd python
   python 01_search/first_search.py
   ```
3. Run a monitoring task if needed

### Browser automation not working

1. Check Browser-use MCP configuration in `.mcp.json`
2. The skill provides manual instructions as fallback

### LinkedIn rate limits

If LinkedIn restricts your account:
1. Wait 24-48 hours before sending more requests
2. Reduce daily request volume
3. Ensure messages are personalized (not copy-paste)

## Related Resources

- [Linkt Documentation](https://docs.linkt.ai)
- [Linkt Python SDK](https://pypi.org/project/linkt-sdk/)
- [Python Examples](../python/README.md)
