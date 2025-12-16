# Quick Start Guide - Testing SchoolSync 2.0

## ⚡ Fastest Way to Test

### 1. Run Quick Test Script

```bash
python test_quick.py
```

This tests everything in 30 seconds:
- ✅ All imports & dependencies
- ✅ Llama 4 (Groq) connection
- ✅ Google Sheets connection
- ✅ Agent routing
- ✅ New features
- ✅ Paystack integration

**Expected Output:**
```
✅ PASS: Imports
✅ PASS: LLM Connection  
✅ PASS: Google Sheets
✅ PASS: Agent Routing
✅ PASS: New Features
✅ PASS: Paystack

Passed: 6/6
🎉 All tests passed!
```

### 2. Start the Server

```bash
python main.py
```

**Expected:**
```
INFO:     Uvicorn running on http://0.0.0.0:14031
```

### 3. Test with WhatsApp

**Terminal 1:**
```bash
python main.py
```

**Terminal 2:**
```bash
ngrok http 14031
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

**Configure Twilio:**
1. Go to [Twilio WhatsApp Sandbox](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Settings → Webhook: `https://abc123.ngrok.io/whatsapp`
3. Save

**Send from your phone:**
```
CHECK ST-001 OKAFOR
```

**Expected response from bot with fees!**

---

## 🎨 Test Dashboard (Optional)

```bash
cd dashboard
npm install
npm run dev
```

Open: http://localhost:3000

---

## 🔧 If Tests Fail

**Fix 1: Dependencies**
```bash
pip install -r requirements.txt
```

**Fix 2: Database**
```bash
python db_setup.py
```
Answer "yes" to initialize

**Fix 3: Environment**
```bash
# Check .env has:
# - GOOGLE_CREDENTIALS_JSON
# - GROQ_API_KEY
# - PAYSTACK_SECRET_KEY
```

---

## 📝 Full Testing Guide

See [TESTING.md](file:///c:/Users/HP/Documents/RAIN/SchoolSyncv2/TESTING.md) for comprehensive tests.

---

**That's it! Run `python test_quick.py` to start.** 🚀
