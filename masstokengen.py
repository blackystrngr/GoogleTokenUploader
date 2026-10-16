# make_token.py
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

# pass account name as CLI arg: python make_token.py alice
name = sys.argv[1] if len(sys.argv) > 1 else "default"
out_file = "token.json" if name == "default" else f"token_{name}.json"

SCOPES = ['https://www.googleapis.com/auth/drive']

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)

# This opens a browser. Make sure the correct Google account
# is signed in (use a separate browser profile for each account).
creds = flow.run_local_server(port=0)

with open(out_file, 'w') as f:
    f.write(creds.to_json())

print(f"Saved {out_file} — account: {creds.client_id[:20]}...")