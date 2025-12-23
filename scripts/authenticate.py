#!/usr/bin/env python
"""
Script to authenticate with the FIB API using OAuth2.

This script runs the interactive OAuth authorization flow to obtain
access tokens for the FIB private API endpoints.

Usage:
    python scripts/authenticate.py
"""

import sys

from src.auth import FIBOAuthClient, FIBOAuthError


def main():
    print("FIB API OAuth Authentication")
    print("=" * 40)

    try:
        client = FIBOAuthClient()
    except FIBOAuthError as e:
        print(f"Error: {e}")
        print("\nMake sure FIB_CLIENT_ID and FIB_CLIENT_SECRET are set in .env")
        return 1

    if client.is_authenticated:
        print("You are already authenticated!")
        print(f"Token file: {client._token_file}")

        choice = input("\nDo you want to re-authenticate? (y/N): ")
        if choice.lower() != 'y':
            return 0
        client.logout()

    print("\nStarting OAuth authorization flow...")
    print("A browser window will open for you to log in with your FIB credentials.")
    print()

    try:
        success = client.authorize_interactive()
        if success:
            print("\n" + "=" * 40)
            print("Authentication successful!")
            print(f"Token saved to: {client._token_file}")
            print("\nYou can now use the private FIB API endpoints.")
            return 0
        else:
            print("\nAuthentication failed or was cancelled.")
            return 1
    except FIBOAuthError as e:
        print(f"\nError during authentication: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\nAuthentication cancelled by user.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
