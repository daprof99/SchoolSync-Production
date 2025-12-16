# 🚀 SchoolSync 2.0 - Post-Deployment User Guide

## After Live Deployment - How to Use SchoolSync

Once deployed to production (Railway, Render, Heroku, etc.), here's how different users interact with the system:

---

## 👨‍👩‍👧‍👦 **For Parents**

### **Setup (One-Time)**
1. **Get Registered** by school admin
   - Admin sends: `REGISTER PARENT +2349075014063, John Doe, ST-001`
   - You receive confirmation SMS/WhatsApp

2. **Save WhatsApp Number**
   - Save the school's WhatsApp number in your contacts
   - Example: "RAIN Academy SchoolSync"

### **Daily Usage**

#### **Via WhatsApp** 📱

**Check Fees:**
```
You: Hi
Bot: Welcome to SchoolSync!

You: CHECK ST-001 Okafor
Bot: 👤 Okafor John Emmanuel
     💰 Owing: ₦25,000
     📝 Second term fees

You: PAY 25000
Bot: 💳 Payment link: https://paystack.com/pay/xxx
```

**Check Results:**
```
You: RESULTS ST-001 Okafor
Bot: 📊 Results for Okafor John
     Mathematics: 85 (A)
     English: 78 (B)
     ...
```

**Check Events:**
```
You: When is the next PTA meeting?
Bot: 📅 Upcoming Events:
     • PTA Meeting - Dec 20, 2024 10:00 AM
     • Inter-House Sports - Jan 15, 2025
```

**Message Teacher:**
```
You: MESSAGE TEACHER My son is sick today
Bot: ✅ Message sent to teacher
```

**Multiple Children:**
```
You: ALL MY CHILDREN
Bot: Your registered students:
     1. ST-001 - John Okafor - ₦25,000 owing
     2. ST-045 - Mary Okafor - ₦0 (Paid)
```

**Get Help:**
```
You: HELP
Bot: [Shows all available commands]
```

---

## 👔 **For School Admins**

### **Setup (One-Time)**
1. **Your school is onboarded** (manually or via super admin)
2. **Your phone number is added** to `ADMIN_PHONES` list
3. **You receive** school details and WhatsApp number

### **Daily Usage**

#### **Via WhatsApp** 📱

**Financial Dashboard:**
```
Admin: SUMMARY
Bot: 💰 Dashboard
     Revenue: ₦2,870,000
     Outstanding: ₦1,513,250
     Debtors: 36/50
```

**Add Student:**
```
Admin: ADD STUDENT ST-101, Adebayo, Tunde, Oluwaseun, JSS1, 08012345678, 50000
Bot: ✅ Added: Adebayo Tunde
```

**Bill Entire Class:**
```
Admin: BILL CLASS JSS1 5000 Field Trip
Bot: ✅ Billed 15 students in JSS1
```

**Take Attendance:**
```
Admin: CLOCKIN 001 002 045 078
Bot: ✅ Marked Present: ST-001, ST-002, ST-045, ST-078
```

**Broadcast Message:**
```
Admin: BROADCAST ALL: School resumes Monday 8 AM
Bot: ✅ Broadcast queued for 50 parents
```

**Approve Payment:**
```
Parent sends receipt image via WhatsApp
Bot: 📸 Receipt Scanned (₦50,000)
     ⏳ Pending Admin Approval

Admin: APPROVE 2025
Bot: ✅ Approved & Confirmation Sent
```

**Register Parent:**
```
Admin: REGISTER PARENT +2349012345678, Mrs. Adebayo, ST-001,ST-045
Bot: ✅ Registered Mrs. Adebayo with students
```

**View Messages:**
```
Admin: SHOW MESSAGES
Bot: 📬 8 Pending Messages:
     1. From +234xxx: My child is sick
     2. From +234yyy: Question about fees
     ...
```

**Send Fee Reminders:**
```
Admin: SEND REMINDERS
Bot: ✅ Queued 36 fee reminders!
```

**Add Event:**
```
Admin: ADD EVENT PTA Meeting | Discuss term progress | 2024-12-20 | 10:00 | PTA
Bot: ✅ Event created: EVT-20241220001
```

**Change Security PIN:**
```
Admin: SET PIN 2025 MYPIN999
Bot: ✅ PIN updated to: MYPIN999
```

#### **Via Web Dashboard** 🖥️

**Access:**
```
https://your-school.schoolsync.app
or
https://your-deployment-url.com:5000
```

**What You See:**
- 📊 Revenue charts and trends
- 💰 Financial summary cards
- ⚠️ Debtor list
- 📅 Event calendar
- 📬 Pending messages (with count)
- ⚡ Quick action buttons

**Quick Actions:**
- Click "Broadcast" → Send message to all
- Click "Upload Results" → Upload PDF
- Click "Messages" → View/reply to parents
- Click "Export Data" → Download reports

---

## 🏢 **For Super Admins (Platform Owners)**

### **Add New School**

#### **Via WhatsApp:**
```
SuperAdmin: ADD SCHOOL St. Patrick's Academy, +2348123456789, admin@stpatrick.com
Bot: 🎉 St. Patrick's Academy Successfully Onboarded!
     📊 Database: Created & Configured
     📱 Admin Phone: +2348123456789
     🔗 Sheet ID: 1ABC...xyz
```

