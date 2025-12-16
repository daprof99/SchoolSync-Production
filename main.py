import uvicorn
from fastapi import FastAPI, Form, Request, Response  # <--- Added Response import
from langchain_core.messages import HumanMessage
from agent import app
from tools import update_balance
from twilio.twiml.messaging_response import MessagingResponse

web_server = FastAPI()


@web_server.get("/")
def home():
    return {"status": "SchoolSync 2.0 is Live"}


@web_server.post("/whatsapp")
async def whatsapp(request: Request):
    form = await request.form()
    phone = form.get('From', '').replace('whatsapp:', '')
    msg = form.get('Body', '')
    print(f"📩 {phone}: {msg}")

    # Store conversation history
    from tools import store_message
    store_message(phone, "user", msg)

    agent_input = f"META_PHONE={phone} || {msg}"
    config = {"configurable": {"thread_id": phone}}

    # Run Agent
    try:
        out = app.invoke({"messages": [HumanMessage(content=agent_input)]}, config=config)

        # Handle Response Type (String vs Object Fix)
        last_message = out['messages'][-1]
        if isinstance(last_message, str):
            resp_text = last_message
        else:
            resp_text = last_message.content
        
        # Store bot response
        store_message(phone, "assistant", resp_text)

    except Exception as e:
        print(f"❌ Error: {e}")
        resp_text = "Sorry, I encountered an error. Please try again."

    print(f"🤖 Bot Reply: {resp_text}")  # Debug log to see what the bot wants to say

    # Generate TwiML
    resp = MessagingResponse()
    resp.message(resp_text)

    # --- CRITICAL FIX: Force XML Response ---
    xml_response = str(resp)
    print(f"📦 TwiML Response: {xml_response}")
    return Response(content=xml_response, media_type="application/xml; charset=utf-8")


@web_server.post("/paystack-webhook")
async def paystack_webhook(request: Request):
    payload = await request.json()
    if payload.get('event') == 'charge.success':
        data = payload['data']
        student_id = data['metadata']['student_id']
        amount = data['amount'] / 100
        
        # Update balance
        # Update balance
        school_id = data['metadata'].get('school_sheet_id') or data['metadata'].get('school_id')
        update_balance(
            school_id,
            student_id,
            amount
        )
        
        # Send payment confirmation
        from tools import send_payment_confirmation
        parent_phone = data['metadata'].get('parent_phone', '')
        if parent_phone:
            send_payment_confirmation(parent_phone, student_id, amount)
        
        print(f"💰 Payment Confirmed: {data['reference']}")
    return {"status": "success"}


if __name__ == "__main__":
    # Use Port 14031 (or whatever port you are currently forwarding)
    uvicorn.run(web_server, host="0.0.0.0", port=14031)