import os
import json
import random
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# --- CONFIG ---
MOCK_CONFIG = {
    "Prince Dao College": {
         "classes": ["JSS1", "JSS2", "JSS3", "SSS1", "SSS2", "SSS3"],
         "subjects": ["Mathematics", "English", "Physics", "Chemistry", "Biology", "Economics"],
         "student_count": 30
    },
    "Aptitude nursery and primary school": {
        "classes": ["Creche", "Playgroup", "Nursery 1", "Nursery 2", "Kindergarten", "Basic 1", "Basic 2", "Basic 3", "Basic 4", "Basic 5", "Basic 6"],
        "subjects": ["Numeracy", "Literacy", "Science", "Social Studies", "Drawing"],
        "student_count": 40
    }
}

# Nigerian Names Dataset
FIRST_NAMES = [
    "Ade", "Chinedu", "Yusuf", "Funke", "Ngozi", "Musa", "Emeka", "Zainab", "Tola", "Amara",
    "Ibrahim", "Kehinde", "Chioma", "Olawale", "Fatima", "Kalu", "Bisi", "Sani", "Tunde", "Uche",
    "Aisha", "Bolaji", "Obi", "Rashida", "Femi", "Nneka", "Danjuma", "Simi", "Chike", "Halima",
    "Kemi", "Tope", "Efe", "Ahmed", "Titilayo", "Bassey", "Idris", "Folake", "Okoro", "Zarah"
]

LAST_NAMES = [
    "Adeleke", "Okonkwo", "Musa", "Balogun", "Eze", "Dangote", "Okafor", "Suleiman", "Awolowo", "Nnamdi",
    "Olawale", "Ibe", "Bello", "Akintola", "Obi", "Sanni", "Fashola", "Umar", "Okeke", "Lawal",
    "Ajayi", "Nwosu", "Mohammed", "Bakare", "Oni", "Igwe", "Abdullahi", "Coker", "Anozie", "Mustapha",
    "Adeyemi", "Chukwu", "Ibrahim", "Banjo", "Osagie", "Aliyu", "Dike", "Ojo", "Kyari", "Adebayo"
]

def generate_phone():
    prefixes = ['080', '081', '090', '070']
    return f"{random.choice(prefixes)}{random.randint(10000000, 99999999)}"

# Payment Logic for ~87% Rate
# 80% Full Pay, 15% Part Pay (50%), 5% No Pay
def get_payment_status(fee):
    dice = random.random()
    if dice < 0.80: return fee # Full
    elif dice < 0.95: return fee / 2 # Part
    else: return 0 # None