**What Happens Automatically:**
1. ✅ New Google Sheet created
2. ✅ 9 worksheets set up
3. ✅ Added to master registry
4. ✅ School admin can immediately use the system

#### **Via Python Script:**
```bash
python onboard_school.py
# Enter school details when prompted
```

**Monitor System:**
- Access master Google Sheet
- View all schools in registry
- Check system health via logs

---

## 📱 **Production Deployment URLs**

### **Option 1: Railway** (Recommended)
```
Backend: https://schoolsync-backend.railway.app
Dashboard: https://schoolsync-dashboard.railway.app
WhatsApp: https://schoolsync-backend.railway.app/whatsapp
```

### **Option 2: Render**
```
Backend: https://schoolsync-api.onrender.com
Dashboard: https://schoolsync-web.onrender.com
```

### **Option 3: Heroku**
```
Backend: https://schoolsync-prod.herokuapp.com
Dashboard: https://schoolsync-admin.herokuapp.com
```

### **Twilio Configuration**
```
Webhook URL: https://YOUR-DEPLOYMENT-URL/whatsapp
Method: POST
```

---

## 🔄 **Daily Workflows**

### **Morning Routine (Admin):**
```
1. SUMMARY → Check overnight payments
2. SHOW MESSAGES → Respond to parent queries
3. CLOCKIN ... → Mark attendance
4. Open dashboard → Review trends
```

### **Parent Payment Flow:**
```
1. Parent: CHECK ST-001 Surname
2. Bot: Shows balance (₦25,000)
3. Parent: PAY 25000
4. Bot: Sends Paystack link
5. Parent: Completes payment
6. System: Auto-confirms, updates balance
7. Parent: Receives SMS confirmation
```

### **Results Publication Flow:**
```
1. Admin uploads PDF to Google Drive
2. Admin: Sends Drive link via WhatsApp
3. Bot: Parses PDF with Vision AI
4. Bot: Stores results in database
5. System: Queues parent notifications
6. Parents: Receive "Results Ready" alerts
7. Parents: RESULTS ST-001 Surname → View grades
```

---

## 📊 **Monitoring & Management**

### **Check System Health:**
```
Admin: SUMMARY
# If responds → System OK
# If timeout → Check server logs
```

### **View Logs:**
```bash
# Railway/Render
View logs in platform dashboard

# Check errors
Look for "ERROR:", "❌", "Failed"
```

### **Database Access:**
```
1. Open Google Sheets
2. Find your school's sheet
3. View worksheets:
   - Students_Fees (live data)
   - Admissions (leads)
   - Attendance (daily)
   - Messages (parent queries)
   - Events (calendar)
   - Results (grades)
   - Parent_Registry (links)
   - Notifications_Queue (pending)
```

---

## 🆘 **Common Questions**

### **"I'm a parent, how do I start?"**
1. Get registered by school admin
2. Save school's WhatsApp number
3. Send "Hi" to get started
4. Type "HELP" for commands

### **"I'm an admin, how do I use this daily?"**
1. Morning: `SUMMARY` → check status
2. Throughout day: Respond to WhatsApp queries
3. Evening: `SEND REMINDERS` if needed
4. Weekly: Check dashboard for trends

### **"How do I add a new school?"**
1. As super admin: `ADD SCHOOL Name, Phone, Email`
2. System creates everything automatically
3. New admin can start using immediately

### **"How do parents make payments?"**
1. Parent: `PAY 5000`
2. Bot sends Paystack link
3. Parent completes payment online
4. System auto-confirms
5. Balance updated instantly

### **"How do I broadcast messages?"**
1. Admin: `BROADCAST ALL: Your message`
2. System queues for all parents
3. Sends hourly in batches
4. Parents receive on WhatsApp

---

## 🌐 **Access Methods Summary**

| User Type | Primary Interface | Alternative |
|-----------|------------------|-------------|
| **Parents** | WhatsApp Bot | None (WhatsApp only) |
| **Admins** | WhatsApp Bot | Web Dashboard |
| **Super Admins** | WhatsApp Bot | Direct Sheet Access + Dashboard |

---

## 💡 **Pro Tips**

### **For Parents:**
- ✅ Save commands you use often
- ✅ Use natural language (AI understands!)
- ✅ Type "HELP" when stuck
- ✅ Check messages for updates

### **For Admins:**
- ✅ Start each day with `SUMMARY`
- ✅ Use dashboard for detailed analysis
- ✅ Broadcast important updates
- ✅ Reply to messages promptly
- ✅ Set a secure custom PIN

### **For Super Admins:**
- ✅ Monitor master registry sheet
- ✅ Use `ADD SCHOOL` for quick onboarding
- ✅ Keep service account credentials secure
- ✅ Regular backups of Google Sheets

---

## 🔐 **Security Reminders**

1. **Change default PIN** immediately after deployment
2. **Don't share** OTP codes
3. **Verify** payment confirmations match receipts
4. **Backup** Google Sheets weekly
5. **Monitor** admin phone numbers list

---

## 📞 **Support & Help**

**For Technical Issues:**
- Check deployment logs
- Verify environment variables
- Test WhatsApp webhook
- Check Google Sheets permissions

**For Usage Questions:**
- Type `HELP` in WhatsApp
- Check `FEATURES.md`
- See `TESTING.md` for examples

---

**That's it! SchoolSync 2.0 is designed to be intuitive and user-friendly. Most features are just a WhatsApp message away!** 🚀
