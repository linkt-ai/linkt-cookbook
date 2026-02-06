"""
Linkt SDK - Signals from Topic

Monitor signals by topic criteria (no pre-existing entities needed).

This script creates a signal-topic task from a natural language description,
executes the first run, and sets up a recurring schedule.

Usage:
    python signals_from_topic.py "<topic_criteria>" --icp-id <icp_id> [--webhook URL] [--frequency weekly]

Examples:
    python signals_from_topic.py "AI startups in healthcare" --icp-id icp_abc123
    python signals_from_topic.py "Series B SaaS companies adopting AI" --icp-id icp_abc123 --frequency daily
    python signals_from_topic.py "Enterprise companies expanding into APAC" --icp-id icp_abc123 --webhook https://example.com/hook

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
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
    """Set up signal monitoring from a topic description."""

    parser = argparse.ArgumentParser(
        description="Monitor signals by topic criteria"
    )
    parser.add_argument(
        "topic_criteria",
        help="Natural language description of the topic to monitor",
    )
    parser.add_argument("--icp-id", required=True, help="ICP ID to associate with the signal task")
    parser.add_argument("--webhook", dest="webhook_url", help="Webhook URL for notifications")
    parser.add_argument(
        "--frequency",
        choices=["daily", "weekly", "monthly"],
        default="weekly",
        help="Monitoring frequency (default: weekly)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Linkt SDK - Signals from Topic")
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
    # [1/3] Create Signal Task
    # =========================================================================
    print(f"\n[1/3] Creating signal-topic task...")
    print(f"   Topic: {args.topic_criteria}")

    task_config = {
        "type": "signal-topic",
        "topic_criteria": args.topic_criteria,
        "signal_types": SIGNAL_TYPES,
        "entity_type": "company",
        "monitoring_frequency": args.frequency,
    }
    if args.webhook_url:
        task_config["webhook_url"] = args.webhook_url

    task = client.task.create(
        name=f"Signal Monitor: {args.topic_criteria[:40]}",
        description=f"{args.frequency.title()} signal monitoring for topic: {args.topic_criteria}",
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
    # [2/3] Execute Task (First Run)
    # =========================================================================
    print("\n[2/3] Starting first monitoring run...")

    execution = client.task.execute(task_id)
    run_id = get_attr(execution, "run_id")
    print(f"   Run ID: {run_id}")

    # =========================================================================
    # [3/3] Create Schedule
    # =========================================================================
    print("\n[3/3] Creating recurring schedule...")

    schedule = client.schedule.create(
        task_id=task_id,
        cron_expression=FREQUENCY_CRONS[args.frequency],
        icp_id=args.icp_id,
        name=f"Signal Monitor: {args.topic_criteria[:30]} ({args.frequency})",
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

    print(f"\n  Topic:        {args.topic_criteria}")
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
