"""
Clean Database - Remove All Students and Parents
Prepares system for production with clean data
"""

from tools import get_creds, DEFAULT_SHEET_ID
import gspread

print("="*60)
print("   Database Cleanup - SchoolSync 2.0")
print("="*60)

# Connect to database
print("\n✓ Connecting to database...")
creds = get_creds()
client = gspread.authorize(creds)
sheet = client.open_by_key(DEFAULT_SHEET_ID)

# Clean Students_Fees
print("\n✓ Cleaning Students_Fees worksheet...")
try:
    ws_students = sheet.worksheet("Students_Fees")
    # Get total rows
    all_values = ws_students.get_all_values()
    total_students = len(all_values) - 1  # Minus header
    
    # Clear all data except header (row 1)
    if total_students > 0:
        ws_students.batch_clear([f"A2:I{len(all_values)}"])
        print(f"   ✅ Deleted {total_students} students")
    else:
        print("   ℹ️  Already empty")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Clean Parent_Registry
print("\n✓ Cleaning Parent_Registry worksheet...")
try:
    ws_parents = sheet.worksheet("Parent_Registry")
    all_values = ws_parents.get_all_values()
    total_parents = len(all_values) - 1
    
    if total_parents > 0:
        ws_parents.batch_clear([f"A2:D{len(all_values)}"])
        print(f"   ✅ Deleted {total_parents} parent registrations")
    else:
        print("   ℹ️  Already empty")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Clean Admissions
print("\n✓ Cleaning Admissions worksheet...")
try:
    ws_admissions = sheet.worksheet("Admissions")
    all_values = ws_admissions.get_all_values()
    total_admissions = len(all_values) - 1
    
    if total_admissions > 0:
        ws_admissions.batch_clear([f"A2:D{len(all_values)}"])
        print(f"   ✅ Deleted {total_admissions} admission leads")
    else:
        print("   ℹ️  Already empty")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Clean Attendance
print("\n✓ Cleaning Attendance worksheet...")
try:
    ws_attendance = sheet.worksheet("Attendance")
    all_values = ws_attendance.get_all_values()
    total_attendance = len(all_values) - 1
    
    if total_attendance > 0:
        ws_attendance.batch_clear([f"A2:D{len(all_values)}"])
        print(f"   ✅ Deleted {total_attendance} attendance records")
    else:
        print("   ℹ️  Already empty")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Clean Messages
print("\n✓ Cleaning Messages worksheet...")
try:
    ws_messages = sheet.worksheet("Messages")
    all_values = ws_messages.get_all_values()
    total_messages = len(all_values) - 1
    
    if total_messages > 0:
        ws_messages.batch_clear([f"A2:E{len(all_values)}"])
        print(f"   ✅ Deleted {total_messages} messages")
    else:
        print("   ℹ️  Already empty")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Summary
print("\n" + "="*60)
print("   CLEANUP COMPLETE!")
print("="*60)
print("\n✅ Database is now clean and ready for production")
print("\nNext steps:")
print("1. Add real students via WhatsApp: ADD STUDENT ...")
print("2. Register parents: REGISTER PARENT ...")
print("3. Start fresh with production data")
print("\n" + "="*60)
