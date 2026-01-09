# Super Simple Guide - No Tech Skills Needed

Follow these steps exactly. Copy and paste commands when you see them.

---

## Step 1: Sign Up for Railway (3 minutes)

### What to do:

1. **Open your web browser**
2. **Go to this website:** https://railway.app
3. **Look for a button that says "Login with GitHub"** - click it
4. **If you're not logged into GitHub:**
   - Enter your GitHub username and password
   - Click "Sign in"
5. **GitHub will ask if Railway can access your account:**
   - Click the green **"Authorize Railway"** button
6. **Done!** You're now on the Railway dashboard

**What you just did:** Created a free account where your apps will live 24/7

---

## Step 2: Login Railway CLI (2 minutes)

### What to do:

1. **Open Terminal on your Mac:**
   - Press `Command + Space`
   - Type "Terminal"
   - Press Enter

2. **Copy this command and paste it into Terminal:**
   ```bash
   export PATH="$HOME/.railway:$PATH"
   railway login
   ```

3. **Press Enter**

4. **Your web browser will open automatically**

5. **Click the button that says "Authorize"**

6. **You'll see "Successfully logged in" in Terminal**

**What you just did:** Connected the Railway tool to your Railway account

---

## Step 3: Create GitHub Repository (5 minutes)

### Part A: Create the Repository

1. **Go to:** https://github.com/new

2. **Where it says "Repository name":**
   - Type: `railway-apps`

3. **Leave everything else as default**
   - **IMPORTANT:** Do NOT check any boxes
   - Do NOT add README
   - Do NOT add .gitignore
   - Do NOT add license

4. **Click the green "Create repository" button**

5. **You'll see a page with instructions - IGNORE THEM for now**

### Part B: Push Your Code

1. **Go back to Terminal** (the window from Step 2)

2. **Copy ALL of these commands and paste them into Terminal:**

   **IMPORTANT:** Replace `YOUR_USERNAME` with your actual GitHub username!

   ```bash
   cd /Users/john/railway-apps
   git remote add origin https://github.com/YOUR_USERNAME/railway-apps.git
   git branch -M main
   git push -u origin main
   ```

3. **Press Enter**

4. **If Terminal asks for a username:**
   - Type your GitHub username
   - Press Enter

5. **If Terminal asks for a password:**
   - **DO NOT use your regular password!**
   - You need a "token" instead (see below)

### How to Get a GitHub Token (if needed):

1. **Open this link in your browser:** https://github.com/settings/tokens

2. **Click "Generate new token"** then **"Generate new token (classic)"**

3. **Where it says "Note":** Type `Railway Apps`

4. **Check the box that says "repo"** (this checks all the boxes under it)

5. **Scroll down and click the green "Generate token" button**

6. **You'll see a long code like:** `ghp_xxxxxxxxxxxxxxxxxxxx`

7. **Click the copy icon** (two squares) next to the token

8. **Go back to Terminal and paste this token** (instead of your password)

9. **Press Enter**

10. **You should see:** "Branch 'main' set up to track remote branch 'main'"

**What you just did:** Uploaded your code to GitHub so Railway can see it

---

## Step 4: Deploy Your First App (2 minutes)

### The Easy Way (Recommended):

1. **Go to:** https://railway.app/dashboard

2. **Click the purple "New Project" button**

3. **Click "Deploy from GitHub repo"**

4. **You'll see your repository "railway-apps":**
   - Click on it

5. **Railway will start deploying automatically!**
   - You'll see a bunch of logs scrolling (that's normal)
   - Wait about 1-2 minutes

6. **When it's done, you'll see "Success" or a checkmark**

7. **Click on your project**

8. **Look for a button or link that says "View Deployment" or shows a URL**
   - Click it

9. **Your app opens in a new tab!**
   - You should see: "Welcome to your Railway API!"

**What you just did:** Made your app live on the internet 24/7!

---

## ✅ How to Know It Worked

### You should be able to:

1. **See your app in Railway dashboard** at https://railway.app/dashboard
2. **Click on it and see it's "Active" or "Running"**
3. **Have a URL that looks like:** `https://starter-app-production-xxxx.railway.app`
4. **Visit that URL and see a welcome message**

### If you can do all that - **CONGRATULATIONS!** 🎉

Your app is now:
- ✅ Running 24/7 in the cloud
- ✅ Accessible from anywhere
- ✅ Working even when your computer is off

---

## What's Next?

### To create more apps:

1. **Open Terminal**

2. **Copy and paste this:**
   ```bash
   cd /Users/john/railway-apps
   ./scripts/create-app.sh my-first-app node-api
   ```

3. **This creates a new app in the `apps` folder**

4. **To deploy it, just repeat Step 4 above** and select your new app

---

## Common Problems & Solutions

### Problem: "railway: command not found"

**Solution:**
```bash
export PATH="$HOME/.railway:$PATH"
```
Then try your command again.

---

### Problem: GitHub asks for username and password but password doesn't work

**Solution:**
You need a token, not a password. Follow the "How to Get a GitHub Token" section above.

---

### Problem: "Permission denied (publickey)"

**Solution:**
GitHub needs a token. See the "How to Get a GitHub Token" section above.

---

### Problem: Railway says "No project found"

**Solution:**
1. Go to https://railway.app/dashboard
2. Use the web dashboard method instead (Step 4, "The Easy Way")

---

### Problem: App won't start or shows errors

**Solution:**
1. Go to https://railway.app/dashboard
2. Click on your app
3. Look for a "Logs" tab
4. Take a screenshot of the errors
5. The errors will tell you what's wrong

---

## Need Help?

### Where to get help:

1. **Railway Discord:** https://discord.gg/railway
   - Join and ask in #help channel
   - Very friendly and fast responses

2. **Check the logs:**
   - Go to Railway dashboard
   - Click your app
   - Click "Logs"
   - This shows what's happening

---

## Summary

**What you did:**
1. ✅ Created Railway account (your cloud hosting)
2. ✅ Logged in Railway CLI (connected the tool)
3. ✅ Pushed code to GitHub (uploaded your code)
4. ✅ Deployed to Railway (made it live 24/7)

**What you have now:**
- An app running 24/7 in the cloud
- A URL anyone can visit
- The ability to create unlimited more apps
- Everything running even when your computer is off

**Cost:**
- Free! ($5/month credit)
- Enough for 2-3 small apps
- No credit card needed

---

## 🎉 You're Done!

You now have apps running in the cloud! From here, you can:
- Create more apps using the templates
- Add databases with one click
- Make changes and they auto-deploy
- Build whatever you want!

**Everything works even when your Mac is asleep or turned off!**
