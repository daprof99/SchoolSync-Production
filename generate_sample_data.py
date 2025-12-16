"""
Sample Data Generator for SchoolSync 2.0
Generates 50 realistic Nigerian students with families, fees, and test data
"""

import random
import gspread
from tools import get_creds, ADMIN_PHONES, get_db_connection
from datetime import date, timedelta

# Nigerian names
SURNAMES = [
    "Okafor", "Adebayo", "Okonkwo", "Ibrahim", "Musa", "Chukwu", "Oluwaseun",
    "Eze", "Nwosu", "Ajayi", "Bello", "Oladele", "Uzoma", "Danjuma", "Okoro",
    "Bakare", "Nnadi", "Yusuf", "Ojo", "Nnamdi", "Hassan", "Olabisi", "Igwe",
    "Chioma", "Abdullahi", "Emeka", "Kalu", "Ogbonna", "Suleiman", "Chinedu"
]

FIRST_NAMES_MALE = [
    "Chukwuemeka", "Olumide", "Tunde", "Segun", "Babatunde", "Chijioke",
    "Adewale", "Kunle", "Nnamdi", "Ifeanyi", "Mohammed", "Abubakar",
    "Temitope", "Olusegun", "Chima", "Obinna", "Tolu", "Kayode", "Femi",
    "Ahmed", "Yakubu", "Chiamaka", "Ikenna", "Uchenna", "Ngozi"
]

FIRST_NAMES_FEMALE = [
    "Amara", "Chidinma", "Funmilayo", "Ngozi", "Yetunde", "Chiamaka",
    "Adeola", "Blessing", "Fatima", "Zainab", "Kemi", "Temi", "Adunni",
    "Nneka", "Ifeyinwa", "Halima", "Aisha", "Oluchi", "Bukola", "Folake",
    "Oluwatoyin", "Chinwe", "Amarachi", "Ifeoma", "Nkechi"
]

OTHER_NAMES = [
    "Oluwaseun", "Emmanuel", "Grace", "Peace", "Joy", "Michael", "David",
    "Daniel", "Samuel", "John", "Mary", "Esther", "Ruth", "Faith", "Hope",
    "Favour", "Divine", "Precious", "Gift", "Miracle", "Victory", "Light"
]

CLASSES = ["JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3"]

def generate_phone():
    """Generate realistic Nigerian phone number"""
    prefixes = ["0803", "0806", "0813", "0817", "0818", "0701", "0708", "0802", "0805", "0807", "0809", "0810", "0814", "0816"]
    return f"+234{random.choice(prefixes)[1:]}{random.randint(1000000, 9999999)}"

def generate_students(count=50):
    """Generate student data"""
    students = []
    used_ids = set()
    
    for i in range(count):
        # Generate unique student ID
        while True:
            student_id = f"ST-{random.randint(100, 999)}"
            if student_id not in used_ids:
                used_ids.add(student_id)
                break
        
        # Random gender
        is_male = random.choice([True, False])
        
        student = {
            "id": student_id,
            "surname": random.choice(SURNAMES),
            "first_name": random.choice(FIRST_NAMES_MALE if is_male else FIRST_NAMES_FEMALE),
            "other_names": random.choice(OTHER_NAMES),
            "class": random.choice(CLASSES),
            "total_fees": random.choice([45000, 50000, 55000, 60000, 65000, 70000]),
            "amount_paid": 0,  # Will be randomized later
            "notes": "",
            "parent_phone": generate_phone()
        }
        
        # Some students have partial payments
        if random.random() > 0.3:  # 70% have made some payment
            payment_percentage = random.choice([0.25, 0.5, 0.75, 1.0, 1.2])  # Some overpaid
            student["amount_paid"] = int(student["total_fees"] * payment_percentage)
        
        # Some have notes
        if random.random() > 0.8:
            notes_options = [
                "Bus fee included", "Early bird discount", "Sibling discount",
                "Payment plan: 3 installments", "Scholarship recipient"
            ]
            student["notes"] = random.choice(notes_options)
        
        students.append(student)
    
    return students

def generate_parent_registry(students):
    """Group students by parent phone (siblings)"""
    parents = {}
    
    # Group students by families (some share parents)
    for student in students:
        # 20% chance of having a sibling
        if random.random() > 0.8 and len(parents) > 0:
            # Assign to existing parent with same surname
            matching_parents = [p for p, data in parents.items() 
                              if any(s["surname"] == student["surname"] for s in data["students"])]
            if matching_parents:
                parent_phone = random.choice(matching_parents)
                parents[parent_phone]["students"].append(student)
                student["parent_phone"] = parent_phone
                continue
        
        # New parent
        if student["parent_phone"] not in parents:
            parent_name = f"Mr/Mrs {student['surname']}"
            parents[student["parent_phone"]] = {
                "name": parent_name,
                "students": [student]
            }
    
    return parents

def generate_events():
    """Generate sample school events"""
    today = date.today()
    events = [
        {
            "title": "PTA Meeting",
            "description": "General PTA meeting to discuss term progress",
            "date": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
            "time": "10:00",
            "type": "PTA"
        },
        {
            "title": "Inter-House Sports",
            "description": "Annual sports competition",
            "date": (today + timedelta(days=14)).strftime("%Y-%m-%d"),
            "time": "08:00",
            "type": "Sports"
        },
        {
            "title": "Mid-Term Exams",
            "description": "Mid-term examination period",
            "date": (today + timedelta(days=21)).strftime("%Y-%m-%d"),
            "time": "09:00",
            "type": "Academic"
        },
        {
            "title": "Parents Open Day",
            "description": "Meet your child's teachers",
            "date": (today + timedelta(days=30)).strftime("%Y-%m-%d"),
            "time": "11:00",
            "type": "PTA"
        },
        {
            "title": "Career Day",
            "description": "Guest speakers on career paths",
            "date": (today + timedelta(days=45)).strftime("%Y-%m-%d"),
            "time": "10:00",
            "type": "Career"
        }
    ]
    return events

