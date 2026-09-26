# Legacy V1: deprecated SDK example. New integrations use v2/run.py.
"""
Linkt SDK - Review Search Results

This script retrieves and displays the companies and contacts discovered
by a completed search workflow.

Entities are fetched from the Entity API by ICP ID and entity type:
    - Companies: client.entity.list(icp_id=..., entity_type="company")
    - Contacts: client.entity.list(icp_id=..., entity_type="person")

Usage:
    python review_search.py <icp_id>

Example:
    python review_search.py abc123-...

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - ICP ID from first_search.py output
    - The discovery run must be COMPLETED (check with monitor_search.py)
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


def get_field_display(data, field_name, default="N/A"):
    """
    Extract the display value from a nested entity data field.

    Entity data fields are structured as:
        {"field_name": {"value": ..., "display": "Human Readable Value", ...}}

    This helper handles both dict and object return types from the SDK.
    """
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


def get_linkedin_url(data, default="N/A"):
    """
    Extract the LinkedIn URL from the linkedin field.

    The linkedin field has a nested structure:
        {"linkedin": {"value": {"platform": "linkedin", "url": "https://..."}, ...}}

    This helper extracts the actual URL from value.url.
    """
    if isinstance(data, dict):
        field = data.get("linkedin", {})
        if isinstance(field, dict):
            value = field.get("value", {})
            if isinstance(value, dict):
                return value.get("url", default)
    else:
        field = getattr(data, "linkedin", None)
        if field:
            value = getattr(field, "value", None)
            if value:
                return getattr(value, "url", default)
    return default


def main():
    """Retrieve and display search results from sheets."""

    # =========================================================================
    # Parse Command Line Arguments
    # =========================================================================
    if len(sys.argv) != 2:
        print("Usage: python review_search.py <icp_id>")
        print("\nExample:")
        print("  python review_search.py abc123-...")
        print("\nGet the ICP ID from first_search.py output.")
        sys.exit(1)

    icp_id = sys.argv[1]

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

    print("=" * 60)
    print("Linkt SDK - Search Results")
    print("=" * 60)

    # =========================================================================
    # Retrieve Discovered Companies
    # =========================================================================
    # The entity.list() method returns entities filtered by ICP ID and type.
    #
    # Response structure:
    #   - total: Total count of entities
    #   - entities: List of entity objects
    #   - page: Current page number
    #   - page_size: Number of entities per page
    #   - Each entity has:
    #       - id: Unique entity identifier
    #       - data: Object containing all enriched fields
    #       - parent_id: (contacts only) Reference to parent company
    #       - entity_type: "company" or "person"
    #       - status: "new", "reviewed", "passed", "contacted", or null
    #
    # Data field structure:
    #   Each field (e.g., "name", "website") is an object with:
    #       - value: Raw value (string, object, etc.)
    #       - display: Human-readable formatted value
    #       - references: Array of source URLs
    #       - created_at/updated_at: Timestamps

    print("\n--- Companies ---\n")

    companies_response = client.entity.list(icp_id=icp_id, entity_type="company")
    total_companies = get_attr(companies_response, "total", 0)
    companies = get_attr(companies_response, "entities", [])

    print(f"Found {total_companies} companies:\n")

    for i, entity in enumerate(companies, 1):
        data = get_attr(entity, "data", {})

        # Extract common company fields
        name = get_field_display(data, "name", "Unknown")
        website = get_field_display(data, "website")
        linkedin = get_linkedin_url(data)
        industry = get_field_display(data, "industry")
        employees = get_field_display(data, "employees")
        revenue = get_field_display(data, "revenue")
        headquarters = get_field_display(data, "headquarters")

        print(f"{i}. {name}")
        print(f"   Website:      {website}")
        print(f"   LinkedIn:     {linkedin}")
        print(f"   Industry:     {industry}")
        print(f"   Employees:    {employees}")
        print(f"   Revenue:      {revenue}")
        print(f"   Headquarters: {headquarters}")
        print()

    # =========================================================================
    # Retrieve Discovered Contacts
    # =========================================================================
    # Contact entities include a parent_id field linking them to their company.
    # The data object contains person-specific fields like title, email, etc.
    # Filter by entity_type="person" to get only contacts.

    print("\n--- Contacts ---\n")

    contacts_response = client.entity.list(icp_id=icp_id, entity_type="person")
    total_contacts = get_attr(contacts_response, "total", 0)
    contacts = get_attr(contacts_response, "entities", [])

    print(f"Found {total_contacts} contacts:\n")

    for i, entity in enumerate(contacts, 1):
        data = get_attr(entity, "data", {})

        # Extract common person fields
        name = get_field_display(data, "name", "Unknown")
        title = get_field_display(data, "title")
        company = get_field_display(data, "company")
        email = get_field_display(data, "email")
        mobile_phone = get_field_display(data, "mobile_phone")
        location = get_field_display(data, "location")
        linkedin = get_linkedin_url(data)

        print(f"{i}. {name}")
        print(f"   Title:    {title}")
        print(f"   Company:  {company}")
        print(f"   Email:    {email}")
        print(f"   Phone:    {mobile_phone}")
        print(f"   Location: {location}")
        print(f"   LinkedIn: {linkedin}")
        print()

    # =========================================================================
    # Entity Status
    # =========================================================================
    # Each entity has a status field for tracking workflow progress:
    #   - new: Newly discovered, not yet reviewed
    #   - reviewed: Reviewed and qualified
    #   - passed: Not a fit, disqualified
    #   - contacted: Outreach initiated
    #
    # To update entity status:
    #   client.entity.update(entity_id, status="reviewed")
    #
    # To bulk update status:
    #   client.entity.bulk_update_status(entity_ids=[...], status="reviewed")

    print("\n--- Status Summary ---\n")

    # Count companies by status
    status_counts = {}
    for company in companies:
        status = get_attr(company, "status", "new") or "new"
        status_counts[status] = status_counts.get(status, 0) + 1

    print("Companies by status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"\nTotal companies discovered: {total_companies}")
    print(f"Total contacts discovered:  {total_contacts}")
    print("\nView in dashboard:")
    print(f"  https://app.linkt.ai/icp/{icp_id}")

    print("\nNext steps:")
    print("  1. Update entity status:")
    print(f"     python ../04_advanced/entity_status_workflow.py {icp_id}")
    print("\n  2. Set up signal monitoring:")
    print(f"     python ../03_signals/signals_from_sheet.py {icp_id}")


if __name__ == "__main__":
    main()
