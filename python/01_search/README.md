# Search Examples

This directory contains examples for discovering companies and contacts using the Linkt API, from your first search to advanced targeting and pagination.

## Prerequisites

- LINKT_API_KEY in `.env` file at repository root
- Python 3.9+
- `pip install -r requirements.txt` from parent directory

## Examples

| File | Description | Duration |
|------|-------------|----------|
| `first_search.py` | Complete search workflow end-to-end | 15-20 min |
| `monitor_search.py` | Monitor a running search task in real-time | Ongoing |
| `review_search.py` | Review discovered companies and contacts | Instant |
| `advanced_targeting.py` | Create ICP with specific targeting criteria | 15-20 min |
| `pagination_patterns.py` | Paginate through large result sets | Instant |

### first_search.py

Creates all necessary resources and launches a search task:
1. Create an Ideal Customer Profile (ICP) with company and person criteria
2. Create Sheets to store discovered companies and contacts
3. Create a Search Task
4. Execute the Task (async - returns immediately)

```bash
python first_search.py
```

### monitor_search.py

Monitor a running search task with real-time entity processing progress.

```bash
python monitor_search.py <run_id>
```

### review_search.py

Retrieve and display companies and contacts discovered by a completed search.

```bash
python review_search.py <icp_id>
```

### advanced_targeting.py

Create an ICP with specific targeting criteria and contact enrichment settings.

```bash
python advanced_targeting.py
```

### pagination_patterns.py

Demonstrate pagination through large result sets using `page` and `page_size` parameters.

```bash
python pagination_patterns.py <icp_id>
```

## Core Concepts

### Ideal Customer Profile (ICP)
Defines your target companies AND contacts using natural language criteria.
- **Entity targets**: Both `company` and `person` types for search workflows
- **Criteria section**: Specific, measurable requirements in markdown format
- **Person targets** include `desired_count` (contacts per company)

### Sheet
A collection that stores discovered entities. Linked to one ICP.
- Search workflows need TWO sheets: one for companies, one for contacts
- Contacts link to their parent company via `parent_id`

### Task
A reusable workflow template (search, ingest, or signal monitoring).
- **Search tasks** require `desired_contact_count >= 1`
- Configuration uses `type: "search"`

### Run
A single execution of a task. Progresses through states until completion.

### Pagination Parameters

| Parameter | Description | Default | Max |
|-----------|-------------|---------|-----|
| `page` | Page number (1-indexed) | 1 | - |
| `page_size` | Results per page | 20 | 100 |

### ICP Creation Parameters

| Parameter | Description |
|-----------|-------------|
| `name` | Human-readable name |
| `description` | AI agent targeting instructions |
| `search_type` | "discovery" or "monitoring" |
| `desired_company_count` | Target number of companies |
| `desired_contact_count` | Contacts per company |

## What's Next?

After completing these examples:
- Try `../02_ingest/` to enrich your own data
- Set up `../03_signals/` to monitor accounts
- Explore `../04_advanced/` for bulk operations and export
