# Getting Started

Verify your setup and learn the fundamental Linkt workflow.

## Examples

| File | Description | Duration |
|------|-------------|----------|
| `hello_world.py` | Verify SDK connection and credentials | Instant |
| `first_discovery.py` | Complete search workflow end-to-end | 15-20 min |

## Prerequisites

- Completed setup from `python/README.md`
- Valid API key with staging or production access

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

## What's Next?

After completing these examples:
- Explore `02_search/` for advanced targeting options
- Try `03_ingest/` to enrich your own data
- Set up `04_signals/` to monitor accounts
