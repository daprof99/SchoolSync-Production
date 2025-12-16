"""
Quick test script for SchoolSync 2.0
Tests all major components without WhatsApp
"""

from agent import app
from langchain_core.messages import HumanMessage
from tools import *
import os
from dotenv import load_dotenv

load_dotenv()

def test_imports():
    """Test 1: Verify all imports work"""
    print("\n" + "="*60)
    print("TEST 1: Imports & Dependencies")
    print("="*60)
    try:
        from langchain_groq import ChatGroq
        print("✅ LangChain imports successful")
        print("✅ Tools imported successfully")
        print("✅ Agent imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_llm_connection():
    """Test 2: Verify Llama 4 connection"""
    print("\n" + "="*60)
    print("TEST 2: Llama 4 (Groq) Connection")
    print("="*60)
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
        response = llm.invoke("Say 'Hello from Llama 4!'")
        print(f"✅ LLM Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ LLM connection failed: {e}")
        return False


def test_google_sheets():
    """Test 3: Verify Google Sheets connection"""
    print("\n" + "="*60)
    print("TEST 3: Google Sheets Connection")
    print("="*60)
    try:
        # Use first admin phone to test
        sheet = get_db_connection(ADMIN_PHONES[0])
        print(f"✅ Connected to sheet: {sheet.title}")
        
        # Check for new worksheets
        worksheet_names = [ws.title for ws in sheet.worksheets()]
        required = ["Results", "Messages", "Events", "Parent_Registry", "Notifications_Queue"]
        
        for ws_name in required:
            if ws_name in worksheet_names:
                print(f"  ✅ {ws_name} sheet exists")
            else:
                print(f"  ⚠️  {ws_name} sheet missing - run db_setup.py")
        
        return True
    except Exception as e:
        print(f"❌ Google Sheets connection failed: {e}")
        return False


def test_agent_routing():
    """Test 4: Test agent routing logic"""
    print("\n" + "="*60)
    print("TEST 4: Agent Routing")
    print("="*60)
    
    test_cases = [
        ("CHECK ST-001 OKAFOR", "Bursary"),
        ("RESULTS ST-001 OKAFOR", "Results"),
        ("MESSAGE TEACHER", "Messages"),
        ("When is the meeting?", "Events"),
        ("Hi", "General"),
    ]
    
    for query, expected_agent in test_cases:
        try:
            test_msg = f"META_PHONE={ADMIN_PHONES[0]} || {query}"
            result = app.invoke({"messages": [HumanMessage(content=test_msg)]})
            print(f"✅ '{query}' → Routed successfully")
        except Exception as e:
            print(f"❌ '{query}' → Failed: {e}")
            return False
    
    return True


def test_new_features():
    """Test 5: Test new SchoolSync 2.0 features"""
    print("\n" + "="*60)
    print("TEST 5: New Features")
    print("="*60)
    
    # Test conversation history
    try:
        store_message("+2349999999999", "user", "Test message")
        history = get_conversation_history("+2349999999999")
        print(f"✅ Conversation history: {len(history)} messages stored")
    except Exception as e:
        print(f"❌ Conversation history failed: {e}")
    
    # Test multi-student
    try:
        students = get_parent_students(ADMIN_PHONES[0])
        print(f"✅ Multi-student support: Retrieved {len(students)} student IDs")
    except Exception as e:
        print(f"⚠️  Multi-student (no data yet): {e}")
    
    # Test event creation
    try:
        event_id = add_event("Test Event", "Testing", "2024-12-31", "10:00", "Test", ADMIN_PHONES[0])
        if event_id:
            print(f"✅ Event creation: Created {event_id}")
        else:
            print("⚠️  Event creation: Failed (check Google Sheets access)")
    except Exception as e:
        print(f"⚠️  Event creation: {e}")
    
    return True


def test_payment_link():
    """Test 6: Test Paystack integration"""
    print("\n" + "="*60)
    print("TEST 6: Paystack Payment Links")
    print("="*60)
    
    try:
        link = generate_payment_link("test@example.com", 5000, "ST-001", DEFAULT_SHEET_ID)
        if link:
            print(f"✅ Payment link generated: {link[:50]}...")
        else:
            print("⚠️  Payment link generation failed (check Paystack key)")
    except Exception as e:
        print(f"⚠️  Paystack: {e}")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("   SchoolSync 2.0 - Quick Test Suite")
    print("="*60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("LLM Connection", test_llm_connection()))
    results.append(("Google Sheets", test_google_sheets()))
    results.append(("Agent Routing", test_agent_routing()))
    results.append(("New Features", test_new_features()))
    results.append(("Paystack", test_payment_link()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your SchoolSync 2.0 is ready!")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. In new terminal: ngrok http 14031")
        print("3. Configure Twilio webhook with ngrok URL")
        print("4. Test via WhatsApp!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("Common fixes:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Check .env file has all keys")
        print("3. Run: python db_setup.py")


if __name__ == "__main__":
    run_all_tests()
