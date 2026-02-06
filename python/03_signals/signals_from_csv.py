"""
Linkt SDK - Signals from CSV

Monitor signals on companies from an uploaded CSV file.

This script uploads a CSV (or uses an existing file_id), creates a signal-csv
task, executes the first run, and sets up a recurring schedule.

Usage:
    python signals_from_csv.py <csv_path_or_file_id> --icp-id <icp_id> [--webhook URL] [--frequency daily]

Examples:
    python signals_from_csv.py ../02_ingest/sample_data/companies.csv --icp-id icp_abc123
    python signals_from_csv.py file_abc123 --icp-id icp_abc123
    python signals_from_csv.py companies.csv --icp-id icp_abc123 --webhook https://example.com/hook --frequency daily

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - CSV file with company data (minimum: name or domain column)
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
    """Set up signal monitoring from a CSV file."""

    parser = argparse.ArgumentParser(
        description="Monitor signals on companies from a CSV file"
    )
    parser.add_argument(
        "source",
        help="CSV file path to upload, or existing file_id",
    )
    parser.add_argument("--icp-id", required=True, help="ICP ID to associate with the signal task")
    parser.add_argument("--webhook", dest="webhook_url", help="Webhook URL for notifications")
    parser.add_argument(
        "--frequency",
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="Monitoring frequency (default: daily)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Linkt SDK - Signals from CSV")
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
    # [1/4] Upload CSV or Use Existing File ID
    # =========================================================================
    csv_path = Path(args.source)

    if csv_path.exists() and csv_path.suffix == ".csv":
        print(f"\n[1/4] Uploading CSV file: {csv_path}")

        with open(csv_path, "rb") as f:
            file_content = f.read()

        upload_response = client.files.upload(
            file=(csv_path.name, file_content, "text/csv"),
        )

        file_id = get_attr(upload_response, "file_id")
        row_count = get_attr(upload_response, "row_count", "unknown")
        print(f"   File ID: {file_id}")
        print(f"   Rows: {row_count}")
    else:
        file_id = args.source
        print(f"\n[1/4] Using existing file: {file_id}")

    # =========================================================================
    # [2/4] Create Signal Task
    # =========================================================================
    print("\n[2/4] Creating signal-csv task...")

    task_config = {
        "type": "signal-csv",
        "file_id": file_id,
        "signal_types": SIGNAL_TYPES,
        "entity_type": "company",
        "primary_column": "name",
        "monitoring_frequency": args.frequency,
    }
    if args.webhook_url:
        task_config["webhook_url"] = args.webhook_url

    task = client.task.create(
        name=f"Signal Monitor: CSV ({file_id[:20]}...)",
        description=f"{args.frequency.title()} signal monitoring from CSV file",
        flow_name="signal",
        deployment_name="main",
        icp_id=args.icp_id,
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

    execution = client.task.execute(task_id)
    run_id = get_attr(execution, "run_id")
    print(f"   Run ID: {run_id}")

    # =========================================================================
    # [4/4] Create Schedule
    # =========================================================================
    print("\n[4/4] Creating recurring schedule...")

    schedule = client.schedule.create(
        task_id=task_id,
        cron_expression=FREQUENCY_CRONS[args.frequency],
        icp_id=args.icp_id,
        name=f"Signal Monitor: CSV ({args.frequency})",
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

    print(f"\n  Source:       CSV file ({file_id})")
    print(f"  Frequency:    {args.frequency}")
    print(f"  Task ID:      {task_id}")
    print(f"  Run ID:       {run_id}")
    print(f"  Schedule ID:  {schedule_id}")
    print(f"  Status:       {schedule_status}")
    if args.webhook_url:
        print(f"  Webhook:      {args.webhook_url}")

    print("\nNext steps:")
    print("  1. Query signals once the run completes:")
    print(f"     python query_signals.py --icp {args.icp_id}")
    print("\n  2. Manage your schedule:")
    print(f"     python ../04_advanced/schedule_management.py get {schedule_id}")


if __name__ == "__main__":
    main()
