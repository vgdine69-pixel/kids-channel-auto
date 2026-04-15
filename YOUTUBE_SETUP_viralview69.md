# 🔑 YouTube API Setup for viralview69@gmail.com

## Important: Use This Email
**Login with:** `viralview69@gmail.com`

This is your YouTube channel account. All credentials must be created with this email.

---

## Step 1: Create Google Cloud Project

1. Go to: **https://console.cloud.google.com**
2. **Sign in with:** `viralview69@gmail.com`
3. Click project dropdown (top left) → **"New Project"**
4. Name: `Kids Channel Auto`
5. Click **Create**
6. Wait for project to create, then select it

---

## Step 2: Enable YouTube Data API

1. Go to: https://console.cloud.google.com/apis/library/youtube.googleapis.com
2. Make sure you're signed in as `viralview69@gmail.com`
3. Click **ENABLE**
4. Wait for it to enable

---

## Step 3: Create OAuth Credentials

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **"Create Credentials" → "OAuth 2.0 Client ID"**

### If you see "Configure Consent Screen":

1. Click **"Configure Consent Screen"**
2. User Type: **"External"** → Click **Create**
3. Fill in:
   - **App name:** `Kids Channel Auto`
   - **User support email:** `viralview69@gmail.com`
   - **Developer contact:** `viralview69@gmail.com`
4. Click **"Save and Continue"** (3 times)
5. Click **"Back to Dashboard"**

### Back to Credentials:

1. Click **"Create Credentials" → "OAuth 2.0 Client ID"**
2. Application type: **"Desktop app"**
3. Name: `Desktop Client`
4. Click **Create**
5. Click **"Download JSON"**
6. **Rename file to:** `client_secrets.json`
7. Move to your `kids-channel-auto` folder

---

## Step 4: Run Authentication Script

In terminal (on your computer):

```bash
cd /path/to/kids-channel-auto
python3 auth_setup.py
```

This will:
- Open browser
- Login with `viralview69@gmail.com`
- Click **Allow** when prompted
- Create `token.pickle` and `token_b64.txt`

---

## Step 5: Add Token to GitHub Secrets

1. Open `token_b64.txt` file
2. **Copy ALL the text** (it's very long - base64 encoded)
3. Go to: https://github.com/vgdine69-pixel/kids-channel-auto/settings/secrets/actions
4. Click **"New repository secret"**
5. Name: `YOUTUBE_TOKEN_B64`
6. Value: (paste the entire contents from token_b64.txt)
7. Click **Add secret**

---

## ✅ Done!

Once you add `YOUTUBE_TOKEN_B64` to GitHub, your videos will upload automatically!

---

## Quick Links

| Task | URL |
|------|-----|
| Google Cloud Console | https://console.cloud.google.com |
| Enable YouTube API | https://console.cloud.google.com/apis/library/youtube.googleapis.com |
| Create Credentials | https://console.cloud.google.com/apis/credentials |
| GitHub Secrets | https://github.com/vgdine69-pixel/kids-channel-auto/settings/secrets/actions |
| View Workflow Runs | https://github.com/vgdine69-pixel/kids-channel-auto/actions |

---

## Troubleshooting

**"This app isn't verified" warning:**
- Click **"Advanced"**
- Click **"Go to Kids Channel Auto (unsafe)"**
- Click **Allow**
- This is normal for personal projects

**Token expires after 7 days?**
- Go to https://console.cloud.google.com/apis/credentials/consent
- Click **"PUBLISH APP"** (moves from "Testing" to "In production")
- No verification needed for personal use
