"""
Linkt SDK - Hello World

Verifies your SDK installation and API credentials are configured correctly.

Usage:
    python hello_world.py

Prerequisites:
    - LINKT_API_KEY environment variable set (via .env file or shell)
    - linkt-sdk package installed

Expected Output:
    Connected to Linkt API successfully!
    Environment: production
    Found X existing ICP(s)
"""

import os
import sys
from pathlib import Path

# Load environment variables from root .env file
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

import linkt
from linkt import Linkt


def main():
    """Verify SDK connection and list existing ICPs."""

    # Check if API key is configured
    if not os.getenv("LINKT_API_KEY"):
        print("Error: LINKT_API_KEY environment variable not set.")
        print(f"  Expected .env file at: {env_path}")
        print("  Or set the environment variable directly.")
        sys.exit(1)

    # Initialize the Linkt client
    # API key is automatically read from LINKT_API_KEY environment variable
    # Environment can be "staging" or "production" (default)
    try:
        # Initialize client
        environment = os.getenv("LINKT_API_ENVIRONMENT", "production")
        if environment == "dev":
            client = Linkt(base_url="http://localhost:8080")
        else:
            client = Linkt(environment=environment)
    except linkt.AuthenticationError as e:
        print("Authentication failed. Check your LINKT_API_KEY.")
        print(f"  Error: {e}")
        sys.exit(1)

    # Make a simple API call to verify connectivity
    try:
        response = client.icp.list()

        print("Connected to Linkt API successfully!")
        print(f"  Environment: {environment}")
        print(f"  Found {response.total} existing ICP(s)")

        # List ICP names if any exist
        if response.icps:
            print("\n  Your ICPs:")
            for icp in response.icps:
                print(f"    - {icp.name} ({icp.id})")

    except linkt.APIConnectionError as e:
        print("Could not connect to Linkt API.")
        print(f"  Error: {e}")
        sys.exit(1)
    except linkt.APIStatusError as e:
        print(f"API request failed with status {e.status_code}")
        print(f"  Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
