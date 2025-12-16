# SchoolSync 2.0 - Multi-School SaaS Architecture

## Current Setup

**Master Registry Sheet:** ID `1iwpXaw4w6LBUkDEgEghfcO2FmY_RiNaKIDqbmdbL1Vs`

This sheet has columns:
- School_Name
- Phone (admin phone number)
- Sheet_ID (Google Sheet ID for that school)
- Results_Folder_ID (optional)

**How Routing Works:**
1. Parent/Admin sends WhatsApp message
2. System looks up their phone in Master Registry
3. Routes to their school's Google Sheet
4. All operations happen in that school's data

---

## Adding a New School (Current Manual Process)

### Step 1: Create School's Google Sheet
1. Create new Google Sheet
2. Share with service account email
3. Copy the Sheet ID

### Step 2: Run Database Setup
```bash
python -c "from db_setup import setup_school_database; setup_school_database('NEW_SHEET_ID_HERE')"
```

### Step 3: Add to Master Registry
Open master registry sheet and add row:
```
School_Name: St. Patrick's Academy
Phone: +2348012345678
Sheet_ID: 1ABC123...xyz
Results_Folder_ID: (optional)
```

### Step 4: Test
Send WhatsApp message from that phone number - should route to new school!

---

## NEW: Add School via WhatsApp (Enhanced)

I'll create an admin command to do this automatically via WhatsApp.

**Super Admin Command:**
```
ADD SCHOOL St. Patrick's Academy, +2348012345678, admin@stpatrick.com
```

This will:
1. Create Google Sheet for the school
2. Setup all worksheets
3. Add to master registry
4. Send confirmation with credentials

---

## Current Schools

You currently have:
- **RAIN Academy** (your test school)

**Want me to:**
1. Create the "ADD SCHOOL" WhatsApp command?
2. Build a web portal for school onboarding?
3. Show you how to manually add schools now?
