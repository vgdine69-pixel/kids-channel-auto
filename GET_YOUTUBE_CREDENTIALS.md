# 🔑 Get YouTube API Credentials (One-Time Setup)

Follow these steps to create `client_secrets.json`:

## Step 1: Create Google Cloud Project

1. Go to: **https://console.cloud.google.com**
2. Sign in with your **YouTube channel's Google account**
3. Click the project dropdown (top left) → **"New Project"**
4. Name: `Kids Channel Auto`
5. Click **Create**
6. Wait for project to be created, then select it

## Step 2: Enable YouTube Data API

1. Go to: **APIs & Services → Library**
   - Or visit: https://console.cloud.google.com/apis/library
2. Search: `YouTube Data API v3`
3. Click on it → Click **ENABLE**
4. Wait for it to enable (takes a few seconds)

## Step 3: Create OAuth Credentials

1. Go to: **APIs & Services → Credentials**
   - Or visit: https://console.cloud.google.com/apis/credentials
2. Click **"Create Credentials" → "OAuth 2.0 Client ID"**
3. If it asks to "Configure consent screen":
   - Click **"Configure Consent Screen"**
   - User Type: **"External"** → Click **Create**
   - App name: `Kids Channel Auto`
   - User support email: (your email)
   - Developer contact info: (your email)
   - Click **"Save and Continue"** (3 times)
   - Click **"Back to Dashboard"**
4. Now back at Credentials → Click **"Create Credentials" → "OAuth 2.0 Client ID"**
5. Application type: **"Desktop app"**
6. Name: `Desktop Client`
7. Click **Create**
8. Click **"Download JSON"**
9. **Rename the downloaded file to: `client_secrets.json`**
10. Move it to your `kids-channel-auto` folder

## Step 4: Run Authentication

Once you have `client_secrets.json` in your folder:

```bash
python3 auth_setup.py
```

This will:
- Open your browser
- Ask you to login with your YouTube channel
- Create `token.pickle` and `token_b64.txt`

## Step 5: Add Token to GitHub

1. Open `token_b64.txt`
2. Copy ALL the text (it's long!)
3. Go to: https://github.com/vgdine69-pixel/kids-channel-auto/settings/secrets/actions
4. Click **"New repository secret"**
5. Name: `YOUTUBE_TOKEN_B64`
6. Value: (paste the contents)
7. Click **Add secret**

## ✅ Done!

Your workflow will now upload videos automatically!

---

## Quick Reference Links

- Google Cloud Console: https://console.cloud.google.com
- YouTube Data API Library: https://console.cloud.google.com/apis/library/youtube.googleapis.com
- Credentials Page: https://console.cloud.google.com/apis/credentials
- GitHub Secrets: https://github.com/vgdine69-pixel/kids-channel-auto/settings/secrets/actions
