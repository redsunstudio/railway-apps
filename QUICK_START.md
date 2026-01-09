# Quick Start - Get Your First App Running in 5 Minutes

Follow these steps to deploy your first always-on app to Railway.

## Step 1: Sign Up for Railway (2 minutes)

1. Go to https://railway.app
2. Click "Login with GitHub" (easiest option)
3. Authorize Railway to access your GitHub
4. That's it! You get $5 free credit monthly (no credit card needed)

## Step 2: Install Railway CLI (1 minute)

```bash
npm install -g @railway/cli
```

Then login:
```bash
railway login
```

This opens a browser - click "Authorize" and you're done!

## Step 3: Test the Starter App Locally (1 minute)

```bash
cd /Users/john/railway-apps/apps/starter-app
npm install
npm start
```

Visit http://localhost:3000 - you should see a welcome message!

Press Ctrl+C to stop.

## Step 4: Push to GitHub (2 minutes)

Railway needs your code on GitHub to deploy it.

```bash
# Go to the main directory
cd /Users/john/railway-apps

# Initialize git
git init
git add .
git commit -m "Initial setup with starter app"

# Create a new repo on GitHub called "railway-apps"
# Then connect and push:
git remote add origin https://github.com/YOUR_USERNAME/railway-apps.git
git push -u origin main
```

## Step 5: Deploy to Railway (1 minute)

### Option A: Using Dashboard (Recommended First Time)

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `railway-apps` repository
5. Railway automatically detects and deploys the starter-app!

### Option B: Using CLI (Faster)

```bash
cd /Users/john/railway-apps/apps/starter-app
railway init
railway up
```

## Step 6: View Your Live App

Railway gives you a URL like: `https://starter-app-production-xxxx.railway.app`

To open it:
```bash
railway open
```

Or test with curl:
```bash
curl https://your-app-url.railway.app/health
```

## You're Done! 🎉

Your app is now running 24/7 in the cloud, even when your computer is off!

## What's Next?

### Option 1: Create a New App from Template
```bash
cd /Users/john/railway-apps
./scripts/create-app.sh my-first-api node-api
cd apps/my-first-api
npm install
# Edit code as needed
railway init
railway up
```

### Option 2: Customize the Starter App
```bash
cd /Users/john/railway-apps/apps/starter-app
# Edit index.js to add your own endpoints
# Commit and push - Railway auto-deploys!
git add .
git commit -m "Added new features"
git push
```

### Option 3: Add a Database
```bash
cd /Users/john/railway-apps/apps/starter-app
railway add postgresql
# Database URL is now available as process.env.DATABASE_URL
```

## Useful Commands

```bash
# View logs
railway logs

# Check app status
railway status

# View all your apps
railway list

# Open app in browser
railway open

# Set environment variables
railway variables set API_KEY=secret123

# Check your usage/billing
railway billing
```

## Troubleshooting

**"railway: command not found"**
- Run: `npm install -g @railway/cli`
- Or install globally: `curl -fsSL https://railway.app/install.sh | sh`

**App won't deploy**
- Check Railway dashboard for error messages
- Run `railway logs` to see what went wrong
- Ensure package.json has a "start" script

**Can't push to GitHub**
- Make sure you created the repo on GitHub first
- Check you're using the correct repository URL
- Try: `git remote -v` to verify remote

**Railway asks for payment**
- You get $5 free per month
- No credit card needed for free tier
- Small apps usually stay within free tier

## Need Help?

- Read the full guide: [README.md](README.md)
- Railway documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

---

**Ready to build?** All your future apps follow the same pattern:
1. Create app (from template or scratch)
2. Push to GitHub
3. Deploy to Railway
4. App runs forever!
