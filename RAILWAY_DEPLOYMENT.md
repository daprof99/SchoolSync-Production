# 🚂 Railway Deployment Guide - SchoolSync 2.0

Complete step-by-step guide to deploy SchoolSync to production on Railway.app

---

## 📋 **Prerequisites**

Before you start, ensure you have:
- ✅ GitHub account
- ✅ Your SchoolSync code pushed to GitHub
- ✅ All API keys ready (Groq, Twilio, Paystack)
- ✅ Google Service Account credentials JSON
- ✅ 10 minutes of time

---

## 🚀 **Step 1: Prepare Your Code**

### **1.1 Create Procfile**

Create `Procfile` in your project root:

```
web: gunicorn dashboard_app:app --log-file -
```

### **1.2 Update requirements.txt**

Ensure it includes `flask`, `gunicorn`, `openpyxl`, `supabase`, `twilio`, etc. (Already updated).

### **1.3 Create railway.json** (Optional but recommended)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn dashboard_app:app --log-file -",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **1.4 Push to GitHub**

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

---

## 🎯 **Step 2: Create Railway Account**

1. **Go to**: https://railway.app
2. **Click**: "Start a New Project"
3. **Sign up** with GitHub (recommended) or email
4. **Verify** your email
5. **Get $5 free credits** (no credit card needed!)

---

## 📦 **Step 3: Deploy from GitHub**

### **3.1 Create New Project**

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. **Authorize Railway** to access your GitHub
4. **Select** your `SchoolSyncv2` repository
5. Click **"Deploy Now"**

### **3.2 Watch Deployment**

Railway will automatically:
- ✅ Detect Python
- ✅ Install dependencies from `requirements.txt`
- ✅ Build your app
- ✅ Start the server

**Initial deployment takes 2-3 minutes**

---

## 🔐 **Step 4: Configure Environment Variables**

### **4.1 Access Variables**

1. In Railway dashboard, click your **service**
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**

### **4.2 Add All Variables**

Add these one by one:

**Groq API:**
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
```

**Google Sheets:**
```
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"schoolsync-xxx"...}
```
*Copy entire JSON from your service account file*

**Twilio:**
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=+14155238886
TWILIO_PHONE_NUMBER=+14155238886
```

**Paystack:**
```
PAYSTACK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxx
```

**Optional (for production):**
```
PORT=14031
ENVIRONMENT=production
```

### **4.3 Save & Redeploy**

1. Click **"Save"** after adding all variables
2. Railway automatically **redeploys** with new variables
3. Wait 1-2 minutes for redeploy

---

## 🌐 **Step 5: Get Your Production URL**

### **5.1 Find Your URL**

1. In Railway dashboard, go to **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. You'll get: `https://schoolsync-production-xxxx.up.railway.app`

### **5.2 Test Your URL**

Open in browser:
```
https://your-railway-url.up.railway.app
```

You should see:
```json
{"message": "SchoolSync API is running"}
```

---

## 📱 **Step 6: Configure Twilio Webhook**

### **6.1 Update WhatsApp Webhook**

1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Click **"Sandbox settings"**
3. Find **"When a message comes in"**
4. Enter your Railway URL:
   ```
   https://your-railway-url.up.railway.app/whatsapp
   ```
5. Method: **POST**
6. Click **"Save"**

### **6.2 Test WhatsApp**

Send a message to your Twilio sandbox number:
```
Hi
```

You should get the SchoolSync welcome message! 🎉

---

## 🔧 **Step 7: Enable Background Scheduler**

### **7.1 Add Worker Service**

Railway free tier runs one process. For scheduler, you have two options:

**Option A: Run in same service (simpler)**

Update your `main.py` to start scheduler:
```python
import threading
from scheduler import start_scheduler

# At the bottom of main.py, add:
if __name__ == "__main__":
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start FastAPI
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 14031)))
```

**Option B: Separate worker service (requires paid plan)**

1. Create new service in Railway
2. Same repo, different start command
3. Use `Procfile` worker command

**For free tier, use Option A** ✅

---

## 🎨 **Step 8: Deploy Dashboard**

### **8.1 Same Service Method** (Recommended)

Your `main.py` already runs on port 14031. Add Flask dashboard:

```python
# In main.py, add:
from dashboard_app import app as dashboard_app
import threading

def run_dashboard():
    dashboard_app.run(host="0.0.0.0", port=5000)

# Start dashboard in background
dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
dashboard_thread.start()
```

### **8.2 Access Dashboard**

```
https://your-railway-url.up.railway.app:5000
```

---

## 📊 **Step 9: Monitor Your Deployment**

### **9.1 View Logs**

In Railway dashboard:
1. Go to **"Deployments"** tab
2. Click latest deployment
3. View real-time logs
4. Look for errors or warnings

### **9.2 Check Metrics**

1. **"Metrics"** tab shows:
   - CPU usage
   - Memory usage
   - Network traffic
   - Request count

