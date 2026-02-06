"""
Linkt SDK - Export Entities

This script demonstrates how to export entities to CSV format.

Features demonstrated:
    - CSV export with configurable fields
    - Multi-ICP export with separate files
    - Export formats and options
    - Handling large exports

Usage:
    python export_entities.py <icp_id> [options]

Examples:
    python export_entities.py abc123
    python export_entities.py abc123 --entity-type person --output contacts.csv
    python export_entities.py --icp-ids abc123 def456 --format separate

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - ICP with discovered entities
"""

import argparse
import csv
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


def get_field_display(data, field_name, default=""):
    """Extract the display value from a nested entity data field."""
    if isinstance(data, dict):
        field = data.get(field_name, {})
        if isinstance(field, dict):
            return field.get("display", default)
        return str(field) if field else default
    else:
        field = getattr(data, field_name, None)
        if field is None:
            return default
        display = getattr(field, "display", None)
        return str(display) if display else default


def get_linkedin_url(data, default=""):
    """Extract LinkedIn URL from entity data."""
    if isinstance(data, dict):
        field = data.get("linkedin", {})
        if isinstance(field, dict):
            value = field.get("value", {})
            if isinstance(value, dict):
                return value.get("url", default)
    return default


# Default fields to export for each entity type
COMPANY_FIELDS = [
    "name", "website", "industry", "employees", "revenue",
    "headquarters", "description", "linkedin"
]

PERSON_FIELDS = [
    "name", "title", "company", "email", "mobile_phone",
    "location", "linkedin"
]


def fetch_all_entities(client, icp_id, entity_type, status=None):
    """Fetch all entities from an ICP."""
    entities = []
    page = 1
    page_size = 100

    while True:
        query_params = {
            "icp_id": icp_id,
            "entity_type": entity_type,
            "page": page,
            "page_size": page_size,
        }
        if status:
            query_params["status"] = status

        response = client.entity.list(**query_params)
        batch = get_attr(response, "entities", [])

        if not batch:
            break

        entities.extend(batch)
        total = get_attr(response, "total", 0)

        if len(entities) >= total:
            break

        page += 1
        print(f"   Fetched {len(entities)}/{total} entities...")

    return entities


def entity_to_row(entity, fields, entity_type):
    """Convert an entity to a CSV row dict."""
    data = get_attr(entity, "data", {})
    row = {
        "entity_id": get_attr(entity, "id", ""),
        "status": get_attr(entity, "status", "new") or "new",
    }

    for field in fields:
        if field == "linkedin":
            row["linkedin_url"] = get_linkedin_url(data)
        else:
            row[field] = get_field_display(data, field)

    return row


def export_to_csv(entities, entity_type, output_path, fields=None):
    """Export entities to a CSV file."""
    if fields is None:
        fields = COMPANY_FIELDS if entity_type == "company" else PERSON_FIELDS

    # Build header
    header = ["entity_id", "status"] + [
        "linkedin_url" if f == "linkedin" else f for f in fields
    ]

    # Convert entities to rows
    rows = [entity_to_row(e, fields, entity_type) for e in entities]

    # Write CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def main():
    """Export entities CLI."""

    parser = argparse.ArgumentParser(description="Export Entities to CSV")
    parser.add_argument("icp_id", nargs="?", help="ICP ID to export")
    parser.add_argument("--icp-ids", nargs="+", help="Multiple ICP IDs")
    parser.add_argument("--entity-type", default="company", help="Entity type")
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", choices=["combined", "separate"], default="combined",
                        help="Multi-ICP format")

    args = parser.parse_args()

    print("=" * 60)
    print("Linkt SDK - Export Entities")
    print("=" * 60)

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
    # Determine ICP IDs
    # =========================================================================
    icp_ids = args.icp_ids or ([args.icp_id] if args.icp_id else None)

    if not icp_ids:
        print("\nError: ICP ID required")
        print("Usage: python export_entities.py <icp_id>")
        sys.exit(1)

    # =========================================================================
    # Fetch and Export Entities
    # =========================================================================
    print(f"\n[Exporting {args.entity_type} entities]")
    print("-" * 60)

    if len(icp_ids) == 1 or args.format == "combined":
        # Single file export
        all_entities = []

        for icp_id in icp_ids:
            print(f"\nFetching from ICP: {icp_id[:30]}...")
            entities = fetch_all_entities(client, icp_id, args.entity_type, args.status)
            print(f"   Found {len(entities)} entities")
            all_entities.extend(entities)

        # Determine output path
        output_path = args.output or f"export_{args.entity_type}s.csv"

        print(f"\nExporting {len(all_entities)} entities to {output_path}...")
        count = export_to_csv(all_entities, args.entity_type, output_path)
        print(f"   Exported {count} rows")

    else:
        # Separate files per ICP
        print(f"\nExporting to separate files (format=separate)")

        for icp_id in icp_ids:
            print(f"\nFetching from ICP: {icp_id[:30]}...")
            entities = fetch_all_entities(client, icp_id, args.entity_type, args.status)
            print(f"   Found {len(entities)} entities")

            if entities:
                output_path = f"export_{icp_id[:20]}_{args.entity_type}s.csv"
                count = export_to_csv(entities, args.entity_type, output_path)
                print(f"   Exported to {output_path} ({count} rows)")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 60)
    print("Export Complete")
    print("=" * 60)

    print(f"\nEntity type: {args.entity_type}")
    print(f"ICPs: {len(icp_ids)}")
    if args.status:
        print(f"Status filter: {args.status}")

    print("\nExported fields:")
    fields = COMPANY_FIELDS if args.entity_type == "company" else PERSON_FIELDS
    for field in fields:
        print(f"  - {field}")


if __name__ == "__main__":
    main()
