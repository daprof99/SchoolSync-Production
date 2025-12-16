# SchoolSync 2.0 - Testing Guide

Complete guide to test all features before production deployment.

---

## 🚀 Quick Start Testing

### Step 1: Install Dependencies

```bash
cd c:\Users\HP\Documents\RAIN\SchoolSyncv2
pip install -r requirements.txt
```

### Step 2: Verify Environment Variables

Check your `.env` file has all required keys:

```bash
# Display (without showing sensitive values)
Get-Content .env | ForEach-Object { $_.Split('=')[0] }
```

Should show:
- GOOGLE_CREDENTIALS_JSON
- GROQ_API_KEY
- PAYSTACK_SECRET_KEY
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_WHATSAPP_NUMBER

### Step 3: Initialize Database

```bash
python db_setup.py
```

Answer "yes" when prompted. This creates all worksheets in your Google Sheets.

**✅ Verify:** Open your Google Sheet and confirm these new tabs exist:
- Results
- Messages
- Events
- Parent_Registry
- Notifications_Queue

---

## 🧪 Testing the Backend

### Test 1: Basic Import Check

```bash
python -c "from tools import *; from agent import app; print('✅ All imports successful!')"
```

**Expected:** `✅ All imports successful!`

### Test 2: LLM Connection

```bash
python -c "from langchain_groq import ChatGroq; import os; from dotenv import load_dotenv; load_dotenv(); llm = ChatGroq(model='llama-3.3-70b-versatile', api_key=os.getenv('GROQ_API_KEY')); response = llm.invoke('Say hello'); print(f'✅ Llama 4 working: {response.content}')"
```

**Expected:** Llama 4 responds with a greeting

### Test 3: Google Sheets Connection

```bash
python -c "from tools import get_db_connection; sheet = get_db_connection('2348189678261'); print(f'✅ Connected to: {sheet.title}')"
```

**Expected:** Shows your school's Google Sheet name

### Test 4: Start Server

```bash
python main.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:14031
```

Keep this running and open a new terminal for next tests.

---

## 📱 Testing Without WhatsApp (Local Testing)

### Test 5: Agent Direct Testing

Create `test_agent.py`:

```python
from agent import app
from langchain_core.messages import HumanMessage

# Test router
test_cases = [
    "META_PHONE=2348189678261 || CHECK ST-001 OKAFOR",
    "META_PHONE=2348189678261 || RESULTS ST-001 OKAFOR",
    "META_PHONE=2348189678261 || When is the next PTA meeting?",
    "META_PHONE=2348189678261 || MESSAGE TEACHER about ST-001",
    "META_PHONE=2348189678261 || ALL MY CHILDREN",
]

for test in test_cases:
    print(f"\n{'='*60}")
    print(f"INPUT: {test}")
    print(f"{'='*60}")
    
    result = app.invoke({"messages": [HumanMessage(content=test)]})
    response = result['messages'][-1]
    
    if isinstance(response, str):
        print(f"RESPONSE: {response}")
    else:
        print(f"RESPONSE: {response.content}")
```

Run:
```bash
python test_agent.py
```

**Expected:** See appropriate responses for each query type

### Test 6: Test Individual Features

Create `test_features.py`:

```python
from tools import *

# Test 1: Multi-student support
print("Testing multi-student support...")
result = register_parent("+2349999999999", "Test Parent", "ST-001,ST-002", "2348189678261")
print(f"✅ Register parent: {result}")

students = get_parent_students("+2349999999999")
print(f"✅ Retrieved students: {students}")

# Test 2: Conversation history
print("\nTesting conversation history...")
store_message("+2349999999999", "user", "Hello")
store_message("+2349999999999", "assistant", "Hi! How can I help?")
history = get_conversation_history("+2349999999999")
print(f"✅ History stored: {len(history)} messages")

# Test 3: Events
print("\nTesting events...")
event_id = add_event("Test Event", "Testing calendar", "2024-12-25", "10:00", "Test", "2348189678261")
print(f"✅ Event created: {event_id}")

# Test 4: Notifications
print("\nTesting notifications...")
queued = queue_notification("+2349999999999", "Test notification", "Test", "2024-12-14T20:00:00", "2348189678261")
print(f"✅ Notification queued: {queued}")

print("\n✅ All feature tests passed!")
```

