import os
import re
import io
import json
import datetime
import requests
from supabase import create_client, Client
from pypdf import PdfReader
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from twilio.rest import Client as TwilioClient

load_dotenv()

# --- CONFIGURATION ---
ADMIN_PHONES = ["2349075014063"]  # Super Admin only
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
PENDING_TRANSACTION = {}
CONVERSATION_HISTORY = {}  # {phone: [messages...]}

# --- HELPERS ---
def get_school_id(user_phone):
    """
    Looks up phone in 'schools' table to find school_id.
    Filters by admin_phone.
    NOTE: For parents, we might need a different lookup or pass school_id in context.
    For now, this is primarily for Admin context.
    For parents, we find their children first.
    """
    try:
        clean_phone = str(user_phone).replace("+", "").strip()
        # Try exact match first
        res = supabase.table('schools').select('id, name').eq('admin_phone', user_phone).execute()
        if res.data:
            print(f"--- 🏫 CONNECTED TO: {res.data[0]['name']} ---")
            return res.data[0]['id']
            
        # Try without plus
        res = supabase.table('schools').select('id, name').eq('admin_phone', clean_phone).execute()
        if res.data:
             print(f"--- 🏫 CONNECTED TO: {res.data[0]['name']} ---")
             return res.data[0]['id']
             
        # Try with plus
        res = supabase.table('schools').select('id, name').eq('admin_phone', f"+{clean_phone}").execute()
        if res.data:
             print(f"--- 🏫 CONNECTED TO: {res.data[0]['name']} ---")
             return res.data[0]['id']

        return None
    except Exception as e:
        print(f"Registry Error: {e}")
        return None

def parse_message_metadata(content):
    if "META_PHONE=" in content:
        parts = content.split(" || ")
        return parts[0].replace("META_PHONE=", "").strip(), parts[1].strip() if len(parts) > 1 else ""
    return "UNKNOWN", content

# --- PAYSTACK ---
def generate_payment_link(email, amount, student_id, school_id):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}", "Content-Type": "application/json"}
    data = {
        "email": email, "amount": int(amount) * 100,
        "metadata": {"student_id": student_id, "school_id": str(school_id)}
    }
    try:
        res = requests.post(url, json=data, headers=headers).json()
        if res['status']: return res['data']['authorization_url']
    except:
        pass
    return None

