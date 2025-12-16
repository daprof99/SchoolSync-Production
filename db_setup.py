import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import json

load_dotenv()

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "google_credentials.json"


def get_creds():
    """Get Google API credentials"""
    json_creds = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if json_creds:
        creds_dict = json.loads(json_creds)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    return ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)


def setup_school_database(sheet_id):
    """
    Initialize all required worksheets for a school's Google Sheet
    Creates missing worksheets and sets up proper headers
    """
    try:
        creds = get_creds()
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        
        # Get existing worksheet titles
        existing_sheets = {ws.title for ws in spreadsheet.worksheets()}
        
        # Define required sheets and their headers
        required_sheets = {
            "Students_Fees": [
                "Student_ID", "Surname", "First_Name", "Other_Names", "Class", 
                "Total Fees", "Amount Paid", "Notes", "Parent_Phone"
            ],
            "Admissions": [
                "Full_Name", "Parent_Phone", "Status", "Date_Submitted"
            ],
            "Attendance": [
                "Date", "Student_ID", "Time", "Status"
            ],
            "Policy": [
                "Keyword", "Answer"
            ],
            "Results": [
                "Student_ID", "Term", "Session", "Subject", "Score", "Grade", 
                "Position", "Upload_Date", "PDF_Link"
            ],
            "Messages": [
                "Date", "Parent_Phone", "Student_ID", "Message", "Status", 
                "Admin_Reply", "Reply_Date"
            ],
            "Events": [
                "Event_ID", "Title", "Description", "Date", "Time", "Type", 
                "Created_By", "Created_Date"
            ],
            "Parent_Registry": [
                "Parent_Phone", "Parent_Name", "Student_IDs", "Registration_Date"
            ],
            "Notifications_Queue": [
                "Queue_ID", "Recipient_Phone", "Message", "Type", "Scheduled_Time", 
                "Status", "Sent_Time"
            ]
        }
        
        created_sheets = []
        
        for sheet_name, headers in required_sheets.items():
            if sheet_name not in existing_sheets:
                # Create new worksheet
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=len(headers))
                worksheet.append_row(headers)
                created_sheets.append(sheet_name)
                print(f"✅ Created worksheet: {sheet_name}")
            else:
                print(f"⏭️  Worksheet already exists: {sheet_name}")
        
        if created_sheets:
            print(f"\n🎉 Successfully created {len(created_sheets)} new worksheets!")
        else:
            print("\n✅ All required worksheets already exist!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False


def initialize_all_schools(master_registry_id):
    """
    Initialize database schema for all schools in the master registry
    """
    try:
        creds = get_creds()
        client = gspread.authorize(creds)
        master = client.open_by_key(master_registry_id)
        records = master.get_worksheet(0).get_all_records()
        
        print(f"Found {len(records)} schools in registry\n")
        
        for row in records:
            school_name = row.get('School_Name', 'Unknown')
            sheet_id = row.get('Sheet_ID', '')
            
            if sheet_id:
                print(f"\n🏫 Setting up: {school_name}")
                setup_school_database(sheet_id)
        
        print("\n✅ All schools initialized!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    # Example: Setup a single school
    # setup_school_database("YOUR_SCHOOL_SHEET_ID_HERE")
    
    # Or setup all schools from master registry
    MASTER_REGISTRY_ID = "1iwpXaw4w6LBUkDEgEghfcO2FmY_RiNaKIDqbmdbL1Vs"
    
    print("=" * 60)
    print("   SchoolSync 2.0 - Database Setup Utility")
    print("=" * 60)
    print("\nThis will create missing worksheets in all school databases.")
    print("Existing worksheets will NOT be modified.\n")
    
    choice = input("Initialize all schools? (yes/no): ").strip().lower()
    
    if choice == "yes":
        initialize_all_schools(MASTER_REGISTRY_ID)
    else:
        print("\nSetup cancelled.")
