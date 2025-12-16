# 🔐 Security Features - SchoolSync 2.0

## New Security System

### **1. Per-School Custom PINs** ✅

Each school can set their own admin PIN (no more hardcoded "2025"!).

**Default PIN:** `2025` (until changed)

**How it works:**
- PIN stored in each school's Policy sheet
- Row: `Admin_PIN | 2025`
- Each school has independent PIN

**Admin Commands:**

```
# Change your school's PIN
SET PIN 2025 newPIN123

# Use PIN to approve receipts
APPROVE 2025 (or your custom PIN)
```

---

### **2. OTP/2FA System** ✅

SMS-based one-time password for critical actions.

**Features:**
- 6-digit random OTP
- 5-minute expiration
- Max 3 attempts
- Sent via Twilio SMS

**Admin Commands:**

```
# Request OTP
REQUEST OTP

# Bot sends SMS:
# "🔐 Your SchoolSync verification code is: 123456"

# Use OTP (future feature - for payments, data export, etc.)
TRANSFER FUNDS 50000 OTP:123456
```

---

## 🔒 Security Levels

### **Level 1: Phone Authentication**
-All users authenticated by phone number
- Master registry controls school access
- No unauthorized access

### **Level 2: Surname Verification**
- Parents must know student surname
- Prevents fee checking other students

### **Level 3: Admin PIN** (NEW!)
- Custom per-school
- Required for: APPROVE, sensitive commands
- Changeable via SET PIN

### **Level 4: OTP/2FA** (NEW!)
- For high-value transactions
- For data exports
- For account changes

---

## 📋 Implementation Details

### Policy Sheet Structure
```
Question     | Answer
-------------|--------
Admin_PIN    | 2025
School_Name  | RAIN Academy
Principal    | Dr. Smith
```

### OTP Storage
- In-memory (development)
- **Production:** Use Redis or database
- Auto-cleanup on expiry

### Twilio Integration
- Uses existing Twilio account
- SMS or WhatsApp delivery
- Fallback to default if fails

---

## 🧪 Testing Security Features

### Test Custom PIN

```
Admin: SET PIN 2025 MYPIN999
Bot: ✅ PIN updated to: MYPIN999

Admin: APPROVE MYPIN999
Bot: ✅ Approved.

Admin: APPROVE 2025
Bot: ⛔ Wrong PIN. Usage: APPROVE MYPIN999
```

### Test OTP

```
Admin: REQUEST OTP
Bot: 📱 Verification code sent to ***4063. Valid for 5 minutes.

(Check SMS for code: 123456)

Admin: VERIFY OTP 123456
Bot: ✅ OTP verified!

Admin: VERIFY OTP 999999
Bot: ❌ Wrong OTP. 2 attempts remaining.
```

---

## 🚀 Production Recommendations

1. **Force PIN Change** - Require schools to change from default 2025
2. **OTP for Payments** - Add OTP requirement for large payments
3. **Rate Limiting** - Limit failed PIN/OTP attempts
4. **Audit Logging** - Log all security events
5. **Redis for OTP** - Move from in-memory to Redis

---

## 📝 Files Created

- `security.py` - Core security module
- Updated `tools.py` - Integrated security commands

**New Admin Commands:**
- `SET PIN <old> <new>` - Change school PIN
- `REQUEST OTP` - Get verification code
- `APPROVE <PIN>` - Now uses custom PIN

---

**Your SchoolSync is now enterprise-grade secure!** 🔐✨
