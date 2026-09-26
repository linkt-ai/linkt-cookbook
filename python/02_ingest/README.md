# Legacy V1

These examples target the deprecated V1 SDK. Existing versions remain available.
New integrations use the [V2 HTTP examples](../../v2/README.md).

# Ingest Examples

This directory contains examples for importing and enriching your own data using the Linkt API.

## Prerequisites

- LINKT_API_KEY in `.env` file at repository root
- Python 3.9+
- `pip install -r requirements.txt` from parent directory

## Examples

### csv_upload.py

Upload a CSV file to Linkt for enrichment.

**Features:**
- File upload to Linkt storage
- CSV preview and validation
- File ID retrieval for subsequent tasks

**Usage:**
```bash
python csv_upload.py sample_data/companies.csv
```

**Expected Output:**
```
Connected to Linkt API (production)

[1/2] Previewing CSV file: sample_data/companies.csv
   Columns: name,domain,industry,employees,headquarters
   Rows: 10

   Preview (first 3 rows):
     Meta Platforms,meta.com,Social Media & Technology,67000,Menlo Park CA
     Apple,apple.com,Consumer Electronics & Technology,164000,Cupertino CA
     Amazon,amazon.com,E-Commerce & Cloud Computing,1540000,Seattle WA

[2/2] Uploading file...
   Upload successful!
     File ID: file_abc123
     Filename: companies.csv
     Rows: 10
```

### csv_enrichment.py

Complete workflow for enriching CSV data with company and contact information.

**Features:**
- Upload CSV (or use existing file_id)
- Create ICP for enrichment
- Create ingest task with enrichment config
- Monitor enrichment progress
- Retrieve enriched results

**Usage:**
```bash
# Upload and enrich a new file
python csv_enrichment.py sample_data/companies.csv

# Or use an existing file_id
python csv_enrichment.py --file-id file_abc123
```

**Expected Output:**
```
Connected to Linkt API (production)

[1/6] Uploading CSV file: sample_data/companies.csv
   File ID: file_abc123
   Rows: 10

[2/6] Creating ICP for enrichment...
   ICP ID: icp_xyz789

[3/6] Creating ingest task...
   Task ID: task_def456

[4/6] Starting enrichment run...
   Run ID: run_ghi012

[5/6] Monitoring progress...
   Status: running (3/10)
   Status: running (7/10)
   Status: completed (10/10)

[6/6] Retrieving enriched results...
   Enriched companies: 10
     - TechCorp Solutions | Enterprise Software | 500 employees
     - DataFlow Systems | Data Infrastructure | 250 employees
     ...

   Contacts found: 20
```

## Sample Data

The `sample_data/` directory contains example CSV files:

### companies.csv

A sample list of 10 well-known companies (FANG+) for testing enrichment:

```csv
name,domain,industry,employees,headquarters
Meta Platforms,meta.com,Social Media & Technology,67000,Menlo Park CA
Apple,apple.com,Consumer Electronics & Technology,164000,Cupertino CA
...
```

## CSV Column Mapping

Linkt auto-detects common column names:

| CSV Column | Entity Field | Description |
|------------|-------------|-------------|
| `name`, `company_name` | `name` | Company name |
| `domain`, `website` | `domain` | Company website |
| `industry` | `industry` | Industry category |
| `employees`, `employee_count` | `employees` | Employee count |
| `revenue` | `revenue` | Revenue range |
| `headquarters`, `location` | `headquarters` | HQ location |
| `linkedin_url`, `linkedin` | `linkedin` | LinkedIn URL |

Custom columns are preserved and can be used for filtering.

## Enrichment Options

The `enrichment_config` parameter controls what data is enriched:

```python
"enrichment_config": {
    "enrich_company_data": True,   # Fetch additional company info
    "find_contacts": True,          # Find contacts at companies
    "desired_contact_count": 2,     # Contacts per company
}
```

## Next Steps

1. **Review enriched results**:
   ```bash
   python ../01_search/review_search.py <icp_id>
   ```

2. **Set up signal monitoring**:
   ```bash
   python ../03_signals/signals_from_sheet.py <icp_id>
   ```

3. **Export enriched data**:
   ```bash
   python ../04_advanced/export_entities.py <icp_id>
   ```
