# Simple Checklist - Do These 4 Things

Print this or keep it open while you work.

---

## ☐ Step 1: Sign Up (3 min)

1. Go to: https://railway.app
2. Click "Login with GitHub"
3. Click "Authorize Railway"
4. ✅ Done when you see the Railway dashboard

---

## ☐ Step 2: Login CLI (2 min)

1. Open Terminal
2. Copy & paste:
   ```
   export PATH="$HOME/.railway:$PATH"
   railway login
   ```
3. Press Enter
4. Browser opens - click "Authorize"
5. ✅ Done when Terminal says "Successfully logged in"

---

## ☐ Step 3: Push to GitHub (5 min)

### Part 1: Create Repo
1. Go to: https://github.com/new
2. Name: `railway-apps`
3. DON'T check any boxes
4. Click "Create repository"

### Part 2: Push Code
1. In Terminal, paste (replace YOUR_USERNAME):
   ```
   cd /Users/john/railway-apps
   git remote add origin https://github.com/YOUR_USERNAME/railway-apps.git
   git branch -M main
   git push -u origin main
   ```
2. Enter GitHub username if asked
3. Enter token (NOT password) if asked
   - Get token: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Check "repo" box
   - Copy the token
   - Paste as password

4. ✅ Done when you see "Branch 'main' set up to track"

---

## ☐ Step 4: Deploy (2 min)

1. Go to: https://railway.app/dashboard
2. Click "New Project"
3. Click "Deploy from GitHub repo"
4. Click "railway-apps"
5. Wait 1-2 minutes
6. Click your app when done
7. Find the URL (looks like: `https://...railway.app`)
8. Click it
9. ✅ Done when you see "Welcome to your Railway API!"

---

## ✅ Success!

If you can visit your Railway URL and see a welcome message:
- **Your app is live 24/7!**
- **It runs even when your computer is off!**
- **You can create more apps anytime!**

---

## Quick Troubleshooting

**"railway: command not found"**
→ Run: `export PATH="$HOME/.railway:$PATH"`

**"Permission denied" on GitHub**
→ Use a token, not password: https://github.com/settings/tokens

**App won't start**
→ Check logs at: https://railway.app/dashboard → click your app → "Logs"

---

## Need detailed help?

Open: [SIMPLE_GUIDE.md](SIMPLE_GUIDE.md)
