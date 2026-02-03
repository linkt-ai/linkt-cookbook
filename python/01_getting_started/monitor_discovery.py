"""
Linkt SDK - Monitor Discovery Progress

This script monitors a running discovery task and shows real-time progress
using the queue endpoint to see entities being processed.

Features:
    - Shows count of entities in each state (queued/processing/completed/discarded)
    - Displays real-time state transitions as they happen
    - Shows discard reasons when entities are rejected

The queue endpoint provides visibility into:
    - queued: Entities waiting to be processed
    - processing: Entities currently being worked on
    - completed: Entities successfully processed and saved
    - discarded: Entities skipped (with reason)

Usage:
    python monitor_discovery.py <run_id>

Example:
    python monitor_discovery.py abc123-def456-...

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed
    - A run_id from first_discovery.py

Note:
    Search operations typically take 15-20 minutes to complete.
    This script will show progress updates until the run finishes.
"""

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from linkt import Linkt

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# =============================================================================
# Configuration
# =============================================================================
POLL_INTERVAL_SECONDS = 10  # How often to check status
MAX_WAIT_MINUTES = 45  # Maximum time to wait before timeout

# Terminal states - run has finished (successfully or not)
TERMINAL_STATES = {"COMPLETED", "FAILED", "CANCELED", "CRASHED"}


