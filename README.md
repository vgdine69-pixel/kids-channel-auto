# 🌟 Kids Channel - 100% FREE Cloud Automation
### No Computer Needed • No Monthly Costs • Works Forever • 24/7 Automatic

---

## 💰 TOTAL COST = ₹0 / $0 FOREVER

| Service | Cost |
|---|---|
| GitHub (hosts & runs code) | **FREE** |
| Google Gemini AI (writes scripts) | **FREE** (1500 req/day) |
| YouTube Data API (uploads videos) | **FREE** (10,000 units/day) |
| gTTS Voice (text to speech) | **FREE** (no limit) |
| Animation (Python/PIL/MoviePy) | **FREE** (open source) |
| **TOTAL** | **₹0 / $0** |

---

## 🚀 COMPLETE SETUP GUIDE (Do This Once, Then NEVER Again!)

---

### 📋 STEP 1: Get Your FREE Gemini AI Key

1. Open: **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (looks like: `AIzaSy...`)
5. **Save it** — you'll need it in Step 5

✅ **FREE** — No credit card, no payment ever!

---

### 📋 STEP 2: Get Your FREE YouTube API Access

1. Open: **https://console.cloud.google.com**
2. Click the project dropdown → **"New Project"**
3. Name: `Kids Channel Auto` → Click **Create**
4. Go to: **APIs & Services → Library**
5. Search: `YouTube Data API v3` → Click it → Click **ENABLE**
6. Go to: **APIs & Services → Credentials**
7. Click: **Create Credentials → OAuth 2.0 Client ID**
8. Application type: **Desktop App** → Name it → **Create**
9. Click **DOWNLOAD JSON** → Save as `client_secrets.json`

✅ **FREE** — YouTube gives 10,000 units/day (you need ~6,400 for 4 uploads)

---

### 📋 STEP 3: Create FREE GitHub Account & Repository

1. Go to: **https://github.com** → Sign Up (free)
2. Click **"New Repository"**
3. Name: `kids-channel-auto`
4. Set to: **Public** ← IMPORTANT (makes GitHub Actions unlimited free!)
5. Click **Create Repository**
6. Note your repo URL: `https://github.com/YOUR_USERNAME/kids-channel-auto`

✅ **FREE** — Public repos get UNLIMITED GitHub Actions minutes!

---

### 📋 STEP 4: Upload Code to GitHub

**Option A: GitHub Website (Easiest)**
1. Open your repository on GitHub
2. Click **"uploading an existing file"** or **"Add file"**
3. Drag and drop ALL files from this folder
4. Click **Commit changes**

**Option B: Git (if you know it)**
```bash
git init
git add .
git commit -m "Kids channel automation"
git remote add origin https://github.com/YOUR_USERNAME/kids-channel-auto
git push -u origin main
```

---

### 📋 STEP 5: Run One-Time YouTube Login (Last Time on Computer!)

You need to do this **just ONCE** on your computer.

1. Install Python from **python.org** (if not installed)
2. Double-click **`SETUP_AUTH.bat`** (or run: `python auth_setup.py`)
3. It will install needed packages automatically
4. **Your browser opens** → Login with your **YouTube channel Google account**
5. Click **Allow**
6. Done! It creates `token_b64.txt`

---

### 📋 STEP 6: Add Secrets to GitHub (Your API Keys)

Go to your GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**

Add these 6 secrets one by one:

| Secret Name | Value | Where to get it |
|---|---|---|
| `GEMINI_API_KEY` | Your Gemini key | From Step 1 |
| `YOUTUBE_TOKEN_B64` | Contents of `token_b64.txt` | Created in Step 5 |
| `CHANNEL_NAME` | Your channel name | e.g. `Wonder Kids World` |
| `YOUTUBE_CLIENT_ID` | From client_secrets.json | Open file, copy `client_id` value |
| `YOUTUBE_CLIENT_SECRET` | From client_secrets.json | Open file, copy `client_secret` value |
| `GH_PAT` | GitHub Personal Token | github.com → Settings → Developer Settings → Personal Access Tokens → Generate new token (classic) → check `repo` scope |