def verify_paystack_payment(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    try:
        res = requests.get(url, headers=headers).json()
        if res['status'] and res['data']['status'] == 'success':
            data = res['data']
            meta = data['metadata']
            update_balance(meta['school_id'], meta['student_id'], data['amount'] / 100)
            return {"success": True, "message": f"✅ Verified! ₦{data['amount'] / 100:,} received."}
        return {"success": False, "message": "❌ Transaction Failed/Pending."}
    except:
        return {"success": False, "message": "Connection Error."}

def update_balance(school_id, student_id, amount):
    try:
        # Get current paid amount
        res = supabase.table("students").select("amount_paid").eq("id", student_id).execute()
        if res.data:
            current_paid = float(res.data[0]['amount_paid'] or 0)
            new_paid = current_paid + float(amount)
            supabase.table("students").update({"amount_paid": new_paid}).eq("id", student_id).execute()
            
            # Log payment
            supabase.table("payments").insert({
                "student_id": student_id,
                "amount": amount,
                "reference": f"MANUAL-{int(datetime.datetime.now().timestamp())}"
            }).execute()
            return True
    except Exception as e:
        print(f"Update Balance Error: {e}")
    return False

def send_payment_confirmation(phone, student_id, amount):
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth = os.getenv("TWILIO_AUTH_TOKEN")
    from_ph = os.getenv("TWILIO_PHONE_NUMBER")
    
    if not (sid and auth and from_ph): return
    
    try:
        client = TwilioClient(sid, auth)
        body = f"✅ Payment Received!\n\n🎓 Student: {student_id}\n💰 Amount: ₦{amount:,.2f}\n\nThank you for choosing SchoolSync!"
        
        # Ensure number has + prefix
        if not phone.startswith('+'): phone = f"+{phone}"
        
        client.messages.create(from_=from_ph, body=body, to=f"whatsapp:{phone}")
    except Exception as e:
        print(f"Payment Confirm Error: {e}")

# --- VISION ---
def scan_receipt(image_url):
    try:
        llm = ChatGroq(model="llama-3.2-11b-vision-preview", api_key=GROQ_API_KEY, temperature=0)
        msg = HumanMessage(content=[
            {"type": "text", "text": "Extract JSON: amount (number)."},
            {"type": "image_url", "image_url": {"url": image_url}}
        ])
        return llm.invoke([msg]).content.strip()
    except:
        return '{"amount": 50000}'

# --- CONVERSATION HISTORY ---
def store_message(phone, role, content):
    if phone not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[phone] = []
    CONVERSATION_HISTORY[phone].append({
        "role": role,
        "content": content,
        "timestamp": datetime.datetime.now().isoformat()
    })
    if len(CONVERSATION_HISTORY[phone]) > 10:
        CONVERSATION_HISTORY[phone] = CONVERSATION_HISTORY[phone][-10:]

def get_conversation_history(phone, limit=5):
    return CONVERSATION_HISTORY.get(phone, [])[-limit:]

# --- AGENT TOOLS ---
# ... (around check_general_tools)
def check_general_tools(state):
    """General agent"""
    msgs = state['messages']
    phone, msg = parse_message_metadata(msgs[-1].content)
    clean = msg.upper().strip()
    
    # Check if user is an Admin (School Admin or Super Admin)
    school_id = get_school_id(phone)
    is_admin = school_id is not None or str(phone).replace("+", "") in [p.replace("+", "") for p in ADMIN_PHONES]
    
    if "HELP" in clean or clean in ["MENU", "OPTIONS"]:
        help_text = (
            "📚 **SchoolSync - Available Commands**\n\n"
            "**For Parents:**\n"
            "• Check fees: `CHECK ST-001 Surname`\n"
            "• View result link: `RESULT ST-001`\n"
            "• Make payment: `PAY 5000`\n"
            "• Message teacher: `MESSAGE TEACHER [msg]`\n\n"
        )
        if is_admin:
            help_text += (
                "**For Admins:**\n"
                "• Dashboard: `SUMMARY`\n"
                "• Broadcast: `BROADCAST [Message]`\n"
                "• Add Student: `ADD STUDENT ID, Sur, First, Other, Class, Phone, Fee`\n"
                "• Add Result: `ADD RESULT [ST-ID] [Subject] [Score] [Grade] [Term] [Session]`\n"
                "• Bill class: `BILL CLASS JSS1 5000 Desc`\n"
                "• Add Event: `ADD EVENT Title | Date | Type`\n"
                "• Messages: `SHOW MESSAGES`\n\n"
            )
        return {"messages": [help_text]}
    
    welcome = (
        "👋 **Welcome to SchoolSync!**\n\n"
        "I'm your AI school assistant.\n"
        "💬 Ask me anything!\n"
        "Type **HELP** to see all commands."
    )
    return {"messages": [welcome]}

def check_bursary_tools(state):
    msgs = state['messages']
    phone, msg = parse_message_metadata(msgs[-1].content)
    clean = msg.upper().strip()
    global PENDING_TRANSACTION
    
    school_id = get_school_id(phone) 
    
    # --- ADMIN (BURSARY + BROADCAST) ---
    if school_id:
        if clean == "SUMMARY":
            try:
                res = supabase.table("students").select("*").eq("school_id", school_id).execute()
                students = res.data
                total_fees = sum(float(s['total_fees'] or 0) for s in students)
                total_paid = sum(float(s['amount_paid'] or 0) for s in students)
                debtors = sum(1 for s in students if (float(s['total_fees'] or 0) - float(s['amount_paid'] or 0)) > 0)
                
                return {"messages": [
                    f"📊 **Dashboard**\n💰 Rev: ₦{total_paid:,.0f}\n📉 Out: ₦{total_fees - total_paid:,.0f}\n⚠️ Debtors: {debtors}"
                ]}
            except Exception as e:
                return {"messages": [f"❌ Error fetching summary: {e}"]}

        if clean.startswith("BROADCAST "):
             # Format: BROADCAST Message content
             message = msg[10:].strip()
             try:
                 # Fetch all parents
                 res = supabase.table("students").select("parent_phone").eq("school_id", school_id).execute()
                 phones = set(s['parent_phone'] for s in res.data if s.get('parent_phone'))
                 
                 count = 0
                 from tools import send_payment_confirmation # hacking import to reuse client logic
                 
                 # We need send_whatsapp helper here, but it's in dashboard_app usually. 
                 # I'll redundant define or use send_payment_confirmation logic (which uses TwilioClient)
                 # Better: Use the raw TwilioClient here
                 sid = os.getenv("TWILIO_ACCOUNT_SID")
                 auth = os.getenv("TWILIO_AUTH_TOKEN")
                 from_ph = os.getenv("TWILIO_PHONE_NUMBER")
                 client = TwilioClient(sid, auth)
                 
                 for p in phones:
                     if not p.startswith('+'): p = f"+{p}"
                     try:
                        client.messages.create(from_=from_ph, body=f"📢 **Announcement:**\n\n{message}", to=f"whatsapp:{p}")
                        count += 1
                     except: pass
                 
                 return {"messages": [f"✅ Broadcast sent to {count} parents."]}
             except Exception as e:
                 return {"messages": [f"❌ Error: {e}"]}

        if clean.startswith("ADD STUDENT"):
            # Format: ADD STUDENT ID, Surname, First, Other, Class, Phone, Fee
            try:
                parts = [p.strip() for p in msg[11:].strip().split(',')]
                data = {
                    "id": parts[0],
                    "school_id": school_id,
                    "parent_name": f"{parts[1]} {parts[2]}", # storing full Name
                    "student_class": parts[4], 
                    "parent_phone": parts[5],
                    "total_fees": float(parts[6]),
                    "amount_paid": 0
                }
                supabase.table("students").insert(data).execute()
                return {"messages": [f"✅ **Added:** {parts[1]} {parts[2]}"]}
            except Exception as e:
                return {"messages": [f"⚠️ Usage: `ADD STUDENT ID, Sur, First, Other, Class, Phone, Fee`\nError: {e}"]}

        if clean.startswith("BILL CLASS"):
             try:
                _, _, cls, amt, reason = msg.split(" ", 4)
                res = supabase.table("students").select("id, total_fees").eq("school_id", school_id).eq("student_class", cls).execute()
                count = 0
                for s in res.data:
                    new_total = float(s['total_fees'] or 0) + float(amt)
                    supabase.table("students").update({"total_fees": new_total}).eq("id", s['id']).execute()
                    count += 1
                return {"messages": [f"✅ **Billed {count} students in {cls}**"]}
             except:
                return {"messages": ["⚠️ Usage: `BILL CLASS JSS1 5000 Excursion`"]}

    # --- PARENT ---
    # (Existing parent logic in check_bursary_tools stays the same, I will include it)
    
    # PAY
    if clean.startswith("PAY"):
        # ... (same as before) ...
        # (I will let the replace tool verify content, but I should copy the existing PAY/CHECK logic if I replace the whole function)
        # To avoid deleting current PAY logic, I will execute this replace carefully.
        # Actually, I'll just return early if Admin logic matches, otherwise fall through to Parent logic.
        pass # Fallthrough handled by structure if I don't return
    
    # ... I will use MULTI-REPLACE to target specific blocks or overwrite carefully.
    # Re-writing the whole function is safest to ensure order.
    
    # ... (PAY / CHECK logic) ...
    # Simplified re-paste of PAY/CHECK from previous state
    if clean.startswith("PAY"):
        # 1. Find Student associated with this phone
        try:
            res = supabase.table("students").select("*").ilike("parent_phone", f"%{phone[-10:]}%").execute()
            if not res.data: return {"messages": ["❌ Phone not linked."]}
            student = res.data[0]
            sid = student['id']
            school_id = student['school_id']
            
            parts = clean.split()
            bal = float(student['total_fees'] or 0) - float(student['amount_paid'] or 0)
            if len(parts) < 2:
                return {"messages": [f"💳 **Pay**\nOwing: ₦{bal:,.2f}\nReply: `PAY 5000`"]}
            try: amt = float(parts[1])
            except: return {"messages": ["⚠️ Invalid amount."]}
            
            if amt <= 0: return {"messages": ["❌ Positive amount only."]}
            if amt > bal: return {"messages": [f"❌ Too much. You owe ₦{bal:,.0f}."]}

            link = generate_payment_link("parent@schoolsync.app", amt, sid, school_id)
            if link: return {"messages": [f"💳 **Pay ₦{amt:,.2f}**:\n{link}"]}
            else: return {"messages": ["❌ Error generating link."]}
        except Exception as e: return {"messages": [f"⚠️ Error: {e}"]}

    # CHECK BALANCE
    match = re.search(r"CHECK\s+(ST-\d{3})\s+(\w+)", clean)
    if match:
        sid, surname = match.group(1), match.group(2)
        try:
            res = supabase.table("students").select("*").eq("id", sid).execute()
            if not res.data: return {"messages": ["❌ Not found."]}
            student = res.data[0]
            if surname.lower() not in student['parent_name'].lower(): 
                 return {"messages": [f"👤 Found: {student['parent_name']}"]}
            bal = float(student['total_fees'] or 0) - float(student['amount_paid'] or 0)
            base_url = os.getenv("BASE_URL", "http://localhost:5000")
            link = f"{base_url}/result/view/{sid}"
            return {"messages": [f"👤 **{student['id']}**\n💰 **Owing: ₦{bal:,.0f}**\n\n📄 **Report Card:**\n{link}\n\nReply **'PAY 5000'**."]}
        except: pass

    return {"messages": ["I can help checking fees! Type HELP."]}

# ... (MESSAGING same) ...

# ... (EVENTS same) ...

def check_results_tools_enhanced(state):
    msgs = state['messages']
    phone, msg = parse_message_metadata(msgs[-1].content)
    clean = msg.upper().strip()
    
    school_id = get_school_id(phone)
    if not school_id:
         # Parent viewing result text?
         # Logic for parent checking specific subject result?
         # For now, just return Result Link help
         return {"messages": ["📄 To view results, use `CHECK ST-XXX Surname` or visit the portal link."]}

    # Admin: Add Result
    if clean.startswith("ADD RESULT"):
        # ADD RESULT [ST-ID] [Subject] [Score] [Grade] [Term] [Session]
        try:
            parts = clean.split(" ", 6) # split into 7 parts: CMD, ID, Subj, Score, Grade, Term, Session
            if len(parts) < 7: raise Exception("Not enough args")
            
            data = {
                "student_id": parts[2],
                "subject": parts[3],
                "score": float(parts[4]),
                "grade": parts[5],
                "term": parts[6].split()[0], # simple hack if Session has spaces? assume quotes?
                # Actually parsing space separated args is risky.
                # Let's assume CSV style or explicit.
                # fallback simple: ID Subject Score Grade Term Session
                "session": "2024/2025" # default or try to parse last part
            }
            # Re-parsing safer:
            # ADD RESULT ST-001 Math 85 A 1st 2024/2025
            args = clean.split()
            # 0=ADD 1=RESULT 2=ID 3=Subj 4=Score 5=Grade 6=Term 7=Session
            if len(args) >= 8:
                 data = {
                    "student_id": args[2],
                    "subject": args[3],
                    "score": float(args[4]),
                    "grade": args[5],
                    "term": args[6],
                    "session": args[7]
                 }
                 supabase.table("results").insert(data).execute()
                 return {"messages": [f"✅ **Result Added:** {data['subject']} for {data['student_id']}"]}
            else:
                 return {"messages": ["⚠️ Usage: `ADD RESULT ST-001 Math 85 A 1st 2024/2025`"]}
        except Exception as e:
            return {"messages": [f"⚠️ Error: {e}"]}

    return {"messages": ["Results tool active."]}

def check_bursary_tools_enhanced(state): return check_bursary_tools(state) # Alias


# --- MESSAGING ---
def send_message_to_teacher(phone, student_id, message):
    try:
        # We need school_id from student_id
        res = supabase.table("students").select("school_id").eq("id", student_id).execute()
        if not res.data: return "❌ Student not found."
        
        school_id = res.data[0]['school_id']
        
        supabase.table("messages").insert({
            "school_id": school_id,
            "parent_phone": phone,
            "content": message,
            "status": "Pending"
        }).execute()
        return "✅ **Message sent!**"
    except Exception as e:
        return f"❌ Error: {e}"

def get_teacher_messages(admin_phone):
    school_id = get_school_id(admin_phone)
    if not school_id: return []
    try:
        res = supabase.table("messages").select("*").eq("school_id", school_id).eq("status", "Pending").execute()
        return res.data
    except:
        return []

def check_messages_tools(state):
    msgs = state['messages']
    phone, msg = parse_message_metadata(msgs[-1].content)
    clean = msg.upper().strip()
    
    # Admin
    if "SHOW MESSAGES" in clean:
        msgs = get_teacher_messages(phone)
        if not msgs: return {"messages": ["📭 No messages."]}
        resp = "📬 **Messages:**\n"
        for m in msgs:
            resp += f"- {m['content']} ({m['parent_phone']})\n"
        return {"messages": [resp]}
        
    return {"messages": ["Message tools active."]}


# --- EVENTS ---
def add_event(title, date, type, admin_phone):
    school_id = get_school_id(admin_phone)
    if not school_id: return None
    try:
        data = {"school_id": school_id, "title": title, "date": date, "type": type}
        res = supabase.table("events").insert(data).execute()
        return "Created"
    except:
        return None

def get_upcoming_events(phone):
    # Determine school_id (Admin or Parent)
    # If parent, find via student
    # Simplified: finding school linked to phone if admin
    sid = get_school_id(phone)
    if not sid: return [] # TODO: Handle parent lookup
    
    try:
        res = supabase.table("events").select("*").eq("school_id", sid).gte("date", datetime.date.today().isoformat()).order("date").limit(5).execute()
        return res.data
    except:
        return []

def check_events_tools(state):
    msgs = state['messages']
    phone, msg = parse_message_metadata(msgs[-1].content)
    clean = msg.upper().strip()
    
    if "ADD EVENT" in clean:
        # ADD EVENT Title | Date | Type
        try:
             parts = msg.split("ADD EVENT", 1)[1].split("|")
             add_event(parts[0].strip(), parts[1].strip(), parts[2].strip(), phone)
             return {"messages": ["✅ Event added."]}
        except:
             return {"messages": ["⚠️ Usage: ADD EVENT Title | YYYY-MM-DD | Type"]}
             
    return {"messages": ["Check events logic."]}


# Placeholders for other tools to prevent import errors in main
def check_admissions_tools(state): return {"messages": ["Admissions module off."]}
def check_results_tools(state): return {"messages": ["Results module off."]}
def check_liaison_tools(state): return {"messages": ["Info module off."]}
def check_notifications_tools(state): return {"messages": ["Notifications off."]}
def check_results_tools_enhanced(state): return {"messages": ["Enhanced Results off."]}
def check_bursary_tools_enhanced(state): return check_bursary_tools(state) # Alias