def get_attr(obj, key, default=None):
    """Get attribute from object or dict (handles mixed SDK return types)."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def get_entity_states(queue_response):
    """
    Extract entity states from queue response.

    Returns a dict mapping entity name to current state info:
        {
            "Acme Inc": {"state": "processing", "reason": None},
            "Widget Co": {"state": "discarded", "reason": "Unable to find contact..."},
        }
    """
    entities = get_attr(queue_response, "entities", [])
    states = {}

    for entity in entities:
        name = get_attr(entity, "name", "Unknown")
        state = get_attr(entity, "state", "unknown")

        # Get discard reason if present (available on discarded entities)
        reason = get_attr(entity, "reason")
        if not reason:
            # Also check stage_metadata for reason
            stage_metadata = get_attr(entity, "stage_metadata", {})
            if isinstance(stage_metadata, dict):
                reason = stage_metadata.get("reason")
            else:
                reason = get_attr(stage_metadata, "reason")

        states[name] = {"state": state, "reason": reason}

    return states


def get_state_counts(queue_response):
    """
    Extract state counts from queue response.

    The queue response includes a state_counts object:
        {"queued": 2, "processing": 3, "completed": 4, "discarded": 1}
    """
    # Try state_counts first, then stats as fallback
    counts = get_attr(queue_response, "state_counts")
    if not counts:
        counts = get_attr(queue_response, "stats", {})

    if isinstance(counts, dict):
        return {
            "queued": counts.get("queued", 0),
            "processing": counts.get("processing", 0),
            "completed": counts.get("completed", 0),
            "discarded": counts.get("discarded", 0),
        }

    return {
        "queued": get_attr(counts, "queued", 0),
        "processing": get_attr(counts, "processing", 0),
        "completed": get_attr(counts, "completed", 0),
        "discarded": get_attr(counts, "discarded", 0),
    }


def detect_transitions(previous_states, current_states):
    """
    Compare previous and current entity states to detect transitions.

    Returns a list of transition dicts:
        [
            {"name": "Acme Inc", "from": "processing", "to": "completed", "reason": None},
            {"name": "Widget Co", "from": "processing", "to": "discarded", "reason": "..."},
        ]
    """
    transitions = []

    for name, current in current_states.items():
        current_state = current["state"]

        if name in previous_states:
            previous_state = previous_states[name]["state"]
            if previous_state != current_state:
                transitions.append({
                    "name": name,
                    "from": previous_state,
                    "to": current_state,
                    "reason": current.get("reason"),
                })
        else:
            # New entity appeared (first time seeing it)
            # Only report if it's not in 'queued' state (to avoid noise)
            if current_state != "queued":
                transitions.append({
                    "name": name,
                    "from": "queued",
                    "to": current_state,
                    "reason": current.get("reason"),
                })

    return transitions


def format_transition(transition):
    """Format a state transition for display."""
    name = transition["name"]
    from_state = transition["from"]
    to_state = transition["to"]
    reason = transition.get("reason")

    # Use arrow symbols for visual clarity
    line = f"   → {name}: {from_state} → {to_state}"

    if to_state == "discarded" and reason:
        # Truncate long reasons for display
        reason_display = reason[:80] + "..." if len(reason) > 80 else reason
        line += f"\n     Reason: {reason_display}"

    return line


def main():
    """Monitor a discovery run until completion."""

    # =========================================================================
    # Parse Command Line Arguments
    # =========================================================================
    if len(sys.argv) != 2:
        print("Usage: python monitor_discovery.py <run_id>")
        print("\nExample:")
        print("  python monitor_discovery.py abc123-def456-...")
        print("\nGet the run_id from first_discovery.py output.")
        sys.exit(1)

    run_id = sys.argv[1]

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

    print("=" * 70)
    print("Linkt SDK - Monitor Discovery Progress")
    print("=" * 70)
    print(f"\nMonitoring run: {run_id}")
    print(f"Polling every {POLL_INTERVAL_SECONDS} seconds...")
    print(f"Timeout after {MAX_WAIT_MINUTES} minutes\n")

    # =========================================================================
    # Monitor Loop
    # =========================================================================
    # We poll two endpoints:
    #   1. /run/{run_id} - Get overall run status
    #   2. /run/{run_id}/queue - Get real-time entity processing progress
    #
    # The queue endpoint returns entities with their current state and history.
    # By comparing states between polls, we can detect and report transitions.

    start_time = time.time()
    max_wait_seconds = MAX_WAIT_MINUTES * 60

    # Track entity states between polls to detect transitions
    previous_entity_states = {}

    while True:
        elapsed = int(time.time() - start_time)
        elapsed_min = elapsed // 60
        elapsed_sec = elapsed % 60
        timestamp = f"[{elapsed_min:02d}:{elapsed_sec:02d}]"

        # ---------------------------------------------------------------------
        # Check Run Status
        # ---------------------------------------------------------------------
        # The run object contains the overall workflow status.
        # States: SCHEDULED -> PENDING -> RUNNING -> COMPLETED/FAILED/etc.

        run = client.run.retrieve(run_id)
        status = get_attr(run, "status")

        # ---------------------------------------------------------------------
        # Check Queue Progress (Real-Time Entity Processing)
        # ---------------------------------------------------------------------
        # The queue endpoint shows entities in various processing states.
        # Key fields per entity:
        #   - name: Entity name (e.g., "Acme Inc")
        #   - state: Current state (queued/processing/completed/discarded)
        #   - state_history: Full transition history
        #   - reason: Discard reason (for discarded entities)
        #   - justification: Why entity matched ICP
        #
        # Use include_history=True to get all entities regardless of state.

        try:
            # Fetch all entities with history to track state transitions
            queue_response = client.run.get_queue(run_id, limit=100, include_history=True)

            # Extract state counts for summary display
            counts = get_state_counts(queue_response)

            # Print status line with counts
            print(
                f"{timestamp} Status: {status:12} | "
                f"Queued: {counts['queued']:3} | "
                f"Processing: {counts['processing']:3} | "
                f"Completed: {counts['completed']:3} | "
                f"Discarded: {counts['discarded']:3}"
            )

            # Extract current entity states
            current_entity_states = get_entity_states(queue_response)

            # Detect and report state transitions
            transitions = detect_transitions(previous_entity_states, current_entity_states)
            for transition in transitions:
                print(format_transition(transition))

            # Update previous states for next iteration
            previous_entity_states = current_entity_states

        except Exception as e:
            # Queue may not be available in all states (e.g., PENDING)
            # Print the actual error for debugging
            print(f"{timestamp} Status: {status} (queue error: {e})")

        # ---------------------------------------------------------------------
        # Check for Terminal State
        # ---------------------------------------------------------------------
        if status in TERMINAL_STATES:
            break

        # ---------------------------------------------------------------------
        # Check for Timeout
        # ---------------------------------------------------------------------
        if elapsed > max_wait_seconds:
            print(f"\nTimeout after {MAX_WAIT_MINUTES} minutes.")
            print(f"Run {run_id} is still processing.")
            print("\nYou can re-run this script to continue monitoring:")
            print(f"  python monitor_discovery.py {run_id}")
            sys.exit(0)

        time.sleep(POLL_INTERVAL_SECONDS)

    # =========================================================================
    # Report Final Status
    # =========================================================================
    print("\n" + "=" * 70)

    if status == "COMPLETED":
        print("Discovery Completed Successfully!")
        print("=" * 70)

        # Show final counts
        try:
            queue_response = client.run.get_queue(run_id, limit=1, include_history=True)
            counts = get_state_counts(queue_response)
            print(f"\nFinal results:")
            print(f"  Completed: {counts['completed']} entities")
            print(f"  Discarded: {counts['discarded']} entities")
        except Exception:
            pass

        # Show run summary if available
        output = get_attr(run, "output", {})
        if output:
            run_time = get_attr(output, "run_time")
            if run_time:
                minutes = int(run_time) // 60
                seconds = int(run_time) % 60
                print(f"\nRun time: {minutes}m {seconds}s")

        print("\nNext step - Review results:")
        print("  python review_discovery.py <icp_id>")
    else:
        print(f"Discovery ended with status: {status}")
        print("=" * 70)
        error = get_attr(run, "error")
        if error:
            print(f"\nError: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
