# Legacy V1

These examples target the deprecated V1 SDK. Existing versions remain available.
New integrations use the [V2 HTTP examples](../v2/README.md).

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
   python 01_search/first_search.py
   ```

## Examples by Category

| Directory | Description |
|-----------|-------------|
| `01_search/` | Company and contact discovery examples |
| `02_ingest/` | CSV import and data enrichment |
| `03_signals/` | Signal sources and querying |
| `04_advanced/` | Schedule management, bulk operations, export |

## Requirements

- Python 3.9+
- Linkt API key ([get one here](https://app.linkt.ai/settings/api-keys))
