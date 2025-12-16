from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import os
import smtplib
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from supabase import create_client, Client
from dotenv import load_dotenv
from twilio.rest import Client as TwilioClient
from twilio.twiml.messaging_response import MessagingResponse
from langchain_core.messages import HumanMessage
# Deferred import or try/except to verify agent exists
try:
    from agent import app as agent_chain
    from tools import store_message, update_balance, send_payment_confirmation
except ImportError: 
    print("Agent module missing or error")
    agent_chain = None

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-key')

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("❌ CRITICAL ERROR: SUPABASE_URL and SUPABASE_KEY must be set in Environment Variables. Deployment failed.")

supabase: Client = create_client(url, key)

# --- CONFIG HELPER ---
def get_school_classes(school_name):
    try:
        if not school_name: return ["JSS1", "JSS2", "JSS3", "SSS1", "SSS2", "SSS3"]
        
        config_path = os.path.join(os.path.dirname(__file__), 'school_config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Exact match
        if school_name in config:
            return config[school_name]['classes']
            
        # Case insensitive
        for key in config:
            if key.lower().strip() == school_name.lower().strip():
                return config[key]['classes']

    except Exception as e:
        print(f"Config Error: {e}")
        return ["JSS1", "JSS2", "JSS3", "SSS1", "SSS2", "SSS3"]
        
    # Robust fallback: Word overlap count
    best_match = None
    max_overlap = 0
    
    target_words = set(school_name.lower().replace('&', 'and').split())
    
    for key in config:
        key_words = set(key.lower().replace('&', 'and').split())
        overlap = len(target_words.intersection(key_words))
        
        # If significant overlap (e.g. > 1 word or > 50% match)
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = key
            
    if best_match and max_overlap >= 1: # At least one unique word matches
        return config[best_match]['classes']

    return ["JSS1", "JSS2", "JSS3", "SSS1", "SSS2", "SSS3"]

def get_all_schools():
    try:
        res = supabase.table("schools").select("*").execute()
        return res.data
    except:
        return []

import csv
import io
from flask import Response

# ... (rest of imports)

def get_unread_messages_count(school_id):
    try:
        res = supabase.table("messages").select("*", count="exact").eq("school_id", school_id).eq("status", "Pending").execute()
        return res.count
    except:
        return 0

def get_dashboard_stats(school_id):
    try:
        res = supabase.table("students").select("*").eq("school_id", school_id).execute()
        students = res.data
        
        total_fees = sum(float(s['total_fees'] or 0) for s in students)
        total_paid = sum(float(s['amount_paid'] or 0) for s in students)
        debtors = sum(1 for s in students if (float(s['total_fees'] or 0) - float(s['amount_paid'] or 0)) > 0)
        
        # Fetch school name
        school_res = supabase.table("schools").select("name").eq("id", school_id).execute()
        school_name = school_res.data[0]['name'] if school_res.data else "Unknown School"

        # Messages count
        msg_count = get_unread_messages_count(school_id)
        
        # Class Breakdown
        class_stats = {}
        for s in students:
            c = s.get('student_class', 'Unknown')
            if c not in class_stats: class_stats[c] = 0
            class_stats[c] += 1
        
        sorted_classes = dict(sorted(class_stats.items()))

        return {
            'school_name': school_name,
            'total_revenue': f"{total_paid:,.2f}",
            'total_outstanding': f"{(total_fees - total_paid):,.2f}",
            'total_fees': f"{total_fees:,.2f}",
            'total_debtors': debtors,
            'total_students': len(students),
            'collection_rate': round((total_paid / total_fees * 100) if total_fees > 0 else 0, 1),
            'messages_count': msg_count,
            'class_breakdown': sorted_classes
        }
    except Exception as e:
        print(f"Stats Error: {e}")
        return {'total_revenue': 0, 'total_outstanding': 0, 'total_students': 0, 'messages_count': 0}

# ... (rest of imports)

# ... (get_all_schools, get_unread_messages_count, get_dashboard_stats unchanged) ...

# --- AUTHENTICATION ---
def is_authenticated(school_id):
    return session.get('school_id') == school_id



@app.route('/login/<school_id>', methods=['GET', 'POST'])
def login(school_id):
    if request.method == 'POST':
        pin = request.form.get('pin')
        try:
            res = supabase.table("schools").select("admin_pin").eq("id", school_id).execute()
            if res.data and res.data[0]['admin_pin'] == pin:
                session['school_id'] = school_id
                return redirect(url_for('dashboard', school_id=school_id))
            else:
                flash("Invalid PIN", "error")
        except Exception as e:
            flash(f"Error: {e}", "error")
            
    # Get school name for display
    try:
        res = supabase.table("schools").select("name").eq("id", school_id).execute()
        school_name = res.data[0]['name'] if res.data else "Login"
    except:
        school_name = "Login"

    return render_template('login.html', school_id=school_id, school_name=school_name)

@app.route('/logout')
def logout():
    session.pop('school_id', None)
    return redirect(url_for('index'))

@app.route('/dashboard/<school_id>')
def dashboard(school_id):
    if not is_authenticated(school_id):
        return redirect(url_for('login', school_id=school_id))
        
    stats = get_dashboard_stats(school_id)
    return render_template('dashboard.html', stats=stats, school_id=school_id, events=[], messages_count=stats.get('messages_count', 0))

@app.route('/dashboard/<school_id>/export')
def export_data(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))

    try:
        # Fetch students
        res = supabase.table("students").select("*").eq("school_id", school_id).execute()
        students = res.data
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Student ID', 'Parent Name', 'Phone', 'Class', 'Total Fees', 'Paid', 'Balance'])
        
        for s in students:
            total = float(s['total_fees'] or 0)
            paid = float(s['amount_paid'] or 0)
            writer.writerow([
                s['id'], s['parent_name'], s['parent_phone'], s['student_class'],
                total, paid, total - paid
            ])
            
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=students_export.csv"}
        )
    except Exception as e:
        return f"Error exporting: {e}"