---

### 📋 STEP 7: Enable GitHub Actions

1. Go to your repo → **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**
3. You'll see **"Kids Channel Upload"** workflow listed

---

### ✅ DONE! Everything Runs Automatically!

**What happens now:**
- Every day at **6:00 AM, 11:00 AM, 4:00 PM, 8:00 PM** (IST):
  - GitHub's FREE servers wake up
  - AI generates a kids story script
  - Animates the video with characters
  - Creates 3D thumbnail
  - Uploads to YouTube with SEO
  - Goes back to sleep
- You do NOTHING. Forever.

---

## 🎯 HOW TO MANUALLY TRIGGER AN UPLOAD

1. Go to your GitHub repo → **Actions** tab
2. Click **"Kids Channel Upload"**
3. Click **"Run workflow"** button (top right)
4. Select video type (or leave as "auto")
5. Click **Run workflow** → Video uploads in ~30-60 minutes

---

## 📊 WATCHING YOUR RESULTS

**See upload logs:**
1. GitHub → Actions tab → Click latest run
2. Click **"create_and_upload"** job
3. See every step with real-time logs

**Download thumbnail:**
1. GitHub → Actions → Latest run
2. Scroll down to **Artifacts**
3. Download `video-log-XXX` → includes thumbnails

---

## 🔄 HOW TO CHANGE YOUR CHANNEL NAME OR SCHEDULE

**Change channel name:**
- GitHub → Settings → Secrets → Click `CHANNEL_NAME` → Update

**Change upload times:**
- GitHub → your repo → `.github/workflows/upload.yml`
- Edit the cron times (UTC = IST - 5:30)

Current schedule (IST → UTC):
```
6:00 AM IST  = 00:30 UTC  → cron: "30 0 * * *"
11:00 AM IST = 05:30 UTC  → cron: "30 5 * * *"
4:00 PM IST  = 10:30 UTC  → cron: "30 10 * * *"
8:00 PM IST  = 14:30 UTC  → cron: "30 14 * * *"
```

---

## ❓ TROUBLESHOOTING

| Problem | Solution |
|---|---|
| "GEMINI_API_KEY not set" | Check spelling in GitHub Secrets |
| "YouTube auth token missing" | Re-run `auth_setup.py`, update `YOUTUBE_TOKEN_B64` secret |
| Workflow doesn't run | Check Actions tab is enabled; public repo required for free |
| Video too slow | GitHub Actions gives 2 CPU cores — videos take 20-60 min |
| Upload fails with quota | YouTube free limit: 6 uploads/day max |
| "token expired" | Re-run `auth_setup.py`, upload new `YOUTUBE_TOKEN_B64` |

---

## 📱 FREE VIDEO TYPES (Auto-Rotated Daily)

| Type | % Chance | Example Topics |
|---|---|---|
| 🧚 Fairy Tale Story | 25% | "The Brave Little Bunny" |
| 📚 Learning Video | 20% | "Amazing Facts About Space" |
| 🧠 Brain Boost | 15% | "5 Tricky Riddles for Kids" |
| 💪 Motivational | 15% | "The Boy Who Never Gave Up" |
| 🌈 Good Habits | 15% | "Why We Brush Our Teeth" |
| 🗺️ Adventure Story | 10% | "Dragon Mountain Quest" |

---

## 🌟 SEO FEATURES (Auto-Applied to Every Video)

- ✅ Power-word optimized title (40-60 chars)
- ✅ 300+ word keyword-rich description
- ✅ YouTube chapter timestamps
- ✅ 20 targeted tags (broad + long-tail)
- ✅ 15 trending kids hashtags
- ✅ Education category (ID 27)
- ✅ Pinned first comment for engagement
- ✅ Kids-specific 2025 trending keywords

---

*100% Free • Cloud-Powered • Zero Maintenance • Forever Automatic 🚀*
