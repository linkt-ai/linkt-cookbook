# Legacy V1: deprecated SDK example. New integrations use v2/run.py.
"""
Linkt SDK - Bulk Operations

This script demonstrates bulk operations for managing large numbers of entities.

Features demonstrated:
    - Bulk status update endpoint
    - Processing entities in batches
    - Progress tracking for large operations
    - Error handling for bulk operations

Usage:
    python bulk_operations.py <icp_id> --action <action> [options]

Actions:
    status      Bulk update entity status
    count       Count entities by status

Examples:
    python bulk_operations.py abc123 --action count
    python bulk_operations.py abc123 --action status --from new --to reviewed
    python bulk_operations.py abc123 --action status --entity-ids id1 id2 id3 --to contacted

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - ICP with entities
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


VALID_STATUSES = ["new", "reviewed", "passed", "contacted"]


def count_entities(client, icp_id, entity_type):
    """Count entities by status."""
    print("\n[Entity Counts by Status]")
    print("-" * 60)

    counts = {}
    total = 0

    for status in VALID_STATUSES:
        response = client.entity.list(
            icp_id=icp_id,
            entity_type=entity_type,
            status=status,
            page_size=1,
        )
        count = get_attr(response, "total", 0)
        counts[status] = count
        total += count

    print(f"\nICP: {icp_id}")
    print(f"Entity type: {entity_type}\n")

    for status, count in counts.items():
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {status:12} {count:6} ({pct:5.1f}%)")

    print(f"  {'Total':12} {total:6}")

    return counts


def get_entity_ids_by_status(client, icp_id, entity_type, status, limit=None):
    """Get all entity IDs with a specific status."""
    entity_ids = []
    page = 1
    page_size = 100

    while True:
        response = client.entity.list(
            icp_id=icp_id,
            entity_type=entity_type,
            status=status,
            page=page,
            page_size=page_size,
        )

        entities = get_attr(response, "entities", [])
        if not entities:
            break

        for entity in entities:
            entity_ids.append(get_attr(entity, "id"))
            if limit and len(entity_ids) >= limit:
                return entity_ids

        total = get_attr(response, "total", 0)
        if len(entity_ids) >= total:
            break

        page += 1

    return entity_ids


def bulk_update_status(client, entity_ids, new_status, batch_size=100):
    """
    Bulk update entity status.

    Uses the bulk_update_status endpoint for efficient updates.
    """
    print(f"\n[Bulk Status Update]")
    print("-" * 60)

    if not entity_ids:
        print("\nNo entities to update.")
        return {"updated": 0, "failed": 0}

    print(f"\nEntities to update: {len(entity_ids)}")
    print(f"New status: {new_status}")
    print(f"Batch size: {batch_size}")

    # Confirm for large operations
    if len(entity_ids) > 50:
        print(f"\nWarning: This will update {len(entity_ids)} entities.")
        response = input("Continue? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            print("Operation cancelled.")
            return {"updated": 0, "failed": 0, "cancelled": True}

    # Process in batches
    total_updated = 0
    total_failed = 0
    batches = [entity_ids[i:i + batch_size] for i in range(0, len(entity_ids), batch_size)]

    print(f"\nProcessing {len(batches)} batch(es)...")

    for batch_num, batch in enumerate(batches, 1):
        print(f"\n  Batch {batch_num}/{len(batches)} ({len(batch)} entities)...")

        try:
            # Use the bulk update endpoint
            result = client.entity.bulk_update_status(
                entity_ids=batch,
                status=new_status,
            )

            updated = get_attr(result, "updated", len(batch))
            failed = get_attr(result, "failed", 0)

            total_updated += updated
            total_failed += failed

            print(f"    Updated: {updated}, Failed: {failed}")

        except Exception as e:
            print(f"    Error: {e}")
            total_failed += len(batch)

    print(f"\nBulk update complete!")
    print(f"  Total updated: {total_updated}")
    print(f"  Total failed: {total_failed}")

    return {"updated": total_updated, "failed": total_failed}


def main():
    """Bulk operations CLI."""

    parser = argparse.ArgumentParser(description="Bulk Operations")
    parser.add_argument("icp_id", help="ICP ID")
    parser.add_argument("--action", required=True, choices=["count", "status"])
    parser.add_argument("--entity-type", default="company", help="Entity type")
    parser.add_argument("--from", dest="from_status", help="Source status filter")
    parser.add_argument("--to", dest="to_status", help="Target status")
    parser.add_argument("--entity-ids", nargs="+", help="Specific entity IDs")
    parser.add_argument("--limit", type=int, help="Max entities to update")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")

    args = parser.parse_args()

    print("=" * 60)
    print("Linkt SDK - Bulk Operations")
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
    # Execute Action
    # =========================================================================
    if args.action == "count":
        count_entities(client, args.icp_id, args.entity_type)

    elif args.action == "status":
        if not args.to_status:
            print("Error: --to (target status) is required for status action")
            sys.exit(1)

        if args.to_status not in VALID_STATUSES:
            print(f"Error: Invalid status '{args.to_status}'")
            print(f"Valid values: {', '.join(VALID_STATUSES)}")
            sys.exit(1)

        # Get entity IDs to update
        if args.entity_ids:
            entity_ids = args.entity_ids
            print(f"\nUsing {len(entity_ids)} specified entity IDs")
        elif args.from_status:
            if args.from_status not in VALID_STATUSES:
                print(f"Error: Invalid source status '{args.from_status}'")
                sys.exit(1)
            print(f"\nFinding entities with status: {args.from_status}")
            entity_ids = get_entity_ids_by_status(
                client,
                args.icp_id,
                args.entity_type,
                args.from_status,
                args.limit,
            )
            print(f"Found {len(entity_ids)} entities")
        else:
            print("Error: Either --from (source status) or --entity-ids required")
            sys.exit(1)

        # Execute bulk update
        bulk_update_status(client, entity_ids, args.to_status)


if __name__ == "__main__":
    main()