@app.route('/dashboard/<school_id>/messages')
def view_messages(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))

    try:
        res = supabase.table("messages").select("*").eq("school_id", school_id).order('created_at', desc=True).execute()
        messages = res.data
        
        # Determine school name for header
        school_res = supabase.table("schools").select("name").eq("id", school_id).execute()
        school_name = school_res.data[0]['name'] if school_res.data else "School"

        return render_template('messages.html', messages=messages, school_name=school_name, school_id=school_id)
    except Exception as e:
        return f"Error loading messages: {e}"

# ... (existing code)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find-school', methods=['POST'])
def find_school():
    phone = request.form.get('phone', '').strip().replace(" ", "").replace("-", "")
    try:
        # Simple exact match first or check +234
        res = supabase.table("schools").select("id").or_(f"admin_phone.eq.{phone},admin_phone.eq.+{phone}").execute()
        if res.data:
            school_id = res.data[0]['id']
            return redirect(url_for('login', school_id=school_id))
        
        flash("School not found with this phone number.", "error")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Error: {e}", "error")
        return redirect(url_for('index'))

def get_school_name(school_id):
    try:
        res = supabase.table("schools").select("name").eq("id", school_id).execute()
        return res.data[0]['name'] if res.data else "School"
    except:
        return "School"

# ... (existing routes up to dashboard) ...

