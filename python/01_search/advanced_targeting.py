# Legacy V1: deprecated SDK example. New integrations use v2/run.py.
"""
Linkt SDK - Advanced Targeting with ICP

This script demonstrates how to create an ICP with specific targeting criteria
and use the desired_contact_count parameter for contact enrichment.

Features demonstrated:
    - Creating ICP with detailed criteria
    - Using desired_contact_count parameter
    - Multi-entity search (company + person)
    - Viewing targeting results

Usage:
    python advanced_targeting.py

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
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


def main():
    """Create an ICP with advanced targeting criteria."""

    print("=" * 60)
    print("Linkt SDK - Advanced Targeting")
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
    # Step 1: Create ICP with Detailed Criteria
    # =========================================================================
    # ICPs (Ideal Customer Profiles) define the target companies and contacts.
    #
    # Key parameters:
    #   - name: Human-readable name for the ICP
    #   - description: Detailed targeting criteria (used by AI agents)
    #   - entity_targets: List of entity types to find, each with:
    #       - entity_type: "company" or "person"
    #       - description: Criteria for this entity type
    #       - root: True for the primary entity type (e.g. company)
    #       - desired_count: (person only) Contacts per company
    #
    # The description is crucial - it guides the AI agent's search behavior.
    # Be specific about:
    #   - Industry/vertical
    #   - Company size (employees, revenue)
    #   - Geographic location
    #   - Technology stack or signals
    #   - Exclusion criteria

    print("\n[1/4] Creating ICP with targeting criteria...")

    icp_description = """
    Target companies:
    - Industry: Enterprise SaaS, specifically sales/marketing automation
    - Size: 100-1000 employees (growth stage)
    - Location: United States, preferably SF Bay Area or NYC
    - Signals: Companies showing AI adoption (hiring AI roles, AI product announcements)

    Exclude:
    - Companies already using competitor products
    - Companies with less than $10M ARR
    - Companies in regulated industries (healthcare, finance)

    Contact preferences:
    - Titles: VP Sales, Head of Sales, Sales Director, RevOps
    - Seniority: Director level and above
    - Must have LinkedIn profile
    """

    icp = client.icp.create(
        name="AI-Ready SaaS Companies",
        description=icp_description.strip(),
        entity_targets=[
            {
                "entity_type": "company",
                "description": icp_description.strip(),
                "root": True,
            },
            {
                "entity_type": "person",
                "description": "VP Sales, Head of Sales, Sales Director, RevOps — Director level and above",
                "desired_count": 3,
            },
        ],
    )

    icp_id = get_attr(icp, "id")
    icp_name = get_attr(icp, "name")

    print(f"   Created ICP: {icp_name}")
    print(f"     ID: {icp_id}")
    print(f"     Entity targets: company (root) + person (3 per company)")

    # =========================================================================
    # Step 2: Create and Execute Discovery Task
    # =========================================================================
    # To actually find companies, we need to create and execute a discovery task.
    # The task uses the ICP's criteria to search and enrich entities.

    print("\n[2/4] Creating discovery task...")

    task = client.task.create(
        name="Find AI-Ready SaaS Companies",
        description="Discovery task for AI-ready SaaS companies in the US",
        flow_name="search",
        deployment_name="main",
        icp_id=icp_id,
        task_config={
            "type": "search",
            "icp_id": icp_id,
        },
    )

    task_id = get_attr(task, "id")
    print(f"   Created Task ID: {task_id}")

    print("\n[3/4] Starting discovery run...")

    execution = client.task.execute(task_id, icp_id=icp_id)
    run_id = get_attr(execution, "run_id")

    print(f"   Run ID: {run_id}")
    print("   Discovery is running asynchronously...")

    # =========================================================================
    # Step 3: Check Initial Results
    # =========================================================================
    # The discovery runs asynchronously. For this example, we'll just show
    # how to query results. In production, you'd poll or use webhooks.

    print("\n[4/4] Checking for existing entities...")

    # Check for companies
    companies_response = client.entity.list(
        icp_id=icp_id,
        entity_type="company",
        page_size=5,
    )
    total_companies = get_attr(companies_response, "total", 0)
    companies = get_attr(companies_response, "entities", [])

    print(f"\n   Companies found: {total_companies}")
    for entity in companies[:5]:
        data = get_attr(entity, "data", {})
        name = get_field_display(data, "name", "Unknown")
        industry = get_field_display(data, "industry", "N/A")
        print(f"     - {name} ({industry})")

    # Check for contacts
    contacts_response = client.entity.list(
        icp_id=icp_id,
        entity_type="person",
        page_size=5,
    )
    total_contacts = get_attr(contacts_response, "total", 0)

    print(f"\n   Contacts found: {total_contacts}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 60)
    print("Advanced Targeting Summary")
    print("=" * 60)

    print(f"\nICP Created: {icp_name}")
    print(f"  ID: {icp_id}")
    print(f"  Entity targets: company (root) + person (3 per company)")

    print(f"\nDiscovery Run: {run_id}")
    print(f"  Status: Running (async)")

    print("\nNext steps:")
    print(f"  1. Monitor run progress:")
    print(f"     python monitor_search.py {run_id}")
    print(f"\n  2. Review results when complete:")
    print(f"     python review_search.py {icp_id}")
    print(f"\n  3. View in dashboard:")
    print(f"     https://app.linkt.ai/icp/{icp_id}")


if __name__ == "__main__":
    main()
