# Legacy V1: deprecated SDK example. New integrations use v2/run.py.
"""
Linkt SDK - CSV Enrichment Workflow

This script demonstrates the complete workflow for enriching CSV data:
    1. Upload a CSV file (or use existing file_id)
    2. Create an ICP for the enrichment
    3. Create sheets to store enriched companies and contacts
    4. Create an ingest task with IngestTaskConfigRequest
    5. Execute the task
    6. Monitor progress
    7. Retrieve enriched results

Usage:
    python csv_enrichment.py <csv_file_path>
    python csv_enrichment.py --file-id <file_id>

Example:
    python csv_enrichment.py sample_data/companies.csv
    python csv_enrichment.py --file-id file_abc123

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - CSV file with company data OR existing file_id
"""

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from linkt import Linkt

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


def get_attr(obj, key, default=None):
    """Get attribute from object or dict (handles mixed SDK return types)."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def get_field_display(data, field_name, default="N/A"):
    """Extract the display value from a nested entity data field."""
    if isinstance(data, dict):
        field = data.get(field_name, {})
        if isinstance(field, dict):
            return field.get("display", default)
        return getattr(field, "display", default)
    else:
        field = getattr(data, field_name, None)
        if field is None:
            return default
        return getattr(field, "display", default)


def main():
    """Run complete CSV enrichment workflow."""

    print("=" * 60)
    print("Linkt SDK - CSV Enrichment Workflow")
    print("=" * 60)

    # =========================================================================
    # Parse Command Line Arguments
    # =========================================================================
    file_id = None
    csv_path = None

    if len(sys.argv) == 2:
        csv_path = Path(sys.argv[1])
        if not csv_path.exists():
            print(f"\nError: File not found: {csv_path}")
            sys.exit(1)
    elif len(sys.argv) == 3 and sys.argv[1] == "--file-id":
        file_id = sys.argv[2]
    else:
        print("\nUsage:")
        print("  python csv_enrichment.py <csv_file_path>")
        print("  python csv_enrichment.py --file-id <file_id>")
        print("\nExamples:")
        print("  python csv_enrichment.py sample_data/companies.csv")
        print("  python csv_enrichment.py --file-id file_abc123")
        sys.exit(1)

    # =========================================================================
    # Initialize Client
    # =========================================================================
    if not os.getenv("LINKT_API_KEY"):
        print("Error: LINKT_API_KEY environment variable not set.")
        print(f"  Expected .env file at: {env_path}")
        sys.exit(1)

    environment = os.getenv("LINKT_API_ENVIRONMENT", "production")
    if environment == "dev":
        client = Linkt(base_url="http://localhost:8080")
    else:
        client = Linkt(environment=environment)
    print(f"\nConnected to Linkt API ({environment})")

    # =========================================================================
    # Step 1: Upload CSV (if not using existing file_id)
    # =========================================================================
    if csv_path:
        print(f"\n[1/7] Uploading CSV file: {csv_path}")

        with open(csv_path, "rb") as f:
            file_content = f.read()

        upload_response = client.files.upload(
            file=(csv_path.name, file_content, "text/csv"),
        )

        file_id = get_attr(upload_response, "file_id")
        row_count = get_attr(upload_response, "row_count", "unknown")
        print(f"   File ID: {file_id}")
        print(f"   Rows: {row_count}")
    else:
        print(f"\n[1/7] Using existing file: {file_id}")

    # =========================================================================
    # Step 2: Create ICP for Enrichment
    # =========================================================================
    # Even for ingest workflows, we need an ICP to store the enriched entities.

    print("\n[2/7] Creating ICP for enrichment...")

    icp = client.icp.create(
        name=f"CSV Import - {time.strftime('%Y-%m-%d %H:%M')}",
        description="Companies imported from CSV for enrichment",
        entity_targets=[
            {
                "entity_type": "company",
                "description": "Companies imported from CSV for enrichment",
                "root": True,
            },
            {
                "entity_type": "person",
                "description": "Key contacts at imported companies",
                "desired_count": 2,
            },
        ],
    )

    icp_id = get_attr(icp, "id")
    print(f"   ICP ID: {icp_id}")

    # =========================================================================
    # Step 3: Create Sheets
    # =========================================================================
    # The ingest backend requires sheets to exist on the ICP before execution.
    # Sheets define where enriched entities (companies, contacts) are stored.

    print("\n[3/7] Creating sheets to store results...")

    company_sheet = client.sheet.create(
        name="Imported Companies",
        description="Companies imported from CSV for enrichment",
        icp_id=icp_id,
        entity_type="company",
    )

    print(f"   Created Company Sheet: {get_attr(company_sheet, 'name')}")
    print(f"     ID: {get_attr(company_sheet, 'id')}")

    person_sheet = client.sheet.create(
        name="Imported Contacts",
        description="Contacts found at imported companies",
        icp_id=icp_id,
        entity_type="person",
    )

    print(f"   Created Person Sheet: {get_attr(person_sheet, 'name')}")
    print(f"     ID: {get_attr(person_sheet, 'id')}")

    # =========================================================================
    # Step 4: Create Ingest Task
    # =========================================================================
    # The ingest task type processes uploaded files and enriches the data.
    #
    # IngestTaskConfigRequest fields:
    #   - type: "ingest" (discriminator)
    #   - file_id: ID of the uploaded file
    #   - entity_type: "company" or "person"
    #   - column_mapping: Map CSV columns to entity fields (optional)
    #   - enrichment_config: What fields to enrich (optional)

    print("\n[4/7] Creating ingest task...")

    task_config = {
        "type": "ingest",
        "file_id": file_id,
        "csv_entity_type": "company",
        "primary_column": "name",
        # Column mapping is auto-detected but can be explicit:
        # "column_mapping": {
        #     "Company Name": "name",
        #     "Website": "domain",
        #     "Industry": "industry",
        # },
    }

    task = client.task.create(
        name="CSV Enrichment",
        description="Enrich companies from uploaded CSV",
        flow_name="ingest",
        deployment_name="main",
        icp_id=icp_id,
        task_config=task_config,
    )

    task_id = get_attr(task, "id")
    print(f"   Task ID: {task_id}")

    # =========================================================================
    # Step 5: Execute Task
    # =========================================================================
    print("\n[5/7] Starting enrichment run...")

    # Pass empty input_entities to satisfy Prefect deployment schema validation.
    # The ingest workflow loads entities from the CSV file_id in task_config,
    # but the deployment still requires input_entities to be present.
    execution = client.task.execute(task_id, icp_id=icp_id, parameters={"input_entities": []})
    run_id = get_attr(execution, "run_id")
    print(f"   Run ID: {run_id}")

    # =========================================================================
    # Step 6: Monitor Progress
    # =========================================================================
    print("\n[6/7] Monitoring progress...")

    max_wait = 300  # 5 minutes max
    poll_interval = 10  # Check every 10 seconds
    elapsed = 0

    while elapsed < max_wait:
        run = client.run.retrieve(run_id)
        status = get_attr(run, "status", "unknown")
        progress = get_attr(run, "progress", {})

        if isinstance(progress, dict):
            completed = progress.get("completed", 0)
            total = progress.get("total", 0)
        else:
            completed = getattr(progress, "completed", 0)
            total = getattr(progress, "total", 0)

        print(f"   Status: {status} ({completed}/{total})")

        if status.lower() in ["completed", "failed", "cancelled"]:
            break

        time.sleep(poll_interval)
        elapsed += poll_interval
    else:
        print("   Timeout waiting for completion. Check run status manually.")

    # =========================================================================
    # Step 7: Retrieve Results
    # =========================================================================
    print("\n[7/7] Retrieving enriched results...")

    # Fetch enriched companies
    companies_response = client.entity.list(
        icp_id=icp_id,
        entity_type="company",
        page_size=10,
    )
    total_companies = get_attr(companies_response, "total", 0)
    companies = get_attr(companies_response, "entities", [])

    print(f"\n   Enriched companies: {total_companies}")
    for entity in companies[:5]:
        data = get_attr(entity, "data", {})
        name = get_field_display(data, "name", "Unknown")
        industry = get_field_display(data, "industry", "N/A")
        employees = get_field_display(data, "employees", "N/A")
        print(f"     - {name} | {industry} | {employees} employees")

    # Fetch enriched contacts
    contacts_response = client.entity.list(
        icp_id=icp_id,
        entity_type="person",
        page_size=10,
    )
    total_contacts = get_attr(contacts_response, "total", 0)

    print(f"\n   Contacts found: {total_contacts}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 60)
    print("Enrichment Complete")
    print("=" * 60)

    print(f"\nICP ID: {icp_id}")
    print(f"Companies enriched: {total_companies}")
    print(f"Contacts found: {total_contacts}")

    print("\nNext steps:")
    print(f"  1. Review results:")
    print(f"     python ../01_search/review_search.py {icp_id}")
    print(f"\n  2. Set up signal monitoring:")
    print(f"     python ../03_signals/signals_from_sheet.py {icp_id}")
    print(f"\n  3. View in dashboard:")
    print(f"     https://app.linkt.ai/icp/{icp_id}")


if __name__ == "__main__":
    main()
