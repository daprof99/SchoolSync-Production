# 🧪 Live WhatsApp Testing Guide

## Quick Functionality Test - Step by Step

### **Current Status:**
- ✅ Dashboard running (port 5000)
- ✅ Main server starting (port 14031)
- ⏳ Need ngrok tunnel

---

## 🚀 **Test Setup (5 minutes)**

### Step 1: Verify Servers Running
```bash
# Should see these running:
python main.py          # Port 14031
python dashboard_app.py # Port 5000
ngrok http 14031        # Tunnel
```

### Step 2: Get ngrok URL
```bash
# In ngrok terminal, look for:
Forwarding    https://abc123.ngrok-free.app -> http://localhost:14031
```

### Step 3: Update Twilio Webhook
```
1. Go to: console.twilio.com
2. WhatsApp Sandbox → Settings
3. "When a message comes in": https://YOUR-NGROK-URL/whatsapp
4. Save
```

---

## ✅ **Quick Tests (Send via WhatsApp)**

### Test 1: Basic Connection (30 sec)
```
You send: Hi
Expected: Welcome message with HELP prompt
✅ Pass / ❌ Fail: _____
```

### Test 2: Help Command (30 sec)
```
You send: HELP
Expected: Full command list for parents & admins
✅ Pass / ❌ Fail: _____
```

### Test 3: Fee Check (1 min)
```
You send: CHECK ST-962 Nnamdi
Expected: Balance, owing amount
✅ Pass / ❌ Fail: _____
```

### Test 4: Admin Summary (1 min)
```
You send: SUMMARY
Expected: Revenue, outstanding, debtors count
✅ Pass / ❌ Fail: _____
```

### Test 5: Natural Language (1 min)
```
You send: How much do I owe?
Expected: AI understands and routes correctly
✅ Pass / ❌ Fail: _____
```

### Test 6: Payment Link (1 min)
```
You send: PAY 5000
Expected: Paystack payment link
✅ Pass / ❌ Fail: _____
```

### Test 7: Events Query (1 min)
```
You send: When is the next meeting?
Expected: Event list with dates
✅ Pass / ❌ Fail: _____
```

### Test 8: Results Check (1 min)
```
You send: RESULTS ST-962 Nnamdi
Expected: Grades or "No results found"
✅ Pass / ❌ Fail: _____
```

---

## 🖥️ **Dashboard Test (2 minutes)**

### Test 9: Web Dashboard
```
1. Open: http://localhost:5000
2. Check: Stats cards display
3. Check: Events list shows
4. Check: No errors in browser console (F12)
✅ Pass / ❌ Fail: _____
```

---

## 🔐 **Security Test (2 minutes)**

### Test 10: Surname Verification
```
You send: CHECK ST-962 WrongName
Expected: ⛔ Access Denied
✅ Pass / ❌ Fail: _____
```

### Test 11: PIN Change
```
You send: SET PIN 2025 NEWPIN123
Expected: ✅ PIN updated
✅ Pass / ❌ Fail: _____
```

---

## 📊 **Expected Success Rate**

**Minimum Passing:** 8/11 tests  
**Good:** 10/11 tests  
**Excellent:** 11/11 tests  

---

## 🐛 **If Tests Fail:**

### WhatsApp not responding:
1. Check main.py terminal for errors
2. Verify ngrok URL in Twilio
3. Check WhatsApp sandbox is active
4. Test API endpoint: https://YOUR-NGROK-URL (should say "running")

### Wrong responses:
1. Check agent.py routing keywords
2. Verify Google Sheets access
3. Check environment variables loaded
4. Review main.py logs for errors

### Dashboard not loading:
1. Restart: python dashboard_app.py
2. Try: http://127.0.0.1:5000
3. Check Flask errors in terminal
4. Clear browser cache

---

## ✅ **Quick Verification Commands**

**Test Database:**
```python
python -c "from tools import get_db_connection, ADMIN_PHONES; sheet = get_db_connection(ADMIN_PHONES[0]); print(f'Connected: {sheet.title if sheet else \"FAILED\"}')"
```

**Test Imports:**
```python
python -c "from main import app; from agent import router_node; print('✅ Imports OK')"
```

**Test Server:**
```bash
curl http://localhost:14031
curl http://localhost:5000
```

---

## 🎯 **Your Results:**

**Tests Passed:** __ / 11  
**Status:** PASS / FAIL / NEEDS FIXES  
**Ready for deployment:** YES / NO  

**Notes:**
___________________________________
___________________________________
___________________________________
