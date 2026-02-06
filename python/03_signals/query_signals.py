"""
Linkt SDK - Query Signals

Query and display signals produced by any signal task.

Supports querying by ICP ID with optional time range and filters.
Displays signal score with tier labels (HIGH/MEDIUM/LOW) and summary statistics.

Usage:
    python query_signals.py --icp <icp_id>               # All signals for an ICP
    python query_signals.py --icp <icp_id> --days 7      # Recent signals (last 7 days)
    python query_signals.py --icp <icp_id> --type funding      # Filter by type
    python query_signals.py --icp <icp_id> --strength strong   # Filter by strength

Examples:
    python query_signals.py --icp icp_abc123
    python query_signals.py --icp icp_abc123 --days 7
    python query_signals.py --icp icp_abc123 --type funding --strength strong

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - Signal monitoring set up (see signals_from_sheet.py, signals_from_csv.py, or signals_from_topic.py)
"""

import argparse
import os
import sys
from datetime import datetime
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


def score_tier(score):
    """Convert numeric score to tier label."""
    if score >= 0.8:
        return "HIGH"
    elif score >= 0.5:
        return "MEDIUM"
    else:
        return "LOW"


# All 17 signal types supported by Linkt
ALL_SIGNAL_TYPES = [
    ("funding", "Funding rounds, investments"),
    ("leadership_change", "New executives, leadership changes"),
    ("layoff", "Workforce reductions, layoffs"),
    ("product_launch", "New product announcements"),
    ("partnership", "Strategic partnerships"),
    ("acquisition", "M&A activity"),
    ("expansion", "Geographic or market expansion"),
    ("award", "Industry recognition, awards"),
    ("pivot", "Strategic direction changes"),
    ("regulatory", "Compliance, regulatory news"),
    ("rfp", "Request for proposals"),
    ("contract_renewal", "Contract renewals"),
    ("hiring_surge", "Rapid hiring activity"),
    ("infrastructure", "Technology investments"),
    ("compliance", "Compliance updates"),
    ("job_posting", "Specific job postings"),
    ("other", "Custom signal types (AI Initiatives, etc.)"),
]


def main():
    """Query and display signals."""

    parser = argparse.ArgumentParser(description="Query signals from Linkt API")
    parser.add_argument("--icp", dest="icp_id", required=True, help="ICP ID to filter signals")
    parser.add_argument("--days", type=int, default=30, help="Days to look back (default: 30)")
    parser.add_argument("--type", dest="signal_type", help="Signal type filter")
    parser.add_argument("--strength", help="Strength filter (strong/moderate/weak)")
    args = parser.parse_args()

    print("=" * 60)
    print("Linkt SDK - Query Signals")
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
    # [1/3] Build Query
    # =========================================================================
    print("\n[1/3] Building query...")

    query_params = {
        "days": args.days,
        "page_size": 50,
    }

    query_params["icp_id"] = args.icp_id
    print(f"   ICP: {args.icp_id}")

    if args.signal_type:
        query_params["signal_type"] = args.signal_type
        print(f"   Type: {args.signal_type}")

    if args.strength:
        query_params["strength"] = args.strength
        print(f"   Strength: {args.strength}")

    print(f"   Days: {args.days}")

    # =========================================================================
    # [2/3] Fetch Signals
    # =========================================================================
    print("\n[2/3] Fetching signals...")

    response = client.signal.list(**query_params)
    total = get_attr(response, "total", 0)
    signals = get_attr(response, "signals", [])

    print(f"\n   Found {total} signals")

    if not signals:
        print("\n   No signals found matching criteria.")
        print("\n   Tips:")
        print("   - Set up signal monitoring first:")
        print("     python signals_from_sheet.py <icp_id>")
        print("     python signals_from_csv.py <csv_path>")
        print("     python signals_from_topic.py \"<topic>\"")
        print("   - Wait for monitoring run to complete")
        print("   - Try a longer date range: --days 90")
        return

    # =========================================================================
    # [3/3] Display Signals
    # =========================================================================
    print("\n[3/3] Signals:")
    print("=" * 60)

    for i, signal in enumerate(signals, 1):
        signal_id = get_attr(signal, "id", "N/A")
        signal_type = get_attr(signal, "signal_type", "unknown")
        display_type = get_attr(signal, "display_type", signal_type)
        strength = get_attr(signal, "strength", "N/A")
        score = get_attr(signal, "score", 0.0)
        tier = score_tier(score)
        summary = get_attr(signal, "summary", "No summary")
        detected_at = get_attr(signal, "detected_at", "")
        entity_id = get_attr(signal, "entity_id", "")
        source_url = get_attr(signal, "source_url", "")

        # Format date
        if detected_at:
            try:
                if isinstance(detected_at, str):
                    dt = datetime.fromisoformat(detected_at.replace("Z", "+00:00"))
                else:
                    dt = detected_at
                date_str = dt.strftime("%b %d, %Y")
            except (ValueError, AttributeError):
                date_str = str(detected_at)[:10]
        else:
            date_str = "N/A"

        print(f"\n{i}. [{tier}] {display_type}")
        print(f"   Score: {score:.2f} | Strength: {strength} | Detected: {date_str}")
        print(f"   Summary: {summary[:100]}{'...' if len(str(summary)) > 100 else ''}")
        print(f"   Entity: {entity_id}")
        if source_url:
            print(f"   Source: {source_url}")

    # =========================================================================
    # Summary Statistics
    # =========================================================================
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("=" * 60)

    # Count by type
    type_counts = {}
    strength_counts = {}
    scores = []

    for signal in signals:
        sig_type = get_attr(signal, "display_type", get_attr(signal, "signal_type", "unknown"))
        strength = get_attr(signal, "strength", "unknown")
        score = get_attr(signal, "score", 0.0)

        type_counts[sig_type] = type_counts.get(sig_type, 0) + 1
        strength_counts[strength] = strength_counts.get(strength, 0) + 1
        scores.append(score)

    print("\n   By Type:")
    for sig_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"     {sig_type}: {count}")

    print("\n   By Strength:")
    for strength, count in sorted(strength_counts.items()):
        print(f"     {strength}: {count}")

    if scores:
        high = len([s for s in scores if s >= 0.8])
        medium = len([s for s in scores if 0.5 <= s < 0.8])
        low = len([s for s in scores if s < 0.5])
        avg_score = sum(scores) / len(scores)

        print(f"\n   Score Distribution:")
        print(f"     HIGH (0.8+):    {high}")
        print(f"     MEDIUM (0.5+):  {medium}")
        print(f"     LOW (<0.5):     {low}")
        print(f"     Average score:  {avg_score:.2f}")

    print(f"\n   Total: {total}")


if __name__ == "__main__":
    main()