@app.route('/dashboard/<school_id>/change-pin', methods=['GET', 'POST'])
def change_pin(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    
    if request.method == 'POST':
        current = request.form.get('current_pin')
        new = request.form.get('new_pin')
        confirm = request.form.get('confirm_pin')
        
        if new != confirm:
            flash("New PINs do not match", "error")
        else:
            try:
                # Verify current
                res = supabase.table("schools").select("admin_pin").eq("id", school_id).execute()
                if res.data and res.data[0]['admin_pin'] == current:
                    supabase.table("schools").update({"admin_pin": new}).eq("id", school_id).execute()
                    flash("PIN updated successfully!", "success")
                else:
                    flash("Incorrect current PIN", "error")
            except Exception as e:
                flash(f"Error: {e}", "error")

    return render_template('change_pin.html', school_id=school_id, school_name=get_school_name(school_id))


# --- SUPERADMIN ---
SUPER_PIN = "admin123" # Simple hardcoded PIN for superadmin

@app.route('/superadmin', methods=['GET', 'POST'])
def superadmin_login():
    if request.method == 'POST':
        if request.form.get('pin') == SUPER_PIN:
            session['superadmin'] = True
            return redirect(url_for('superadmin_dashboard'))
        flash("Invalid Super PIN", "error")
    return render_template('login.html', school_id="SUPER", school_name="⭐ Super Admin")

@app.route('/superadmin/dashboard')
def superadmin_dashboard():
    if not session.get('superadmin'): return redirect(url_for('superadmin_login'))
    schools = get_all_schools()
    return render_template('superadmin.html', schools=schools)

@app.route('/superadmin/reset/<school_id>')
def superadmin_reset_pin(school_id):
    if not session.get('superadmin'): return redirect(url_for('superadmin_login'))
    
    try:
        # Reset to default '1234'
        supabase.table("schools").update({"admin_pin": "1234"}).eq("id", school_id).execute()
        flash(f"Reset PIN for school {school_id} to 1234", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
        
    return redirect(url_for('superadmin_dashboard'))


# ... (other imports)

def send_email(to_email, subject, body):

    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    
    if not sender_email or not sender_password:
        print("❌ SMTP credentials missing")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Email Error: {e}")
        return False

# ... (rest of code) ...

# ... (rest of code) ...

# --- PUBLIC RESULT PORTAL ---

@app.route('/result/login/<student_id>', methods=['GET', 'POST'])
def result_login(student_id):
    # Public page for parents to access result
    if request.method == 'POST':
        phone = request.form.get('phone').replace('+', '').strip()
        
        try:
            # Verify phone against student record
            res = supabase.table("students").select("parent_phone").eq("id", student_id).execute()
            if res.data:
                # Normalize stored phone
                stored = res.data[0]['parent_phone'].replace('+', '').strip()
                # Simple check (last 4 digits or full match)
                if phone == stored or phone in stored or stored in phone:
                    session[f'auth_result_{student_id}'] = True
                    return redirect(url_for('result_view', student_id=student_id))
                else:
                    flash("Phone number does not match our records.", "error")
            else:
                flash("Student not found.", "error")
        except Exception as e:
            flash(f"Error: {e}", "error")
            
    return render_template('result_login.html', student_id=student_id)

@app.route('/result/view/<student_id>')
def result_view(student_id):
    # Check if authorized for THIS student
    if not session.get(f'auth_result_{student_id}'):
        return redirect(url_for('result_login', student_id=student_id))
        
    try:
        # Fetch Student
        st_res = supabase.table("students").select("*").eq("id", student_id).execute()
        student = st_res.data[0]
        
        # Fetch School
        sc_res = supabase.table("schools").select("name").eq("id", student['school_id']).execute()
        school_name = sc_res.data[0]['name']
        
        # Fetch Results
        r_res = supabase.table("results").select("*").eq("student_id", student_id).execute()
        results = r_res.data
        
        # Calculate stats
        total_score = sum(float(r['score'] or 0) for r in results)
        avg_score = round(total_score / len(results), 1) if results else 0
        
        return render_template('result_card.html', student=student, results=results, school_name=school_name, average=avg_score)
    except Exception as e:
        return f"Error loading result: {e}"

# --- ADMIN ROUTES ---

# ... (start of file) ...
# ... (existing imports, ensure requests is imported if needed, usually is)
import requests

# ...

@app.route('/pay/<school_id>/<student_id>')
def pay_student_fees(school_id, student_id):
    try:
        # 1. Fetch Student Debt
        res = supabase.table("students").select("surname, first_name, parent_phone, total_fees, amount_paid").eq("id", student_id).eq("school_id", school_id).execute()
        if not res.data:
            return "Student not found."
            
        student = res.data[0]
        debt = float(student['total_fees'] or 0) - float(student['amount_paid'] or 0)
        
        if debt <= 0:
            return f"<h1>No outstanding fees for {student['surname']} {student['first_name']}! 🎉</h1>"
            
        # 2. Initialize Paystack
        secret = os.getenv("PAYSTACK_SECRET_KEY")
        if not secret: return "Payment Gateway not configured."
        
        # Paystack expects amount in Kobo (x100)
        amount_kobo = int(debt * 100)
        email = f"parent_{student_id}@schoolsync.com" # Dummy email as we rely on ID
        
        headers = {
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/json"
        }
        
        data = {
            "email": email,
            "amount": amount_kobo,
            "reference": f"{school_id}_{student_id}_{int(time.time())}",
            "metadata": {
                "school_id": school_id,
                "student_id": student_id,
                "custom_fields": [
                    {"display_name": "Student Name", "variable_name": "student_name", "value": f"{student['surname']} {student['first_name']}"},
                    {"display_name": "Class", "variable_name": "class", "value": "Unknown"}
                ]
            },
            # Verify URL should point to a verification route in this app
            "callback_url": url_for('verify_payment', _external=True) 
        }
        
        req = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
        response = req.json()
        
        if response['status']:
            return redirect(response['data']['authorization_url'])
        else:
            return f"Payment Initialization Failed: {response['message']}"
            
    except Exception as e:
        return f"Error: {e}"

@app.route('/payment/verify')
def verify_payment():
    ref = request.args.get('reference')
    if not ref: return "No reference provided."
    
    try:
        secret = os.getenv("PAYSTACK_SECRET_KEY")
        headers = {"Authorization": f"Bearer {secret}"}
        
        req = requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers=headers)
        res = req.json()
        
        if res['status'] and res['data']['status'] == 'success':
            # Update DB
            meta = res['data']['metadata']
            amount_paid = float(res['data']['amount']) / 100
            
            # Record Payment
            supabase.table("payments").insert({
                "student_id": meta['student_id'],
                "amount": amount_paid,
                "date": datetime.now().isoformat(),
                "reference": ref,
                "method": "Paystack"
            }).execute()
            
            # Update Student Record
            # Need to fetch current paid first to add - handled by trigger? 
            # Or manually fetch, add, update. Supabase has no easy atomic increment via API without RPC.
            # Manual way:
            st = supabase.table("students").select("amount_paid").eq("id", meta['student_id']).execute()
            current = float(st.data[0]['amount_paid'] or 0)
            new_bal = current + amount_paid
            supabase.table("students").update({"amount_paid": new_bal}).eq("id", meta['student_id']).execute()
            
            return "<h1>Payment Successful! ✅</h1><p>The student record has been updated.</p>"
        else:
            return "Payment Verification Failed."
            
    except Exception as e:
        return f"Error verifying: {e}"

def send_whatsapp(to_number, body):
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth = os.getenv("TWILIO_AUTH_TOKEN")
    from_ph = os.getenv("TWILIO_PHONE_NUMBER")
    
    if not (sid and auth and from_ph): return False
    
    try:
        from twilio.rest import Client as TwilioClient # Safe import
        client = TwilioClient(sid, auth)
        if not to_number.startswith('+'): to_number = f"+{to_number}"
        
        client.messages.create(from_=from_ph, body=body, to=f"whatsapp:{to_number}")
        return True
    except Exception as e:
        print(f"Twilio Error ({to_number}): {e}")
        return False

# ... (rest of code) ...

# ... (start of file) ...

@app.route('/dashboard/<school_id>/students')
def view_students(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    try:
        res = supabase.table("students").select("*").eq("school_id", school_id).execute()
        students = res.data
        
        # Prepare data for table
        headers = ["ID", "Parent Name", "Phone", "Class", "Total Fees", "Paid", "Balance"]
        items = []
        for s in students:
            bal = float(s['total_fees'] or 0) - float(s['amount_paid'] or 0)
            items.append([
                s['id'], s['parent_name'], s['parent_phone'], s['student_class'],
                f"₦{float(s['total_fees'] or 0):,.2f}",
                f"₦{float(s['amount_paid'] or 0):,.2f}",
                f"<span class='badge {'red' if bal > 0 else 'green'}'>₦{bal:,.2f}</span>"
            ])
            
        return render_template('data_table.html', school_id=school_id, school_name=get_school_name(school_id), title="Total Students", headers=headers, items=items)
    except Exception as e:
        return f"Error: {e}"

@app.route('/dashboard/<school_id>/debtors')
def view_debtors(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    try:
        res = supabase.table("students").select("*").eq("school_id", school_id).execute()
        # Filter in python for complex logic or use DB filter
        debtors = [s for s in res.data if (float(s['total_fees'] or 0) - float(s['amount_paid'] or 0)) > 0]
        
        headers = ["ID", "Parent Name", "Phone", "Class", "Outstanding"]
        items = []
        for s in debtors:
            bal = float(s['total_fees'] or 0) - float(s['amount_paid'] or 0)
            items.append([
                s['id'], s['parent_name'], s['parent_phone'], s['student_class'],
                f"<span class='badge red'>₦{bal:,.2f}</span>"
            ])
            
        return render_template('data_table.html', school_id=school_id, school_name=get_school_name(school_id), title="Debtors List", headers=headers, items=items)
    except Exception as e:
        return f"Error: {e}"

@app.route('/dashboard/<school_id>/payments')
def view_payments(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    try:
        # Join not easily supported in simple client, fetch separate or assuming view
        # We will just fetch payments and try to map details or just show raw
        res = supabase.table("payments").select("*").order("date", desc=True).limit(50).execute()
        payments = res.data
        
        # Filter by school? Payments table doesn't have school_id directly, it references student.
        # We need to filter payments where student.school_id = school_id
        # This is N+1 or need a better query.
        # Workaround: Get all student IDs for this school first.
        st_res = supabase.table("students").select("id").eq("school_id", school_id).execute()
        st_ids = [s['id'] for s in st_res.data]
        
        # Process payments
        headers = ["Date", "Student ID", "Amount", "Reference"]
        items = []
        for p in payments:
            if p['student_id'] in st_ids:
                items.append([
                    p['date'][:10], # Simple date format
                    p['student_id'],
                    f"₦{float(p['amount']):,.2f}",
                    p['reference']
                ])
                
        return render_template('data_table.html', school_id=school_id, school_name=get_school_name(school_id), title="Recent Revenue", headers=headers, items=items)
    except Exception as e:
        return f"Error: {e}"


@app.route('/dashboard/<school_id>/attendance', methods=['GET', 'POST'])
def attendance_page(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    
    school_name = get_school_name(school_id)
    classes = get_school_classes(school_name)
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # Logic for Bulk Posting
    if request.method == 'POST' and 'bulk_action' in request.form:
        selected_ids = request.form.getlist('selected_students')
        if not selected_ids:
            flash("No students selected.", "warning")
        else:
            count = 0
            for student_id in selected_ids:
                try:
                    # Check if already marked to avoid error
                    check = supabase.table("attendance").select("id").eq("school_id", school_id).eq("student_id", student_id).eq("date", today_str).execute()
                    if not check.data:
                        supabase.table("attendance").insert({
                            "school_id": school_id,
                            "student_id": student_id,
                            "date": today_str,
                            "timestamp": datetime.now().isoformat(),
                             "status": "Present" # Default status
                        }).execute()
                        count += 1
                except: continue
            flash(f"✅ Marked {count} students present!", "success")
            
    # Logic for Single ID Posting (Scanner Mode)
    elif request.method == 'POST':
        student_id = request.form.get('student_id', '').strip().upper()
        if student_id:
            try:
                res = supabase.table("students").select("surname, first_name").eq("school_id", school_id).eq("id", student_id).execute()
                if not res.data:
                    flash(f"Student ID {student_id} not found!", "error")
                else:
                    s_name = f"{res.data[0]['surname']} {res.data[0]['first_name']}"
                    check = supabase.table("attendance").select("*").eq("school_id", school_id).eq("student_id", student_id).eq("date", today_str).execute()
                    if check.data:
                        flash(f"{s_name} already marked.", "warning")
                    else:
                        supabase.table("attendance").insert({
                            "school_id": school_id,
                            "student_id": student_id,
                            "date": today_str,
                            "timestamp": datetime.now().isoformat(),
                            "status": "Present"
                        }).execute()
                        flash(f"✅ {s_name} marked present!", "success")
            except Exception as e:
                flash(f"Error: {e}", "error")

    # Fetch Class Data if Filter active
    class_filter = request.args.get('class_filter')
    class_students = []
    
    if class_filter:
        try:
            # 1. Get all students in class
            s_res = supabase.table("students").select("id, surname, first_name, other_name").eq("school_id", school_id).eq("student_class", class_filter).order('surname').execute()
            students = s_res.data
            
            # 2. Get today's attendance for this class to map checkboxes
            # We can't join easily, so we fetch all attendance for today and python map
            att_res = supabase.table("attendance").select("student_id").eq("school_id", school_id).eq("date", today_str).execute()
            present_ids = set(a['student_id'] for a in att_res.data)
            
            for s in students:
                is_present = s['id'] in present_ids
                class_students.append({
                    "id": s['id'],
                    "name": f"{s['surname']} {s['first_name']} {s.get('other_name','')}",
                    "is_present": is_present
                })
        except Exception as e:
            print(f"Class Fetch Error: {e}")

    # Fetch Log (Recent 20)
    todays_log = []
    try:
        logs = supabase.table("attendance").select("*").eq("school_id", school_id).eq("date", today_str).order("timestamp", desc=True).limit(20).execute()
        if logs.data:
             ids = [l['student_id'] for l in logs.data]
             if ids:
                 s_res = supabase.table("students").select("id, surname, first_name").eq("school_id", school_id).in_("id", ids).execute()
                 s_map = {s['id']: f"{s['surname']} {s['first_name']}" for s in s_res.data}
                 for l in logs.data:
                     t = l['timestamp'].split('T')[1][:5] if 'T' in l['timestamp'] else "--:--"
                     todays_log.append({
                         "student_id": l['student_id'],
                         "student_name": s_map.get(l['student_id'], "Unknown"),
                         "time": t
                     })
    except: pass

    return render_template('attendance.html', school_id=school_id, school_name=school_name, todays_log=todays_log, classes=classes, class_filter=class_filter, class_students=class_students)

@app.route('/dashboard/<school_id>/download-template')
def download_template(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Student Template"
        
        # Headers
        headers = ['ID', 'Surname', 'First Name', 'Other Name', 'Class', 'Parent Phone', 'Total Fees']
        ws.append(headers)
        
        # Add a sample row to guide them?
        ws.append(['ST-001', 'Doe', 'John', 'Paul', 'JSS1', '08012345678', '50000'])
        
        # Save to buffer
        out = io.BytesIO()
        wb.save(out)
        out.seek(0)
        
        return Response(
            out.getvalue(),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-disposition": "attachment; filename=student_import_template.xlsx"}
        )
    except Exception as e:
        return f"Error generating template: {e}"

@app.route('/dashboard/<school_id>/import-students', methods=['GET', 'POST'])
def import_students(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    
    if request.method == 'POST':
        if 'file' not in request.files: return "No file"
        file = request.files['file']
        if file.filename == '': return "No filename"
        
        try:
            filename = file.filename.lower()
            rows = []
            
            if filename.endswith('.xlsx') or filename.endswith('.xls'):
                import openpyxl
                wb = openpyxl.load_workbook(file)
                sheet = wb.active
                # Convert sheet to list of lists
                for row in sheet.iter_rows(values_only=True):
                    rows.append(list(row))
            else:
                # CSV Fallback
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_input = csv.reader(stream)
                rows = list(csv_input)
            
            count = 0
            errors = 0
            
            for row in rows:
                if not row: continue
                # Skip header
                first_cell = str(row[0]).lower() if row[0] is not None else ""
                if first_cell in ['id', 'student id', 'student_id']: continue
                
                # Expecting: ID, Surname, First, Other, Class, Phone, Fee
                if len(row) < 6: 
                    errors += 1
                    continue
                    
                try:
                    # Clean fee
                    fee_val = row[6] if len(row) > 6 else 0
                    if fee_val is None: fee_val = 0
                    fee_str = str(fee_val).replace(',', '').replace('₦', '')
                    
                    # Handle Phone (Excel might make it float/int)
                    phone_val = row[5]
                    if isinstance(phone_val, float): phone_val = str(int(phone_val))
                    phone_val = str(phone_val)

                    supabase.table("students").insert({
                        "school_id": school_id,
                        "id": str(row[0]),
                        "surname": str(row[1]),
                        "first_name": str(row[2]),
                        "other_name": str(row[3]) if len(row) > 3 and row[3] else "",
                        "student_class": str(row[4]),
                        "parent_phone": phone_val,
                        "total_fees": float(fee_str) if fee_str else 0
                    }).execute()
                    count += 1
                except Exception as ex:
                    print(f"Row failed: {row} - {ex}")
                    errors += 1
            
            flash(f"Imported {count} students. {errors} failed.", "success" if errors == 0 else "warning")
            return redirect(url_for('dashboard', school_id=school_id))
            
        except Exception as e:
            return f"Error: {e}"
            
    return render_template('import_students.html', school_id=school_id, school_name=get_school_name(school_id))

@app.route('/dashboard/<school_id>/broadcast', methods=['GET', 'POST'])
def broadcast_page(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    
    school_name = get_school_name(school_id)
    classes = get_school_classes(school_name)
    
    # Get Recipient Count (Approximate, for All)
    try:
        res = supabase.table("students").select("parent_phone").eq("school_id", school_id).execute()
        phones = set(s['parent_phone'] for s in res.data if s.get('parent_phone'))
        recipient_count = len(phones)
    except:
        recipient_count = 0

    if request.method == 'POST':
        message = request.form.get('message')
        audience = request.form.get('audience', 'all')
        selected_classes = request.form.getlist('target_classes')
        
        if not message:
            flash("Message cannot be empty", "error")
        else:
            try:
                # 1. Fetch Students
                s_res = supabase.table("students").select("*").eq("school_id", school_id).execute()
                all_students = s_res.data
                
                # 2. Filter using helper (returns list of student dicts)
                target_students = get_filtered_students(all_students, audience, selected_classes)
                
                if not target_students:
                    flash("No parents found for these criteria.", "warning")
                else:
                    sent = 0
                    for s in target_students:
                        ph = s.get('parent_phone')
                        if not ph: continue
                        
                        # Personalize Message
                        personalized = message
                        if '{Student}' in personalized:
                            personalized = personalized.replace('{Student}', f"{s['surname']}")
                        
                        debt = float(s['total_fees'] or 0) - float(s['amount_paid'] or 0)
                        if '{Amount}' in personalized:
                            personalized = personalized.replace('{Amount}', f"₦{debt:,.2f}")
                            
                        if '{Link}' in personalized:
                            # Generate safe payment link
                            link = url_for('pay_student_fees', school_id=school_id, student_id=s['id'], _external=True)
                            personalized = personalized.replace('{Link}', link)

                        if send_whatsapp(ph, personalized):
                            sent += 1
                            
                    flash(f"✅ Broadcast sent to {sent} parents ({audience})!", "success")
            except Exception as e:
                flash(f"Error: {e}", "error")

    return render_template('broadcast.html', school_id=school_id, school_name=school_name, recipient_count=recipient_count, classes=classes)

@app.route('/dashboard/<school_id>/add-event', methods=['GET', 'POST'])
def add_event(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    
    if request.method == 'POST':
        try:
            event_type = request.form['type']
            if event_type == 'Others':
                event_type = request.form.get('custom_type', 'Others')
                
            supabase.table("events").insert({
                "school_id": school_id,
                "title": request.form['title'],
                "date": request.form['date'],
                "time": request.form['time'],
                "type": event_type
            }).execute()
        except Exception as e:
            return f"Error: {e}"
        return redirect(url_for('dashboard', school_id=school_id))
        
    return render_template('add_event.html', school_id=school_id, school_name=get_school_name(school_id))

@app.route('/dashboard/<school_id>/bill-class', methods=['GET', 'POST'])
def bill_class(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    
    school_name = get_school_name(school_id)
    classes = get_school_classes(school_name)
    
    if request.method == 'POST':
        cls = request.form.get('class') # HTML name="class" not "student_class"
        try:
            amt = float(request.form.get('amount'))
            reason = request.form.get('reason')
            
            # Fetch students
            res = supabase.table("students").select("id, total_fees").eq("school_id", school_id).eq("student_class", cls).execute()
            
            count = 0
            for s in res.data:
                new_total = float(s['total_fees'] or 0) + amt
                supabase.table("students").update({"total_fees": new_total}).eq("id", s['id']).execute()
                count += 1
                
            flash(f"Updated {count} students in {cls}.", "success")
            return redirect(url_for('dashboard', school_id=school_id))
            
        except Exception as e:
            flash(f"Error: {e}", "error")
            
    return render_template('bill_class.html', school_id=school_id, school_name=school_name, classes=classes)

@app.route('/dashboard/<school_id>/add-result', methods=['GET', 'POST'])
def add_result(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    
    if request.method == 'POST':
        try:
            # Basic validation: check if student exists in this school? 
            # Skipping for speed, or basic check:
            sid = request.form['student_id']
            # res = supabase.table("students").select("id").eq("school_id", school_id).eq("id", sid).execute()
            # if not res.data: return "Student not found in this school"
            
            supabase.table("results").insert({
                "student_id": sid,
                "subject": request.form['subject'],
                "score": request.form['score'],
                "grade": request.form['grade'],
                "term": request.form['term'],
                "session": request.form['session']
            }).execute()
        except Exception as e:
            return f"Error: {e}"
        return redirect(url_for('dashboard', school_id=school_id))
        
    return render_template('add_result.html', school_id=school_id, school_name=get_school_name(school_id))

@app.route('/dashboard/<school_id>/add-student', methods=['GET', 'POST'])
def add_student(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    
    school_name = get_school_name(school_id)
    classes = get_school_classes(school_name)
    
    if request.method == 'POST':
        try:
            # HTML sends: student_id, surname, first_name, other_name, student_class, parent_name, parent_phone, total_fees
            data = {
                "id": request.form.get('student_id').strip().upper(),
                "school_id": school_id,
                "surname": request.form.get('surname'),
                "first_name": request.form.get('first_name'),
                "other_name": request.form.get('other_name'),
                "student_class": request.form.get('student_class'),
                "parent_name": request.form.get('parent_name'),
                "parent_phone": request.form.get('parent_phone'),
                "total_fees": float(request.form.get('total_fees')),
                "amount_paid": 0
            }
            # Check ID uniqueness (simple check)
            exists = supabase.table("students").select("id").eq("id", data['id']).execute()
            if exists.data:
                flash(f"Student ID {data['id']} already exists!", "error")
            else:
                supabase.table("students").insert(data).execute()
                flash(f"✅ Student {data['surname']} {data['first_name']} added successfully!", "success")
        except Exception as e:
            flash(f"Error adding student: {e}", "error")

    return render_template('add_student.html', school_id=school_id, school_name=school_name, classes=classes)

@app.route('/dashboard/<school_id>/upload-results', methods=['GET', 'POST'])
def upload_results(school_id):
    if not is_authenticated(school_id): return redirect(url_for('login', school_id=school_id))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
        else:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file', 'error')
            elif file and file.filename.endswith('.csv'):
                try:
                    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                    reader = csv.reader(stream)
                    # Skip header check for now, assume valid or check row[0]
                    # Expected: Student ID, Subject, Score, Grade, Term, Session
                    
                    count = 0
                    errors = 0
                    
                    for row in reader:
                        if len(row) < 6: continue
                        if row[0].lower() == 'student id': continue # Header
                        
                        try:
                            # Verify student belongs to this school
                            st = supabase.table("students").select("id").eq("id", row[0]).eq("school_id", school_id).execute()
                            if st.data:
                                supabase.table("results").insert({
                                    "student_id": row[0],
                                    "subject": row[1],
                                    "score": float(row[2]),
                                    "grade": row[3],
                                    "term": row[4],
                                    "session": row[5]
                                }).execute()
                                count += 1
                            else:
                                errors += 1 # Student not found or wrong school
                        except:
                            errors += 1
                            
                    flash(f"✅ Uploaded {count} results. {errors} failed/skipped.", "success" if count > 0 else "error")
                except Exception as e:
                    flash(f"CSV Error: {e}", "error")
            else:
                flash('Invalid file type. Please upload a CSV.', 'error')

    return render_template('upload_results.html', school_id=school_id, school_name=get_school_name(school_id))



@app.route('/forgot-pin/<school_id>')
def forgot_pin(school_id):
    if school_id == "SUPER":
        flash("Cannot reset Super Admin PIN.", "error")
        return redirect(url_for('superadmin_login'))

    try:
        # Fetch school details
        res = supabase.table("schools").select("admin_email, admin_pin, name").eq("id", school_id).execute()
        if res.data:
            school = res.data[0]
            email = school['admin_email']
            pin = school['admin_pin']
            
            if email:
                subject = f"🔐 Your SchoolSync PIN - {school['name']}"
                body = f"Hello Admin,\n\nHere is your PIN for access to the SchoolSync Dashboard:\n\nPIN: {pin}\n\nKeep this safe!\n\n- SchoolSync Team"
                
                if send_email(email, subject, body):
                    flash(f"PIN sent to {email}. Check your inbox/spam.", "success")
                else:
                    flash("Failed to send email. Check server logs.", "error")
            else:
                flash("No email registered for this school. Contact Super Admin.", "error")
        else:
            flash("School not found.", "error")
    except Exception as e:
        flash(f"Error: {e}", "error")
        
    return redirect(url_for('login', school_id=school_id))

@app.route('/dashboard/<school_id>/api/recipient-count')
def get_recipient_count_api(school_id):
    if not is_authenticated(school_id): return jsonify({"count": 0})
    
    audience = request.args.get('audience', 'all')
    classes = request.args.getlist('classes[]') # AJAX array convention
    
    try:
        s_res = supabase.table("students").select("*").eq("school_id", school_id).execute()
        students = get_filtered_students(s_res.data, audience, classes)
        return jsonify({"count": len(students)})
    except Exception as e:
        print(e)
        return jsonify({"count": 0})

def get_filtered_students(students, audience, selected_classes):
    target_students = []
    seen_ids = set() # Avoid duplicates if any
    
    for s in students:
        if s['id'] in seen_ids: continue
        
        phone = s.get('parent_phone', '').replace(" ", "").replace("-", "")
        if not phone: continue
        
        debt = float(s.get('total_fees') or 0) - float(s.get('amount_paid') or 0)
        s_class = s.get('student_class')
        
        include = False
        if audience == 'all':
            include = True
        elif audience == 'debtors' and debt > 0:
            include = True
        elif audience == 'paid' and debt <= 0:
            include = True
        elif audience == 'classes':
            if s_class in selected_classes:
                include = True
                
        if include:
            target_students.append(s)
            seen_ids.add(s['id'])
            
    return target_students

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    if not agent_chain: return Response("Service Unavailable", 503)
    
    phone = request.form.get('From', '').replace('whatsapp:', '')
    msg = request.form.get('Body', '')
    print(f"📩 {phone}: {msg}")

    # Store user message
    store_message(phone, "user", msg)

    agent_input = f"META_PHONE={phone} || {msg}"
    config = {"configurable": {"thread_id": phone}}

    try:
        # Run Agent
        out = agent_chain.invoke({"messages": [HumanMessage(content=agent_input)]}, config=config)
        
        last_message = out['messages'][-1]
        resp_text = last_message if isinstance(last_message, str) else last_message.content
        
        # Store bot response
        store_message(phone, "assistant", resp_text)

    except Exception as e:
        print(f"❌ Error: {e}")
        resp_text = "Sorry, I encountered an error. Please contact admin."

    print(f"🤖 Bot Reply: {resp_text}")

    # Generate TwiML
    resp = MessagingResponse()
    resp.message(resp_text)
    
    return Response(str(resp), mimetype="application/xml")

@app.route("/paystack-webhook", methods=['POST'])
def paystack_webhook():
    payload = request.json
    if payload.get('event') == 'charge.success':
        data = payload['data']
        student_id = data['metadata']['student_id']
        amount = data['amount'] / 100
        
        # Update balance (using tools logic or direct DB)
        school_id = data['metadata'].get('school_sheet_id') or data['metadata'].get('school_id')
        
        # Use existing helper if available, else direct DB
        try:
            update_balance(school_id, student_id, amount)
            
            # Send confirmation
            parent_phone = data['metadata'].get('parent_phone', '')
            if parent_phone:
                send_payment_confirmation(parent_phone, student_id, amount)
                
            print(f"💰 Payment Confirmed: {data['reference']}")
        except Exception as e:
            print(f"Webhook Error: {e}")
            
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
