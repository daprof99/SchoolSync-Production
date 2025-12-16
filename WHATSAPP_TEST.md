# 🚀 WhatsApp Testing - Quick Reference

## Your Servers (Already Running ✅)
- ✅ `python main.py` - Backend server
- ✅ `ngrok http 14031` - Public URL tunnel

---

## Step 1: Get ngrok URL

**Look at your ngrok terminal window**, find the line:
```
Forwarding   https://xxxx-xxxx.ngrok-free.app -> http://localhost:14031
```

**Copy the HTTPS URL** (e.g., `https://xxxx-xxxx.ngrok-free.app`)

---

## Step 2: Configure Twilio

1. Open: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Click **"Sandbox settings"**
3. **"When a message comes in"**: `https://YOUR-NGROK-URL/whatsapp`
4. Click **Save**

---

## Step 3: Test Messages

**From your phone to Twilio WhatsApp number:**

```
You: Hi
Bot: 👋 Hello! I'm SchoolSync...

You: 1
Bot: 🎓 Admissions info...

You: CHECK ST-001 OKAFOR
Bot: Shows fee balance

You: When is the next meeting?
Bot: 📅 Shows events
```

---

## Watch for Logs

**In your `python main.py` terminal:**
```
📩 +234xxx: Hi
🤖 Bot Reply: Hello! I'm SchoolSync...
```

---

## If Bot Doesn't Respond

1. Check ngrok URL is correct in Twilio
2. Check `main.py` terminal for errors
3. Verify WhatsApp joined sandbox (send `join [code]` first)

---

## Next: Test Admin Commands

**From admin phone number:**
```
SUMMARY
REGISTER PARENT +234xxx, Name, ST-001
ADD EVENT Test | Description | 2024-12-25 | 10:00 | Meeting
SEND REMINDERS
```

---

**You're all set! Send your first message!** 🎉
