# Troubleshooting Guide

> **Don't panic!** Most problems have simple solutions.

---

## Quick Diagnostic

**First, ask yourself:**
1. Did it work before? What changed?
2. Are there any error messages?
3. Did I save and commit my changes?
4. Did I check the logs?

---

## Common Problems & Solutions

### 1. Deployment Failed

**Symptoms:** Railway shows red/failed status, build errors

**Check Build Logs:**
1. Go to Railway Dashboard
2. Click on your project
3. Click on your service
4. Go to "Deployments" tab
5. Click on failed deployment
6. Read the error message

**Common Causes:**

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError` | Add missing package to `requirements.txt` |
| `SyntaxError` | Fix the syntax error in your code |
| `No module named 'x'` | Run `pip install x` and add to requirements.txt |
| `Invalid requirement` | Check `requirements.txt` for typos |
| `Build timeout` | Simplify dependencies or contact Railway |

**Fix Missing Module:**
```bash
# Add to requirements.txt
echo "package-name==1.0.0" >> requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Add missing dependency"
git push
```

---

### 2. App Crashes on Startup

**Symptoms:** Deploys but immediately crashes, restarts repeatedly

**Check Runtime Logs:**
1. Railway Dashboard > Your Service > Logs
2. Look for error messages

**Common Causes:**

| Error | Solution |
|-------|----------|
| `Port already in use` | Make sure code uses `PORT` env var |
| `Missing env variable` | Add missing variable in Railway dashboard |
| `Connection refused` | Check database/API connections |
| `Memory limit` | Optimize code or upgrade Railway plan |

**Fix Port Issues:**
```python
# In app.py, make sure you have:
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

---

### 3. Emails Not Sending

**Symptoms:** App runs but no emails received

**Checklist:**
- [ ] Check spam folder
- [ ] Verify `SENDER_EMAIL` is correct
- [ ] Verify `SENDER_PASSWORD` is an App Password (not regular password)
- [ ] Verify `RECIPIENT_EMAIL` is correct
- [ ] Check Railway logs for email errors

**Gmail App Password Setup:**
1. Go to Google Account > Security
2. Enable 2-Factor Authentication
3. Go to App Passwords
4. Generate new password for "Mail"
5. Use this password in `SENDER_PASSWORD`

**Test Email Manually:**
```bash
curl https://your-app.railway.app/test-email
```

---

### 4. Scraper Not Finding Content

**Symptoms:** Empty results, missing news items

**Common Causes:**

| Issue | Solution |
|-------|----------|
| Website changed layout | Update scraper selectors |
| Rate limited | Add delays between requests |
| Blocked by website | Add user agent, use different approach |
| RSS feed moved | Update feed URL in `news_sources.json` |

**Debug Scraping:**
```bash
# Test scraper locally
python scraper.py

# Check specific source
python -c "from scraper import scrape_source; print(scrape_source('Source Name'))"
```

---

### 5. Schedule Not Working

**Symptoms:** Emails not sent at expected time

**Checklist:**
- [ ] Is `SCHEDULE_TIME` set correctly? (24-hour format: "07:00")
- [ ] Is timezone correct? (Railway uses UTC by default)
- [ ] Is the app actually running?

**Time Zone Fix:**
```bash
# In Railway dashboard, add:
TZ=America/New_York  # or your timezone
```

**Common Timezones:**
- `UTC` - Coordinated Universal Time
- `America/New_York` - Eastern US
- `America/Los_Angeles` - Pacific US
- `Europe/London` - UK
- `Europe/Paris` - Central Europe
- `Asia/Tokyo` - Japan

**Check Current Time in App:**
```bash
curl https://your-app.railway.app/status
```

---

### 6. Git Push Rejected

**Symptoms:** `git push` fails with error

**Error: "Permission denied"**
```bash
# Check if SSH key is set up
ssh -T git@github.com

# If not, use HTTPS instead
git remote set-url origin https://github.com/username/repo.git
```

**Error: "Updates were rejected"**
```bash
# Someone else pushed changes - pull first
git pull origin main

# Then push again
git push origin main
```

**Error: "Merge conflict"**
```bash
# Open conflicted files, look for:
# <<<<<<< HEAD
# your changes
# =======
# their changes
# >>>>>>> branch

# Edit to keep what you want, remove markers
# Then:
git add .
git commit -m "Resolve merge conflict"
git push
```

---

### 7. Environment Variables Not Working

**Symptoms:** App can't find config values

