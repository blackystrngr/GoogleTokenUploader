#!/usr/bin/env python3
"""
Generate a Google Drive OAuth token locally, upload it to the VPS
via the /upload_token HTTP route (no SSH needed).

Usage:
    python make_token.py <account_name>

Example:
    python make_token.py alice       → saves token_alice.json, POSTs it
    python make_token.py default     → saves token.json, POSTs it

Requires:
    pip install google-auth-oauthlib google-api-python-client requests
"""

import os
import sys
from pathlib import Path

import requests

# ================================================================
# CONFIG
# ================================================================
VPS_URL = "http://hi.blackstrngr.qzz.io:5000"          # no trailing slash
UPLOAD_SECRET = "whyyouleftme"               # matches COOKIE_UPLOAD_TOKEN on VPS
CLIENT_SECRET_FILE = "credentials.json"      # in the same dir as this script
SCOPES = ["https://www.googleapis.com/auth/drive"]
# ================================================================


def die(msg, code=1):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(code)

def info(m): print(f"ℹ️  {m}")
def ok(m):   print(f"✅ {m}")
def warn(m): print(f"⚠️  {m}")


def run_oauth_flow(out_path):
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        die("Missing dep. Run: pip install google-auth-oauthlib")

    if not Path(CLIENT_SECRET_FILE).exists():
        die(f"'{CLIENT_SECRET_FILE}' not found in {Path.cwd()}")

    info("Opening browser for Google sign-in...")
    info("Use the correct browser profile for this account.")

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0, prompt="select_account")

    with open(out_path, "w") as f:
        f.write(creds.to_json())
    ok(f"Saved locally: {out_path}")
    return out_path


def verify_token(token_path):
    """Confirm which Google account the token belongs to."""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        svc = build("drive", "v3", credentials=creds, cache_discovery=False)
        email = svc.about().get(fields="user").execute()["user"]["emailAddress"]
        ok(f"Token belongs to: {email}")
        return email
    except Exception as e:
        warn(f"Verify failed: {e}")
        return None


def upload_to_vps(token_path, account):
    with open(token_path, "rb") as f:
        content = f.read()

    url = f"{VPS_URL.rstrip('/')}/upload_token"
    headers = {
        "X-Upload-Token": UPLOAD_SECRET,
        "X-Account-Name": account,
        "Content-Type": "application/json",
    }

    info(f"POSTing {len(content)} bytes to {url}")
    try:
        resp = requests.post(url, headers=headers, data=content, timeout=30)
    except requests.RequestException as e:
        die(f"HTTP request failed: {e}")

    if resp.status_code != 200:
        die(f"Upload rejected ({resp.status_code}): {resp.text[:300]}")

    try:
        data = resp.json()
    except Exception:
        die(f"Non-JSON response: {resp.text[:300]}")

    if data.get('status') != 'ok':
        die(f"Server error: {data.get('error', data)}")

    ok(f"Uploaded to VPS as '{data['filename']}'")
    if data.get('email'):
        ok(f"Server verified token for: {data['email']}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        die("Missing argument: account name")

    account = sys.argv[1].strip()
    if account.startswith("token_"):
        die("Pass just the name, e.g. 'alice', not 'token_alice.json'")

    filename = "token.json" if account == "default" else f"token_{account}.json"

    print(f"\n=== Token for account: {account} ===\n")

    run_oauth_flow(filename)
    verify_token(filename)

    print()
    confirm = input(f"Upload to {VPS_URL} as '{filename}'? [y/N] ").strip().lower()
    if confirm != "y":
        warn("Cancelled. Local file kept.")
        return

    upload_to_vps(filename, account)

    print()
    ok(f"Done. Account '{account}' registered on VPS.")
    print("Refresh the Drive tab in your browser to see it in the dropdown.")
    print()


if __name__ == "__main__":
    main()