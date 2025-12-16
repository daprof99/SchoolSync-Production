# 🧪 Complete Testing Guide - SchoolSync 2.0

**Your servers have been running for 18+ hours - impressive!** ✅

Let's test everything systematically.

---

## 🚀 **Quick Start (Your Current Setup)**

**Already Running:**
- ✅ `python main.py` (18+ hours)
- ✅ `ngrok http 14031` (18+ hours)
- ✅ WhatsApp connected via Twilio

**Your Phone:** +2349075014063
**Status:** Super Admin + RAIN Academy Admin

---

## 📱 **Phase 1: Basic Features**

### Test 1: Welcome Menu
```
You: Hi
Expected: Welcome menu with 6 options (1-6)
```

### Test 2: Admissions
```
You: 1
Expected: Admissions prompt

You: John Doe, JSS1, 08012345678
Expected: Lead captured confirmation
```

### Test 3: Fee Check
```
You: CHECK ST-962 Nnamdi
Expected: Shows balance (from sample data)

You: CHECK ST-500 Wrong
Expected: ⛔ Access Denied
```

### Test 4: Payment Link
```
You: PAY 5000
Expected: Paystack payment link
```

---

## 🎓 **Phase 2: Results System**

### Test 5: Check Results
```
You: RESULTS ST-962 Nnamdi
Expected: Shows grades (if data exists)
Or: No results found
```

### Test 6: Natural Language
```
You: 3
Expected: Routes to results agent

You: Show me my son's grades
Expected: AI routes to results
```

---

## 💬 **Phase 3: Communication**

### Test 7: Message Teacher
```
You: MESSAGE TEACHER My child is absent today
Expected: ✅ Message sent to teacher

You: 5
Expected: Routes to messages agent
```

### Test 8: Admin View Messages (from your phone)
```
You: SHOW MESSAGES
Expected: List of pending parent messages
```

---

## 📅 **Phase 4: Events & Calendar**

### Test 9: Query Events
```
You: When is the next PTA meeting?
Expected: Shows upcoming events (from sample data)

You: 4
Expected: Routes to events agent
```

### Test 10: Add Event (Admin)
```
You: ADD EVENT Test Event | Testing | 2024-12-25 | 10:00 | Meeting
Expected: ✅ Event created: EVT-...
```

---

## 👨‍👩‍👧‍👦 **Phase 5: Multi-Student Support**

### Test 11: Check All Children
```
You: ALL MY CHILDREN
Expected: Shows all students linked to your phone
(Or: No students registered - need to register first)
```

### Test 12: Register Parent (Admin)
```
You: REGISTER PARENT +2348111111111, Test Parent, ST-962,ST-427
Expected: ✅ Registered Test Parent with students

Then from +2348111111111:
Test Parent: ALL MY CHILDREN
Expected: Shows both students
```

---

## 📊 **Phase 6: Admin Commands**

### Test 13: Financial Summary
```
You: SUMMARY
Expected: Dashboard with revenue, outstanding, debtors
```

### Test 14: Add Student
```
You: ADD STUDENT ST-999, Test, Student, John, JSS1, 08099999999, 50000
Expected: ✅ Student added
```

### Test 15: Bill Class
```
You: BILL CLASS JSS1 5000 Field Trip
Expected: ✅ Billed X students
```

### Test 16: Attendance
```
You: CLOCKIN 962 427 500
Expected: ✅ Marked 3 students present
```

---

## 🔐 **Phase 7: Security Features (NEW!)**

### Test 17: Set Custom PIN
```
You: SET PIN 2025 MYPIN999
Expected: ✅ PIN updated to: MYPIN999

You: APPROVE MYPIN999
Expected: ✅ Approved (if pending transaction)

You: APPROVE 2025
Expected: ⛔ Wrong PIN
```

### Test 18: Request OTP
```
You: REQUEST OTP
Expected: 📱 Verification code sent to ***4063
(Check SMS for 6-digit code)
```

---

## 🏫 **Phase 8: Multi-School (Super Admin)**

### Test 19: Add New School
```
You: ADD SCHOOL Test Academy, +2348111111111, test@test.com
Expected: 
✅ Creates Google Sheet
✅ Sets up database
✅ Adds to registry

You: Check Google Drive
Expected: See "Test Academy_Database" sheet
```

---

## 🎨 **Phase 9: Web Dashboard**

### Test 20: Dashboard
```bash
# In new terminal:
cd dashboard
npm run dev

# Open browser:
http://localhost:3000
```

**Expected:**
- Revenue charts
- Stats cards
- Quick actions
- Responsive design

---

## 🤖 **Phase 10: AI & Natural Language**

### Test 21: Natural Language Queries
```
You: How much does my son owe?
Expected: AI extracts context, shows balance

You: Is there a meeting this week?
Expected: AI routes to events

You: I want to pay
Expected: AI generates payment link
```

### Test 22: Context Awareness
```
You: CHECK ST-962 Nnamdi
Bot: Shows balance

You: What about his grades?
Expected: AI remembers ST-962 from context
```

---

## 🐛 **Known Issues to Check**

### Issue 1: Payment Amount
```
Problem: Bot might show "PAY 5000" instead of actual balance
Fix: Being addressed - will show real amount owed
```

### Issue 2: Numbered Options 2-6
```
Problem: Some options might show fallback
Workaround: Use natural language instead
```

---

## ✅ **Success Criteria**

**Your app is working if:**
- ✅ Bot responds to WhatsApp messages
- ✅ Natural language works ("when is meeting?")
- ✅ Admin commands work (SUMMARY, ADD STUDENT)
- ✅ Security commands work (SET PIN, REQUEST OTP)
- ✅ Multi-school onboarding works (ADD SCHOOL)
- ✅ 50 students visible in Google Sheet
- ✅ Events and messages logged

---

## 🚨 **If Something Doesn't Work**

### Server Not Responding?
```bash
# Check if running:
# Ctrl+C to stop
python main.py
```

### ngrok URL Changed?
```
# Get new URL from ngrok terminal
# Update Twilio webhook:
https://YOUR-NEW-NGROK-URL/whatsapp
```

### Database Errors?
```bash
python db_setup.py
# Answer: yes
```

### Import Errors?
```bash
pip install -r requirements.txt
```

---

## 📊 **Expected Test Results Summary**

| Feature | Test | Expected Result |
|---------|------|----------------|
| Welcome | Hi | 6-option menu |
| Fee Check | CHECK ST-962 Nnamdi | Balance shown |
| Results | RESULTS ST-962 Nnamdi | Grades or "No data" |
| Events | When is meeting? | Event list |
| Multi-Student | ALL MY CHILDREN | Student list |
| Admin | SUMMARY | Financial dashboard |
| Security | SET PIN | PIN updated |
| OTP | REQUEST OTP | SMS sent |
| Multi-School | ADD SCHOOL | Sheet created |
| Dashboard | localhost:3000 | Charts shown |

---

## 🎯 **Production Readiness Checklist**

Before deploying:
- [ ] All tests passing
- [ ] Real student data added
- [ ] Parents registered
- [ ] Events created
- [ ] PINs changed from default
- [ ] ngrok replaced with permanent URL
- [ ] Environment variables secured
- [ ] Twilio production approved
- [ ] Paystack live mode

---

## 🎉 **You're Ready!**

Send your first test message:
```
You: Hi
```

And watch the magic happen! 🚀

**Questions?** Just ask!
