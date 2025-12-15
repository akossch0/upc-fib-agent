"""Script to authenticate with FIB API using OAuth."""

from src.auth import FIBOAuthClient, FIBOAuthError


def main():
    print("FIB OAuth Authentication")
    print("=" * 40)

    try:
        client = FIBOAuthClient()
    except FIBOAuthError as e:
        print(f"Error: {e}")
        print("\nMake sure you have set:")
        print("  - FIB_CLIENT_ID")
        print("  - FIB_CLIENT_SECRET")
        return

    if client.is_authenticated:
        print("Already authenticated!")
        print(f"Token file: {client._token_file}")
        return

    print("\nStarting OAuth flow...")
    print("A browser window will open for FIB login.")
    print()

    if client.authorize_interactive():
        print("\n✅ Authentication successful!")
        print(f"Token saved to: {client._token_file}")
    else:
        print("\n❌ Authentication failed.")
        print("Make sure to complete the login in your browser.")


if __name__ == "__main__":
    main()
