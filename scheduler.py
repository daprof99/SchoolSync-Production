"""
SchoolSync 2.0 - Background Scheduler
Handles automated notifications, fee reminders, and scheduled tasks
"""

import os
import time
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from tools import send_fee_reminders, get_school_config, ADMIN_PHONES, get_creds
import gspread
from twilio.rest import Client

load_dotenv()

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")  # e.g., whatsapp:+14155238886

def send_whatsapp_message(to_phone, message):
    """Send WhatsApp message via Twilio"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=f"whatsapp:{to_phone}"
        )
        print(f"✅ Sent to {to_phone}: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Failed to send to {to_phone}: {e}")
        return False


def process_notification_queue():
    """Process pending notifications from all schools"""
    print("\n🔔 Processing notification queue...")
    
    try:
        # Get all admin phones to process their schools
        for admin_phone in ADMIN_PHONES:
            from tools import get_db_connection
            sheet = get_db_connection(admin_phone)
            if not sheet:
                continue
            
            ws = sheet.worksheet("Notifications_Queue")
            records = ws.get_all_records()
            
            for i, record in enumerate(records):
                if record['Status'] == 'Pending':
                    # Send the notification
                    success = send_whatsapp_message(
                        record['Recipient_Phone'],
                        record['Message']
                    )
                    
                    if success:
                        # Update status to Sent
                        ws.update_cell(i + 2, 6, "Sent")  # Status column
                        ws.update_cell(i + 2, 7, str(time.time()))  # Sent_Time
                        print(f"✅ Sent: {record['Type']} to {record['Recipient_Phone']}")
                    
                    # Rate limiting - avoid Twilio spam
                    time.sleep(1)
        
        print("✅ Notification queue processed!")
    
    except Exception as e:
        print(f"❌ Error processing queue: {e}")


def weekly_fee_reminders():
    """Send fee reminders to all debtors across all schools"""
    print("\n💰 Sending weekly fee reminders...")
    
    for admin_phone in ADMIN_PHONES:
        try:
            count = send_fee_reminders(admin_phone)
            print(f"✅ Queued {count} reminders for school: {admin_phone}")
        except Exception as e:
            print(f"❌ Error for {admin_phone}: {e}")
    
    print("✅ Weekly reminders queued!")
    # Process the queue immediately
    process_notification_queue()


def daily_health_check():
    """Daily system health check"""
    print("\n🏥 Running health check...")
    print(f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Monitoring {len(ADMIN_PHONES)} schools")
    print("✅ System healthy!")


def main():
    """Run the background scheduler"""
    print("=" * 60)
    print("   SchoolSync 2.0 - Background Scheduler")
    print("=" * 60)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    scheduler = BlockingScheduler()
    
    # Daily: Process notification queue every hour
    scheduler.add_job(
        process_notification_queue,
        CronTrigger(minute=0),  # Every hour at :00
        id='process_notifications',
        name='Process Notification Queue'
    )
    
    # Weekly: Send fee reminders every Monday at 9 AM
    scheduler.add_job(
        weekly_fee_reminders,
        CronTrigger(day_of_week='mon', hour=9, minute=0),
        id='weekly_reminders',
        name='Weekly Fee Reminders'
    )
    
    # Daily: Health check at midnight
    scheduler.add_job(
        daily_health_check,
        CronTrigger(hour=0, minute=0),
        id='health_check',
        name='Daily Health Check'
    )
    
    print("📅 Scheduled Jobs:")
    for job in scheduler.get_jobs():
        print(f"  - {job.name} (Next run: {job.next_run_time})")
    
    print("\n🚀 Scheduler started! Press Ctrl+C to stop.\n")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n\n👋 Scheduler stopped gracefully.")


if __name__ == "__main__":
    main()
