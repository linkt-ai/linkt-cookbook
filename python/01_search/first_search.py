# Legacy V1: deprecated SDK example. New integrations use v2/run.py.
"""
Linkt SDK - Launch Search Workflow

This script creates all necessary resources and launches a search task.
It returns immediately with the IDs needed for monitoring and retrieval.

Workflow:
    1. Create an Ideal Customer Profile (ICP) with company and person criteria
    2. Create Sheets to store discovered companies and contacts
    3. Create a Search Task
    4. Execute the Task (async - returns immediately)
    5. Output IDs for use with monitor_search.py and review_search.py

Usage:
    python first_search.py

Output:
    Prints run_id, company_sheet_id, and person_sheet_id which you'll need
    for the monitoring and review scripts.

Next Steps:
    1. Run: python monitor_search.py <run_id>
    2. Once complete, run: python review_search.py <icp_id>

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

# =============================================================================
# Configuration
# =============================================================================
NUM_COMPANIES_TO_FIND = 25  # Number of companies to discover (default: 25)
CONTACTS_PER_COMPANY = 1  # Number of contacts to find per company

# =============================================================================
# Company Targeting Criteria
# =============================================================================
# Criteria should be specific and measurable. Avoid vague terms.
# Use markdown format with clear bullet points.

COMPANY_CRITERIA = """
## Criteria

Find B2B SaaS companies that meet ALL of the following requirements:

- **Location**: Headquarters in the United States
- **Company Size**: Between 50 and 500 employees
- **Business Model**: Sells software-as-a-service to businesses (not consumers)
- **Funding Stage**: Has raised at least one round of venture capital funding
- **Industry Focus**: Provides solutions for business operations, sales, marketing, HR, or cybersecurity
"""

# =============================================================================
# Person (Contact) Targeting Criteria
# =============================================================================
# Person criteria define WHO you want to find at each discovered company.

PERSON_CRITERIA = """
## Criteria

Find contacts at the target companies who meet ALL of the following requirements:

- **Role**: VP of Sales, Head of Sales, CRO, or similar revenue leadership title
- **Seniority**: Director level or above
- **Department**: Sales, Revenue, or Business Development
"""


def main():
    """Launch the search workflow and output IDs for monitoring."""

    print("=" * 60)
    print("Linkt SDK - Launch Search Workflow")
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
    # Step 1: Create Ideal Customer Profile (ICP)
    # =========================================================================
    # The ICP defines WHO you want to find. Search workflows need entity
    # targets for BOTH companies and persons (contacts).
    #
    # Entity target fields:
    #   - entity_type: "company" or "person"
    #   - description: Markdown criteria (specific, measurable requirements)
    #   - desired_count: (person only) How many contacts per company

    print("\n[1/4] Creating Ideal Customer Profile...")

    icp = client.icp.create(
        name="Example: B2B SaaS Companies + Sales Leaders",
        description="Mid-market B2B SaaS companies with sales leadership contacts",
        entity_targets=[
            {
                "entity_type": "company",
                "description": COMPANY_CRITERIA,
            },
            {
                "entity_type": "person",
                "description": PERSON_CRITERIA,
                "desired_count": CONTACTS_PER_COMPANY,
            },
        ],
    )

    print(f"   Created ICP: {icp.name}")
    print(f"     ID: {icp.id}")

    # =========================================================================
    # Step 2: Create Sheets
    # =========================================================================
    # Sheets store discovered entities. Search workflows need TWO sheets:
    #   - Company sheet: Stores discovered organizations
    #   - Person sheet: Stores discovered contacts (linked via parent_id)
    #
    # Both sheets reference the same ICP via icp_id.

    print("\n[2/4] Creating Sheets to store results...")

    company_sheet = client.sheet.create(
        name="Discovered Companies",
        description="Companies found via discovery workflow",
        icp_id=icp.id,
        entity_type="company",
    )

    print(f"   Created Company Sheet: {company_sheet.name}")
    print(f"     ID: {company_sheet.id}")

    person_sheet = client.sheet.create(
        name="Discovered Contacts",
        description="Contacts found via discovery workflow",
        icp_id=icp.id,
        entity_type="person",
    )

    print(f"   Created Person Sheet: {person_sheet.name}")
    print(f"     ID: {person_sheet.id}")

    # =========================================================================
    # Step 3: Create Search Task
    # =========================================================================
    # Tasks are reusable workflow templates.
    #
    # Required fields:
    #   - flow_name: "search" for discovery tasks
    #   - deployment_name: "main" (required, cannot be changed)
    #   - icp_id: Which ICP to use for targeting
    #
    # task_config fields:
    #   - type: "search" (discriminator for search workflows)
    #   - desired_contact_count: Contacts per company
    #   - user_feedback: Optional guidance to refine results

    print("\n[3/4] Creating Search Task...")

    task = client.task.create(
        name="Discovery Search Task",
        description="Search for B2B SaaS companies and sales leaders",
        flow_name="search",
        deployment_name="main",
        icp_id=icp.id,
        task_config={
            "type": "search",
            "desired_contact_count": CONTACTS_PER_COMPANY,
            "user_feedback": "",
        },
    )

    print(f"   Created Task: {task.name}")
    print(f"     ID: {task.id}")

    # =========================================================================
    # Step 4: Execute Task
    # =========================================================================
    # Executing creates a "run" - an async execution instance.
    # The run progresses through states: PENDING -> RUNNING -> COMPLETED
    #
    # Parameters:
    #   - icp_id: Required for search tasks (attaches ICP context)
    #   - parameters.num_results: Number of root entities (companies) to find
    #                             Defaults to 25 if not specified
    #
    # This call returns immediately - the search runs asynchronously.

    print("\n[4/4] Executing Task...")

    execution = client.task.execute(
        task.id,
        icp_id=icp.id,
        parameters={"num_results": NUM_COMPANIES_TO_FIND},
    )

    print("   Task execution started")
    print(f"     Run ID: {execution.run_id}")

    # =========================================================================
    # Output IDs for Next Steps
    # =========================================================================
    # Save these IDs - you'll need them for monitoring and reviewing results.
    # The search runs asynchronously and typically takes 15-20 minutes.

    print("\n" + "=" * 60)
    print("Search Launched Successfully!")
    print("=" * 60)

    print("\nSave these IDs for the next steps:\n")
    print(f"  RUN_ID={execution.run_id}")
    print(f"  ICP_ID={icp.id}")

    print("\nNext steps:")
    print("  1. Monitor progress:")
    print(f"     python monitor_search.py {execution.run_id}")
    print("\n  2. Once complete, review results:")
    print(f"     python review_search.py {icp.id}")

    print("\nNote: Search operations typically take 15-20 minutes to complete.")


if __name__ == "__main__":
    main()