def populate_database():
    """Populate Google Sheets with sample data"""
    print("\n" + "="*60)
    print("   SchoolSync 2.0 - Sample Data Generator")
    print("="*60)
    
    # Get database connection - use direct connection
    print("\n📊 Connecting to database...")
    try:
        from tools import DEFAULT_SHEET_ID
        creds = get_creds()
        client = gspread.authorize(creds)
        sheet = client.open_by_key(DEFAULT_SHEET_ID)
        
        print(f"✅ Connected to: {sheet.title}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Generate data
    print("\n🎲 Generating 50 students...")
    students = generate_students(50)
    print(f"✅ Generated {len(students)} students")
    
    print("\n👨‍👩‍👧‍👦 Creating parent registry...")
    parents = generate_parent_registry(students)
    print(f"✅ Created {len(parents)} parent accounts")
    
    print("\n📅 Generating events...")
    events = generate_events()
    print(f"✅ Generated {len(events)} events")
    
    # Populate Students_Fees
    print("\n📝 Adding students to Students_Fees sheet...")
    try:
        ws_students = sheet.worksheet("Students_Fees")
        
        for student in students:
            ws_students.append_row([
                student["id"],
                student["surname"],
                student["first_name"],
                student["other_names"],
                student["class"],
                student["total_fees"],
                student["amount_paid"],
                student["notes"],
                student["parent_phone"]
            ])
        
        print(f"✅ Added {len(students)} students")
    except Exception as e:
        print(f"❌ Error adding students: {e}")
    
    # Populate Parent_Registry
    print("\n📱 Adding parents to Parent_Registry...")
    try:
        ws_parents = sheet.worksheet("Parent_Registry")
        
        for phone, data in parents.items():
            student_ids = ",".join([s["id"] for s in data["students"]])
            ws_parents.append_row([
                phone,
                data["name"],
                student_ids,
                date.today().strftime("%Y-%m-%d")
            ])
        
        print(f"✅ Added {len(parents)} parent registrations")
    except Exception as e:
        print(f"❌ Error adding parents: {e}")
    
    # Populate Events
    print("\n📅 Adding events to Events sheet...")
    try:
        ws_events = sheet.worksheet("Events")
        
        for i, event in enumerate(events):
            event_id = f"EVT-{date.today().strftime('%Y%m%d')}{i:03d}"
            ws_events.append_row([
                event_id,
                event["title"],
                event["description"],
                event["date"],
                event["time"],
                event["type"],
                ADMIN_PHONES[0],
                date.today().strftime("%Y-%m-%d")
            ])
        
        print(f"✅ Added {len(events)} events")
    except Exception as e:
        print(f"❌ Error adding events: {e}")
    
    # Sample results for a few students
    print("\n📊 Adding sample results...")
    try:
        ws_results = sheet.worksheet("Results")
        subjects = ["Mathematics", "English", "Biology", "Chemistry", "Physics", "Economics"]
        
        # Add results for first 10 students
        for student in students[:10]:
            for subject in subjects:
                score = random.randint(40, 98)
                grade = "A" if score >= 75 else "B" if score >= 65 else "C" if score >= 50 else "D"
                
                ws_results.append_row([
                    student["id"],
                    "First Term",
                    "2024/2025",
                    subject,
                    score,
                    grade,
                    "",  # Position
                    date.today().strftime("%Y-%m-%d"),
                    ""  # PDF link
                ])
        
        print(f"✅ Added results for 10 students")
    except Exception as e:
        print(f"❌ Error adding results: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("✅ DATA POPULATION COMPLETE!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  • Students: {len(students)}")
    print(f"  • Parents: {len(parents)}")
    print(f"  • Events: {len(events)}")
    print(f"  • Results: 10 students × 6 subjects")
    
    # Calculate statistics
    total_fees = sum(s["total_fees"] for s in students)
    total_paid = sum(s["amount_paid"] for s in students)
    total_owing = total_fees - total_paid
    debtors = sum(1 for s in students if s["total_fees"] - s["amount_paid"] > 0)
    
    print(f"\n💰 Financial Summary:")
    print(f"  • Total Fees: ₦{total_fees:,}")
    print(f"  • Amount Paid: ₦{total_paid:,}")
    print(f"  • Outstanding: ₦{total_owing:,}")
    print(f"  • Debtors: {debtors}/{len(students)}")
    
    # Sample test commands
    print(f"\n🧪 Test Commands:")
    sample_student = students[0]
    sample_parent = list(parents.keys())[0]
    
    print(f"\n  Test with WhatsApp:")
    print(f"  1. CHECK {sample_student['id']} {sample_student['surname']}")
    print(f"  2. RESULTS {sample_student['id']} {sample_student['surname']}")
    print(f"  3. When is the next PTA meeting?")
    print(f"  4. ALL MY CHILDREN (from: {sample_parent})")
    print(f"  5. SUMMARY (admin only)")
    
    print("\n🎉 Ready to test!")

if __name__ == "__main__":
    populate_database()
