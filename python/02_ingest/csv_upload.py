"""
Linkt SDK - CSV File Upload

This script demonstrates how to upload a CSV file to Linkt for enrichment.

The uploaded file can then be used with ingest tasks to:
    - Enrich company data with additional fields
    - Find contacts for uploaded companies
    - Add LinkedIn profiles to existing contacts

Usage:
    python csv_upload.py <csv_file_path>

Example:
    python csv_upload.py sample_data/companies.csv

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - CSV file with company data (minimum: name or domain column)
"""

import os
import sys
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


def main():
    """Upload a CSV file to Linkt."""

    print("=" * 60)
    print("Linkt SDK - CSV File Upload")
    print("=" * 60)

    # =========================================================================
    # Parse Command Line Arguments
    # =========================================================================
    if len(sys.argv) != 2:
        print("\nUsage: python csv_upload.py <csv_file_path>")
        print("\nExample:")
        print("  python csv_upload.py sample_data/companies.csv")
        print("\nThe CSV file should have columns like:")
        print("  - name: Company name")
        print("  - domain: Company website domain")
        print("  - industry: Industry (optional)")
        print("  - employees: Employee count (optional)")
        sys.exit(1)

    csv_path = Path(sys.argv[1])

    if not csv_path.exists():
        print(f"\nError: File not found: {csv_path}")
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
    # Preview CSV Contents
    # =========================================================================
    print(f"\n[1/2] Previewing CSV file: {csv_path}")

    # Read first few lines to show preview
    with open(csv_path, "r") as f:
        lines = f.readlines()

    if len(lines) < 2:
        print("Error: CSV file must have a header and at least one row")
        sys.exit(1)

    header = lines[0].strip()
    print(f"\n   Columns: {header}")
    print(f"   Rows: {len(lines) - 1}")

    print("\n   Preview (first 3 rows):")
    for line in lines[1:4]:
        print(f"     {line.strip()}")

    # =========================================================================
    # Upload File
    # =========================================================================
    # The files.upload() endpoint accepts CSV files and returns a file_id
    # that can be used in subsequent ingest tasks.
    #
    # Supported columns are automatically detected:
    #   - name / company_name: Company name
    #   - domain / website: Company domain
    #   - linkedin_url / linkedin: LinkedIn URL
    #   - industry: Industry category
    #   - employees / employee_count: Employee count
    #   - revenue: Revenue range
    #   - headquarters / location: HQ location
    #
    # Custom columns are preserved and can be used for filtering.

    print("\n[2/2] Uploading file...")

    # Read file content
    with open(csv_path, "rb") as f:
        file_content = f.read()

    # Upload to Linkt
    upload_response = client.files.upload(
        file=(csv_path.name, file_content, "text/csv"),
    )

    file_id = get_attr(upload_response, "file_id")
    filename = get_attr(upload_response, "filename")
    row_count = get_attr(upload_response, "row_count", len(lines) - 1)

    print(f"\n   Upload successful!")
    print(f"     File ID: {file_id}")
    print(f"     Filename: {filename}")
    print(f"     Rows: {row_count}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 60)
    print("Upload Complete")
    print("=" * 60)

    print(f"\nFile ID: {file_id}")
    print(f"Rows uploaded: {row_count}")

    print("\nNext steps:")
    print("  1. Create an ICP for the uploaded data:")
    print("     See advanced_targeting.py for ICP creation")
    print("\n  2. Enrich the uploaded data:")
    print(f"     python csv_enrichment.py {file_id}")
    print("\n  3. Or use the file_id in the Linkt dashboard")


if __name__ == "__main__":
    main()
