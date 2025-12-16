import os
import io
import csv
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def check_export():
    # Get first school
    schools = supabase.table("schools").select("id, name").limit(1).execute()
    if not schools.data: 
        print("No schools found")
        return
    
    sid = schools.data[0]['id']
    print(f"Checking export for {schools.data[0]['name']} ({sid})")
    
    res = supabase.table("students").select("*").eq("school_id", sid).execute()
    students = res.data
    print(f"Found {len(students)} students.")
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student ID', 'Parent Name', 'Phone', 'Class', 'Total Fees', 'Paid', 'Balance'])
    
    for s in students:
        total = float(s.get('total_fees') or 0)
        paid = float(s.get('amount_paid') or 0)
        writer.writerow([
            s.get('id'), s.get('parent_name'), s.get('parent_phone'), s.get('student_class'),
            total, paid, total - paid
        ])
    
    content = output.getvalue()
    print(f"CSV Size: {len(content)} bytes")
    print("--- PREVIEW ---")
    print(content[:200])

if __name__ == "__main__":
    check_export()
