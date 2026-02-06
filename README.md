# Linkt Cookbook

Build AI-powered GTM workflows with the Linkt platform. This cookbook includes:

- **Claude Code Skills**: Interactive workflows for signal monitoring and LinkedIn outreach
- **Python Examples**: Ready-to-run scripts for lead discovery, data enrichment, and signal monitoring
- **TypeScript Examples**: Coming soon

## Quick Start (Claude Code Skills)

The fastest way to experience Linkt is through Claude Code skills.

### 1. Clone and Configure

```bash
git clone https://github.com/linkt-ai/linkt-cookbook.git
cd linkt-cookbook

# Create .env file with your API key
echo "LINKT_API_KEY=sk-your-key-here" > .env
```

Get your API key from [app.linkt.ai/settings/api-keys](https://app.linkt.ai/settings/api-keys).

### 2. Open in Claude Code

```bash
claude
```

### 3. Use the Skills

| Command | Description |
|---------|-------------|
| `/linkt-init` | Set up your profile for personalized outreach |
| `/linkt-signals` | Pull recent signals and find contacts for outreach |
| `/linkt-outreach` | Draft personalized LinkedIn connection requests |
| `/linkt-schedule` | Manage recurring signal monitoring schedules |
| `/linkt-status` | Bulk update entity status for workflow management |

**Demo flow:**
1. Run `/linkt-init` to set up your profile
2. Run `/linkt-signals` to see recent AI-focused signals (with scores)
3. Select a contact from the results
4. Claude drafts a personalized connection message
5. Review, edit, and send via LinkedIn
6. Use `/linkt-status` to mark entities as contacted

For detailed skill documentation, see [docs/skills-overview.md](docs/skills-overview.md).

### Prerequisites for Skills

- **Required:** Linkt API key
- **Optional:** Browser-use MCP for LinkedIn automation

---

## Quick Start (Python SDK)

### 1. Clone the Repository

```bash
git clone https://github.com/linkt-ai/linkt-cookbook.git
cd linkt-cookbook
```

### 2. Set Up Environment Variables

Create a `.env` file in the repository root:

```bash
LINKT_API_KEY=your-api-key-here
```

Get your API key from [app.linkt.ai/settings/api-keys](https://app.linkt.ai/settings/api-keys).

### 3. Set Up Python Environment

```bash
cd python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run Your First Example

```bash
python 01_search/first_search.py
```

## Directory Structure

```
linkt-cookbook/
├── .env                        # API credentials (create this)
├── .claude/                    # Claude Code configuration
│   ├── CLAUDE.md               # Project context
│   └── skills/                 # Claude Code skills
│       ├── linkt-init/         # Profile setup skill
│       ├── linkt-signals/      # Signal monitoring skill
│       ├── linkt-outreach/     # LinkedIn outreach skill
│       ├── linkt-schedule/     # Schedule management skill
│       └── linkt-status/       # Entity status skill
├── docs/
│   └── skills-overview.md      # Skills documentation
├── python/
│   ├── requirements.txt        # Python dependencies
│   ├── 01_search/              # Company and contact discovery
│   ├── 02_ingest/              # CSV import and enrichment
│   ├── 03_signals/             # Signal sources and querying
│   └── 04_advanced/            # Schedule management, bulk ops, export
└── typescript/                 # TypeScript examples (coming soon)
```

## Example Categories

| Directory | Description | Examples |
|-----------|-------------|----------|
| `01_search/` | Discover companies and contacts | `first_search.py`, `monitor_search.py`, `review_search.py`, `advanced_targeting.py`, `pagination_patterns.py` |
| `02_ingest/` | Import and enrich your data | `csv_upload.py`, `csv_enrichment.py` |
| `03_signals/` | Signal sources and querying | `signals_from_sheet.py`, `signals_from_csv.py`, `signals_from_topic.py`, `query_signals.py` |
| `04_advanced/` | Schedule management, bulk operations | `schedule_management.py`, `bulk_operations.py`, `export_entities.py`, `entity_status_workflow.py` |

## Prerequisites

- **For Claude Code Skills:**
  - Linkt API key
  - Claude Code CLI ([installation guide](https://claude.ai/claude-code))
  - Optional: Browser-use MCP for LinkedIn automation

- **For Python SDK:**
  - Python 3.9+
  - Linkt API key

## Resources

- [Linkt Documentation](https://docs.linkt.ai)
- [Python SDK on PyPI](https://pypi.org/project/linkt-sdk/)
- [SDK API Reference](https://github.com/linkt-ai/linkt-python-sdk/blob/main/api.md)

## License

MIT
