# Railway Apps - Multi-App Hosting Infrastructure

This directory contains all your Railway-hosted applications that run 24/7 in the cloud.

## Quick Start Guide

### One-Time Setup (5 minutes)

1. **Sign up for Railway**
   - Go to https://railway.app
   - Click "Login with GitHub" (recommended) or "Sign up"
   - No credit card required for free tier ($5/month credit)

2. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

3. **Login to Railway**
   ```bash
   railway login
   ```
   This opens a browser window - click "Authorize" and you're done!

4. **Initialize Git** (if not already done)
   ```bash
   cd railway-apps
   git init
   git add .
   git commit -m "Initial setup"
   ```

5. **Push to GitHub** (Railway needs this)
   - Create a new repo on GitHub called "railway-apps"
   - Run:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/railway-apps.git
   git push -u origin main
   ```

---

## Deploying Your First App

### Option 1: Using Railway Dashboard (Easiest)
1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `railway-apps` repository
5. Railway auto-detects and deploys!

### Option 2: Using CLI (Fastest for multiple apps)
```bash
cd railway-apps/apps/your-app-name
railway init
railway up
```

---

## Directory Structure

```
railway-apps/
├── apps/                    # All your individual apps
│   ├── starter-app/        # Example Node.js API (ready to deploy!)
│   └── your-next-app/      # Add more apps here
├── templates/              # Reusable templates for new apps
│   ├── node-api/          # Node.js/Express API template
│   ├── python-api/        # Python/Flask API template
│   └── nextjs-app/        # Next.js full-stack template
└── scripts/               # Deployment automation scripts
```

---

## Creating a New App

### Method 1: Copy a Template
```bash
cd railway-apps/apps
cp -r ../templates/node-api my-new-app
cd my-new-app
npm install
# Edit code as needed
railway init
railway up
```

### Method 2: Use the Creation Script
```bash
cd railway-apps
./scripts/create-app.sh my-new-app node-api
```

---

## Managing Multiple Apps

### View All Deployments
```bash
railway list
```

### Switch Between Apps
```bash
railway link
# Then select your app from the list
```

### Check App Status
```bash
railway status
```

### View Logs
```bash
railway logs
```

### Open App in Browser
```bash
railway open
```

---

## Adding Databases

Railway makes databases incredibly easy:

1. **Via Dashboard:**
   - Open your project on railway.app
   - Click "New" → "Database"
   - Choose: PostgreSQL, MySQL, Redis, or MongoDB
   - Railway automatically creates connection variables

2. **Via CLI:**
   ```bash
   railway add
   # Select database type
   ```

3. **Access Database URL:**
   - Automatically available as environment variable
   - PostgreSQL: `DATABASE_URL`
   - Redis: `REDIS_URL`
   - MySQL: `MYSQL_URL`

---

## Environment Variables

### Set Variables via CLI
```bash
railway variables set KEY=VALUE
railway variables set API_KEY=your-secret-key
```

### Set Variables via Dashboard
1. Open project on railway.app
2. Go to "Variables" tab
3. Add your variables

### Access in Your Code
```javascript
// Node.js
const apiKey = process.env.API_KEY;
```

```python
# Python
import os
api_key = os.getenv('API_KEY')
```

---

## Pricing Guide

### Free Tier
- $5 usage credit per month (no credit card needed)
- Enough for 2-3 small apps running 24/7
- Resets monthly

### What Uses Credits
- **RAM:** ~$0.000231 per GB-hour
- **CPU:** Minimal cost for small apps
- **Bandwidth:** Included

### Cost Examples
- Small Node.js API (512MB RAM): ~$3-4/month
- Medium app with database (1GB RAM): ~$7-10/month
- 3 small apps: ~$10-15/month total

### Monitor Usage
- Dashboard shows real-time costs
- Set up billing alerts
- View usage: `railway billing`

---

## Common Commands Cheat Sheet

```bash
# Deploy current directory
railway up

# View logs (live)
railway logs

# Open app in browser
railway open

# Run command in Railway environment
railway run node index.js

# Connect to database
railway connect postgres

# View all environment variables
railway variables

# Delete deployment (careful!)
railway down
```

---

## Troubleshooting

### App Won't Start
1. Check logs: `railway logs`
2. Verify `start` script in package.json
3. Ensure PORT environment variable is used:
   ```javascript
   const PORT = process.env.PORT || 3000;
   ```

### Database Connection Issues
1. Check variables: `railway variables`
2. Ensure `DATABASE_URL` is being read
3. Check database is running in Railway dashboard

### Deploy Not Working
1. Ensure code is pushed to GitHub
2. Check Railway is watching correct branch
3. Look for build errors in dashboard

---

## Best Practices

1. **Use Environment Variables** - Never hardcode secrets
2. **Enable Health Checks** - Add `/health` endpoint
3. **Log Important Events** - Railway captures stdout
4. **Use Git Tags** - For versioning deployments
5. **Monitor Costs** - Check dashboard weekly
6. **Backup Databases** - Railway has auto-backups, but export critical data

---

## Next Steps

1. ✅ Complete one-time setup above
2. ✅ Deploy the included `starter-app` to test
3. ✅ Create your first real app using templates
4. ✅ Add a database if needed
5. ✅ Set up custom domain (optional, in Railway dashboard)

---

## Getting Help

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check logs first: `railway logs`

---

**You're all set!** Once you complete the one-time setup above, you can deploy unlimited apps. Each new app is just a `railway up` command away from running 24/7 in the cloud.
