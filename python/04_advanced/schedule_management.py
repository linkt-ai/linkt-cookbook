"""
Linkt SDK - Schedule Management

This script demonstrates how to manage recurring schedules for task execution.

Features demonstrated:
    - Creating schedules with cron expressions
    - Listing and viewing schedules
    - Updating schedule frequency and status
    - Deleting schedules

Schedules automate task execution at regular intervals:
    - Daily: Run every day at a specified time
    - Weekly: Run every week on a specified day
    - Monthly: Run on a specified day of each month
    - Custom: Any valid cron expression

Usage:
    python schedule_management.py <action> [options]

Actions:
    list                    List all schedules
    create <task_id>        Create a schedule for a task
    get <schedule_id>       Get schedule details
    update <schedule_id>    Update a schedule
    delete <schedule_id>    Delete a schedule

Examples:
    python schedule_management.py list
    python schedule_management.py create task_abc123 --icp-id icp_xyz --frequency daily
    python schedule_management.py create task_abc123 --icp-id icp_xyz --cron "0 9 * * 1"
    python schedule_management.py update sched_xyz789 --frequency weekly
    python schedule_management.py update sched_xyz789 --status paused
    python schedule_management.py delete sched_xyz789

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - At least one task created (signal monitoring task recommended)
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


# Predefined cron expressions for common frequencies
FREQUENCY_CRONS = {
    "daily": "0 9 * * *",  # Daily at 9 AM
    "weekly": "0 9 * * 1",  # Weekly on Monday at 9 AM
    "monthly": "0 9 1 * *",  # Monthly on the 1st at 9 AM
}

# Reverse lookup: cron expression -> friendly label
CRON_LABELS = {v: k for k, v in FREQUENCY_CRONS.items()}


def cron_to_label(cron_expression):
    """Convert a cron expression to a human-friendly label."""
    return CRON_LABELS.get(cron_expression, "custom")


def list_schedules(client):
    """List all schedules."""
    print("\n[Listing Schedules]")
    print("-" * 60)

    response = client.schedule.list()
    schedules = get_attr(response, "schedules", [])
    total = get_attr(response, "total", len(schedules))

    if not schedules:
        print("\nNo schedules found.")
        print("\nTo create a schedule:")
        print("  python schedule_management.py create <task_id> --icp-id <icp_id> --frequency daily")
        return

    print(f"\nFound {total} schedule(s):\n")

    for i, schedule in enumerate(schedules, 1):
        schedule_id = get_attr(schedule, "id", "N/A")
        name = get_attr(schedule, "name", "N/A")
        task_id = get_attr(schedule, "task_id", "N/A")
        cron = get_attr(schedule, "cron_expression", "N/A")
        status = get_attr(schedule, "status", "N/A")
        icp_id = get_attr(schedule, "icp_id", "N/A")

        frequency_label = cron_to_label(cron)

        print(f"{i}. {name}")
        print(f"   Schedule ID: {schedule_id}")
        print(f"   Task: {task_id}")
        print(f"   Frequency: {frequency_label} ({cron})")
        print(f"   Status: {status}")
        print(f"   ICP: {icp_id}")
        print()


def create_schedule(client, task_id, icp_id, name=None, frequency="daily", cron_expression=None):
    """Create a new schedule for a task."""
    print("\n[Creating Schedule]")
    print("-" * 60)

    # Use predefined cron or custom
    if cron_expression:
        cron = cron_expression
    else:
        cron = FREQUENCY_CRONS.get(frequency, FREQUENCY_CRONS["daily"])

    if not name:
        name = f"Schedule: {frequency} ({task_id[:20]})"

    print(f"\nTask ID: {task_id}")
    print(f"ICP ID: {icp_id}")
    print(f"Name: {name}")
    print(f"Frequency: {frequency}")
    print(f"Cron expression: {cron}")

    schedule = client.schedule.create(
        task_id=task_id,
        cron_expression=cron,
        icp_id=icp_id,
        name=name,
    )

    schedule_id = get_attr(schedule, "id")
    status = get_attr(schedule, "status", "N/A")

    print(f"\nSchedule created successfully!")
    print(f"  Schedule ID: {schedule_id}")
    print(f"  Status: {status}")

    return schedule


def get_schedule(client, schedule_id):
    """Get details for a specific schedule."""
    print("\n[Schedule Details]")
    print("-" * 60)

    schedule = client.schedule.retrieve(schedule_id)

    sched_id = get_attr(schedule, "id", "N/A")
    name = get_attr(schedule, "name", "N/A")
    task_id = get_attr(schedule, "task_id", "N/A")
    icp_id = get_attr(schedule, "icp_id", "N/A")
    cron = get_attr(schedule, "cron_expression", "N/A")
    status = get_attr(schedule, "status", "N/A")
    description = get_attr(schedule, "description", "N/A")
    created_at = get_attr(schedule, "created_at", "N/A")
    updated_at = get_attr(schedule, "updated_at", "N/A")

    frequency_label = cron_to_label(cron)

    print(f"\nSchedule ID: {sched_id}")
    print(f"Name: {name}")
    print(f"Task ID: {task_id}")
    print(f"ICP ID: {icp_id}")
    print(f"Frequency: {frequency_label} ({cron})")
    print(f"Status: {status}")
    if description and description != "N/A":
        print(f"Description: {description}")
    print(f"Created: {created_at}")
    print(f"Updated: {updated_at}")


def update_schedule(client, schedule_id, frequency=None, status=None, cron_expression=None, name=None):
    """Update an existing schedule."""
    print("\n[Updating Schedule]")
    print("-" * 60)

    update_params = {}

    if frequency and not cron_expression:
        update_params["cron_expression"] = FREQUENCY_CRONS.get(frequency)

    if cron_expression:
        update_params["cron_expression"] = cron_expression

    if status:
        update_params["status"] = status

    if name:
        update_params["name"] = name

    if not update_params:
        print("\nNo updates specified.")
        return

    print(f"\nSchedule ID: {schedule_id}")
    print(f"Updates: {update_params}")

    schedule = client.schedule.update(schedule_id, **update_params)

    print("\nSchedule updated successfully!")
    print(f"  Name: {get_attr(schedule, 'name')}")
    print(f"  Cron: {get_attr(schedule, 'cron_expression')}")
    print(f"  Status: {get_attr(schedule, 'status')}")


def delete_schedule(client, schedule_id, confirm=False):
    """Delete a schedule."""
    print("\n[Deleting Schedule]")
    print("-" * 60)

    if not confirm:
        print(f"\nSchedule ID: {schedule_id}")
        print("\nThis action cannot be undone.")
        response = input("Confirm deletion? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            print("Deletion cancelled.")
            return

    client.schedule.delete(schedule_id)
    print(f"\nSchedule {schedule_id} deleted successfully!")


def main():
    """Schedule management CLI."""

    parser = argparse.ArgumentParser(description="Linkt Schedule Management")
    parser.add_argument("action", choices=["list", "create", "get", "update", "delete"])
    parser.add_argument("id", nargs="?", help="Task ID (for create) or Schedule ID (for get/update/delete)")
    parser.add_argument("--icp-id", help="ICP ID (required for create)")
    parser.add_argument("--name", help="Schedule name")
    parser.add_argument("--frequency", choices=["daily", "weekly", "monthly"])
    parser.add_argument("--cron", help="Custom cron expression")
    parser.add_argument("--status", choices=["active", "paused", "disabled"], help="Schedule status")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")

    args = parser.parse_args()

    print("=" * 60)
    print("Linkt SDK - Schedule Management")
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
    if args.action == "list":
        list_schedules(client)

    elif args.action == "create":
        if not args.id:
            print("Error: Task ID required for create action")
            print("Usage: python schedule_management.py create <task_id> --icp-id <icp_id> --frequency daily")
            sys.exit(1)
        if not args.icp_id:
            print("Error: --icp-id required for create action")
            print("Usage: python schedule_management.py create <task_id> --icp-id <icp_id> --frequency daily")
            sys.exit(1)
        frequency = args.frequency or "daily"
        create_schedule(client, args.id, args.icp_id, args.name, frequency, args.cron)

    elif args.action == "get":
        if not args.id:
            print("Error: Schedule ID required for get action")
            sys.exit(1)
        get_schedule(client, args.id)

    elif args.action == "update":
        if not args.id:
            print("Error: Schedule ID required for update action")
            sys.exit(1)
        update_schedule(client, args.id, args.frequency, args.status, args.cron, args.name)

    elif args.action == "delete":
        if not args.id:
            print("Error: Schedule ID required for delete action")
            sys.exit(1)
        delete_schedule(client, args.id, args.yes)


if __name__ == "__main__":
    main()
