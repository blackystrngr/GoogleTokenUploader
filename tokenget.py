import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive']
CREDS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def main():
    print("=" * 50)
    print("Google Drive Token Generator")
    print("=" * 50)

    # ---- 1. Check credentials.json ----
    if not os.path.exists(CREDS_FILE):
        print(f"❌ ERROR: '{CREDS_FILE}' not found in current folder!")
        print(f"   Current directory: {os.getcwd()}")
        print("   Make sure you downloaded the OAuth client JSON and renamed it to credentials.json")
        sys.exit(1)

    print(f"✅ Found {CREDS_FILE}")

    # ---- 2. Delete old token if exists ----
    if os.path.exists(TOKEN_FILE):
        print(f"⚠️  {TOKEN_FILE} already exists. Deleting to regenerate...")
        os.remove(TOKEN_FILE)

    # ---- 3. Start OAuth flow ----
    print("🌐 Starting OAuth flow...")
    print("   A browser window will open. Log in with your Google account.")
    print()

    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
        # run_local_server opens a browser and captures the code automatically
        creds = flow.run_local_server(port=0, open_browser=True)

        # ---- 4. Save token ----
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())

        print()
        print("=" * 50)
        print(f"✅ SUCCESS! Saved {TOKEN_FILE}")
        print("=" * 50)
        print(f"Token expires: {creds.expiry}")
        print()
        print("Next steps:")
        print("  1. Copy token.json to your VPS (same folder as app.py)")
        print("  2. Restart Flask on the VPS")

    except Exception as e:
        print()
        print("=" * 50)
        print(f"❌ ERROR: {type(e).__name__}")
        print("=" * 50)
        print(str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()