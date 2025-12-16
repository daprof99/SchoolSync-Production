"""
Security Module for SchoolSync 2.0
Handles per-school PINs, OTP generation, and 2FA
"""

import random
import time
from datetime import datetime, timedelta

# Global OTP storage (in production, use Redis or database)
OTP_STORE = {}

def generate_otp(length=6):
    """Generate random OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def store_otp(phone, otp, expires_in=300):
    """Store OTP with expiration (default 5 minutes)"""
    expiry = datetime.now() + timedelta(seconds=expires_in)
    OTP_STORE[phone] = {
        'otp': otp,
        'expiry': expiry,
        'attempts': 0
    }


def verify_otp(phone, otp):
    """Verify OTP for a phone number"""
    if phone not in OTP_STORE:
        return False, "No OTP found. Request a new one."
    
    stored = OTP_STORE[phone]
    
    # Check expiry
    if datetime.now() > stored['expiry']:
        del OTP_STORE[phone]
        return False, "OTP expired. Request a new one."
    
    # Check attempts (max 3)
    if stored['attempts'] >= 3:
        del OTP_STORE[phone]
        return False, "Too many failed attempts. Request a new one."
    
    # Verify OTP
    if stored['otp'] == otp:
        del OTP_STORE[phone]
        return True, "OTP verified!"
    else:
        stored['attempts'] += 1
        return False, f"Wrong OTP. {3 - stored['attempts']} attempts remaining."


def get_school_pin(sheet):
    """Get school's custom PIN from Policy sheet"""
    try:
        ws = sheet.worksheet("Policy")
        records = ws.get_all_records()
        
        for row in records:
            if row.get('Question', '').upper() == 'ADMIN_PIN':
                return str(row.get('Answer', '2025'))  # Default to 2025
        
        # If not found, return default
        return "2025"
    except Exception as e:
        print(f"Error getting school PIN: {e}")
        return "2025"  # Fallback


def set_school_pin(sheet, new_pin):
    """Set/update school's custom PIN in Policy sheet"""
    try:
        ws = sheet.worksheet("Policy")
        records = ws.get_all_records()
        
        # Check if Admin_PIN row exists
        for i, row in enumerate(records):
            if row.get('Question', '').upper() == 'ADMIN_PIN':
                # Update existing
                ws.update_cell(i + 2, 2, new_pin)  # Answer column
                return True
        
        # Add new row
        ws.append_row(['Admin_PIN', new_pin])
        return True
    except Exception as e:
        print(f"Error setting school PIN: {e}")
        return False


def send_otp_sms(phone, otp):
    """Send OTP via Twilio SMS"""
    try:
        import os
        from twilio.rest import Client
        
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        
        # Format phone for Twilio
        if not phone.startswith("+"):
            phone = f"+{phone}"
        
        message = client.messages.create(
            body=f"🔐 Your SchoolSync verification code is: {otp}\n\nValid for 5 minutes.\n\nDo not share this code.",
            from_=os.getenv("TWILIO_PHONE_NUMBER") or os.getenv("TWILIO_WHATSAPP_NUMBER"),
            to=phone
        )
        
        print(f"✅ OTP sent to {phone}: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Error sending OTP: {e}")
        return False


def request_otp(phone):
    """Generate and send OTP to phone"""
    otp = generate_otp()
    store_otp(phone, otp)
    
    # Send via SMS
    if send_otp_sms(phone, otp):
        return True, f"📱 Verification code sent to {phone[-4:]}***. Valid for 5 minutes."
    else:
        return False, "❌ Failed to send OTP. Try again."


def verify_admin_action(phone, pin_or_otp, sheet, use_otp=False):
    """
    Verify admin action using either PIN or OTP
    
    Args:
        phone: Admin phone number
        pin_or_otp: PIN or OTP code provided
        sheet: Google Sheet object
        use_otp: If True, verify OTP. If False, verify PIN.
    
    Returns:
        (success: bool, message: str)
    """
    if use_otp:
        # Verify OTP
        return verify_otp(phone, pin_or_otp)
    else:
        # Verify school PIN
        school_pin = get_school_pin(sheet)
        if pin_or_otp == school_pin:
            return True, "PIN verified!"
        else:
            return False, "⛔ Wrong PIN."


# Admin commands for security management
def handle_security_commands(state):
    """Handle SET PIN and REQUEST OTP commands"""
    from tools import parse_message_metadata, get_db_connection
    
    msgs = state['messages']
    phone, msg = parse_message_metadata(msgs[-1].content)
    clean = msg.upper().strip()
    
    sheet = get_db_connection(phone)
    if not sheet:
        return {"messages": ["❌ Could not connect to your school database."]}
    
    # SET PIN command
    if "SET PIN" in clean:
        try:
            # Format: SET PIN oldPIN newPIN
            parts = msg.split()
            if len(parts) < 4:
                return {"messages": ["⚠️ Format: SET PIN <old_pin> <new_pin>"]}
            
            old_pin = parts[2]
            new_pin = parts[3]
            
            # Verify old PIN
            current_pin = get_school_pin(sheet)
            if old_pin != current_pin:
                return {"messages": ["⛔ Wrong current PIN."]}
            
            # Set new PIN
            if set_school_pin(sheet, new_pin):
                return {"messages": [f"✅ PIN updated to: {new_pin}\n\nKeep it secure!"]}
            else:
                return {"messages": ["❌ Failed to update PIN."]}
        except Exception as e:
            return {"messages": [f"❌ Error: {e}"]}
    
    # REQUEST OTP command
    if "REQUEST OTP" in clean or "SEND OTP" in clean:
        success, message = request_otp(phone)
        return {"messages": [message]}
    
    return {"messages": ["Command not recognized."]}


if __name__ == "__main__":
    # Test OTP system
    print("Testing OTP System\n")
    
    phone = "+2349075014063"
    
    # Generate OTP
    success, msg = request_otp(phone)
    print(f"{msg}")
    
    if success:
        # Simulate user entering OTP
        test_otp = input("\nEnter the OTP you received: ")
        verified, result = verify_otp(phone, test_otp)
        print(f"\n{result}")
        
        if verified:
            print("✅ Access granted!")
        else:
            print("❌ Access denied!")
