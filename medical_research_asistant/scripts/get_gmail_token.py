"""
get_gmail_token.py
──────────────────
CLI helper to generate Google OAuth2 Refresh Token for the Medpedia Gmail API dispatcher.

Usage:
    uv run python scripts/get_gmail_token.py
"""

import sys
import urllib.parse
import requests

GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"

def main():
    print("=" * 70)
    print(" Medpedia — Google Gmail OAuth2 Refresh Token Setup")
    print("=" * 70)
    print("\nBefore running this, make sure you have:")
    print("1. Created a project in Google Cloud Console (https://console.cloud.google.com)")
    print("2. Enabled the 'Gmail API' under APIs & Services > Library")
    print("3. Created OAuth 2.0 Client ID under APIs & Services > Credentials")
    print("   - Application type: 'Web application' or 'Desktop app'")
    print("   - Authorized redirect URI: https://developers.google.com/oauthplayground (if web)")
    print("     or http://localhost:8080 (if desktop)\n")

    client_id = input("Enter your GMAIL_CLIENT_ID: ").strip()
    if not client_id:
        print("Error: Client ID is required.")
        sys.exit(1)

    client_secret = input("Enter your GMAIL_CLIENT_SECRET: ").strip()
    if not client_secret:
        print("Error: Client Secret is required.")
        sys.exit(1)

    # Build OAuth Consent URL
    redirect_uri = "https://developers.google.com/oauthplayground"
    auth_params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": GMAIL_SEND_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(auth_params)}"

    print("\n" + "─" * 70)
    print("STEP 1: Open this URL in your browser and authorize your Gmail account:")
    print("─" * 70)
    print(auth_url)
    print("─" * 70)
    print("After authorizing, you will be redirected to OAuth Playground.")
    print("Look at the URL address bar or page for the 'code=...' parameter.")
    print("─" * 70 + "\n")

    code = input("Paste the authorization code here: ").strip()
    if not code:
        print("Error: Authorization code is required.")
        sys.exit(1)

    # Exchange code for tokens
    print("\nExchanging code for Refresh Token...")
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if token_resp.status_code != 200:
        print(f"Error ({token_resp.status_code}): {token_resp.text}")
        sys.exit(1)

    tokens = token_resp.json()
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        print("Warning: Google did not return a refresh token.")
        print("This usually happens if access was already granted. Try revoking app access and running again with prompt=consent.")
        print("Tokens received:", tokens)
        sys.exit(1)

    print("\n" + "=" * 70)
    print(" SUCCESS! Add these to your .env and Render Dashboard:")
    print("=" * 70)
    print(f"GMAIL_CLIENT_ID={client_id}")
    print(f"GMAIL_CLIENT_SECRET={client_secret}")
    print(f"GMAIL_REFRESH_TOKEN={refresh_token}")
    print("GMAIL_SENDER_EMAIL=syedmohammedrayan2007@gmail.com")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