Run:
```bash
python test_features.py
```

---

## 🔗 Testing with WhatsApp (Twilio)

### Test 7: Setup ngrok

```bash
# In a new terminal
ngrok http 14031
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### Test 8: Configure Twilio Sandbox

1. Go to [Twilio Console](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Click "Settings" for WhatsApp Sandbox
3. Set "When a message comes in" to: `https://abc123.ngrok.io/whatsapp`
4. Save

### Test 9: Send Test Messages

From your phone, send to Twilio WhatsApp number:

**Test Message Flow:**
```
You: join [your-sandbox-code]
Bot: (Twilio confirmation)

You: Hi
Bot: 👋 **Hello! I'm SchoolSync...**

You: CHECK ST-001 OKAFOR
Bot: 👤 **Okafor Tunde Ola**
💰 **Owing: ₦X,XXX**

You: RESULTS ST-001 OKAFOR
Bot: 📊 **Results for ST-001:**
[Shows subjects and grades]

You: When is the next meeting?
Bot: 📅 **Upcoming Events:**
[Shows events]

You: MESSAGE TEACHER My son is sick
Bot: ✅ **Message sent to teacher!**
```

### Test 10: Admin Commands

From admin phone number:

```
Admin: SUMMARY
Bot: 📊 **Dashboard**
💰 Rev: ₦X.XM
📉 Out: ₦X.XM

Admin: REGISTER PARENT +2348012345678, Test Parent, ST-001,ST-002
Bot: ✅ **Registered:** Test Parent with students: ST-001,ST-002

Admin: SHOW MESSAGES
Bot: 📬 **Pending Messages:**
1. ST-001 - My son is sick...

Admin: ADD EVENT PTA | Discuss results | 2024-12-20 | 10:00 | Meeting
Bot: ✅ Event created: EVT-...

Admin: SEND REMINDERS
Bot: ✅ **Queued X fee reminders!**
```

---

## 🎨 Testing the Dashboard

### Test 11: Setup Dashboard

```bash
cd dashboard
npm install
```

**Expected:** Installs ~500-800 packages

### Test 12: Run Dashboard

```bash
npm run dev
```

**Expected:**
```
- ready started server on 0.0.0.0:3000
- Local:        http://localhost:3000
```

### Test 13: View Dashboard

Open browser: `http://localhost:3000`

**✅ Verify:**
- [ ] Stats cards display (Revenue, Outstanding, Debtors, Students)
- [ ] Charts render (Weekly Revenue line chart, Payment bar chart)
- [ ] Quick action buttons visible
- [ ] Responsive design (resize browser window)
- [ ] No console errors (F12)

---

## ⏰ Testing the Scheduler

### Test 14: Run Scheduler

```bash
# In a new terminal
python scheduler.py
```

**Expected Output:**
```
============================================================
   SchoolSync 2.0 - Background Scheduler
============================================================
Started at: 2024-12-14 21:06:48

📅 Scheduled Jobs:
  - Process Notification Queue (Next run: ...)
  - Weekly Fee Reminders (Next run: Monday 9:00 AM)
  - Daily Health Check (Next run: Midnight)

🚀 Scheduler started! Press Ctrl+C to stop.
```

### Test 15: Trigger Manual Notification Processing

From WhatsApp (admin):
```
Admin: SEND REMINDERS
```

Watch scheduler terminal - should process queue within the hour.

---

## 🔍 Testing Specific Features

### Feature: Multi-Student Parent

**Setup:**
```
Admin: REGISTER PARENT +234XXXXXXXXX, Mrs. Test, ST-001,ST-002
```

**Test:**
```
Parent (+234XXXXXXXXX): ALL MY CHILDREN
Bot: 📊 **All Children:**
👤 Surname First (ST-001): ₦X,XXX
👤 Surname First (ST-002): ₦X,XXX
```

### Feature: Results Upload (Manual Test)

1. Create test PDF with student results
2. Upload to Google Drive Results folder
3. From admin phone:
```
Admin: (Send via web portal or manually call upload_results_pdf)
```

