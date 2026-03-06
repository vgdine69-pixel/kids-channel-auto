"""
auth_setup.py - ONE-TIME YouTube Authentication Setup
Run this ONCE on your computer to get the YouTube token.
After this, everything runs FREE in the cloud automatically!

Steps:
1. Run: python auth_setup.py
2. Browser opens → login to your YouTube account
3. Token is saved → you upload it to GitHub Secrets
4. DONE! Never need to touch your computer again!
"""

import os
import pickle
import base64
import json
import sys

print("""
╔══════════════════════════════════════════════════════════════╗
║     YouTube One-Time Authentication Setup                     ║
║     You only need to do this ONCE!                           ║
╚══════════════════════════════════════════════════════════════╝
""")

# ── Install required packages if not present ──────────────────────────────────
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except ImportError:
    print("Installing Google API packages...")
    os.system(f"{sys.executable} -m pip install google-api-python-client google-auth-oauthlib --quiet")
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly",
]

# ── Check for client_secrets.json ─────────────────────────────────────────────
if not os.path.exists("client_secrets.json"):
    print("""
❌ client_secrets.json NOT FOUND!

You need to get this from Google Cloud Console:
  1. Go to: https://console.cloud.google.com
  2. Create a new project (e.g. "Kids Channel Auto")
  3. Go to: APIs & Services → Library
  4. Search "YouTube Data API v3" → Enable it
  5. Go to: APIs & Services → Credentials
  6. Click: Create Credentials → OAuth 2.0 Client ID
  7. Application type: Desktop App
  8. Download JSON → rename to: client_secrets.json
  9. Put it in this folder, then run this script again!

Press Enter to exit...
""")
    input()
    sys.exit(1)

print("✅ client_secrets.json found!")
print("\n🔐 Opening browser for YouTube login...")
print("   (Login with your YouTube channel account)\n")

# ── Run OAuth flow ─────────────────────────────────────────────────────────────
try:
    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")

    # Save token
    with open("token.pickle", "wb") as f:
        pickle.dump(creds, f)

    print("✅ YouTube authentication successful!")

    # Verify by getting channel info
    yt = build("youtube", "v3", credentials=creds)
    channel = yt.channels().list(part="snippet,statistics", mine=True).execute()
    if channel.get("items"):
        ch = channel["items"][0]
        name = ch["snippet"]["title"]
        subs = ch["statistics"].get("subscriberCount", "hidden")
        vids = ch["statistics"].get("videoCount", 0)
        print(f"\n🎬 Channel Found: {name}")
        print(f"   Subscribers: {subs}")
        print(f"   Videos: {vids}")
    else:
        print("⚠️  Could not verify channel - but token saved!")

except Exception as e:
    print(f"❌ Authentication failed: {e}")
    print("Make sure you have a valid client_secrets.json")
    input("Press Enter to exit...")
    sys.exit(1)

# ── Convert token to base64 for GitHub Secrets ─────────────────────────────────
with open("token.pickle", "rb") as f:
    token_bytes = f.read()
token_b64 = base64.b64encode(token_bytes).decode()

print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║  ✅ AUTHENTICATION COMPLETE!                                          ║
╚══════════════════════════════════════════════════════════════════════╝

Your token has been saved to: token.pickle
Base64 encoded version (for GitHub):

YOUTUBE_TOKEN_B64 value (copy everything below the line):
─────────────────────────────────────────────────────────
{token_b64[:80]}...
[Full token saved to: token_b64.txt]
─────────────────────────────────────────────────────────
""")

with open("token_b64.txt", "w") as f:
    f.write(token_b64)

print("""
📋 NEXT STEPS - Add to GitHub Secrets:
(GitHub repo → Settings → Secrets → Actions → New secret)

  1. Name: YOUTUBE_TOKEN_B64
     Value: contents of token_b64.txt file

  2. Name: GEMINI_API_KEY
     Value: your key from https://aistudio.google.com/app/apikey

  3. Name: CHANNEL_NAME
     Value: Your YouTube Channel Name

  4. Name: YOUTUBE_CLIENT_ID
     Value: from your client_secrets.json → client_id field

  5. Name: YOUTUBE_CLIENT_SECRET
     Value: from your client_secrets.json → client_secret field

  6. Name: GH_PAT (GitHub Personal Access Token)
     Value: github.com → Settings → Developer Settings → Personal Access Tokens
     Permission needed: repo → secrets

After adding all secrets:
  ✅ System runs FREE in cloud 4x/day automatically!
  ✅ No computer needed!
  ✅ No paid subscriptions!
  ✅ Works forever!

Press Enter to exit...
""")
input()
