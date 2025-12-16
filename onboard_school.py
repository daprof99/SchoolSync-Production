
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

SUPER_ADMIN_PHONES = ["2349075014063"]

def onboard_new_school(school_name, admin_phone, admin_email=None):
    """
    Onboard a new school to Supabase
    """
    print("\n" + "="*60)
    print(f"   Onboarding: {school_name}")
    print("="*60)
    
    try:
        # Check if exists
        res = supabase.table("schools").select("*").eq("admin_phone", admin_phone).execute()
        if res.data:
             return {"success": False, "error": "Admin phone already registered to a school."}

        # Insert
        data = {
            "name": school_name,
            "admin_phone": admin_phone,
            "admin_email": admin_email
        }
        res = supabase.table("schools").insert(data).execute()
        
        # Get ID
        new_school = res.data[0]
        school_id = new_school['id']

        print(f"✅ School Created! ID: {school_id}")
        
        return {
            "success": True,
            "school_name": school_name,
            "admin_phone": admin_phone,
            "sheet_id": school_id, # return ID as reference
            "message": f"🎉 **{school_name} Onboarded!**\nID: {school_id}"
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("SchoolSync Supabase Onboarding")
    name = input("Name: ")
    phone = input("Phone: ")
    onboard_new_school(name, phone)