**Checklist:**
- [ ] Variable name matches exactly (case-sensitive!)
- [ ] No extra spaces around `=` sign
- [ ] Value doesn't have quotes (unless needed)
- [ ] Variable is saved in Railway dashboard

**Debug Env Vars:**
```python
# Add to your app.py temporarily:
import os
print("SENDER_EMAIL:", os.environ.get('SENDER_EMAIL', 'NOT SET'))
print("All env vars:", list(os.environ.keys()))
```

**Common Mistakes:**
```bash
# Wrong (extra spaces)
SENDER_EMAIL = test@email.com

# Wrong (quotes included as value)
SENDER_EMAIL="test@email.com"

# Correct
SENDER_EMAIL=test@email.com
```

---

### 8. Local App Works, Production Doesn't

**Symptoms:** Works on your computer but fails on Railway

**Common Causes:**

| Issue | Solution |
|-------|----------|
| Different Python version | Add `runtime.txt` with `python-3.11.0` |
| Missing env vars | Add all env vars to Railway |
| Hardcoded localhost | Use env vars for URLs |
| File path issues | Use relative paths or env vars |

**Check Python Version:**
```bash
# Create runtime.txt
echo "python-3.11.0" > runtime.txt
git add runtime.txt
git commit -m "Specify Python version"
git push
```

---

### 9. "Internal Server Error"

**Symptoms:** App returns 500 error

**Debug Steps:**
1. Check Railway logs immediately
2. Look for the stack trace
3. Find the line number causing the error

**Common Fixes:**
```python
# Add better error handling
@app.route('/endpoint')
def endpoint():
    try:
        # your code
        return result
    except Exception as e:
        print(f"Error: {e}")  # This shows in logs
        return {"error": str(e)}, 500
```

---

### 10. Can't Access Railway Dashboard

**Symptoms:** Can't log in, page won't load

**Solutions:**
1. Clear browser cache
2. Try incognito/private window
3. Try different browser
4. Check [Railway Status](https://status.railway.app/)
5. Wait and try again (might be temporary outage)

---

## Emergency Recovery

### "I broke everything!"

```bash
# Option 1: Undo last commit
git reset --soft HEAD~1
git checkout -- .

# Option 2: Go back to working version
git log --oneline  # Find the good commit hash
git checkout <commit-hash>

# Option 3: Start fresh from main
git checkout main
git pull origin main
```

### "I deleted important files!"

```bash
# If not committed yet:
git checkout -- deleted_file.py

# If committed:
git log --oneline  # Find commit before deletion
git checkout <commit-hash> -- deleted_file.py
```

### "I pushed secrets to GitHub!"

1. **Immediately** rotate the exposed credentials
2. Remove from code:
   ```bash
   git rm --cached .env  # If you committed .env
   git commit -m "Remove secrets"
   git push
   ```
3. Consider the secret compromised - change passwords!

---

## Where to Get Help

### Check Logs First
```bash
# Railway: Dashboard > Service > Logs

# Local:
python app.py 2>&1 | tee debug.log
```

### Search for Error Message
- Copy the exact error message
- Search on Google or Stack Overflow
- Check Railway Discord community

### Ask for Help
1. Railway Discord: [discord.gg/railway](https://discord.gg/railway)
2. GitHub Issues: Create issue on your repo
3. Stack Overflow: Tag with relevant technologies

### When Asking for Help, Include:
- Exact error message
- What you were trying to do
- What you already tried
- Relevant code snippets
- Railway logs (screenshot or copy)

---

## Preventive Measures

### Avoid Future Problems:

1. **Always test locally first**
2. **Commit often** (small changes are easier to debug)
3. **Read error messages carefully**
4. **Keep backups** (git branches are free!)
5. **Don't edit production directly**

### Good Habits:
```bash
# Before making changes:
git checkout -b my-feature-backup

# After testing locally:
git add .
git commit -m "Feature: description"

# Before pushing to production:
# Test one more time!
```

---

## Quick Fixes Reference

| Problem | Quick Fix |
|---------|-----------|
| Module not found | Add to requirements.txt, redeploy |
| Port error | Use `os.environ.get('PORT', 5000)` |
| Env var missing | Add in Railway dashboard |
| Email not sending | Check App Password, not regular password |
| Wrong timezone | Add `TZ=Your/Timezone` env var |
| Push rejected | `git pull` first, then push |
| App crashing | Check logs for error message |

---

*Remember: Every developer faces these issues. You've got this!*
