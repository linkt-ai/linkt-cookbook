"""
Linkt SDK - Signals from Sheet

Monitor signals on entities already discovered in a sheet (ICP).

This script creates a signal-sheet task to monitor companies from an existing
ICP, executes the first run, and sets up a recurring schedule.

Usage:
    python signals_from_sheet.py <source_icp_id> [--webhook URL] [--frequency weekly]

Examples:
    python signals_from_sheet.py abc123-...
    python signals_from_sheet.py abc123-... --frequency daily
    python signals_from_sheet.py abc123-... --webhook https://example.com/hook

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - ICP ID from a completed search workflow
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


# Signal types to monitor
SIGNAL_TYPES = [
    {
        "type": "other",
        "display": "AI Initiatives",
        "description": "News about AI initiatives, artificial intelligence projects, machine learning implementations, AI partnerships, and AI-powered product launches",
    },
    {
        "type": "funding",
        "display": "Funding Rounds",
        "description": "Venture capital funding, Series A/B/C rounds, IPO filings, and investment announcements",
    },
    {
        "type": "leadership_change",
        "display": "Leadership Changes",
        "description": "New CEO, CTO, VP appointments, executive departures, and leadership restructuring",
    },
    {
        "type": "hiring_surge",
        "display": "Hiring Surge",
        "description": "Rapid hiring activity, large-scale recruitment drives, and significant team expansion",
    },
    {
        "type": "product_launch",
        "display": "Product Launches",
        "description": "New product announcements, feature releases, and major product updates",
    },
]

# Cron expressions for each frequency
FREQUENCY_CRONS = {
    "daily": "0 9 * * *",
    "weekly": "0 9 * * 1",
    "monthly": "0 9 1 * *",
}


def main():
    """Set up signal monitoring from an existing sheet."""

    parser = argparse.ArgumentParser(
        description="Monitor signals on entities in an existing ICP sheet"
    )
    parser.add_argument("source_icp_id", help="ICP ID containing entities to monitor")
    parser.add_argument("--webhook", dest="webhook_url", help="Webhook URL for notifications")
    parser.add_argument(
        "--frequency",
        choices=["daily", "weekly", "monthly"],
        default="weekly",
        help="Monitoring frequency (default: weekly)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Linkt SDK - Signals from Sheet")
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
    # [1/4] Verify Source ICP
    # =========================================================================
    print("\n[1/4] Verifying source ICP...")

    try:
        companies_response = client.entity.list(
            icp_id=args.source_icp_id, entity_type="company"
        )
        total_companies = get_attr(companies_response, "total", 0)
    except Exception as e:
        print(f"\nError: Could not access ICP: {args.source_icp_id}")
        print(f"  {e}")
        print("\nMake sure you've completed a search workflow first:")
        print("  python ../01_search/first_search.py")
        sys.exit(1)

    if total_companies == 0:
        print("\nError: No companies found in this ICP.")
        print("  Signal monitoring requires at least one company to track.")
        sys.exit(1)

    print(f"   Found ICP: {args.source_icp_id}")
    print(f"   Companies to monitor: {total_companies}")

    # =========================================================================
    # [2/4] Create Signal Task
    # =========================================================================
    print("\n[2/4] Creating signal-sheet task...")

    task_config = {
        "type": "signal-sheet",
        "source_icp_id": args.source_icp_id,
        "signal_types": SIGNAL_TYPES,
        "entity_type": "company",
        "monitoring_frequency": args.frequency,
    }
    if args.webhook_url:
        task_config["webhook_url"] = args.webhook_url

    task = client.task.create(
        name=f"Signal Monitor: {total_companies} companies (sheet)",
        description=f"{args.frequency.title()} signal monitoring for {total_companies} companies",
        flow_name="signal",
        deployment_name="main",
        icp_id=args.source_icp_id,
        task_config=task_config,
    )

    task_id = get_attr(task, "id")
    print(f"   Task ID: {task_id}")
    print(f"   Frequency: {args.frequency}")
    print(f"   Signal types: {', '.join(s['display'] for s in SIGNAL_TYPES)}")

    # =========================================================================
    # [3/4] Execute Task (First Run)
    # =========================================================================
    print("\n[3/4] Starting first monitoring run...")

    execution = client.task.execute(task_id, icp_id=args.source_icp_id)
    run_id = get_attr(execution, "run_id")
    print(f"   Run ID: {run_id}")

    # =========================================================================
    # [4/4] Create Schedule
    # =========================================================================
    print("\n[4/4] Creating recurring schedule...")

    schedule = client.schedule.create(
        task_id=task_id,
        cron_expression=FREQUENCY_CRONS[args.frequency],
        icp_id=args.source_icp_id,
        name=f"Signal Monitor: {total_companies} companies ({args.frequency})",
    )

    schedule_id = get_attr(schedule, "id")
    schedule_status = get_attr(schedule, "status", "N/A")
    print(f"   Schedule ID: {schedule_id}")
    print(f"   Status: {schedule_status}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 60)
    print("Signal Monitoring Setup Complete!")
    print("=" * 60)

    print(f"\n  Source ICP:   {args.source_icp_id}")
    print(f"  Companies:    {total_companies}")
    print(f"  Frequency:    {args.frequency}")
    print(f"  Task ID:      {task_id}")
    print(f"  Run ID:       {run_id}")
    print(f"  Schedule ID:  {schedule_id}")
    print(f"  Status:       {schedule_status}")
    if args.webhook_url:
        print(f"  Webhook:      {args.webhook_url}")

    print("\nNext steps:")
    print("  1. Query signals once the run completes:")
    print(f"     python query_signals.py {task_id}")
    print("\n  2. View in dashboard:")
    print(f"     https://app.linkt.ai/icp/{args.source_icp_id}")


if __name__ == "__main__":
    main()
