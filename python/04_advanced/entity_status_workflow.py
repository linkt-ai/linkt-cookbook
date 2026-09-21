"""
Linkt SDK - Entity Status Workflow

This script demonstrates how to manage entity status for sales workflow tracking.

Features demonstrated:
    - Entity status values (new, reviewed, passed, contacted)
    - Updating individual entity status
    - Status-based filtering
    - Workflow progression tracking

Status workflow:
    new -> reviewed -> contacted
           \\-> passed

Usage:
    python entity_status_workflow.py <icp_id> [--status STATUS]

Examples:
    python entity_status_workflow.py abc123
    python entity_status_workflow.py abc123 --status new
    python entity_status_workflow.py abc123 --update entity_xyz789 --set-status reviewed

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - ICP with discovered entities
"""

import argparse
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


# Valid status values
VALID_STATUSES = ["new", "reviewed", "passed", "contacted"]


def main():
    """Entity status workflow management."""

    parser = argparse.ArgumentParser(description="Entity Status Workflow")
    parser.add_argument("icp_id", help="ICP ID")
    parser.add_argument("--status", help="Filter by status (new/reviewed/passed/contacted)")
    parser.add_argument("--update", metavar="ENTITY_ID", help="Entity ID to update")
    parser.add_argument("--set-status", dest="new_status", help="New status value")
    parser.add_argument("--entity-type", default="company", help="Entity type (company/person)")

    args = parser.parse_args()

    print("=" * 60)
    print("Linkt SDK - Entity Status Workflow")
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
    # Handle Status Update
    # =========================================================================
    if args.update and args.new_status:
        print("\n[Updating Entity Status]")
        print("-" * 60)

        if args.new_status not in VALID_STATUSES:
            print(f"Error: Invalid status '{args.new_status}'")
            print(f"Valid values: {', '.join(VALID_STATUSES)}")
            sys.exit(1)

        # Get current entity
        entity = client.entity.retrieve(args.update)
        data = get_attr(entity, "data", {})
        name = get_field_display(data, "name", "Unknown")
        current_status = get_attr(entity, "status", "new")

        print(f"\nEntity: {name}")
        print(f"Current status: {current_status}")
        print(f"New status: {args.new_status}")

        # Update status
        updated = client.entity.update(args.update, status=args.new_status)
        new_status = get_attr(updated, "status", args.new_status)

        print(f"\nStatus updated: {current_status} -> {new_status}")
        return

    # =========================================================================
    # Show Status Workflow
    # =========================================================================
    print("\n[Status Workflow]")
    print("-" * 60)
    print("\n   new --> reviewed --> contacted")
    print("             \\")
    print("              --> passed")
    print("\n   Status meanings:")
    print("     new:       Newly discovered, not yet reviewed")
    print("     reviewed:  Reviewed and qualified")
    print("     passed:    Not a fit, passing on this lead")
    print("     contacted: Outreach initiated")

    # =========================================================================
    # List Entities by Status
    # =========================================================================
    print("\n[Entity Status Summary]")
    print("-" * 60)

    # Count entities by status
    status_counts = {}
    for status in VALID_STATUSES:
        response = client.entity.list(
            icp_id=args.icp_id,
            entity_type=args.entity_type,
            status=status,
            page_size=1,  # Just need the count
        )
        count = get_attr(response, "total", 0)
        status_counts[status] = count

    print(f"\nICP: {args.icp_id}")
    print(f"Entity type: {args.entity_type}")
    print("\nStatus breakdown:")
    total = sum(status_counts.values())
    for status, count in status_counts.items():
        pct = (count / total * 100) if total > 0 else 0
        bar = "#" * int(pct / 5)  # Simple bar chart
        print(f"  {status:10} {count:4} ({pct:5.1f}%) {bar}")
    print(f"  {'Total':10} {total:4}")

    # =========================================================================
    # List Entities (Filtered)
    # =========================================================================
    print("\n[Entities]")
    print("-" * 60)

    query_params = {
        "icp_id": args.icp_id,
        "entity_type": args.entity_type,
        "page_size": 20,
    }

    if args.status:
        if args.status not in VALID_STATUSES:
            print(f"Warning: Invalid status filter '{args.status}', showing all")
        else:
            query_params["status"] = args.status
            print(f"\nFiltering by status: {args.status}")

    response = client.entity.list(**query_params)
    entities = get_attr(response, "entities", [])
    total = get_attr(response, "total", 0)

    print(f"\nShowing {len(entities)} of {total} entities:\n")

    for i, entity in enumerate(entities, 1):
        entity_id = get_attr(entity, "id", "")
        status = get_attr(entity, "status", "new") or "new"
        data = get_attr(entity, "data", {})
        name = get_field_display(data, "name", "Unknown")
        industry = get_field_display(data, "industry", "")

        # Status indicator
        status_icon = {
            "new": "[ ]",
            "reviewed": "[*]",
            "passed": "[x]",
            "contacted": "[>]",
        }.get(status, "[?]")

        print(f"{i:2}. {status_icon} {name}")
        if industry:
            print(f"       {industry}")
        print(f"       ID: {entity_id[:30]}... | Status: {status}")
        print()

    # =========================================================================
    # Usage Examples
    # =========================================================================
    if entities:
        print("\n" + "=" * 60)
        print("Usage Examples")
        print("=" * 60)

        first_entity_id = get_attr(entities[0], "id", "entity_id")
        first_name = get_field_display(get_attr(entities[0], "data", {}), "name", "Entity")

        print(f"\nTo update '{first_name}' to 'reviewed':")
        print(f"  python entity_status_workflow.py {args.icp_id} \\")
        print(f"    --update {first_entity_id} \\")
        print(f"    --set-status reviewed")

        print(f"\nTo view only 'new' entities:")
        print(f"  python entity_status_workflow.py {args.icp_id} --status new")

        print(f"\nTo bulk update, see:")
        print(f"  python bulk_operations.py")


if __name__ == "__main__":
    main()
