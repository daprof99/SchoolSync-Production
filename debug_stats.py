import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def check_stats():
    # Get first school
    schools = supabase.table("schools").select("id, name").limit(1).execute()
    if not schools.data: return
    
    sid = schools.data[0]['id']
    print(f"Checking for {schools.data[0]['name']} ({sid})")
    
    res = supabase.table("students").select("total_fees, amount_paid").eq("school_id", sid).execute()
    students = res.data
    
    t_fees = sum(float(s['total_fees'] or 0) for s in students)
    t_paid = sum(float(s['amount_paid'] or 0) for s in students)
    
    print(f"Total Fees: {t_fees}")
    print(f"Total Paid: {t_paid}")
    
    if t_fees > 0:
        rate = (t_paid / t_fees) * 100
        print(f"Rate: {rate}%")
    else:
        print("Rate: 0 (No fees)")

if __name__ == "__main__":
    check_stats()
