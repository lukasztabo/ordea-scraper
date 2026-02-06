# 🚀 QUICKSTART - 5 Steps to Automatic Meal Updates

## ✅ What You Have

All files are ready in: `/mnt/tank/ordea/github-actions/`

```
github-actions/
├── ordea_scraper.py              ← Your working script
├── requirements.txt               ← Dependencies
├── .github/workflows/
│   └── scrape-meals.yml          ← Automation schedule
├── .gitignore                     ← Git ignore file
├── README.md                      ← Full documentation
└── QUICKSTART.md                  ← This file
```

---

## 📋 5 Simple Steps

### 1️⃣ Create GitHub Account (2 minutes)
- Go to https://github.com/signup
- Create free account
- Verify email

### 2️⃣ Create Repository (1 minute)
- Click **"+"** → **"New repository"**
- Name: `ordea-scraper`
- ✅ Make it **Private**
- ✅ Check "Add README"
- Click **"Create repository"**

### 3️⃣ Upload Files (2 minutes)
- Click **"Add file"** → **"Upload files"**
- Drag and drop:
  - `ordea_scraper.py`
  - `requirements.txt`
- Click **"Commit changes"**

Then:
- Click **"Add file"** → **"Create new file"**
- Name: `.github/workflows/scrape-meals.yml`
- Copy content from the file
- Click **"Commit changes"**

### 4️⃣ Add Secrets (3 minutes)
In your repository:
- Click **"Settings"**
- **"Secrets and variables"** → **"Actions"**
- Click **"New repository secret"** (3 times):

```
Name: ORDEA_EMAIL
Value: taborski.l@gmail.com
```

```
Name: ORDEA_PASSWORD
Value: Ordea123#
```

```
Name: TRUENAS_URL
Value: http://192.168.68.119:3010/api/update
```

### 5️⃣ Test It! (2 minutes)
- Go to **"Actions"** tab
- Click **"Run workflow"** button
- Watch it run (2-3 minutes)
- See ✅ success!

---

## 🎉 Done!

Now it runs **automatically every day at 6:00 AM**.

Check Home Assistant to see your meals! 🍽️

---

## 📖 Need More Help?

Read the full **README.md** for:
- Detailed troubleshooting
- How to change the schedule
- Monitoring and logs
- Security info

---

## ⚡ Super Quick Test

Want to test immediately?

1. Go to repository → **Actions** tab
2. Click **"Scrape Ordea Meals"**
3. Click **"Run workflow"**
4. Wait 2-3 minutes
5. Check logs ✅
6. Check Home Assistant ✅

**That's it!** 🚀