### **9.3 Set Up Alerts** (Optional)

1. Go to **"Settings"** → **"Webhooks"**
2. Add webhook URL for deployment alerts
3. Get notified on failures

---

## 🔒 **Step 10: Production Checklist**

### **Security:**
- [ ] Change default PIN from 2025
- [ ] Use Paystack live mode (not test)
- [ ] Enable Twilio WhatsApp production access
- [ ] Rotate API keys regularly
- [ ] Backup Google Sheets weekly

### **Testing:**
- [ ] Test WhatsApp commands
- [ ] Verify payment flow
- [ ] Check background scheduler (wait 1 hour)
- [ ] Test dashboard access
- [ ] Send test broadcast
- [ ] Verify fee reminders work

### **Monitoring:**
- [ ] Set up uptime monitoring (UptimeRobot)
- [ ] Check Railway logs daily
- [ ] Monitor Google Sheets API quota
- [ ] Track error rates

---

## 🎯 **Your Production URLs**

After deployment, you'll have:

```
API: https://schoolsync-production.up.railway.app
Dashboard: https://schoolsync-production.up.railway.app:5000
WhatsApp Webhook: https://schoolsync-production.up.railway.app/whatsapp
```

---

## 💰 **Cost Breakdown**

### **Free Tier ($5 credits/month):**
- ✅ 1 service (API + Dashboard + Scheduler)
- ✅ 500 execution hours
- ✅ Suitable for 1-5 schools
- ✅ ~150 students

### **If You Exceed Free Tier:**
- **Starter Plan**: $5/month (500 more hours)
- **Pro Plan**: $20/month (unlimited hours)

**Expected usage for SchoolSync:**
- Small school (50 students): **$0-2/month**
- Medium school (200 students): **$3-5/month**
- Large school (500+ students): **$8-15/month**

---

## 🆘 **Troubleshooting**

### **Problem: Build fails**
```
Solution:
1. Check requirements.txt has all dependencies
2. Ensure Python version compatible (3.9+)
3. Check Railway logs for specific error
```

### **Problem: WhatsApp not responding**
```
Solution:
1. Verify Twilio webhook URL is correct
2. Check Railway logs for incoming requests
3. Test API endpoint directly in browser
4. Verify environment variables are set
```

### **Problem: Dashboard not loading**
```
Solution:
1. Check port 5000 is exposed
2. Verify Flask is running (check logs)
3. Try main URL first: https://xxx.railway.app
4. Check firewall/network settings
```

### **Problem: Scheduler not running**
```
Solution:
1. Check if scheduler thread started (logs)
2. Verify APScheduler installed
3. Check for errors in scheduler.py
4. Wait 1 hour to see if fee reminders work
```

### **Problem: Out of credits**
```
Solution:
1. Upgrade to paid plan ($5/month)
2. Optimize background tasks
3. Reduce polling frequency
4. Use Railway's usage dashboard to monitor
```

---

## 🚀 **Post-Deployment Steps**

### **1. Update Twilio Phone Number**
- Change from sandbox to production number
- Apply for WhatsApp Business API access
- Update webhook to production URL

### **2. Custom Domain** (Optional)
```
1. Railway Settings → Domains
2. Add custom domain (e.g., schoolsync.yourschool.com)
3. Update DNS records as shown
4. SSL certificate auto-generated
```

### **3. Add Monitoring**
```
1. Sign up: uptimerobot.com
2. Add monitor for your Railway URL
3. Get alerts if service goes down
4. Free tier: 50 monitors
```

### **4. Setup Backups**
```
1. Enable Google Sheets version history
2. Weekly export to CSV (automation)
3. Backup environment variables securely
4. Document Railway configuration
```

---

## ✅ **Success Indicators**

Your deployment is successful when:

- ✅ Railway shows "Active" status
- ✅ WhatsApp responds to "Hi" message
- ✅ Dashboard loads at :5000 port
- ✅ Logs show no errors
- ✅ Payment test completes successfully
- ✅ Admin can use all commands
- ✅ Scheduler sends reminders (after 1 hour/week)

---

## 📞 **Need Help?**

**Railway Support:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

**SchoolSync Specific:**
- Check `DEPLOYMENT_USAGE.md` for usage guide
- See `FEATURES.md` for feature list
- Review `TESTING.md` for test cases

---

## 🎉 **Congratulations!**

Your SchoolSync 2.0 is now **LIVE IN PRODUCTION** on Railway! 🚀

**Next Steps:**
1. Test all features via WhatsApp
2. Invite school admins to test
3. Add real student data
4. Start onboarding parents
5. Monitor for 24 hours
6. Scale to more schools!

**Your app is now:**
- ✅ 24/7 available
- ✅ Globally accessible
- ✅ Auto-scaling
- ✅ Production-grade
- ✅ Ready for real users!

Welcome to production! 🎓💪
