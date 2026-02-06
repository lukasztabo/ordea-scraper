# 🍽️ Ordea Meal Scraper - GitHub Actions Setup

Automatically scrape meal data from Ordea.net every day at 6:00 AM and send it to your TrueNAS API for Home Assistant.

## 🚀 Quick Setup (10 minutes)

### Step 1: Create GitHub Account (if you don't have one)
1. Go to https://github.com
2. Click "Sign up" (it's free)
3. Follow the registration steps

### Step 2: Create a New Repository
1. Log in to GitHub
2. Click the **"+"** button (top right) → **"New repository"**
3. Fill in:
   - **Repository name**: `ordea-scraper` (or any name you want)
   - **Description**: "Automated meal scraper for Ordea.net"
   - **Visibility**: ✅ **Private** (keep it private for security)
   - ✅ Check "Add a README file"
4. Click **"Create repository"**

### Step 3: Upload Files

You have two options:

#### Option A: Upload via Web Interface (Easiest)

1. In your new repository, click **"Add file"** → **"Upload files"**

2. Upload these files from `/mnt/tank/ordea/github-actions/`:
   - `ordea_scraper.py`
   - `requirements.txt`

3. Click **"Add file"** → **"Create new file"**

4. Name it: `.github/workflows/scrape-meals.yml`

5. Copy the contents from `/mnt/tank/ordea/github-actions/.github/workflows/scrape-meals.yml`

6. Click **"Commit changes"**

#### Option B: Use Git (Advanced)

```bash
# On your computer or TrueNAS
cd /mnt/tank/ordea/github-actions
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ordea-scraper.git
git push -u origin main
```

### Step 4: Add Secrets (IMPORTANT!)

1. In your GitHub repository, click **"Settings"** (top menu)

2. In the left sidebar, click **"Secrets and variables"** → **"Actions"**

3. Click **"New repository secret"** and add these **3 secrets**:

   **Secret 1:**
   - Name: `ORDEA_EMAIL`
   - Value: `taborski.l@gmail.com`
   - Click "Add secret"

   **Secret 2:**
   - Name: `ORDEA_PASSWORD`
   - Value: `Ordea123#`
   - Click "Add secret"

   **Secret 3:**
   - Name: `TRUENAS_URL`
   - Value: `http://192.168.68.119:3010/api/update`
   - Click "Add secret"

   ⚠️ **Important**: Replace `192.168.68.119` with your actual TrueNAS IP if different!

### Step 5: Test It!

1. Go to **"Actions"** tab in your repository

2. Click on **"Scrape Ordea Meals"** in the left sidebar

3. Click **"Run workflow"** button (right side)

4. Click the green **"Run workflow"** button in the dropdown

5. Wait 2-3 minutes and click on the running job to see the logs

6. You should see:
   ```
   ✅ Logged in!
   ✅ Extracted meals for Łucja Taborska
   ✅ Extracted meals for Wiktoria Taborska
   ✅ Successfully sent to TrueNAS!
   ```

### Step 6: Verify in Home Assistant

1. Go to your Home Assistant

2. Check Developer Tools → States

3. Look for your Ordea meal sensors

4. They should now show the scraped meal data!

---

## ⏰ Automatic Schedule

The scraper will now run **automatically every day at 6:00 AM** (Warsaw time).

You don't need to do anything - it just works! 🎉

---

## 🔧 How to Change the Schedule

Edit `.github/workflows/scrape-meals.yml` and change the cron line:

```yaml
schedule:
  - cron: '0 5 * * *'  # This is 6:00 AM Warsaw time
```

**Cron examples:**
- `'0 5 * * *'` = 6:00 AM every day (5 AM UTC = 6 AM CET)
- `'0 7 * * *'` = 8:00 AM every day
- `'0 4 * * 1-5'` = 5:00 AM on weekdays only
- `'0 */12 * * *'` = Every 12 hours

Use https://crontab.guru/ to create your schedule!

---

## 🐛 Troubleshooting

### "Workflow not running"
- Check the "Actions" tab for errors
- Make sure all 3 secrets are set correctly
- Try clicking "Run workflow" manually

### "Login failed"
- Verify your ORDEA_EMAIL and ORDEA_PASSWORD secrets
- Check if your Ordea.net credentials still work

### "TrueNAS connection failed"
- Verify TRUENAS_URL secret is correct
- Check your TrueNAS IP address
- Make sure port 3010 is accessible
- Test: `curl http://192.168.68.119:3010/health`

### "No data extracted"
- Click on the failed job in Actions tab
- Read the logs to see what went wrong
- May be a temporary Ordea.net issue - try manual run

---

## 📊 Monitoring

**View logs:**
1. Go to "Actions" tab
2. Click on any workflow run
3. Click "scrape" job
4. Expand steps to see detailed logs

**Download data:**
- Each run saves `meals.json` as an artifact
- Available in "Artifacts" section at the bottom of each run
- Kept for 7 days

---

## 🔒 Security

✅ **Your repository is private** - only you can see it
✅ **Secrets are encrypted** - GitHub never shows them
✅ **No credentials in code** - everything uses secrets
✅ **Safe to share logs** - no sensitive data exposed

---

## 💰 Cost

**FREE FOREVER!** 🎉

- GitHub Actions free tier: 2,000 minutes/month
- This script uses: ~3 minutes/day = 90 minutes/month
- You have plenty of free time left!

---

## 🎯 What Happens Now

Every day at 6:00 AM:
1. ⏰ GitHub Actions wakes up
2. 🤖 Runs your script in the cloud
3. 🔐 Logs into Ordea.net
4. 📋 Gets meals for both kids
5. 📤 Sends data to TrueNAS
6. 🏠 Home Assistant shows updated meals
7. 😴 Goes back to sleep

**Zero effort. Fully automatic. Forever free.** ✨

---

## 📞 Support

If something doesn't work:
1. Check the Actions tab logs
2. Verify all secrets are set
3. Test TrueNAS API manually: `curl http://192.168.68.119:3010/health`

---

## 🎉 You're Done!

Your meal scraper is now running automatically in the cloud, sending data to TrueNAS, and feeding your Home Assistant dashboard.

Enjoy! 🍕🥗🍰
