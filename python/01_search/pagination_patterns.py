"""
Linkt SDK - Pagination Patterns

This script demonstrates how to use pagination parameters to iterate through
large result sets efficiently.

Features demonstrated:
    - Using page and page_size parameters
    - Iterating through all pages
    - Handling total count
    - Efficient batch processing

Usage:
    python pagination_patterns.py <icp_id>

Example:
    python pagination_patterns.py abc123-...

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - ICP ID with some entities to paginate through
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


def paginate_entities(client, icp_id, entity_type, page_size=20):
    """
    Generator that yields all entities across all pages.

    Args:
        client: Linkt client instance
        icp_id: ICP ID to fetch entities from
        entity_type: "company" or "person"
        page_size: Number of entities per page (max 100)

    Yields:
        Each entity object
    """
    page = 1
    total_fetched = 0

    while True:
        response = client.entity.list(
            icp_id=icp_id,
            entity_type=entity_type,
            page=page,
            page_size=page_size,
        )

        total = get_attr(response, "total", 0)
        entities = get_attr(response, "entities", [])

        if not entities:
            break

        for entity in entities:
            yield entity
            total_fetched += 1

        # Check if we've fetched all entities
        if total_fetched >= total:
            break

        page += 1


def main():
    """Demonstrate pagination patterns."""

    print("=" * 60)
    print("Linkt SDK - Pagination Patterns")
    print("=" * 60)

    # =========================================================================
    # Parse Command Line Arguments
    # =========================================================================
    if len(sys.argv) != 2:
        print("\nUsage: python pagination_patterns.py <icp_id>")
        print("\nExample:")
        print("  python pagination_patterns.py abc123-...")
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
    print(f"\nConnected to Linkt API ({environment})")

    # =========================================================================
    # Example 1: Basic Pagination
    # =========================================================================
    # The entity.list() method supports pagination with:
    #   - page: Page number (1-indexed)
    #   - page_size: Number of results per page (default 20, max 100)
    #
    # Response includes:
    #   - total: Total count of matching entities
    #   - entities: List of entities for current page
    #   - page: Current page number
    #   - page_size: Requested page size

    print("\n[1/3] Basic pagination example...")

    # Fetch first page with small page size
    response = client.entity.list(
        icp_id=icp_id,
        entity_type="company",
        page=1,
        page_size=5,
    )

    total = get_attr(response, "total", 0)
    current_page = get_attr(response, "page", 1)
    page_size = get_attr(response, "page_size", 5)
    entities = get_attr(response, "entities", [])

    print(f"\n   Total companies: {total}")
    print(f"   Current page: {current_page}")
    print(f"   Page size: {page_size}")
    print(f"   Entities on this page: {len(entities)}")

    if entities:
        print("\n   First page results:")
        for i, entity in enumerate(entities, 1):
            data = get_attr(entity, "data", {})
            name = get_field_display(data, "name", "Unknown")
            print(f"     {i}. {name}")

    # =========================================================================
    # Example 2: Iterate Through All Pages
    # =========================================================================
    # For processing large result sets, iterate through all pages.

    print("\n[2/3] Iterating through all pages...")

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    print(f"\n   Total pages (at page_size=5): {total_pages}")

    all_companies = []
    for page_num in range(1, min(total_pages + 1, 4)):  # Limit to 3 pages for demo
        response = client.entity.list(
            icp_id=icp_id,
            entity_type="company",
            page=page_num,
            page_size=5,
        )
        entities = get_attr(response, "entities", [])
        all_companies.extend(entities)
        print(f"   Fetched page {page_num}: {len(entities)} entities")

    print(f"\n   Total fetched (first 3 pages): {len(all_companies)}")

    # =========================================================================
    # Example 3: Using the Generator Pattern
    # =========================================================================
    # For cleaner code, use a generator that handles pagination internally.

    print("\n[3/3] Generator pattern example...")

    company_count = 0
    industry_counts = {}

    # Iterate through all companies using generator
    for entity in paginate_entities(client, icp_id, "company", page_size=20):
        company_count += 1
        data = get_attr(entity, "data", {})
        industry = get_field_display(data, "industry", "Unknown")

        # Count by industry
        industry_counts[industry] = industry_counts.get(industry, 0) + 1

        # Limit for demo
        if company_count >= 50:
            print("   (Stopped at 50 for demo)")
            break

    print(f"\n   Processed {company_count} companies")
    print("\n   Companies by industry:")
    for industry, count in sorted(industry_counts.items(), key=lambda x: -x[1])[:5]:
        print(f"     {industry}: {count}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 60)
    print("Pagination Patterns Summary")
    print("=" * 60)

    print("\nKey parameters:")
    print("  - page: Page number (1-indexed)")
    print("  - page_size: Results per page (max 100)")

    print("\nResponse fields:")
    print("  - total: Total matching entities")
    print("  - entities: Current page results")
    print("  - page: Current page number")
    print("  - page_size: Requested page size")

    print("\nBest practices:")
    print("  - Use page_size=100 for batch processing")
    print("  - Use generator pattern for clean iteration")
    print("  - Check 'total' to calculate page count")


if __name__ == "__main__":
    main()
