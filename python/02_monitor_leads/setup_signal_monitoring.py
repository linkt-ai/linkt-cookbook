"""
Linkt SDK - Setup Weekly Signal Monitoring

This script sets up a signal monitoring task to track AI-related signals
for companies discovered in a previous search workflow.

Uses the signal-sheet task type to monitor entities from an existing ICP.

Workflow:
    1. Verify the source ICP exists and has companies to monitor
    2. Create a signal monitoring task with AI-focused signals
    3. Execute the task to start the first monitoring run
    4. Output task ID and run ID for tracking

Usage:
    python setup_signal_monitoring.py <icp_id> [webhook_url]

Example:
    python setup_signal_monitoring.py abc123-...
    python setup_signal_monitoring.py abc123-... https://example.com/webhook

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - ICP ID from a completed discovery workflow (01_getting_started/first_discovery.py)
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
MONITORING_FREQUENCY = "weekly"  # Options: "daily", "weekly", "monthly"

# Signal types to monitor
# Each signal type requires:
#   - type: Signal category (funding, leadership_change, hiring_surge, etc.)
#   - display: Human-readable name shown in UI
#   - description: Natural language description of what to look for
#
# Valid types: funding, leadership_change, layoff, product_launch, partnership,
#              acquisition, expansion, award, pivot, regulatory, rfp,
#              contract_renewal, hiring_surge, infrastructure, compliance,
#              job_posting, other
#
# Use "other" with custom display/description for signals not in the preset list.
SIGNAL_TYPES = [
    {
        "type": "other",
        "display": "AI Initiatives",
        "description": "News about AI initiatives, artificial intelligence projects, machine learning implementations, AI partnerships, and AI-powered product launches",
    },
    {
        "type": "other",
        "display": "AI Thought Leadership",
        "description": "LinkedIn posts about AI automation, AI powering scaling efforts, generative AI adoption, and executive perspectives on AI transformation",
    },
    {
        "type": "job_posting",
        "display": "AI Job Postings",
        "description": "Job postings for AI-related roles including AI engineers, ML engineers, data scientists, AI product managers, and AI/ML specialists",
    },
]


def get_attr(obj, key, default=None):
    """Get attribute from object or dict (handles mixed SDK return types)."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def main():
    """Set up signal monitoring for companies in an existing ICP."""

    print("=" * 60)
    print("Linkt SDK - Setup Signal Monitoring")
    print("=" * 60)

    # =========================================================================
    # Parse Command Line Arguments
    # =========================================================================
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("\nUsage: python setup_signal_monitoring.py <icp_id> [webhook_url]")
        print("\nExample:")
        print("  python setup_signal_monitoring.py abc123-...")
        print("  python setup_signal_monitoring.py abc123-... https://example.com/webhook")
        print("\nGet the ICP ID from first_discovery.py output.")
        sys.exit(1)

    source_icp_id = sys.argv[1]
    webhook_url = sys.argv[2] if len(sys.argv) == 3 else None

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
    # Step 1: Verify Source ICP and Count Companies
    # =========================================================================
    # Before setting up monitoring, verify the ICP exists and has companies.
    # Signal-sheet tasks monitor entities from an existing ICP's sheet.
    #
    # We verify by listing companies - if the ICP doesn't exist or has no
    # companies, this will fail or return zero results.

    print("\n[1/3] Verifying source ICP...")

    try:
        companies_response = client.entity.list(
            icp_id=source_icp_id, entity_type="company"
        )
        total_companies = get_attr(companies_response, "total", 0)
    except Exception as e:
        print(f"\nError: Could not access ICP with ID: {source_icp_id}")
        print(f"  {e}")
        print("\nMake sure you've completed a discovery workflow first:")
        print("  python 01_getting_started/first_discovery.py")
        sys.exit(1)

    if total_companies == 0:
        print("\nError: No companies found in this ICP.")
        print("  Signal monitoring requires at least one company to track.")
        print("\nMake sure the discovery workflow has completed:")
        print("  python 01_getting_started/monitor_discovery.py <run_id>")
        sys.exit(1)

    print(f"   Found ICP: {source_icp_id}")
    print(f"   Companies to monitor: {total_companies}")

    # =========================================================================
    # Step 2: Create Signal Monitoring Task
    # =========================================================================
    # The signal-sheet task type monitors entities from an existing ICP.
    #
    # Required task_config fields:
    #   - type: "signal-sheet" (discriminator)
    #   - source_icp_id: The ICP containing entities to monitor
    #   - signal_types: Array of signal configurations
    #
    # Optional task_config fields:
    #   - entity_type: "company" (default) or "person"
    #   - entity_filters: MongoDB query to filter entities (optional)
    #   - monitoring_frequency: "daily", "weekly" (default), or "monthly"
    #   - webhook_url: URL for completion notifications (optional)

    print("\n[2/3] Creating signal monitoring task...")

    # Build task config
    task_config = {
        "type": "signal-sheet",
        "source_icp_id": source_icp_id,
        "signal_types": SIGNAL_TYPES,
        "entity_type": "company",
        "monitoring_frequency": MONITORING_FREQUENCY,
    }

    # Add webhook URL if provided
    if webhook_url:
        task_config["webhook_url"] = webhook_url

    task = client.task.create(
        name=f"Signal Monitor: {total_companies} companies",
        description=f"Weekly AI-focused signal monitoring for {total_companies} companies",
        flow_name="signal",
        deployment_name="main",
        icp_id=source_icp_id,
        task_config=task_config,
    )

    task_id = get_attr(task, "id")
    task_name = get_attr(task, "name")

    print(f"   Created Task: {task_name}")
    print(f"     ID: {task_id}")
    print(f"     Frequency: {MONITORING_FREQUENCY}")
    print(f"     Signal types: {', '.join(s['display'] for s in SIGNAL_TYPES)}")
    if webhook_url:
        print(f"     Webhook: {webhook_url}")

    # =========================================================================
    # Step 3: Execute Task (First Monitoring Run)
    # =========================================================================
    # Execute the task to start the first signal monitoring run.
    # This runs asynchronously and checks all configured companies for signals.

    print("\n[3/3] Starting first monitoring run...")

    execution = client.task.execute(
        task_id,
        icp_id=source_icp_id,
    )

    run_id = get_attr(execution, "run_id")

    print("   Monitoring run started")
    print(f"     Run ID: {run_id}")

    # =========================================================================
    # Output Summary
    # =========================================================================
    print("\n" + "=" * 60)
    print("Signal Monitoring Setup Complete!")
    print("=" * 60)

    print("\nConfiguration:")
    print(f"  Source ICP:     {source_icp_id}")
    print(f"  Companies:      {total_companies}")
    print(f"  Frequency:      {MONITORING_FREQUENCY}")
    print("  Signal types:   AI Initiatives, AI Thought Leadership, AI Job Postings")
    if webhook_url:
        print(f"  Webhook:        {webhook_url}")

    print("\nSave these IDs:\n")
    print(f"  TASK_ID={task_id}")
    print(f"  RUN_ID={run_id}")

    print("\nNext steps:")
    print("  1. View signals in the dashboard:")
    print(f"     https://app.linkt.ai/icp/{source_icp_id}")
    print("\n  2. Monitor run progress:")
    print(f"     python 01_getting_started/monitor_discovery.py {run_id}")

    # =========================================================================
    # TODO: Schedule API
    # =========================================================================
    # The monitoring_frequency field is set in the task config, but recurring
    # execution may require a separate schedule API. Currently, each run must
    # be triggered manually or via webhook integration.
    #
    # Future enhancement: If a schedule API becomes available, add:
    #   schedule = client.schedule.create(
    #       task_id=task_id,
    #       frequency=MONITORING_FREQUENCY,
    #   )

    print("\nNote: The first monitoring run has started. To set up recurring")
    print("runs, use the dashboard or integrate with your workflow automation.")


if __name__ == "__main__":
    main()
