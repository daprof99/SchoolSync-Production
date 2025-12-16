# 🧪 Test: Role-Based HELP Command

## Objective
Verify that HELP command shows different content based on user role.

---

## Setup: Register Test Parent

**From your admin phone** (+2349075014063), send:
```
REGISTER PARENT +2348189678261, Test Parent, ST-962
```

Expected response:
```
✅ Registered: Test Parent with students: ST-962
```

---

## Test 1: Admin HELP (Your Phone)

**From**: +2349075014063 (Admin)  
**Send**: `HELP`

**Expected Response:**
```
📚 SchoolSync - Available Commands

**For Parents:**
• Check fees: CHECK ST-001 Surname
• View results: RESULTS ST-001 Surname
• Make payment: PAY 5000
• Message teacher: MESSAGE TEACHER [your message]
• Check events: When is the next meeting?
• Multiple children: ALL MY CHILDREN

**For Admins:**        ← Should see this section ✅
• Dashboard: SUMMARY
• Add student: ADD STUDENT...
• Attendance: CLOCKIN...
• Bill class: BILL CLASS...
• View messages: SHOW MESSAGES
• Add event: ADD EVENT...
• Change PIN: SET PIN...
• Register parent: REGISTER PARENT...
• Broadcast: BROADCAST ALL...

**Just ask naturally!**
Try: 'How much do I owe?' or 'Is there a meeting today?'
```

**✅ / ❌**: _____

---

## Test 2: Parent HELP (Test Account)

**From**: +2348189678261 (Parent - NOT admin)  
**Send**: `HELP`

**Expected Response:**
```
📚 SchoolSync - Available Commands

**For Parents:**
• Check fees: CHECK ST-001 Surname
• View results: RESULTS ST-001 Surname
• Make payment: PAY 5000
• Message teacher: MESSAGE TEACHER [your message]
• Check events: When is the next meeting?
• Multiple children: ALL MY CHILDREN

**Just ask naturally!**      ← NO admin section! ✅
Try: 'How much do I owe?' or 'Is there a meeting today?'
```

**✅ / ❌**: _____

---

## Comparison:

| User Type | Phone | Admin Section Visible? |
|-----------|-------|------------------------|
| Admin | +2349075014063 | ✅ YES |
| Parent | +2348189678261 | ❌ NO |

---

## Additional Tests (Optional):

### Test 3: Parent tries admin command
**From**: +2348189678261 (Parent)  
**Send**: `SUMMARY`

**Expected**: Should either work (if allowed) or be blocked/ignored

### Test 4: Parent checks fees
**From**: +2348189678261 (Parent)  
**Send**: `CHECK ST-962 Nnamdi`

**Expected**: Shows balance (should work - parent registered to ST-962)

---

## Success Criteria:

- [x] Test parent registered successfully
- [ ] Admin sees both parent + admin commands in HELP
- [ ] Parent sees ONLY parent commands in HELP
- [ ] Parent can still use parent features (CHECK, etc.)

**Status**: PASS / FAIL

**Notes:**
_________________________________
_________________________________