4. Test parent access:
```
Parent: RESULTS ST-001 OKAFOR
Bot: 📊 **Results for ST-001:**
Math: 85 (A)
English: 78 (B)
```

### Feature: Payment Flow

**Test:**
```
Parent: PAY 5000
Bot: 💳 **Pay ₦5,000:**
https://paystack.com/pay/xxx
```

Click link → Complete test payment → Check webhook:

**Server logs should show:**
```
💰 Payment Confirmed: [reference]
```

**Parent receives:**
```
Bot: ✅ **Payment Confirmed!**
💰 Amount: ₦5,000
👤 Student: ST-001
```

### Feature: Events & Calendar

**Create Event:**
```
Admin: ADD EVENT PTA Meeting | Discuss term results | 2024-12-25 | 10:00 | PTA
Bot: ✅ Event created: EVT-20241214210648
```

**Query Event:**
```
Parent: When is the PTA meeting?
Bot: 📅 **Upcoming Events:**
PTA Meeting - December 25, 2024 at 10:00 AM
Discuss term results
```

---

## ✅ Final Verification Checklist

### Backend
- [ ] Server starts without errors
- [ ] All imports successful
- [ ] Google Sheets connection working
- [ ] Groq API responding (Llama 4)
- [ ] Database sheets created

### WhatsApp Integration
- [ ] Messages received from parents
- [ ] Bot responds correctly
- [ ] Admin commands working
- [ ] Context preserved across messages

### Features
- [ ] Fee checking working
- [ ] Payment links generated
- [ ] Results querying functional
- [ ] Multi-student support working
- [ ] Parent-teacher messaging operational
- [ ] Events calendar functional
- [ ] Automated notifications queued

### Dashboard
- [ ] Dashboard loads on localhost:3000
- [ ] Charts render correctly
- [ ] Stats display properly
- [ ] No JavaScript errors
- [ ] Responsive design working

### Scheduler
- [ ] Scheduler starts without errors
- [ ] Jobs scheduled correctly
- [ ] Notification queue processes
- [ ] Fee reminders queue properly

---

## 🐛 Troubleshooting Common Issues

### Issue: "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Google Sheets API error
- Check GOOGLE_CREDENTIALS_JSON in .env
- Verify service account has access to sheets
- Run `python db_setup.py` again

### Issue: Groq API rate limit
- Wait 60 seconds between requests
- Or upgrade Groq API plan

### Issue: WhatsApp not responding
- Check ngrok is running
- Verify Twilio webhook URL is correct
- Check server logs for errors

### Issue: Charts not showing
```bash
cd dashboard
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 📊 Performance Testing

### Load Test (Optional)

Create `load_test.py`:

```python
import asyncio
import aiohttp

async def send_message(session, phone):
    data = {
        'From': f'whatsapp:{phone}',
        'Body': 'CHECK ST-001 OKAFOR'
    }
    async with session.post('http://localhost:14031/whatsapp', data=data) as resp:
        return await resp.text()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [send_message(session, f'+23481{i:08d}') for i in range(10)]
        responses = await asyncio.gather(*tasks)
        print(f"✅ Processed {len(responses)} concurrent requests")

asyncio.run(main())
```

**Expected:** All 10 requests complete in < 10 seconds

---

## 🎯 Production Readiness Checklist

Before going live:

- [ ] All tests passing
- [ ] Environment variables secured (not in git)
- [ ] Google Sheets permissions verified
- [ ] Twilio production WhatsApp approved
- [ ] Paystack live mode configured
- [ ] Admin phone numbers correct in tools.py
- [ ] Database backup strategy in place
- [ ] Monitoring/logging configured
- [ ] Error handling tested
- [ ] User acceptance testing completed

---

## 🚀 Deploy to Production

1. **Replace ngrok with permanent URL** (Railway, Render, Heroku)
2. **Deploy dashboard** to Vercel
3. **Setup monitoring** (Sentry, LogRocket)
4. **Configure backups** for Google Sheets
5. **Document runbook** for operations team

---

**You're ready to test! Start with Step 1 and work through systematically.** 🎉
