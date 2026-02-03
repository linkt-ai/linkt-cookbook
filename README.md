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
| `/linkt-signals` | Pull recent signals and find contacts for outreach |
| `/linkt-outreach` | Draft personalized LinkedIn connection requests |

**Demo flow:**
1. Run `/linkt-signals` to see recent AI-focused signals
2. Select a contact from the results
3. Claude drafts a personalized connection message
4. Review, edit, and send via LinkedIn

For detailed skill documentation, see [docs/skills-overview.md](docs/skills-overview.md).

### Prerequisites for Skills

- **Required:** Linkt API key
- **Optional:** Browser-use MCP for LinkedIn automation ([setup guide](docs/browser-use-setup.md))

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
python 01_getting_started/hello_world.py
```

## Directory Structure

```
linkt-cookbook/
├── .env                        # API credentials (create this)
├── .claude/                    # Claude Code configuration
│   ├── CLAUDE.md               # Project context
│   └── skills/                 # Claude Code skills
│       ├── linkt-signals/      # Signal monitoring skill
│       └── linkt-outreach/     # LinkedIn outreach skill
├── docs/
│   ├── skills-overview.md      # Skills documentation
│   └── browser-use-setup.md    # Browser automation setup
├── python/
│   ├── requirements.txt        # Python dependencies
│   ├── 01_getting_started/     # SDK setup and basic workflows
│   ├── 02_monitor_leads/       # Signal monitoring setup
│   ├── 02_search/              # Company and contact discovery
│   ├── 03_ingest/              # CSV import and enrichment
│   ├── 04_signals/             # Business signal monitoring
│   └── 05_advanced/            # Custom fields, webhooks, async
└── typescript/                 # TypeScript examples (coming soon)
```

## Example Categories

| Directory | Description | Examples |
|-----------|-------------|----------|
| `01_getting_started/` | Verify setup, learn core workflow | `hello_world.py`, `first_discovery.py` |
| `02_search/` | Discover companies and contacts | Coming soon |
| `03_ingest/` | Import and enrich your data | Coming soon |
| `04_signals/` | Monitor accounts for business signals | Coming soon |
| `05_advanced/` | Advanced patterns and integrations | Coming soon |

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
