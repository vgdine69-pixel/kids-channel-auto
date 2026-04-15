# 📋 Step-by-Step Guide for viralview69@gmail.com

## Your Project
**Project ID:** `optimal-plate-487820-u3`
**Email:** `viralview69@gmail.com`

---

## Step 1: Enable YouTube API (2 minutes)

1. Go to: https://console.cloud.google.com/apis/library/youtube.googleapis.com?project=optimal-plate-487820-u3
2. Make sure you're logged in as `viralview69@gmail.com`
3. Click the blue **"ENABLE"** button
4. Wait for it to say "API Enabled"

**Done?** Type: `step 1 done`

---

## Step 2: Create OAuth Credentials (3 minutes)

1. Go to: https://console.cloud.google.com/apis/credentials?project=optimal-plate-487820-u3
2. Click **"Create Credentials"** (blue button at top)
3. Select **"OAuth 2.0 Client ID"**

### If you see "Configure Consent Screen":

4. Click **"Configure Consent Screen"**
5. Choose **"External"** → Click **Create**
6. Fill in:
   - App name: `Kids Channel Auto`
   - User support email: `viralview69@gmail.com`
   - Developer contact: `viralview69@gmail.com`
7. Click **"Save and Continue"** (3 times, skip optional stuff)
8. Click **"Back to Dashboard"**

### Create the Credentials:

9. Click **"Create Credentials" → "OAuth 2.0 Client ID"**
10. Application type: **"Desktop app"**
11. Name: `Desktop Client`
12. Click **Create**
13. Click **"Download JSON"**
14. Rename downloaded file to: `client_secrets.json`
15. Move it to your `kids-channel-auto` folder

**Done?** Type: `step 2 done`

---

## Step 3: Run Authentication (2 minutes)

On your computer, open terminal:

```bash
cd /path/to/kids-channel-auto
python3 auth_setup.py
```

This will:
- Open your browser
- Ask you to login with `viralview69@gmail.com`
- Click **"Allow"** when prompted
- Create `token_b64.txt` file

**Done?** Type: `step 3 done`

---

## Step 4: Add Token to GitHub (1 minute)

1. Open `token_b64.txt` file (in your kids-channel-auto folder)
2. Copy ALL the text (it's very long)
3. Go to: https://github.com/vgdine69-pixel/kids-channel-auto/settings/secrets/actions
4. Click **"New repository secret"**
5. Name: `YOUTUBE_TOKEN_B64`
6. Value: (paste the entire contents)
7. Click **Add secret**

**Done?** Type: `step 4 done`

---

## ✅ Finished!

Your videos will now upload automatically to YouTube!

**Test it:** Go to https://github.com/vgdine69-pixel/kids-channel-auto/actions and click "Run workflow"

---

## Need Help?

Tell me which step you're on and I'll help you through it!

Type:
- `help step 1` - YouTube API
- `help step 2` - OAuth credentials
- `help step 3` - Authentication
- `help step 4` - GitHub secret