def seed_school(school_name, config):
    print(f"\n🌱 Seeding {school_name}...")
    
    # 1. Get School ID
    matches = []
    res = supabase.table("schools").select("id, name").eq("name", school_name).execute()
    if res.data: matches = res.data
    else:
        all_res = supabase.table("schools").select("id, name").execute()
        for s in all_res.data:
            if school_name.lower() in s['name'].lower() or s['name'].lower() in school_name.lower():
                matches.append(s)
                break
                
    if not matches:
        print(f"❌ School '{school_name}' not found.")
        return

    school_id = matches[0]['id']
    print(f"   Found ID: {school_id} ({matches[0]['name']})")

    # SPECIAL LOGIC FOR PRINCE DAO COLLEGE
    if "Prince Dao" in school_name:
        print("   🧹 Clearing existing students for cleaner sequential IDs...")
        supabase.table("students").delete().eq("school_id", school_id).execute()
        
        # Exact Class Order as requested: SSS3 -> JSS1
        ordered_classes = ["SSS3", "SSS2", "SSS1", "JSS3", "JSS2", "JSS1"]
        serial_counter = 1
        
        print("   🚀 Generating Sequential Data (Sorted Alphabetically)...")
        
        for cls_name in ordered_classes:
            if cls_name not in config['classes']: continue # Skip if not in config
            
            # 14-25 students
            count = random.randint(14, 25)
            
            # Generate temporary list of names to sort
            class_roster = []
            for _ in range(count):
                last = random.choice(LAST_NAMES)
                first = random.choice(FIRST_NAMES)
                class_roster.append((last, first))
            
            # Sort Alphabetically by Surname
            class_roster.sort(key=lambda x: x[0])
            
            # Determine Fee
            fee = 100000 if "SSS" in cls_name else 85000
            
            for last, first in class_roster:
                # Generate ID: PDC-001, PDC-002...
                sid = f"PDC-{serial_counter:03d}"
                serial_counter += 1
                
                # Payment Status (New Logic)
                paid = get_payment_status(fee)
                
                st_data = {
                    "school_id": school_id,
                    "id": sid,
                    "surname": last,
                    "first_name": first,
                    "other_name": "",
                    "student_class": cls_name,
                    "parent_name": f"Mr/Mrs {last}",
                    "parent_phone": generate_phone(),
                    "total_fees": fee,
                    "amount_paid": paid
                }
                supabase.table("students").insert(st_data).execute()
                
            print(f"      ✅ {cls_name}: Added {count} students. (Last ID: {sid})")
            
        print("   ✅ Prince Dao College population complete.")
        return

    # GENERIC LOGIC FOR OTHER SCHOOLS
    # Same cleaning needed? User said "do same for aptitude".
    print("   🧹 Clearing existing students for fresh rewrite...")
    supabase.table("students").delete().eq("school_id", school_id).execute()

    print(f"   Generating students for ALL classes...")
    students = []
    
    for cls_name in config['classes']:
        # Determine Fee based on level
        fee = 50000
        if "JSS" in cls_name: fee = 85000
        elif "SSS" in cls_name: fee = 100000
        elif "Basic" in cls_name: fee = 60000
        elif "Nursery" in cls_name: fee = 55000
        
        # Add 15 students per class (Generic)
        for i in range(15): 
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            sid = f"{cls_name[:3].upper()}-{random.randint(100, 999)}"
            
            # Payment Status
            paid = get_payment_status(fee)
            
            st_data = {
                "school_id": school_id,
                "id": sid,
                "surname": last,
                "first_name": first,
                "other_name": "",
                "student_class": cls_name,
                "parent_name": f"Mr/Mrs {last}",
                "parent_phone": generate_phone(),
                "total_fees": fee,
                "amount_paid": paid
            }
            
            try:
                supabase.table("students").insert(st_data).execute()
                students.append(st_data)
            except: pass 
            
    print(f"   ✅ Added {len(students)} new students.")
    # ... existing attendance logic ...
    # ... (rest of logic same)
    
    # 3. Seed Attendance (Today)
    print("   Marking attendance...")
    today = datetime.now().strftime('%Y-%m-%d')
    # Mark 60% present
    present_students = random.sample(students, k=int(len(students) * 0.6))
    for s in present_students:
        try:
            # Random time today between 7:30 and 8:30
            h = 7
            m = random.randint(30, 59)
            if random.random() > 0.5: 
                h = 8
                m = random.randint(0, 30)
            
            ts = datetime.now().replace(hour=h, minute=m, second=0).isoformat()
            
            supabase.table("attendance").insert({
                "school_id": school_id,
                "student_id": s['id'],
                "date": today,
                "timestamp": ts,
                "status": "Present"
            }).execute()
        except: pass
        
    print("   ✅ Attendance marked.")

    # 4. Seed Events
    print("   Creating events...")
    events = [
        {"title": "PTA Meeting", "type": "PTA", "days_offset": 5},
        {"title": "Inter-House Sports", "type": "Sports", "days_offset": 14}, 
        {"title": "Mid-Term Break", "type": "Holiday", "days_offset": 20},
        {"title": "Mock Exams", "type": "Academic", "days_offset": 2}
    ]
    
    for e in events:
        d = (datetime.now() + timedelta(days=e['days_offset'])).strftime('%Y-%m-%d')
        try:
            supabase.table("events").insert({
                "school_id": school_id,
                "title": e['title'],
                "date": d,
                "time": "09:00",
                "type": e['type']
            }).execute()
        except: pass
        
    print("   ✅ Events created.")
    
    # 5. Seed Results (Random for a few students)
    print("   Generating results...")
    for s in students[:5]: # just 5 students
        for sub in config['subjects']:
            score = random.randint(40, 95)
            grade = 'A' if score >= 70 else 'B' if score >= 60 else 'C' if score >= 50 else 'D'
            try:
                supabase.table("results").insert({
                    "student_id": s['id'],
                    "subject": sub,
                    "score": score,
                    "grade": grade,
                    "term": "1st",
                    "session": "2024/2025"
                }).execute()
            except: pass
            
    print("   ✅ Results generated.")


def main():
    print("🚀 Starting Data Seeding...")
    for name, conf in MOCK_CONFIG.items():
        seed_school(name, conf)
    print("\n✨ Seeding Complete!")

if __name__ == "__main__":
    main()
