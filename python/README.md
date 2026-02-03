# Python Examples

Practical examples for the Linkt Python SDK.

## Setup

1. Create and activate virtual environment:
   ```bash
   cd python
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file in the repository root with:
   ```
   LINKT_API_KEY=your-api-key-here
   ```

4. Run your first example:
   ```bash
   python 01_getting_started/hello_world.py
   ```

## Examples by Category

| Directory | Description |
|-----------|-------------|
| `01_getting_started/` | SDK setup verification and basic workflows |
| `02_monitor_leads/` | Signal monitoring for discovered companies |
| `02_search/` | Company and contact discovery examples |
| `03_ingest/` | CSV import and data enrichment |
| `04_signals/` | Business signal monitoring |
| `05_advanced/` | Custom fields, webhooks, async patterns |

## Requirements

- Python 3.9+
- Linkt API key ([get one here](https://app.linkt.ai/settings/api-keys))
